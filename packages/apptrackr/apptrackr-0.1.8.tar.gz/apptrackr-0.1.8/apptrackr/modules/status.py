import typer

status = typer.Typer()


@status.command()
def application_status() -> None: ...
