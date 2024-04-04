from sqlalchemy.orm import Session

from switcore.auth.exception import NotFoundException
from switcore.auth.models import User, App


class RepositoryBase:
    def __init__(self, session: Session):
        self.session = session


class AppRepository(RepositoryBase):
    def create(
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
        self.session.commit()
        return token

    def get_or_create(self, access_token: str, refresh_token: str, iss: str, apps_id: str, cmp_id: str) -> App:
        try:
            app = self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
        except NotFoundException:
            app = self.create(
                access_token=access_token,
                refresh_token=refresh_token,
                iss=iss,
                apps_id=apps_id,
                cmp_id=cmp_id
            )
        return app

    def install(self, access_token: str, refresh_token: str, iss: str, apps_id: str, cmp_id: str) -> App:
        try:
            app = self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
            self.session.delete(app)
            self.session.commit()
        except NotFoundException:
            pass

        app = self.create(
            access_token=access_token,
            refresh_token=refresh_token,
            iss=iss,
            apps_id=apps_id,
            cmp_id=cmp_id
        )

        return app

    def get_by_cmp_id_and_apps_id(self, cmp_id: str, apps_id: str) -> App:
        """
        :raises AppNotFoundException:
        """
        app_or_null: App | None = self.session.query(App).filter(App.cmp_id == cmp_id,
                                                                 App.apps_id == apps_id).first()  # type: ignore
        if app_or_null is None:
            raise NotFoundException(f"App with cmp_id: {cmp_id} and apps_id: {apps_id} not found")
        return app_or_null

    def update_token(self, cmp_id: str, apps_id: str, access_token: str, refresh_token: str) -> App:
        app = self.get_by_cmp_id_and_apps_id(cmp_id=cmp_id, apps_id=apps_id)
        app.access_token = access_token
        app.refresh_token = refresh_token
        self.session.commit()
        return app


class UserRepository(RepositoryBase):
    def create(self, swit_id: str, access_token: str, refresh_token: str) -> User:
        user = User(  # type: ignore
            swit_id=swit_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.session.add(user)
        self.session.commit()
        return user

    def get_or_create(self, swit_id: str, access_token: str, refresh_token: str):
        try:
            user = self.get_by_swit_id(swit_id=swit_id)
        except NotFoundException:
            user = self.create(
                swit_id=swit_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
        return user

    def get_by_swit_id(self, swit_id: str) -> User:
        """
        :raises UserNotFoundException:
        """
        user_or_null: User | None = self.session.query(User).filter(User.swit_id == swit_id).first()  # type: ignore
        if user_or_null is None:
            raise NotFoundException(detail="User not found")
        return user_or_null

    def update_token(self, swit_id: str, access_token: str, refresh_token: str) -> User:
        user: User = self.get_by_swit_id(swit_id=swit_id)
        user.access_token = access_token
        user.refresh_token = refresh_token
        self.session.commit()
        return user

    def delete(self, swit_id: str) -> None:
        user = self.get_by_swit_id(swit_id)
        self.session.delete(user)
        self.session.commit()
