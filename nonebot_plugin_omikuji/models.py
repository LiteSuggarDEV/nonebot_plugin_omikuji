import random
from datetime import datetime

from nonebot_plugin_suggarchat.API import (
    FunctionDefinitionSchema,
    FunctionParametersSchema,
    FunctionPropertySchema,
    ToolFunctionSchema,
)
from pydantic import BaseModel, Field

LEVEL = ["大吉", "吉", "中吉", "小吉", "末吉", "凶", "大凶"]
# 定义权重，让"吉"类签出现概率更高
LEVEL_WEIGHTS = [10, 30, 20, 15, 10, 5, 2]


class OmikujiSections(BaseModel):
    name: str
    content: str


class OmikujiData(BaseModel):
    level: str = Field(
        default_factory=lambda: random.choices(LEVEL, weights=LEVEL_WEIGHTS)[0]
    )
    theme: str
    sign_number: str
    divine_title: str
    sections: list[OmikujiSections]
    maxim: str
    intro: str
    end: str

class OmikujiCache(BaseModel):
    data: OmikujiData
    timestamp: datetime = Field(default_factory=datetime.now)

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
