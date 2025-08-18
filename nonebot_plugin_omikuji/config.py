from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """
    Configuration for nonebot_plugin_omikuji
    """

    omikuji_send_by_chat: bool = False  # 是否交给模型进行二次响应
    enable_omikuji: bool = True


def get_config() -> Config:
    return get_plugin_config(Config)
