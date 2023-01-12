import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

current_file = Path(__file__)
project_dir = current_file.parent
dockerfile_dir = project_dir / "dockerfile"
docker_compose_file = project_dir / "docker-compose.yaml"
base_image_tag = "zj-brain-science-platform-base"
base_image_dockerfile = dockerfile_dir / "base.Dockerfile"
mkdirs = [
    "~/log/ZJBrainSciencePlatform/app",
    "~/log/ZJBrainSciencePlatform/mysql",
    "~/data/ZJBrainSciencePlatform/file",
    "~/mysql/ZJBrainSciencePlatform/data",
]

alias = {
    # "docker": "podman",
}

commands = {}


def add_command(func):
    command_name = func.__name__.replace("_", "-")
    commands[command_name] = func
    return func


@add_command
def up_platform():
    for dir_ in mkdirs:
        os.makedirs(dir_, exist_ok=True)
    build_base_image()
    docker_compose("up", "--detach", "--build", "platform")


@add_command
def up_database():
    if not docker_compose_service_running("database"):
        docker_compose("up", "--detach", "--build", "database", check=True)


@add_command
def up_cache():
    if not docker_compose_service_running("cache"):
        docker_compose("up", "--detach", "--build", "cache", check=True)


@add_command
def run_alembic_bash():
    up_database()
    build_base_image()
    docker_compose("run", "--rm", "alembic", "bash")


@add_command
def up_platform_depends():
    up_database()
    up_cache()


@add_command
def clear():
    docker_compose("down", "--rmi", "all", "--remove-orphans", check=False)
    run("docker", "system", "prune")
    run("docker", "image", "rm", base_image_tag)


@add_command
def format():
    poetry_run("isort", str(project_dir))
    poetry_run("black", str(project_dir))


def build_base_image():
    run(
        "docker",
        "build",
        "--file",
        str(base_image_dockerfile),
        "--tag",
        base_image_tag,
        str(project_dir),
    )


def docker_compose_service_running(service: str) -> bool:
    process = docker_compose("top", service, capture_output=True)
    return any(line for line in process.stdout.split("\n"))


def docker_compose(*args: str, **kwargs: Any) -> CompletedProcess:
    return run("docker", "compose", "--file", str(docker_compose_file), *args, **kwargs)


def poetry_run(*args: str, **kwargs: Any) -> CompletedProcess:
    with InProject(project_dir):
        return run("poetry", "run", *args, **kwargs)


def run(executable: str, *args: str, **kwargs: Any) -> CompletedProcess:
    if executable in alias:
        executable = alias[executable]
    command = [executable, *args]
    print(f"RUN {' '.join(command)}")
    return subprocess.run(command, text=True, **kwargs)


class InProject:
    def __init__(self, new_cwd: Path | str, cur_cwd: Path | str | None = None):
        if cur_cwd is None:
            cur_cwd = os.getcwd()
        self.cur_cwd = cur_cwd
        self.new_cwd = new_cwd

    def __enter__(self):
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cur_cwd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("command", help="command to run", choices=commands.keys())
    args = parser.parse_args()
    command_func = commands[args.command]
    command_func()
