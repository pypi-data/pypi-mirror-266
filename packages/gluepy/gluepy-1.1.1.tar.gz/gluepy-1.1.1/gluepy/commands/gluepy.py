import os
import jinja2
import click
from gluepy.exec import bootstrap


@click.group()
def cli():
    """Group of commands for `gluepy` CLI."""
    bootstrap()


@cli.command()
@click.argument("project")
def startproject(project):
    files = {
        f"{project}/manage.py": "manage.j2",
        f"{project}/configs/settings.py": "settings.j2",
        f"{project}/configs/context.yaml": "context.j2",
    }
    for path, template in files.items():
        _create_file_from_jinja(path, template, project=project)

    click.secho(f"Created project '{project}'")


@cli.command()
@click.argument("module")
def startmodule(module):
    files = {
        f"{module}/dags.py": "dags.j2",
        f"{module}/tasks.py": "tasks.j2",
    }
    for path, template in files.items():
        _create_file_from_jinja(path, template, module=module)

    click.secho(f"Created module '{module}'")


def _create_file_from_jinja(file_path, template, **context):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("gluepy", "templates"),
        autoescape=jinja2.select_autoescape(),
    )
    t = env.get_template(template)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode="w") as stream:
        stream.write(t.render(**context))
