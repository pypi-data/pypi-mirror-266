from typing import Optional

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from apptrackr.model import Applications

storage = typer.Typer()
console = Console()


@storage.command()
def count(
    status: Annotated[
        Optional[str],
        typer.Option(
            help="Get applications depending on the status",
        ),
    ] = None
) -> None:
    """
    Fetch counts of applications.

    Args:
        active (Annotated[ bool, typer.Option, optional): Get applications depending on the status.)]=False.
    """
    if status:
        count = Applications.select().where(Applications.status == status).count()
    else:
        count = Applications.select().count()

    typer.echo(
        typer.style(f"Application Count: {count}", fg=typer.colors.BRIGHT_WHITE),
    )


@storage.command()
def add_application(
    name: Annotated[str, typer.Argument(help="Job application name")],
    status: Annotated[str, typer.Argument(help="Job status")],
    apply_link: Annotated[str, typer.Argument(help="Application link")],
    email_id_used: Annotated[
        str, typer.Argument(help="Email Id sent with application")
    ],
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
        email_id_used (Annotated[str], typer.Argument, optional): Optional Application date)].
        location (Annotated[ Optional[str], typer.Argument, optional): Optional Job location)]=None.
        date (Annotated[ Optional[str], typer.Argument, optional): Optional Application date)]=None.:
    Raises:
        typer.Exit: For invalid arguments
    """
    if status not in ("active", "rejected", "accepted"):
        typer.secho("Invalid status argument!", fg=typer.colors.BRIGHT_RED)
        raise typer.Exit(-1)

    application_details = {
        "name": name,
        "status": status,
        "apply_link": apply_link,
        "email_id_used": email_id_used,
    }

    if location:
        application_details["location"] = location

    if date:
        application_details["date"] = date

    application = Applications(**application_details)
    application.save()
    typer.secho(f"Application to {name} add successfully!", fg=typer.colors.GREEN)


@storage.command()
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
    """Fetch applications based on specified filters.

    Args:
        name (Optional[str], optional): Filter by application name. Defaults to None.
        status (Optional[str], optional): Filter by application status. Defaults to None.
        location (Optional[str], optional): Filter by application location. Defaults to None.
        date (Optional[str], optional): Filter by application date. Defaults to None.
        apply_link (Optional[str], optional): Filter by application apply link. Defaults to None.
        page_number (Optional[int], optional): Page number. Defaults to None.

    Returns:
        None

    This function fetches applications based on the specified filters and displays them in a table format.
    """
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
            if k == "name":
                # No one remembers the exact name!
                filters.append(getattr(Applications, k).contains(v))
            else:
                filters.append(getattr(Applications, k) == v)

    applications = (
        Applications.select().where(*filters).paginate(page_number or 1, per_page)
        if filters
        else Applications.select().paginate(page_number or 1, per_page)
    )
    table = Table(
        "ID",
        "Name",
        "Status",
        "Location",
        "Date",
        "Application Link",
        "Email Id Used",
        box=box.MINIMAL,
    )
    for application in applications:
        match application.status:
            case "rejected":
                style = "red"
            case "active":
                style = "yellow"
            case "accepted":
                style = "green"
            case _:
                style = "white"

        table.add_row(
            str(application.application_id),
            application.name,
            application.status,
            application.location,
            application.date,
            application.apply_link,
            application.email_id_used,
            style=style,
        )

    console.print(table)


@storage.command()
def delete_application(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Name of the application"
    ),
    application_id: Optional[str] = typer.Option(
        None, "--id", "-i", help="ID of the application"
    ),
) -> None:
    """Delete an application from the database.

    Args:
        name (Optional[str], optional): Name of the application. Defaults to None.
        application_id (Optional[str], optional): ID of the application. Defaults to None.

    Returns:
        None

    This function deletes an application from the database based on the provided application name or ID.
    If both name and ID are not provided, it raises an error.
    """
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


@storage.command()
def modify_application(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Name of the application"
    ),
    application_id: Optional[int] = typer.Option(
        None, "--id", "-i", help="ID of the application"
    ),
) -> None:
    """Modify attributes of an application stored in the database.

    Args:
        name (Optional[str], optional): Name of the application. Defaults to None.
        application_id (Optional[int], optional): ID of the application. Defaults to None.

    Returns:
        None

    This function prompts the user to select an application either by name or ID, and then allows them to choose which attributes to modify.
    After selecting the attributes, the user can input new values for those attributes, which will be updated in the database.
    If neither name nor ID is provided, the function raises an error.
    """

    def _modify(id: int) -> None:
        can_modify = ["name", "status", "location", "date", "apply_link"]
        to_modify = questionary.checkbox(
            "Select the column you want to modify", choices=can_modify
        ).ask()
        if not to_modify:
            raise typer.Exit(-1)

        modifications = {}
        for modification in to_modify:
            modifications[modification] = questionary.text(
                f"Enter new value for {modification}"
            ).ask()

        updated = (
            Applications.update(**modifications)
            .where(Applications.application_id == id)
            .execute()
        )

        typer.secho(f"Updated records: {updated}", fg=typer.colors.BRIGHT_BLACK)

    if not name and not application_id:
        typer.secho("Enter either the name or the id...")
        raise typer.Exit(-1)

    if application_id:
        _modify(application_id)

    else:
        applications = Applications.select().where(Applications.name.contains(name))
        for application in applications:
            print(
                application.application_id,
                application.name,
                application.status,
                application.location,
                application.date,
                application.apply_link,
            )

        id = typer.prompt("Enter Id to modify", type=int)
        _modify(id)
