import inspect
from pathlib import Path
import re
import docker

from loguru import logger
from deploymodel.io import ModelOutput


def get_input_model(handler):
    input_model = handler.__annotations__.get("input")
    if not input_model:
        raise ValueError(f"Handler {handler.__name__} must have an input type annotation")
    return input_model


def get_response_model(handler):
    response_model = handler.__annotations__.get("return")
    if not response_model:
        raise ValueError(f"Handler {handler.__name__} must have a return type annotation")
    valid_primitives = (str, int, float, bool)
    if not issubclass(response_model, ModelOutput) and not issubclass(response_model, valid_primitives):
        raise ValueError(
            f"Handler {handler.__name__} return type must be one of {valid_primitives} or a subclass of deploymodel {ModelOutput}. got {response_model}"
        )
    return response_model


def register(config):
    handler = config.get("handler")
    init = config.get("init")
    if not handler:
        raise ValueError("Config must have a 'handler' key")
    if not init:
        raise ValueError("Config must have a 'init' key")
    try:
        get_input_model(handler)
        get_response_model(handler)
    except Exception as e:
        raise ValueError(f"Error validating handler: {str(e)}")

    caller_frame_record = inspect.stack()[1]
    frame = caller_frame_record[0]
    info = inspect.getframeinfo(frame)
    module = str(Path(info.filename))
    print(f"Init {module}:{init.__name__} Handler {module}:{handler.__name__} registered successfully.")


def get_module_and_handler_and_init(client, image):
    try:
        stdout = client.containers.run(image, remove=True).decode("utf-8")
    except docker.errors.ContainerError as e:
        raise RuntimeError(e.stderr.decode("utf-8"))
    try:
        match = re.match(r"Init (.*) Handler (.*) registered successfully", stdout)
        module_init = match.group(1)
        module_handler = match.group(2)
        module, handler = module_handler.split(":")
        _, init = module_init.split(":")
        logger.debug(f"Parsed module {module=} {handler=} {init=}")
        return module, handler, init
    except Exception:
        logger.error(
            'Registration failed, does your Dockerfile correctly register the handler by calling register({"handler": handler, "init": init}) as documented?'
        )
        logger.error(stdout.decode("utf-8"))
        raise


def get_remote_env_var(client, image, var):
    stdout = client.containers.run(
        image=image,
        entrypoint="/bin/sh",
        command=["-c", f"echo ${var}"],
        remove=True,  # Automatically remove the container when it exits
    )
    return stdout.decode("utf-8").strip()


__all__ = [
    "register",
    "get_input_model",
    "get_response_model",
    "get_module_and_handler_and_init",
    "get_remote_env_var",
]
