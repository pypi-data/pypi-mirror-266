import click
from typing import List
from lookout_cli.helpers import (
    docker_compose_path,
    get_project_root,
    docker_bake,
    call,
    get_version,
)

from python_on_whales.docker_client import DockerClient
from python_on_whales.utils import ValidPath
import lookout_config
from lookout_config import LookoutConfig, LogLevel, Mode, Network
import os

DOCKER = docker_compose_path("./docker-compose.yaml")
DOCKER_DEV = docker_compose_path("./docker-compose.dev.yaml")
DOCKER_NETWORK_SHARED = docker_compose_path("./docker-compose.network-shared.yaml")
DOCKER_NETWORK_HOST = docker_compose_path("./docker-compose.network-host.yaml")
DOCKER_GPU = docker_compose_path("./docker-compose.gpu.yaml")

SERVICES = [
    "lookout_core",
    "lookout_ui",
    "lookout_greenstream",
    "lookout_docs",
]


def _get_compose_files(
    prod: bool = False, network: Network = Network.HOST, gpu=False
) -> List[ValidPath]:
    compose_files: List[ValidPath] = [DOCKER]

    if not prod:
        compose_files.append(DOCKER_DEV)

    if network == Network.SHARED:
        compose_files.append(DOCKER_NETWORK_SHARED)

    if network == Network.HOST:
        compose_files.append(DOCKER_NETWORK_HOST)

    if gpu:
        compose_files.append(DOCKER_GPU)

    return compose_files


def log_config(config: LookoutConfig):
    click.echo(click.style("[+] Lookout Config:", fg="green"))
    for attr, value in config.__dict__.items():
        click.echo(
            click.style(f" ⠿ {attr}: ".ljust(27), fg="white") + click.style(str(value), fg="green")
        )


@click.command(name="up")
@click.option(
    "--build",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we rebuild the docker containers? Default: False",
)
@click.option(
    "--pull",
    help="Should we do a docker pull",
    is_flag=True,
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def up(
    build: bool,
    pull: bool,
    services: List[str],
):
    """Starts lookout"""
    config = lookout_config.read()
    version = get_version()
    prod = version != "latest"
    log_config(config)

    os.environ["ROS_DOMAIN_ID"] = str(config.ros_domain_id)
    os.environ["LOOKOUT_NAMESPACE_VESSEL"] = config.namespace_vessel
    os.environ["LOOKOUT_VERSION"] = version
    os.environ[
        "LOOKOUT_CORE_COMMAND"
    ] = "platform ros launch lookout_bringup lookout.launch.py --build --watch"

    services_list = list(services) if services else None

    docker = DockerClient(
        compose_files=_get_compose_files(prod, config.network, config.gpu),
        compose_project_directory=get_project_root(),
    )
    docker.compose.up(
        services_list, detach=True, build=build, pull="always" if pull else "missing"
    )

    click.echo(click.style("UI started: http://localhost:4000", fg="green"))


@click.command(name="down")
@click.argument("args", nargs=-1)
def down(args: List[str]):
    """Stops lookout"""

    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.down()


@click.command(name="build")
@click.option(
    "--no-cache",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we rebuild without the docker cache?",
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def build(no_cache: bool, services: List[str]):
    """Builds the Lookout docker containers"""
    config = lookout_config.read()
    os.environ["LOOKOUT_NAMESPACE_VESSEL"] = config.namespace_vessel
    os.environ["GPU"] = "true" if config.gpu else "false"

    docker = DockerClient(
        compose_files=_get_compose_files(gpu=config.gpu),
        compose_project_directory=get_project_root(),
    )
    services_list = list(services) if services else None

    docker.compose.build(services=services_list, cache=not no_cache)


@click.command(name="bake")
@click.option(
    "--version",
    type=str,
    required=True,
    help="The version to bake. Default: latest",
)
@click.option(
    "--push",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we push the images to the registry? Default: False",
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def bake(version: str, push: bool, services: List[str]):  # type: ignore
    """Bakes the docker containers"""
    compose_files = _get_compose_files()
    docker_bake(
        version=version,
        services=services,
        push=push,
        compose_files=compose_files,
    )


@click.command(name="lint")
def lint():
    """Lints all the things"""
    call("pre-commit run --all")


@click.command(name="type-generate")
def type_generate():  # type: ignore
    """Generates typescript types for all ros messages"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run("lookout_core", ["npx", "ros-typescript-generator"])


@click.command(name="upgrade")
@click.option("--version", help="The version to upgrade to.")
def upgrade(version: str):
    """Upgrade Lookout CLI"""
    click.echo(f"Current version: {get_version()}")
    result = click.prompt(
        "Are you sure you want to upgrade?", default="y", type=click.Choice(["y", "n"])
    )
    if result == "n":
        return

    if version:
        call(f"pip install --upgrade lookout-cli=={version}")
    else:
        call("pip install --upgrade lookout-cli")

    click.echo(click.style("Upgrade of Lookout CLI complete.", fg="green"))


@click.command(name="authenticate")
@click.option(
    "--username",
    help="The username to use for authentication.",
    required=True,
    prompt=True,
)
@click.option("--token", help="The token to use for authentication.", required=True, prompt=True)
def authenticate(username: str, token: str):
    """
    Authenticate with the package repository so that you can pull images.

    To get a username and token you'll need to contact a Greenroom Robotics employee.
    """
    call(f"echo {token} | docker login ghcr.io -u {username} --password-stdin")


@click.command(name="config")
def config():  # type: ignore
    """Read Config"""
    config = lookout_config.read()
    log_config(config)


@click.command(name="configure")
@click.option("--default", is_flag=True, help="Use default values")
def configure(default: bool):  # type: ignore
    """Configure Lookout"""

    if default:
        config = LookoutConfig()
        lookout_config.write(config)
    else:
        # Check if the file exists
        if os.path.exists(lookout_config.get_path()):
            click.echo(
                click.style(
                    f"Lookout config already exists: {lookout_config.get_path()}",
                    fg="yellow",
                )
            )
            result = click.prompt(
                "Do you want to overwrite it?", default="y", type=click.Choice(["y", "n"])
            )
            if result == "n":
                return

        try:
            config_current = lookout_config.read()
        except Exception:
            config_current = LookoutConfig()

        config = LookoutConfig(
            ros_domain_id=click.prompt(
                "ROS Domain ID", default=config_current.ros_domain_id, type=int
            ),
            namespace_vessel=click.prompt(
                "Namespace Vessel", default=config_current.namespace_vessel
            ),
            mode=click.prompt(
                "Mode",
                default=config_current.mode,
                type=click.Choice([item.value for item in Mode]),
            ),
            gama_vessel=click.prompt(
                "Is this running on a Gama Vessel?",
                default=config_current.gama_vessel,
                type=bool,
            ),
            log_level=click.prompt(
                "Log level",
                default=config_current.log_level,
                type=click.Choice([item.value for item in LogLevel]),
            ),
            network=click.prompt(
                "Network",
                default=config_current.network,
                type=click.Choice([item.value for item in Network]),
            ),
            gpu=click.prompt(
                "Should we use the GPU?",
                default=config_current.gpu,
                type=bool,
            ),
        )
        lookout_config.write(config)
