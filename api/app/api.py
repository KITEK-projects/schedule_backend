from ninja import NinjaAPI

from schedule.api import router as schedule_router
from rustore.api import router as rustore_router

api = NinjaAPI(
   title="Апи Приложения КИТЕКА",
   description="Эта спецификация содержит актуальное описания API для приложения КИТЕКА.",
)


api.add_router("/schedule", schedule_router, tags=["schedule"])

api.add_router("/rustore", rustore_router, tags=["rustore"])