from ninja import NinjaAPI
from schedule.api import router as schedule_router
from rustore.api import router as rustore_router
from notification.api import router as notification_router

api = NinjaAPI(
    title="Апи Приложения КИТЕКА",
    description="Эта спецификация содержит актуальное описания API для приложения КИТЕКА.",
)


api.add_router("schedule", schedule_router, tags=["Schedule"])
api.add_router("notification", notification_router, tags=["notification"])
api.add_router("rustore", rustore_router, tags=["Rustore"])
