import contextlib

from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_suggarchat")
from importlib import metadata

from nonebot_plugin_suggarchat.API import ToolsManager

from . import llm_tool
from .config import get_config
from .llm_tool import TOOL_DATA

__plugin_meta__ = PluginMetadata(
    name="御神签",
    description="依赖SuggarChat的聊天御神签抽签插件模块",
    usage="/omikuji [板块]\n/omikuji 解签\n或者使用聊天直接抽签。",
    type="application",
    homepage="https://github.com/LiteSuggarDEV/nonebot_plugin_omikuji",
    supported_adapters={"~onebot.v11"},
)

__all__ = ["llm_tool"]

@get_driver().on_startup
async def init():
    version = "Unknown"
    with contextlib.suppress(Exception):
        version = metadata.version("nonebot_plugin_omikuji")
        if "dev" in version:
            logger.warning("当前版本为开发版本，可能存在不稳定情况！")
    logger.info(f"Loading OMIKUJI V{version}......")
    conf = get_config()
    if conf.enable_omikuji:
        ToolsManager().register_tool(TOOL_DATA)
