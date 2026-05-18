import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal

logger = logging.getLogger("uvicorn")


async def mantener_base_de_datos_viva(intervalo: int = 240):
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
        except Exception:
            logger.warning("Fallo el ping a la base de datos", exc_info=True)
        await asyncio.sleep(intervalo)
