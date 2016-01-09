import os
import click

from package import Package

PACKAGE_FILE_NAME = "ppm-package.json"

@click.group()
def cli():
    pass

def test():
    return "abb"

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


cli.add_command(init)

if __name__ == '__main__':
    cli()
