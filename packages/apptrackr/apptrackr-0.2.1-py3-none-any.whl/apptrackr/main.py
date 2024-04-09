import typer
from trogon import Trogon
from typing_extensions import Annotated

from apptrackr.model.migrations import makemigrations
from apptrackr.model.utils import get_last_applied_on, get_new_job
from apptrackr.modules.config import config
from apptrackr.modules.storage import storage

app = typer.Typer(no_args_is_help=True)
app.add_typer(storage, name="store", help="Application management")
app.add_typer(config, name="config", help="Recommendation configs")


time_elapsed, company, link = get_last_applied_on()
typer.secho(
    f"Last application was {time_elapsed} {f'\nMaybe apply to {company}' if company else ''} {link if link else ''}",
    fg=typer.colors.BRIGHT_BLUE,
)


@app.command()
def make_migrations() -> None:
    """Django Style"""
    makemigrations()


@app.command()
def new(
    launch: Annotated[
        bool,
        typer.Option("--launch", "-l", help="Open link"),
    ] = None
):
    """Recommend a new application"""
    company, link = get_new_job()
    if launch:
        typer.launch(link)

    print(f"{company}: {link}")


@app.command()
def tui(ctx: typer.Context) -> None:
    """Lunch tui courtesy trogon

    Args:
        ctx (typer.Context): click context
    """
    Trogon(typer.main.get_group(app), click_context=ctx).run()


if __name__ == "__main__":
    app()
