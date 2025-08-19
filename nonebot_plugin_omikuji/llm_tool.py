import json
import random
import typing
from copy import deepcopy

from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_suggarchat.API import (
    FunctionDefinitionSchema,
    FunctionParametersSchema,
    FunctionPropertySchema,
    ToolContext,
    ToolData,
    ToolFunctionSchema,
    ToolsManager,
    config_manager,
    tools_caller,
)
from pydantic import BaseModel

from .config import get_config

manager = ToolsManager()

LEVEL = ["大吉", "吉", "中吉", "小吉", "末吉", "凶", "大凶"]


class OmikujiSections(BaseModel):
    name: str
    content: str


class OmikujiData(BaseModel):
    level: str
    theme: str
    sign_number: str
    divine_title: str
    sections: list[OmikujiSections]
    maxim: str
    intro: str
    end: str


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
    args["level"] = level
    return OmikujiData.model_validate(args)


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


async def omikuji(ctx: ToolContext):
    logger.info("获取御神签")
    nb_event: MessageEvent = typing.cast(MessageEvent, ctx.event.get_nonebot_event())
    bot = get_bot(str(ctx.event._nbevent.self_id))
    await bot.send(
        ctx.event._nbevent,
        "轻轻摇动古老的签筒，竹签哗啦作响... 心中默念所求之事... 一支签缓缓落下。",
    )
    level = random.choice(LEVEL)
    data = await get_omikuji(
        level,
        ctx.data["theme"],
        is_group=hasattr(nb_event, "group_id"),
    )
    if get_config().omikuji_send_by_chat:
        return data.model_dump_json()
    msg = format_omikuji(data)
    await bot.send(nb_event, msg)
    ctx.matcher.cancel_nonebot_process()


OMIKUJI_SCHEMA_META = ToolFunctionSchema(
    strict=True,
    function=FunctionDefinitionSchema(
        name="御神签",
        description="获取御神签签文",
        parameters=FunctionParametersSchema(
            type="object",
            properties={
                "theme": FunctionPropertySchema(
                    type="string",
                    description="御神签主题",
                ),
                "sign_number": FunctionPropertySchema(
                    type="string",
                    description="御神签编号(中文大写数字)",
                ),
                "divine_title": FunctionPropertySchema(
                    type="string",
                    description="神签标题/天启名（2-4字奇幻风格名称）",
                ),
                "sections": FunctionPropertySchema(
                    type="array",
                    items=FunctionPropertySchema(
                        type="object",
                        properties={
                            "name": FunctionPropertySchema(
                                type="string", description="分类名称"
                            ),
                            "content": FunctionPropertySchema(
                                type="string", description="分类的预言内容（1～2句话）"
                            ),
                        },
                        description="签文主体",
                        required=["name", "content"],
                    ),
                    description="签文主体",
                    maxItems=8,
                    minItems=4,
                    uniqueItems=True,
                ),
                "maxim": FunctionPropertySchema(
                    type="string", description="一句箴言/和歌（结尾注明出处）"
                ),
                "intro": FunctionPropertySchema(
                    type="string",
                    description="主题引入(不包含引号)：e.g. '「欢迎来到古树根下的祠堂。异界之风正为你捎来命运的启示…」\n'",
                ),
                "end": FunctionPropertySchema(
                    type="string",
                    description="主题总结(不包含引号)",
                ),
            },
            required=[
                "theme",
                "sign_number",
                "divine_title",
                "sections",
                "maxim",
                "intro",
            ],
        ),
    ),
)

FUNC_META = ToolFunctionSchema(
    strict=False,
    function=FunctionDefinitionSchema(
        name="御神签(omikuji)",
        description="抽取一个御神签",
        parameters=FunctionParametersSchema(
            type="object",
            properties={
                "theme": FunctionPropertySchema(
                    type="string",
                    description="御神签主题（如果包含不良内容则随机选择）",
                )
            },
            required=["theme"],
        ),
    ),
)

TOOL_DATA = ToolData(data=FUNC_META, func=omikuji, custom_run=True)
