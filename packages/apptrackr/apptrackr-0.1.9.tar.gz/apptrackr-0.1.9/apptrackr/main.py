import typer

from apptrackr.model.migrations import makemigrations
from apptrackr.model.utils import get_last_applied_on
from apptrackr.modules.config import config
from apptrackr.modules.storage import storage

app = typer.Typer()
app.add_typer(storage, name="store")
app.add_typer(config, name="config")


time_elapsed, company, link = get_last_applied_on()
typer.secho(
    f"Last application was {time_elapsed} {f'\nMaybe apply to {company}' if company else ''} {link if link else ''}",
    fg=typer.colors.BRIGHT_BLUE,
)


@app.command()
def make_migrations() -> None:
    """Django Style"""
    makemigrations()


if __name__ == "__main__":
    app()
