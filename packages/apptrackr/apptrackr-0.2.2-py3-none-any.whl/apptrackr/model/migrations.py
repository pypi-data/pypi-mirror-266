import os

from playhouse.migrate import SqliteDatabase, SqliteMigrator, migrate

from apptrackr.model.model import Applications

database_path = os.path.join(os.path.expanduser("~"), "applications.db")
config_path = os.path.join(
    os.path.expanduser("~"), r"Library/Application Support/apptrackr.toml"
)


class DetectedChange:
    def __init__(self, change_type: str, associated: any) -> None:
        self.change_type = change_type
        self.associated = associated


def requires_migrations() -> DetectedChange | bool:
    if not os.path.exists(database_path):
        return False

    database = SqliteDatabase(database_path)
    current_columns = Applications.get_columns()
    old_columns = database.get_columns("applications")

    if len(current_columns) != len(old_columns):
        changed_columns = []
        old_column_names = [column.name for column in old_columns]
        for column in current_columns:
            if column.name not in old_column_names:
                changed_columns.append(column)
        return DetectedChange("add_column", associated=changed_columns)

    if sorted(column.name for column in current_columns) != sorted(
        column.name for column in old_columns
    ):
        return DetectedChange("column_rename", associated=None)

    return False


def makemigrations():
    print("Checking migrations...")
    migrations = requires_migrations()
    if not migrations:
        print("No migrations required!")
        return

    to_apply = []
    migrator = SqliteMigrator(SqliteDatabase(database_path))
    if migrations.change_type == "add_column":
        for column in migrations.associated:
            to_apply.append(
                migrator.add_column("applications", column.name, column),
            )

        migrate(*to_apply)
        print("Applied migrations!")
