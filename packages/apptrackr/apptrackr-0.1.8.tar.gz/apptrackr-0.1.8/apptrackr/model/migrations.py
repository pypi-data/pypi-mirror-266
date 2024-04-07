import os
from itertools import pairwise

from playhouse.migrate import SqliteDatabase, SqliteMigrator, migrate

from apptrackr.model.model import Applications

database_path = os.path.join(os.path.expanduser("~"), "applications.db")
database_migrations_path = os.path.join(os.path.expanduser("~"), "migrations.txt")


def requries_migrations() -> bool:
    if not os.path.exists(database_path):
        return False

    database = SqliteDatabase(database_path)

    current_columns = [
        attr
        for attr in dir(Applications)
        if not callable(getattr(Applications, attr))
        and not attr.startswith("__")
        and not attr.startswith("_")
    ]
    current_columns.remove("dirty_fields")  # Peewee usage
    old_columns = database.get_columns("applications")
    old_columns.sort(key=lambda c: c.name)
    old_columns = [old_column.name for old_column in old_columns]

    if current_columns != old_columns:
        return True


def makemigrations():
    print("Checking migrations...")

    if not requries_migrations():
        print("No migrations required!")
        return

    print("Making migrations...")
    migrator = SqliteMigrator(SqliteDatabase(database_path))
    with open(database_migrations_path, "r") as migrations_log:
        logs = migrations_log.read().replace(" ", "")
        changes = list(pairwise(logs.split("=")))

    for change in changes:
        print(f"Renaming column {change[0]} to {change[1]}")
        migrate(migrator.rename_column("applications", change[0], change[1]))
