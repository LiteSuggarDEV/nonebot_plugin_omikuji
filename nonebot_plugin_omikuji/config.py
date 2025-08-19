from pathlib import Path

from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_plugin_cache_dir
from pydantic import BaseModel


class Config(BaseModel):
    """
    Configuration for nonebot_plugin_omikuji
    """

    omikuji_send_by_chat: bool = False  # 是否交给模型进行二次响应
    enable_omikuji: bool = True
    omikuji_cache_expire_days: int = 7


def get_config() -> Config:
    return get_plugin_config(Config)

def get_cache_dir() -> Path:
    return get_plugin_cache_dir()
