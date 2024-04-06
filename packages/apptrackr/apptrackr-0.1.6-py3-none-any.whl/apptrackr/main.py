import typer

from apptrackr.modules.storage import storage

app = typer.Typer()
app.add_typer(storage, name="store")


if __name__ == "__main__":
    app()
