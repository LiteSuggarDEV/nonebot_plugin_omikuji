import os
from datetime import datetime, timedelta
from typing import overload

import aiofiles
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_orm import AsyncSession, get_session
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from typing_extensions import Self

from .config import get_cache_dir, get_config
from .models import OmikujiData
from .sql_models import OmikujiCache as SQLOmikujiCache
from .sql_models import db_lock


class OmikujiCache(BaseModel):
    data: OmikujiData
    timestamp: datetime = Field(default_factory=datetime.now)


async def cache_omikuji(event: MessageEvent, data: OmikujiData) -> None:
    CACHE_DIR = get_cache_dir()
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = CACHE_DIR / f"{event.user_id!s}.json"
    cache = OmikujiCache(data=data)
    async with aiofiles.open(cache_file, "w", encoding="utf-8") as f:
        await f.write(cache.model_dump_json())


async def get_cached_omikuji(event: MessageEvent) -> OmikujiData | None:
    CACHE_DIR = get_cache_dir()
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = CACHE_DIR / f"{event.user_id!s}.json"
    if not cache_file.exists():
        return None
    async with aiofiles.open(cache_file, encoding="utf-8") as f:
        cache = OmikujiCache.model_validate_json(await f.read())
    if cache.timestamp.date() == datetime.now().date():
        return cache.data
    else:
        os.remove(str(cache_file))


class OmikujiCacheContent(BaseModel):
    content: str


class OmikujiCacheData(BaseModel):
    level: str
    theme: str
    sections: dict[str, list[str]]
    intro: list[OmikujiCacheContent]
    maxim: list[OmikujiCacheContent]
    end: list[OmikujiCacheContent]
    divine_title: list[OmikujiCacheContent]
    sign_number: list[OmikujiCacheContent]
    created_date: str
    updated_date: str

    @overload
    @classmethod
    async def get(cls, level: str, theme: str) -> Self | None: ...

    @overload
    @classmethod
    async def get(cls, level: str) -> dict[str, Self]: ...

    @classmethod
    async def get(
        cls, level: str, theme: str | None = None
    ) -> Self | dict[str, Self] | None:
        async with db_lock(theme, level):
            async with get_session() as session:
                await cls._expire_cache(session=session)
                if theme:
                    stmt = select(SQLOmikujiCache).where(
                        SQLOmikujiCache.level == level,
                        SQLOmikujiCache.theme == theme,
                    )
                    result = await session.execute(stmt)
                    data = result.scalar_one_or_none()
                    return cls.model_validate(data, from_attributes=True)
                else:
                    stmt = select(SQLOmikujiCache).where(
                        SQLOmikujiCache.level == level,
                    )
                    result = await session.execute(stmt)
                    data = result.scalars().all()
                    return {
                        model.theme: cls.model_validate(model, from_attributes=True)
                        for model in data
                    }

    @classmethod
    async def cache_omikuji(cls, data: OmikujiData) -> None:
        async with db_lock(data.theme, data.level):
            async with get_session() as session:
                await cls._expire_cache(session=session)
                stmt = (
                    select(SQLOmikujiCache)
                    .where(
                        SQLOmikujiCache.theme == data.theme,
                        SQLOmikujiCache.level == data.level,
                    )
                    .with_for_update()
                )
                if (
                    cache := (await session.execute(stmt)).scalar_one_or_none()
                ) is None:
                    cache = SQLOmikujiCache(
                        theme=data.theme,
                        level=data.level,
                        sections={i.name: [i.content] for i in data.sections},
                    )
                    session.add(cache)
                    await session.commit()
                    await session.refresh(cache)

                sections = cache.sections
                intro = cache.intro
                maxim = cache.maxim
                end = cache.end
                divine_title = cache.divine_title
                sign_number = cache.sign_number

                for name in sections.keys():
                    for i in data.sections:
                        if i.name == name:
                            if i.content in sections[name]:
                                continue
                            sections[name].append(i.content)

                data_intro = OmikujiCacheContent(content=data.intro).model_dump()
                if data_intro not in intro:
                    intro.append(data_intro)

                data_maxim = OmikujiCacheContent(content=data.maxim).model_dump()
                if data_maxim not in maxim:
                    maxim.append(data_maxim)

                data_end = OmikujiCacheContent(content=data.end).model_dump()
                if data_end not in end:
                    end.append(data_end)

                data_devine_title = OmikujiCacheContent(
                    content=data.divine_title
                ).model_dump()
                if data_devine_title not in divine_title:
                    divine_title.append(data_devine_title)

                data_sign_number = OmikujiCacheContent(
                    content=data.sign_number
                ).model_dump()
                if data_sign_number not in sign_number:
                    sign_number.append(data_sign_number)

                cache.intro = intro
                cache.sections = sections
                cache.maxim = maxim
                cache.end = end
                cache.divine_title = divine_title
                cache.sign_number = sign_number

                await session.commit()

    @staticmethod
    async def _expire_cache(*, session: AsyncSession) -> None:
        config = get_config()
        if config.omikuji_cache_expire_days > 0:
            expire_time = datetime.now() - timedelta(
                days=config.omikuji_cache_expire_days
            )
            await session.execute(
                delete(SQLOmikujiCache).where(
                    SQLOmikujiCache.updated_date < expire_time.strftime("%Y-%m-%d")
                )
            )
            await session.commit()
