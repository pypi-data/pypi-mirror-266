from pathlib import Path
import docker
from loguru import logger


def log_docker_output(build_logs):
    for line in build_logs:
        stream = line.pop("stream", "").strip()
        if stream:
            logger.info(stream)
        if line:
            logger.debug(line)


def log_docker_error(build_logs):
    for line in build_logs:
        if "stream" in line:
            logger.error(line["stream"].strip())


def push_image(client: docker.DockerClient, name, tag):
    try:
        output = client.images.push(name, tag, stream=True, decode=True)
    except docker.errors.APIError as e:
        logger.error(e)
        raise
    for line in output:
        if "errorDetail" in line:
            raise RuntimeError(f"Failed to push {name}:{tag} - {line['errorDetail']['message']}")


def build_image(
    context: Path,
    tag: str,
    buildargs: dict = None,
    rm: bool = True,
    quiet: bool = False,
    nocache: bool = False,
    dockerfile: str = None,
    timeout: int = 600,
):
    buildargs = buildargs or {}
    client = docker.from_env(timeout=timeout)
    try:
        image, build_logs = client.images.build(
            path=str(context),
            tag=tag,
            rm=rm,
            quiet=quiet,
            buildargs=buildargs,
            nocache=nocache,
            dockerfile=dockerfile,
        )
    except docker.errors.BuildError as e:
        log_docker_error(e.build_log)
        raise
    log_docker_output(build_logs)
    return image
