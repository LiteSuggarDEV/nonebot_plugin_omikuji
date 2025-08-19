import json
from copy import deepcopy

from nonebot_plugin_suggarchat.API import (
    config_manager,
    tools_caller,
)

from .models import OMIKUJI_SCHEMA_META, OmikujiData


async def get_omikuji(level: str, theme: str, is_group: bool = False) -> OmikujiData:
    system_prompt = deepcopy(
        config_manager.group_train if is_group else config_manager.private_train
    )
    system_prompt["content"] += "\n你现在需要结合你的角色设定生成御神签。"
    user_prompt = {
        "role": "user",
        "content": f"御神签的运势是：'{level}'\n现在生成一张主题为：'{theme}'的御神签",
    }
    msg_input = [system_prompt, user_prompt]
    data = await tools_caller(
        messages=msg_input, tools=[OMIKUJI_SCHEMA_META], tool_choice="required"
    )
    assert data.tool_calls
    args = json.loads(data.tool_calls[0].function.arguments)
    model = OmikujiData.model_validate(args)
    model.level = level
    return model


def format_omikuji(data: OmikujiData, user_name: str | None = ""):
    ln = "\n"
    msg = f"""{data.intro}
{(user_name + "，" if user_name else "")}你的签上刻了什么？

＝＝＝ 御神签 第{data.sign_number} ＝＝＝
✨ 天启：{data.divine_title}
🌸 运势：{data.level} - {data.theme}

{"".join(f"▫ {section.name}{ln}{section.content}{ln}" for section in data.sections)}

⚖ 真言偈：{data.maxim}

{data.end}
"""
    return msg
