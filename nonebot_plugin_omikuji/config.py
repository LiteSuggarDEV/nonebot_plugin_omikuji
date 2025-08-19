from pathlib import Path

from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_plugin_cache_dir
from pydantic import BaseModel


class Config(BaseModel):
    """
    Configuration for nonebot_plugin_omikuji
    """

    omikuji_send_by_chat: bool = False  # 是否交给模型进行二次响应
    enable_omikuji: bool = True  # 是否启用
    omikuji_add_system_prompt: bool = (
        True  # 是否加入SuggarChat的系统提示(生成更符合角色设定的答案)
    )
    omikuji_use_cache: bool = True  # 是否使用语料库的缓存（LLM生成后的缓存）
    omikuji_cache_expire_days: int = 7  # 御神签语料缓存有效期（-1表示长期有效，但是在语料库建立完成后不会更新语料库的内容。）
    omikuji_long_cache_update: bool = True  # 仅在语料库长期模式下生效，是否自动更新语料


def get_config() -> Config:
    return get_plugin_config(Config)


def get_cache_dir() -> Path:
    return get_plugin_cache_dir()
