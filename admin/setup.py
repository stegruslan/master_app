from core.config import settings
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from core.database import engine
from admin.views import MasterAdmin, BookingAdmin, ServiceAdmin, ScheduleAdmin


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form["username"] == "admin" and form["password"] == settings.ADMIN_PASSWORD:
            request.session.update({"token": "admin"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request) -> bool:
        return request.session.get("token") == "admin"


def setup_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.ADMIN_SECRET_KEY)
    admin = Admin(app, engine, authentication_backend=authentication_backend)

    admin.add_view(MasterAdmin)
    admin.add_view(BookingAdmin)
    admin.add_view(ServiceAdmin)
    admin.add_view(ScheduleAdmin)
