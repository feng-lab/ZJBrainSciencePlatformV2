import os
import subprocess
from pathlib import Path

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
def start_database():
    docker_compose("up", "--detach", "--build", "database")


@app.command()
def run_alembic_bash():
    start_database()
    build_base_image()
    docker_compose("run", "--rm", "alembic", "bash")


@app.command()
def clear():
    docker_compose("down", "--rmi", "all", "--remove-orphans")
    run("docker", "system", "prune")
    run("docker", "image", "rm", base_image_tag)


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


def docker_compose(*args: str) -> subprocess.CompletedProcess:
    return run("docker-compose", "--file", str(docker_compose_file), *args)


def run(*command: str) -> subprocess.CompletedProcess:
    print(f"[bold]RUN {' '.join(command)}[/bold]")
    return subprocess.run(command, check=True)


if __name__ == "__main__":
    app()
