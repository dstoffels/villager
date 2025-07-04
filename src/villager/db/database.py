from peewee import SqliteDatabase
import atexit

db = SqliteDatabase("src/villager/db/villager.db")

db.connect()


@atexit.register
def close_db() -> None:
    if not db.is_closed():
        db.close()
