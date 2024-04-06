import os
from typing import List, Optional
import click
from gluepy.conf import default_context_manager
from . import cli


@cli.command()
@click.option("--patch", "-p", type=str, multiple=True)
@click.option("--retry", type=str)
@click.argument("label")
def task(label, retry: Optional[str] = None, patch: Optional[List[str]] = None):
    Task = _get_task_by_label(label)

    if retry:
        default_context_manager.load_context(
            os.path.join(retry, "context.yaml"), patches=list(patch)
        )
    elif patch:
        default_context_manager.create_context(patches=list(patch))

    Task().run()


def _get_task_by_label(label):
    from gluepy.exec import TASK_REGISTRY

    try:
        Task = TASK_REGISTRY[label]
    except KeyError:
        raise ValueError(f"Task with label '{label}' was not found in registry.")

    return Task
