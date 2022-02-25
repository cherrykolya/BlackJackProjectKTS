import typing
#from gino import Gino
from hashlib import sha256
from typing import Optional
from app.store.database.gino import db


from app.base.base_accessor import BaseAccessor
#from app.admin.models import Admin, AdminModel

if typing.TYPE_CHECKING:
    from app.web.app import Application



class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        #URL = f'postgresql://{app.config.database.user}:{app.config.database.password}@{app.config.database.host}:{app.config.database.port}/{app.config.database.database}'
        #await db.set_bind(URL)
        await db.gino.create_all()
        admin_existence = await self.get_by_email('admin@admin.com')

        if admin_existence is None:
            await self.create_admin(
            email=app.config.admin.email, password=app.config.admin.password
        )
        else:
            pass
        

    async def get_by_email(self, email: str) -> Optional[Admin]:
        admins =  await AdminModel.query.gino.all()
        admins = [Admin(id=admin.id, email=admin.email, password=admin.password) for admin in admins]
        for admin in admins:
            if admin.email == email:
                return Admin(id=admin.id, email=admin.email, password=admin.password)
                break
        else:
            return None


    async def create_admin(self, email: str, password: str) -> Admin:
        await AdminModel.create(id=1, email=email, password=sha256(password.encode()).hexdigest())
        return Admin(id=1, email=email, password=sha256(password.encode()).hexdigest())

