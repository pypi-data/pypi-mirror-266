import typer

from apptrackr.model.migrations import makemigrations
from apptrackr.modules.storage import storage

app = typer.Typer()
app.add_typer(storage, name="store")


@app.command()
def make_migrations() -> None:
    """Django Style"""
    makemigrations()


if __name__ == "__main__":
    app()
