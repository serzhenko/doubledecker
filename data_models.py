from datetime import datetime

from playhouse.sqlite_ext import *
from decouple import config

sqlite_db = SqliteExtDatabase(config('sqlite_db_path', default='db.sqlite'), pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64,
    'foreign_keys': 'on'})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = sqlite_db


class User(BaseModel):
    class Meta:
        table_name = 'users'

    id = AutoIncrementField(primary_key=True)
    username = CharField(unique=True)
    name = CharField()
    telegram_id = IntegerField(unique=True)


class Deck(BaseModel):
    class Meta:
        table_name = 'decks'

    STATUS = {'PENDING': 0, 'PROCESSED': 1, 'CORRUPTED': -1}

    id = AutoIncrementField(primary_key=True)
    user_id = ForeignKeyField(User, index=True)
    slides_count = IntegerField()
    pubdate = DateTimeField(default=datetime.now)
    views = IntegerField(default=0)
    status = IntegerField(default=STATUS['PENDING'])


def create_tables():
    sqlite_db.connect()
    sqlite_db.create_tables([User, Deck])
    sqlite_db.close()


if __name__ == '__main__':
    create_tables()
