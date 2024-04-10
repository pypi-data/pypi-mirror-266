import asyncio
import copy
import json

from jupyterhub.crypto import decrypt
from jupyterhub.crypto import encrypt
from outpostspawner.misc import Thread
from tornado import web

from ..misc import get_custom_config
from ..misc import get_encrypted_user_options

_general_spawn_event = asyncio.Event()


def get_general_spawn_event():
    global _general_spawn_event
    return _general_spawn_event


def check_formdata_keys(data):
    keys = data.keys()
    custom_config = get_custom_config()
    systems_config = custom_config.get("systems")
    unicore_systems = []
    for system_name, sys_config in systems_config.items():
        backend_service = sys_config.get("backendService", "")
        if (
            custom_config.get("backendServices", {})
            .get(backend_service, {})
            .get("type", "")
            == "unicore"
        ):
            unicore_systems.append(system_name)
    required_keys = {"name", "profile", "system"}
    if data.get("system") in unicore_systems:
        required_keys = required_keys | {"account", "project", "partition"}
    allowed_keys = required_keys | {
        "image",
        "userdata_path",
        "flavor",
        "reservation",
        "nodes",
        "gpus",
        "runtime",
        "xserver",
        "userModules",
        "dockerregistry",
    }

    if not required_keys <= keys:
        raise KeyError(f"Keys must include {required_keys}, but got {keys}.")
    if not keys <= allowed_keys:
        raise KeyError(f"Got keys {keys}, but only {allowed_keys} are allowed.")


async def get_options_from_form(formdata):
    check_formdata_keys(formdata)

    custom_config = get_custom_config()
    systems_config = custom_config.get("systems")
    resources = custom_config.get("resources")

    def skip_resources(key, value):
        system = formdata.get("system")[0]
        partition = formdata.get("partition")[0]
        resource_keys = ["nodes", "gpus", "runtime"]
        if key in resource_keys:
            if partition in systems_config.get(system, {}).get(
                "interactivePartitions", []
            ):
                return True
            else:
                if key not in resources.get(system.upper()).get(partition).keys():
                    return True
        else:
            if value in ["undefined", "None"]:
                return True
        return False

    def runtime_update(key, value_list):
        if key == "resource_runtime":
            return int(value_list[0]) * 60
        return value_list[0]

    return {
        key: runtime_update(key, value)
        for key, value in formdata.items()
        if not skip_resources(key, value[0])
    }


def sync_encrypt(data):
    loop = asyncio.new_event_loop()

    async def wait_for_future(future):
        return await future

    def t_encrypt(loop, data):
        asyncio.set_event_loop(loop)
        ret = loop.run_until_complete(wait_for_future(encrypt(data)))
        return ret

    t = Thread(target=t_encrypt, args=(loop, data))
    t.start()
    ret = t.join()
    return ret


def sync_decrypt(data):
    loop = asyncio.new_event_loop()

    async def wait_for_future(future):
        return await future

    def t_decrypt(loop, data):
        asyncio.set_event_loop(loop)
        ret = loop.run_until_complete(
            wait_for_future(decrypt(data[len("encrypted-") :]))
        )
        return ret

    t = Thread(target=t_decrypt, args=(loop, data))
    t.start()
    ret = t.join()
    return ret


class EncryptJSONBody:
    def get_json_body(self):
        """Return the body of the request as JSON data."""
        if not self.request.body:
            return None
        body = self.request.body.strip().decode("utf-8")
        try:
            model = json.loads(body)
        except Exception:
            self.log.debug("Bad JSON: %r", body)
            self.log.error("Couldn't parse JSON", exc_info=True)
            raise web.HTTPError(400, "Invalid JSON in body of request")
        encrypted_user_options = get_encrypted_user_options()
        for user_option in encrypted_user_options:
            if user_option in model.keys():
                user_option_bytes = sync_encrypt(model[user_option])
                model[user_option] = f"encrypted-{user_option_bytes.decode('utf-8')}"
        return model


def decrypted_user_options(user):
    if not user:
        return {}
    try:
        username = user.name
    except:
        username = "unknown"
    try:
        encrypted_user_options = get_encrypted_user_options()
        decrypted_user_options = {}
        for orm_spawner in user.orm_user._orm_spawners:
            if not orm_spawner.user_options:
                decrypted_user_options[orm_spawner.name] = {}
                continue
            decrypted_user_options[orm_spawner.name] = copy.deepcopy(
                orm_spawner.user_options
            )
            for key in encrypted_user_options:
                if orm_spawner.user_options and key in orm_spawner.user_options:
                    decrypted_user_options[orm_spawner.name][key] = sync_decrypt(
                        orm_spawner.user_options[key]
                    )
        return decrypted_user_options
    except:
        user.log.exception(f"Could not load decrypted user options for {username}")
        return {}
