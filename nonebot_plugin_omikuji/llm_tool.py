import typing

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_suggarchat.API import (
    FunctionDefinitionSchema,
    FunctionParametersSchema,
    FunctionPropertySchema,
    ToolData,
    ToolFunctionSchema,
    ToolsManager,
)
from nonebot_plugin_suggarchat.utils.llm_tools.models import ToolContext
from pydantic import BaseModel

from .config import get_config

manager = ToolsManager()

class OmikujiSections(BaseModel):
    name:str
    content:str

class OmikujiData(BaseModel):
    level:str
    theme:str
    sign_number:str
    divine_title:str
    sections:list[OmikujiSections]
    maxim:str
    intro:str
    end:str

async def omikuji(ctx: ToolContext):
    nb_event:MessageEvent = typing.cast(MessageEvent,ctx.event.get_nonebot_event())
    data = OmikujiData.model_validate(ctx.data)
    bot = get_bot(str(ctx.event._nbevent.self_id))
    await bot.send(ctx.event._nbevent, "轻轻摇动古老的签筒，竹签哗啦作响... 心中默念所求之事... 一支签缓缓落下。")
    ln = "\n"
    msg = f"""{data.intro}
{nb_event.sender.nickname}，你的签上刻了什么？

＝＝＝ 御神签 第{data.sign_number} ＝＝＝
✨ 天启：{data.divine_title}
🌸 运势：{data.level} - {data.theme}

{"".join(f"▫ {section.name}{ln}{section.content}{ln}" for section in data.sections)}

⚖ 真言偈：{data.maxim}

{data.end}
"""
    if get_config().omikuji_send_by_chat:
        return msg
    await bot.send(nb_event, msg)
    ctx.matcher.cancel_nonebot_process()


FUNC_META = ToolFunctionSchema(
    strict=True,
    function=FunctionDefinitionSchema(
        name="御神签",
        description="获取御神签签文",
        parameters=FunctionParametersSchema(
            type="object",
            properties={
                "level": FunctionPropertySchema(
                    type="string",
                    description="御神签等级(随机选择)",
                    enum=["大吉", "吉", "中吉", "小吉", "末吉", "凶", "大凶"],
                ),
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
                    type="string", description="主题引入(不包含引号)：e.g. '「欢迎来到古树根下的祠堂。异界之风正为你捎来命运的启示…」\n'"
                ),
                "end": FunctionPropertySchema(
                    type="string", description="主题总结(不包含引号)：e.g. '🦊 小狐甩着尾巴：「虽是中吉，但会有趣事发生呢！要找月光石的话，今晚满月正是好时机哟～」'"
                )
            },
            required=[
                "level",
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

TOOL_DATA = ToolData(data=FUNC_META, func=omikuji, custom_run=True)
