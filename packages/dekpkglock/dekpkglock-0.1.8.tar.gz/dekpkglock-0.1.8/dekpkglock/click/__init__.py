import typer
from typing_extensions import Annotated
from dektools.typer import command_version
from ..core import lock_path, patch_lock

app = typer.Typer(add_completion=False)

command_version(app, __name__)


@app.command()
def lock(name, path, remove: Annotated[bool, typer.Option("--remove/--no-remove")] = True):
    if not lock_path(name, path, remove):
        raise typer.Exit(1)


@app.command()
def patch(name, path, index: int = 0):
    patch_lock(name, path, index)
