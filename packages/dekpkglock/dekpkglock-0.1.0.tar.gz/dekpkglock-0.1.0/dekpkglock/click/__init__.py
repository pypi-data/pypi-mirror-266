import typer
from dektools.typer import command_version
from ..core import lock_path, patch_lock

app = typer.Typer(add_completion=False)

command_version(app, __name__)


@app.command()
def lock(name, path):
    lock_path(name, path)


@app.command()
def patch(name, path, index=0):
    patch_lock(name, path, int(index))
