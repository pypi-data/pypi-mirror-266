from typing import Optional

import typer
from typing_extensions import Annotated

from .model import Applications

tracker = typer.Typer()


@tracker.command()
def count(
    active: Annotated[
        bool,
        typer.Option(
            help="Get only active application",
        ),
    ] = False
) -> None:
    """
    Fetch counts of applications.

    Args:
        active (Annotated[ bool, typer.Option, optional): Fetch only active applications.)]=False.
    """
    if active:
        count = Applications.select().where(Applications.status == "active").count()
    else:
        count = Applications.select().count()

    typer.echo(
        typer.style(f"Application Count: {count}", fg=typer.colors.BRIGHT_WHITE),
    )


@tracker.command()
def add_application(
    name: Annotated[str, typer.Argument(help="Job application name")],
    status: Annotated[str, typer.Argument(help="Job status")],
    apply_link: Annotated[str, typer.Argument(help="Application link")],
    location: Annotated[
        Optional[str], typer.Argument(help="Optional Job location")
    ] = None,
    date: Annotated[
        Optional[str], typer.Argument(help="Optional Application date")
    ] = None,
) -> None:
    """Add new application to the database.

    Args:
        name (Annotated[str, typer.Argument, optional): Job application name)].
        status (Annotated[str, typer.Argument, optional): Job status)].
        apply_link (Annotated[str, typer.Argument, optional): Application link)].
        location (Annotated[ Optional[str], typer.Argument, optional): Optional Job location)]=None.
        date (Annotated[ Optional[str], typer.Argument, optional): Optional Application date)]=None.

    Raises:
        typer.Exit: For invalid arguments
    """
    if status not in ("active", "rejected", "accepted"):
        typer.echo("Invalid status argument!")
        raise typer.Exit(-1)

    application_details = {"name": name, "status": status, "apply_link": apply_link}

    if location:
        application_details["location"] = location

    if date:
        application_details["date"] = date

    application = Applications(**application_details)
    application.save()


@tracker.command()
def fetch_applications(
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Filter by application name"),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", "-s", help="Filter by application status"),
    ] = None,
    location: Annotated[
        Optional[str],
        typer.Option("--location", "-l", help="Filter by application location"),
    ] = None,
    date: Annotated[
        Optional[str],
        typer.Option("--date", "-d", help="Filter by application date"),
    ] = None,
    apply_link: Annotated[
        Optional[str],
        typer.Option("--apply-link", "-a", help="Filter by application apply link"),
    ] = None,
    page_number: Annotated[
        Optional[int], typer.Option("--page", "-p", help="Page number")
    ] = None,
):
    filters = []
    columns = {
        "name": name,
        "status": status,
        "location": location,
        "date": date,
        "apply_link": apply_link,
    }
    per_page = 10

    for k, v in columns.items():
        if v:
            filters.append(getattr(Applications, k) == v)

    applications = (
        Applications.select().where(*filters).paginate(page_number or 1, per_page)
        if filters
        else Applications.select().paginate(page_number or 1, per_page)
    )
    for application in applications:
        print(
            application.application_id,
            application.name,
            application.status,
            application.location,
            application.date,
            application.apply_link,
        )


@tracker.command()
def delete_application(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Name of the application"
    ),
    application_id: Optional[str] = typer.Option(
        None, "--id", "-i", help="ID of the application"
    ),
) -> None:
    deleted_records: int = 0
    if not name and not application_id:
        typer.secho(
            "Provide either application Id or application Name to delete.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(-1)

    if application_id:
        typer.confirm(f"Deleting application: {application_id}", abort=True)
        deleted_records = Applications.delete_by_id(application_id)

    if name:
        deleting_options = Applications.select().where(Applications.name == name)
        if deleting_options:
            typer.secho("Type the application Id to delete the record...")
            for deleting_option in deleting_options:
                print(
                    deleting_option.application_id,
                    deleting_option.name,
                    deleting_option.status,
                    deleting_option.location,
                    deleting_option.date,
                    deleting_option.apply_link,
                )
            selected_id = typer.prompt(
                "Select one of the above ids to delete", type=int
            )
            typer.confirm(f"Deleting application: {selected_id}", abort=True)
            deleted_records = Applications.delete_by_id(selected_id)

    typer.secho(f"Deleted records: {deleted_records}", fg=typer.colors.BRIGHT_BLACK)


if __name__ == "__main__":
    tracker()
