import os
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, Model, SqliteDatabase

database = SqliteDatabase(
    (
        os.path.join(os.path.expanduser("~"), "applications.db")
        if not os.getenv("dev")
        else "./applications.db"
    ),
)


class Applications(Model):
    application_id = AutoField()
    name = CharField(max_length=100)
    status = CharField()
    location = CharField(default="uk")
    date = DateTimeField(formats="%d/%m/%y %H:%M:%S.%f", default=datetime.now)
    apply_link = CharField(max_length=150)
    email_id_used = CharField()
    expectations = CharField(default="")

    class Meta:
        database = database

    @classmethod
    def get_columns(cls) -> list:
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("__")
            and not callable(getattr(cls, attr))
            and isinstance(getattr(cls, attr), (AutoField, CharField, DateTimeField))
        ]


if not Applications.table_exists():
    print("Creating Application Table...")
    Applications.create_table()
