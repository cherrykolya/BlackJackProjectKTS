from gino import create_engine
from gino.api import Gino
from sqlalchemy.engine.url import URL

from app.admin.models import *
from app.blackjack.models import *
from app.store.database.gino import db


class Database:
    db: Gino

    def __init__(self, app: "Application"):
        self.app = app
        self.db: Optional[Gino] = None

    async def connect(self, *_, **kw):
        self._engine = await create_engine(
            URL(
                drivername="asyncpg",
                host=self.app.config.database.host,
                database=self.app.config.database.database,
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                port=self.app.config.database.port,
            ),
            min_size=1,
            max_size=1,
        )
        self.db = db
        self.db.bind = self._engine
        await db.gino.create_all()  # добавил сам

    async def disconnect(self, *_, **kw):
        await db.pop_bind().close()
        print("disconnected from database")
