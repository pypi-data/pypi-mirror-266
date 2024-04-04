from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from switcore.auth.exception import NotFoundException
from switcore.auth.models import User, App


class RepositoryBase:
    def __init__(self, session: AsyncSession):
        self.session = session


class AppRepository(RepositoryBase):
    async def create(
            self,
            access_token: str,
            refresh_token: str,
            iss: str,
            apps_id: str,
            cmp_id: str
    ) -> App:
        token = App(
            access_token=access_token,
            refresh_token=refresh_token,
            iss=iss,
            apps_id=apps_id,
            cmp_id=cmp_id
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def get_or_create(self, access_token: str, refresh_token: str, iss: str, apps_id: str, cmp_id: str) -> App:
        try:
            app = await self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
        except NotFoundException:
            app = await self.create(
                access_token=access_token,
                refresh_token=refresh_token,
                iss=iss,
                apps_id=apps_id,
                cmp_id=cmp_id
            )
        return app

    async def install(self, access_token: str, refresh_token: str, iss: str, apps_id: str, cmp_id: str) -> App:
        try:
            app = await self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
            await self.session.delete(app)
            await self.session.commit()
        except NotFoundException:
            pass

        app = await self.create(
            access_token=access_token,
            refresh_token=refresh_token,
            iss=iss,
            apps_id=apps_id,
            cmp_id=cmp_id
        )
        return app

    async def get_by_cmp_id_and_apps_id(self, cmp_id: str, apps_id: str) -> App:
        result = await self.session.execute(select(App).filter(App.cmp_id == cmp_id, App.apps_id == apps_id))
        app_or_null = result.scalars().first()
        if app_or_null is None:
            raise NotFoundException(f"App with cmp_id: {cmp_id} and apps_id: {apps_id} not found")
        return app_or_null

    async def update_token(self, cmp_id: str, apps_id: str, access_token: str, refresh_token: str) -> App:
        app = await self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
        app.access_token = access_token
        app.refresh_token = refresh_token
        await self.session.commit()
        await self.session.refresh(app)
        return app


class UserRepository(RepositoryBase):
    async def create(self, swit_id: str, access_token: str, refresh_token: str) -> User:
        user = User(
            swit_id=swit_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, swit_id: str, access_token: str, refresh_token: str):
        try:
            user = await self.get_by_swit_id(swit_id=swit_id)
        except NotFoundException:
            user = await self.create(
                swit_id=swit_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
        return user

    async def get_by_swit_id(self, swit_id: str) -> User:
        result = await self.session.execute(select(User).filter(User.swit_id == swit_id))
        user_or_null = result.scalars().first()
        if user_or_null is None:
            raise NotFoundException(detail="User not found")
        return user_or_null

    async def update_token(self, swit_id: str, access_token: str, refresh_token: str) -> User:
        user = await self.get_by_swit_id(swit_id=swit_id)
        user.access_token = access_token
        user.refresh_token = refresh_token
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, swit_id: str) -> None:
        user = await self.get_by_swit_id(swit_id)
        await self.session.delete(user)
        await self.session.commit()
