import os
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, Model, SqliteDatabase

database = SqliteDatabase(
    os.path.join(os.path.expanduser("~"), "applications.db"),
)


class Applications(Model):
    application_id = AutoField()
    name = CharField(max_length=100)
    status = CharField()
    location = CharField(default="uk")
    date = DateTimeField(formats="%d/%m/%y %H:%M:%S.%f", default=datetime.now)
    apply_link = CharField(max_length=150)

    class Meta:
        database = database


if not Applications.table_exists():
    print("Creating Application Table...")
    Applications.create_table()
