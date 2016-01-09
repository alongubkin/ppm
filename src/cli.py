import os
import click

import dockerpty

from docker_client_factory import DockerClientFactory

from package import Package
from package_serializer import PackageSerializer
from package_loader import PackageLoader

MOUNT_DIRECTORY = "/usr/src/app"

@click.group()
def cli():
    pass

@click.command()
@click.option("--name", prompt="Name",
              default=lambda: os.path.basename(os.getcwd()))
@click.option("--version", prompt="Version", default="1.0.0")
@click.option("--description", prompt="Description", default="")
@click.option("--entry-point", prompt="Entry Point", default="main.py")
@click.option("--base-image", prompt="Base Image",
              default="library/python:3-onbuild")
def init(name, version, description, entry_point, base_image):
    package = Package(name, version, description, entry_point, base_image)

    loader = PackageLoader()
    loader.save(os.getcwd(), package)

@click.command()
def run():
    loader = PackageLoader()
    package = loader.load(os.getcwd())

    client_factory = DockerClientFactory()
    client = client_factory.get_client()

    container = client.create_container(
        image=package.current_image,
        stdin_open=True,
        tty=True,
        command="python {}".format(package.entry_point),
        working_dir=MOUNT_DIRECTORY,
        host_config=client.create_host_config(binds={
            os.getcwd(): {
                "bind": MOUNT_DIRECTORY,
                "mode": "rw"
            }
        })
    )

    dockerpty.start(client, container)

@click.command()
def install():
    loader = PackageLoader()
    package = loader.load(os.getcwd())

    client_factory = DockerClientFactory()
    client = client_factory.get_client()

    container = client.create_container(
        image=package.current_image,
        stdin_open=True,
        tty=True,
        command="pip install flask",
        working_dir=MOUNT_DIRECTORY,
        host_config=client.create_host_config(binds={
            os.getcwd(): {
                "bind": MOUNT_DIRECTORY,
                "mode": "rw"
            }
        })
    )

    dockerpty.start(client, container)

    # Update package image
    package.current_image = client.commit(container.get("Id")).get("Id")
    loader.save(os.getcwd(), package)

cli.add_command(init)
cli.add_command(run)
cli.add_command(install)

if __name__ == "__main__":
    cli()
