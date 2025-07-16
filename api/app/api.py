from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from schedule.api import router as schedule_router
from rustore.api import router as rustore_router
from my_user.api import router as auth_router

api = NinjaExtraAPI(
    title="Апи Приложения КИТЕКА",
    description="Эта спецификация содержит актуальное описания API для приложения КИТЕКА.",
)

api.register_controllers(NinjaJWTDefaultController)

api.add_router("schedule", schedule_router, tags=["Schedule"])
api.add_router("rustore", rustore_router, tags=["Rustore"])
api.add_router("user", auth_router, tags=["User"])
