import os
from pathlib import Path

import click

from vokab import Collection


@click.group()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    help="Path to vokab collection.",
)
@click.pass_context
def app(ctx, path: str):
    ctx.ensure_object(dict)
    path = path or os.environ.get("VOKAB_HOME") or "~/.local/vokab/"
    path = Path(os.path.expanduser(path))

    if path is None:
        msg = "You must specify a project path (--path or VOKAB_HOME)."
        raise click.UsageError(msg)

    ctx.obj["collection"] = Collection.load(path)
