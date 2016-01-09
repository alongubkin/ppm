import os
import click

import dockerpty

from docker_client_factory import DockerClientFactory
from package import Package

PACKAGE_FILE_NAME = "ppm-package.json"
MOUNT_DIRECTORY = "/mnt/app"

@click.group()
def cli():
    pass

@click.command()
@click.option("--name", prompt="Name",
              default=lambda: os.path.basename(os.getcwd()))
@click.option("--version", prompt="Version", default="1.0.0")
@click.option("--description", prompt="Description", default="")
@click.option("--entry-point", prompt="Entry Point", default="main.py")
def init(name, version, description, entry_point):
    package = Package(name, version, description, entry_point)
    data = package.serialize()

    package_file_path = os.path.join(os.getcwd(), PACKAGE_FILE_NAME)

    click.echo()
    click.echo(click.style("About to write to {}:".format(package_file_path),
                           fg="green", bold=True))
    click.echo()

    click.echo(data)
    click.echo()

    if click.confirm(click.style("Is this OK?", fg="green"), default=True):
        with open(package_file_path, "w") as package_file:
            package_file.write(data)
    else:
        click.echo(click.style("Aborted.", fg="red", bold=True))

@click.command()
def run():
    # Open package
    package_file_path = os.path.join(os.getcwd(), PACKAGE_FILE_NAME)
    with open(package_file_path, "r") as package_file:
        package = Package.deserialize(package_file.read())

    # Open image id
    try:
        with open(".ppm_id", "r") as ppm_id_file:
            image_id = ppm_id_file.read()
    except IOError:
        image_id = "library/python:3-onbuild"

    client_factory = DockerClientFactory()
    client = client_factory.get_client()

    container = client.create_container(
        image=image_id,
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
    package_file_path = os.path.join(os.getcwd(), PACKAGE_FILE_NAME)
    with open(package_file_path, "r") as package_file:
        package = Package.deserialize(package_file.read())

    # Open image id
    try:
        with open(".ppm_id", "r") as ppm_id_file:
            image_id = ppm_id_file.read()
    except IOError:
        image_id = "library/python:3-onbuild"

    client_factory = DockerClientFactory()
    client = client_factory.get_client()

    container = client.create_container(
        image=image_id,
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

    image_id = client.commit(container=container.get("Id")).get("Id")
    with open(".ppm_id", "w") as ppm_id_file:
        ppm_id_file.write(image_id)

cli.add_command(init)
cli.add_command(run)
cli.add_command(install)

if __name__ == "__main__":
    cli()
