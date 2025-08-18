from nonebot import get_driver
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_suggarchat")
from . import llm_tool
from .config import get_config
from .llm_tool import TOOL_DATA, manager

__plugin_meta__ = PluginMetadata(
    name="御神签",
    description="SuggarChat联动的御神签插件",
    usage="/omikuji [板块]\n/omikuji 解签\n或者使用聊天直接抽签。",
    type="application",
    homepage="https://github.com/LiteSuggarDEV/nonebot_plugin_omikuji",
    supported_adapters={"~onebot.v11"},
)

__all__ = ["llm_tool"]

@get_driver().on_startup
async def init():
    conf = get_config()
    if conf.enable_omikuji:
        manager.register_tool(TOOL_DATA)
