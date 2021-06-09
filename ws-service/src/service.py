import attr
from typing import Dict, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReplaceOne


@attr.attrs(slots=True, auto_attribs=True)
class Components:
    db: AsyncIOMotorDatabase

    async def get_next_page(self, next_page: int, page_size: int) -> List[Dict]:
        skip_docs_num: int = page_size * (next_page - 1)
        cursor = self.db.components.find().skip(skip_docs_num).limit(page_size)
        res: List[Dict] = [doc async for doc in cursor]
        return res

    async def insert_bulk(self, records: List[Dict], upsert: bool = False) -> None:
        if not upsert:
            await self.db.components.insert_many(records)
            return
        records = [ReplaceOne(record, record, upsert=True) for record in records]
        await self.db.components.bulk_write(records)
