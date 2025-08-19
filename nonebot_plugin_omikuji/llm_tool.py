import typing

from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_suggarchat.API import (
    ToolContext,
    ToolData,
)

from .cache import get_cached_omikuji
from .config import get_config
from .models import FUNC_META
from .utils import format_omikuji, get_omikuji


async def omikuji(ctx: ToolContext):
    logger.info("获取御神签")
    nb_event: MessageEvent = typing.cast(MessageEvent, ctx.event.get_nonebot_event())
    bot = get_bot(str(ctx.event._nbevent.self_id))
    await bot.send(
        ctx.event._nbevent,
        "轻轻摇动古老的签筒，竹签哗啦作响... 心中默念所求之事... 一支签缓缓落下。",
    )
    if (data := await get_cached_omikuji(nb_event)) is None:
        data = await get_omikuji(
            ctx.data["theme"],
            is_group=hasattr(nb_event, "group_id"),
        )
    if get_config().omikuji_send_by_chat:
        return data.model_dump_json()
    msg = format_omikuji(data)
    await bot.send(nb_event, msg)
    ctx.matcher.cancel_nonebot_process()


TOOL_DATA = ToolData(data=FUNC_META, func=omikuji, custom_run=True)
