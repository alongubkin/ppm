import os
import click

import json
import subprocess

from docker import Client
from docker.tls import TLSConfig
import dockerpty

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
    click.echo()

    package = Package(name, version, description, entry_point)
    data = package.serialize()

    package_file_path = os.path.join(os.getcwd(), PACKAGE_FILE_NAME)

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
    package_file_path = os.path.join(os.getcwd(), PACKAGE_FILE_NAME)
    with open(package_file_path, "r") as package_file:
        package = Package.deserialize(package_file.read())

    config = json.loads(subprocess.check_output(["docker-machine", "inspect", "dev"]))

    if not config["HostOptions"]["EngineOptions"]["TlsVerify"]:
        raise Exception("TLS is required.")

    base_url = "https://{}:2376".format(config["Driver"]["IPAddress"])

    cert_path = config["HostOptions"]["AuthOptions"]["StorePath"]

    tls_config = TLSConfig(client_cert=(os.path.join(cert_path, 'cert.pem'),
                                        os.path.join(cert_path, 'key.pem')),
                           ca_cert=os.path.join(cert_path, 'ca.pem'),
                           verify=True,
                           assert_hostname=False)

    client = Client(base_url=base_url, tls=tls_config)

    container = client.create_container(
        image="library/python:3-onbuild",
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

cli.add_command(init)
cli.add_command(run)

if __name__ == "__main__":
    cli()
