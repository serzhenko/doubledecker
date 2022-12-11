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
    id = AutoIncrementField()
    username = CharField(unique=True)
    telegram_id = IntegerField(unique=True)


class Deck(BaseModel):
    id = AutoIncrementField()
    user_id = ForeignKeyField(User)
    slides_count = IntegerField()
    pubdate = DateTimeField()


# sqlite_db.create_tables([User, Deck])
