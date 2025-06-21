import asyncio
import logging

from rustore.models import RustoreVersion
from rustore.rustore import get_current_version

logger = logging.getLogger(__name__)

async def run_loop():
    while True:
        try:
            version = await get_current_version()

            await RustoreVersion.objects.aget_or_create(
                versionName=version["version_name"],
                versionCode=version["version_code"]
            )
        except Exception as e:
            logger.error(f"Ошибка при обновлении версии: {e}")
        await asyncio.sleep(30)

def start_background_tasks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_loop())
