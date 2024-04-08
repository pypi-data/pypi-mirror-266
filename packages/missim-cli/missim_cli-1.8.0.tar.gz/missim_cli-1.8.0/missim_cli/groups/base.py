import os
from typing import List

import click
from python_on_whales.docker_client import DockerClient
from python_on_whales.utils import ValidPath

import missim_config
from missim_config import MissimConfig, LogLevel, Network, Mode

from missim_cli.helpers import (
    docker_compose_path,
    get_project_root,
    call,
    get_missim_version,
    is_dev_version,
    docker_bake,
)

DOCKER_ORG = "ghcr.io/greenroom-robotics"

DOCKER = docker_compose_path("./docker-compose.yaml")
DOCKER_DEV = docker_compose_path("./docker-compose.dev.yaml")
DOCKER_NETWORK_SHARED = docker_compose_path("./docker-compose.network-shared.yaml")
DOCKER_NETWORK_HOST = docker_compose_path("./docker-compose.network-host.yaml")
DOCKER_UE_EDITOR = docker_compose_path("./docker-compose.ue_editor.yaml")
DOCKER_UE_EDITOR_SHARED = docker_compose_path("./docker-compose.ue_editor.shared.yaml")
DOCKER_UE_EDITOR_HOST = docker_compose_path("./docker-compose.ue_editor.host.yaml")
DOCKER_UE_STANDALONE = docker_compose_path("./docker-compose.ue_standalone.yaml")
DOCKER_UE_STANDALONE_SHARED = docker_compose_path("./docker-compose.ue_standalone.shared.yaml")
DOCKER_UE_STANDALONE_HOST = docker_compose_path("./docker-compose.ue_standalone.host.yaml")


SERVICES = [
    "missim_ui",
    "missim_core",
    "missim_ue",
    "missim_ue_standalone",
    "missim_chart_tiler",
]


def _get_compose_files(
    mode: Mode, dev_mode: bool = False, network: Network = Network.HOST
) -> List[ValidPath]:
    compose_files: List[ValidPath] = [DOCKER]
    if dev_mode:
        compose_files.append(DOCKER_DEV)

    if network == Network.HOST:
        compose_files.append(DOCKER_NETWORK_HOST)
    if network == Network.SHARED:
        compose_files.append(DOCKER_NETWORK_SHARED)

    if mode == Mode.UE_EDITOR:
        compose_files.append(DOCKER_UE_EDITOR)
        if network == Network.HOST:
            compose_files.append(DOCKER_UE_EDITOR_HOST)
        if network == Network.SHARED:
            compose_files.append(DOCKER_UE_EDITOR_SHARED)
    elif mode == Mode.UE_STANDALONE:
        compose_files.append(DOCKER_UE_STANDALONE)
        if network == Network.HOST:
            compose_files.append(DOCKER_UE_STANDALONE_HOST)
        if network == Network.SHARED:
            compose_files.append(DOCKER_UE_STANDALONE_SHARED)

    return compose_files


def log_config(config: MissimConfig):
    click.echo(click.style("[+] MIS-SIM Config:", fg="green"))
    for attr, value in config.__dict__.items():
        click.echo(
            click.style(f" ⠿ {attr}: ".ljust(26), fg="white") + click.style(str(value), fg="green")
        )


@click.group(help="Commands for the sim")
def sim():
    pass


@click.command(name="build")
@click.option(
    "-m",
    "--mode",
    type=click.Choice(Mode),  # type: ignore
)
@click.option(
    "-c",
    "--clean",
    help="Should the UE project be cleaned?",
    is_flag=True,
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def build(mode: Mode, clean: bool, services: List[str]):
    """Builds the sim"""
    # If building standalone, we first build the dev sim

    config = missim_config.read()
    os.environ["ROS_DOMAIN_ID"] = str(config.ros_domain_id)
    log_config(config)

    services_list = list(services) if services else None
    if config.mode == Mode.LOW_FIDELITY:
        docker = DockerClient(
            compose_files=_get_compose_files(config.mode, config.network),
            compose_project_directory=get_project_root(),
        )
        docker.compose.build(services=services_list)
        return

    # If we are not low-fidelity, we must do Unreal things....

    # check UE cache dir
    prj_root = get_project_root()
    if not prj_root:
        raise RuntimeError("Could not find project root")

    docker_ue_editor = DockerClient(
        compose_files=_get_compose_files(Mode.UE_EDITOR, config.network),
        compose_project_directory=get_project_root(),
    )
    # build ue-dev container
    docker_ue_editor.compose.build(cache=True, services=services_list)

    if config.mode == Mode.UE_STANDALONE:

        if clean:
            clean_command = """cd "${PROJECTS_HOME}/MissimProject" && ue4 clean && rm -rf dist"""
            docker_ue_editor.compose.run("missim_ue", ["bash", "-c", clean_command])

        # run compile command first to build the Plugins for the Editor target
        compile.callback(clean=False)  # type: ignore

        missing_dir_hack = """ && mkdir -p dist/Linux/Engine/Binaries"""
        proj_hack = """ && mkdir -p "dist/Linux/Engine/Plugins/Runtime/GeoReferencing/Resources/" && cp -r ${UNREAL_HOME}/Engine/Plugins/Runtime/GeoReferencing/Resources/PROJ dist/Linux/Engine/Plugins/Runtime/GeoReferencing/Resources/"""
        # run UE package command to compile and cook the UE project, making the `dist` directory
        ue_project_package_command = (
            """cd "${PROJECTS_HOME}/MissimProject" && ${UNREAL_HOME}/Engine/Build/BatchFiles/RunUAT.sh  -ScriptsForProject="${PWD}/${PROJECT_NAME}.uproject" Turnkey -command=VerifySdk -platform=Linux -UpdateIfNeeded -project="${PWD}/${PROJECT_NAME}.uproject" BuildCookRun -nop4 -utf8output -nocompileeditor -skipbuildeditor -cook  -project="${PWD}/${PROJECT_NAME}.uproject"  -unrealexe="${UNREAL_HOME}/Engine/Binaries/Linux/UnrealEditor" -platform=Linux -stage -archive -package -build -pak -compressed -prereqs -archivedirectory="${PWD}/dist/" -clientconfig=Development -nocompile -nocompileuat"""
            + missing_dir_hack
            + proj_hack
        )
        docker_ue_editor.compose.run("missim_ue", ["bash", "-c", ue_project_package_command])

        # for some reason this directory is required to exist otherwise standalone does not launch
        # projects/MissimProject/dist/Linux/Engine/Binaries
        # the PROJ resources are also not installed correctly during the package command
        # what in the actual hell is going on with packaging?

        docker_ue_standalone = DockerClient(
            compose_files=_get_compose_files(Mode.UE_STANDALONE, config.network),
            compose_project_directory=get_project_root(),
        )

        docker_ue_standalone.compose.build()


@click.command(name="up")
@click.option(
    "--spin",
    help="Sleep indefinitely instead of bringing up Unreal",
    is_flag=True,
)
@click.option(
    "--build",
    help="Should we do a docker build",
    is_flag=True,
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def up(spin: bool, build: bool, services: List[str]):
    """Starts the simulator"""
    config = missim_config.read()
    mode = config.mode
    dev_mode = is_dev_version()
    os.environ["ROS_DOMAIN_ID"] = str(config.ros_domain_id)
    os.environ["USE_HTTPS"] = "true" if config.use_https else "false"
    os.environ["MISSIM_VERSION"] = get_missim_version()
    os.environ["MISSIM_CONFIG"] = missim_config.serialise(config)
    log_config(config)

    docker = DockerClient(
        compose_files=_get_compose_files(mode, dev_mode=dev_mode, network=config.network),
        compose_project_directory=get_project_root(),
    )
    if spin:
        if mode == "standalone":
            docker.compose.run(
                "missim_ue",
                ["sleep", "inf"],
                remove=True,
            )
        if mode == "dev":
            docker.compose.run(
                "missim",
                ["sleep", "inf"],
                remove=True,
            )
    else:
        services_list = list(services) if services else None
        docker.compose.up(detach=True, services=services_list, build=build)


@click.command(name="compile")
@click.option(
    "-c",
    "--clean",
    help="Should the UE project be cleaned?",
    is_flag=True,
)
def compile(clean: bool = False):
    """Compile the UE project"""
    docker = DockerClient(
        compose_files=[DOCKER_UE_EDITOR],
        compose_project_directory=get_project_root(),
    )
    if clean:
        docker.compose.run(
            "missim_ue",
            ["bash", "--login", "-c", 'cd "${PROJECTS_HOME}/MissimProject" && ue4 clean'],
            remove=True,
        )
    # TODO RENAME TARGETS WITH SAME SUFFIX AS PROJECT NAME CASE SENSITIVE!
    build_cmd = """${UNREAL_HOME}/Engine/Build/BatchFiles/RunUBT.sh MissimProjectEditor Development Linux -Project="${PWD}/${PROJECT_NAME}.uproject" -SkipUBTBuild -NoEngineChanges"""
    docker.compose.run(
        "missim_ue",
        ["bash", "--login", "-c", 'cd "${PROJECTS_HOME}/MissimProject" && ' + build_cmd],
        remove=True,
    )


@click.command(name="down")
@click.argument("args", nargs=-1)
def down(args: List[str]):
    """Stops the sim"""
    config = missim_config.read()
    mode = config.mode
    os.environ["ROS_DOMAIN_ID"] = str(config.ros_domain_id)
    log_config(config)

    docker = DockerClient(
        compose_files=_get_compose_files(mode),
        compose_project_directory=get_project_root(),
    )
    docker.compose.down()


@click.command(name="base-ue")
@click.option(
    "--ue-version",
    type=str,
    default="5.3.2",
    help="The release version of Unreal Engine to build",
)
@click.option(
    "--memory",
    type=str,
    default=None,
    help="Set maximum memory for the docker build",
)
def base_ue(ue_version: str, memory: str):
    """Builds the base Unreal Engine image for development"""

    cuda_ver = "12.2.0"
    ubuntu_ver = "22.04"

    args = ""
    if memory is not None:
        args += f" --memory {memory}"

    call(
        f"ue4-docker build {ue_version} --cuda={cuda_ver} -basetag=ubuntu{ubuntu_ver} --target=full -username={os.environ['GH_USERNAME']} -password={os.environ['API_TOKEN_GITHUB']}{args} --opt credential_mode=secrets --exclude ddc",
        env={"UE4DOCKER_TAG_NAMESPACE": DOCKER_ORG},
    )


@click.command(name="upgrade")
@click.option("--version", help="The version to upgrade to.")
def upgrade(version: str):
    """Upgrade MISSIM CLI"""
    click.echo(f"Current version: {get_missim_version()}")
    result = click.prompt(
        "Are you sure you want to upgrade?", default="y", type=click.Choice(["y", "n"])
    )
    if result == "n":
        return

    if version:
        call(f"pip install --upgrade missim-cli=={version}")
    else:
        call("pip install --upgrade missim-cli")

    click.echo(click.style("Upgrade of MISSIM CLI complete.", fg="green"))
    click.echo(
        click.style(
            "Run `missim vessel install` or `missim gs install` to upgrade MISSIM.", fg="green"
        )
    )


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
    Authenticate with the MISSIM package repository so that you can pull images.

    To get a username and token you'll need to contact a Greenroom Robotics employee.
    """
    call(f"echo {token} | docker login ghcr.io -u {username} --password-stdin")


@click.command(name="configure")
@click.option("--default", is_flag=True, help="Use default values")
def configure(default: bool):  # type: ignore
    """Configure MIS-SIM"""

    if default:
        config = MissimConfig()
        missim_config.write(config)
    else:
        # Check if the file exists
        if os.path.exists(missim_config.get_path()):
            click.echo(
                click.style(
                    f"MIS-SIM config already exists: {missim_config.get_path()}",
                    fg="yellow",
                )
            )
            result = click.prompt(
                "Do you want to overwrite it?", default="y", type=click.Choice(["y", "n"])
            )
            if result == "n":
                return

        try:
            config_current = missim_config.read()
        except Exception:
            config_current = MissimConfig()

        config = MissimConfig(
            ros_domain_id=click.prompt(
                "ROS domain ID", default=config_current.ros_domain_id, type=int
            ),
            network=click.prompt(
                "Network",
                default=config_current.network,
                type=click.Choice([item.value for item in Network]),
            ),
            log_level=click.prompt(
                "Log level",
                default=config_current.log_level,
                type=click.Choice([item.value for item in LogLevel]),
            ),
            mode=click.prompt(
                "Mode",
                default=config_current.mode,
                type=click.Choice([item.value for item in Mode]),
            ),
            sim_speed=click.prompt(
                "Simulation speed", default=config_current.sim_speed, type=float
            ),
        )
        missim_config.write(config)


@click.command(name="type-generate")
def type_generate():  # type: ignore
    """Generates typescript types for all ros messages"""
    docker = DockerClient(
        compose_files=_get_compose_files(Mode.LOW_FIDELITY),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run("missim_core", ["npx", "ros-typescript-generator"])


@click.command(name="test-core")
def test_core():  # type: ignore
    """Runs the tests for missim_core"""
    docker = DockerClient(
        compose_files=_get_compose_files(Mode.LOW_FIDELITY, dev_mode=True),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run(
        "missim_core", ["platform", "ros", "test", "--package", "vessel_manager", "--build"]
    )


@click.command(name="config")
def config():  # type: ignore
    """Read Config"""
    config = missim_config.read()
    log_config(config)


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
@click.argument("services", nargs=-1)
def bake(version: str, push: bool, services: List[str]):  # type: ignore
    """Bakes the docker containers"""
    compose_files = _get_compose_files(Mode.LOW_FIDELITY, dev_mode=True)
    docker_bake(
        version=version,
        services=services,
        push=push,
        compose_files=compose_files,
    )
