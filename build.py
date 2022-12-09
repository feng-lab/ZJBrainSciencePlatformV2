import os
import subprocess
from pathlib import Path
from subprocess import CompletedProcess

from rich import print
from typer import Typer

app = Typer()

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


@app.command()
def up_backend():
    for dir_ in mkdirs:
        os.makedirs(dir_, exist_ok=True)
    build_base_image()
    docker_compose("up", "--detach", "--build", "backend")


@app.command()
def up_database():
    docker_compose("up", "--detach", "--build", "database")


@app.command()
def run_alembic_bash():
    up_database()
    build_base_image()
    docker_compose("run", "--rm", "alembic", "bash")


@app.command()
def clear():
    docker_compose("down", "--rmi", "all", "--remove-orphans", check=False)
    run("docker", "system", "prune")
    run("docker", "image", "rm", base_image_tag)


@app.command()
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


def docker_compose(*args: str, check: bool = True) -> CompletedProcess:
    return run("docker", "compose", "--file", str(docker_compose_file), *args, check=check)


def poetry_run(*args: str, check: bool = True) -> CompletedProcess:
    with InProject(os.getcwd(), project_dir):
        return run("poetry", "run", *args, check=check)


def run(*command: str, check: bool = True) -> CompletedProcess:
    print(f"[bold green]RUN {' '.join(command)}[/bold green]")
    return subprocess.run(command, check=check)


class InProject:
    def __init__(self, prev_cwd: Path | str, new_cwd: Path | str):
        self.prev_cwd = prev_cwd
        self.new_cwd = new_cwd

    def __enter__(self):
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.prev_cwd)


if __name__ == "__main__":
    app()
