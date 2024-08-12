from nonebot import get_plugin_config, on_command, on_message, require, get_bot
from nonebot.adapters.telegram import Event as TelegramEvent
from nonebot.adapters.telegram.event import MessageEvent as TelegramMessageEvent
from nonebot.adapters.feishu import Event as FeishuEvent, MessageEvent as FeishuMessageEvent
from nonebot.adapters import Event
require("nonebot_plugin_saa")
from nonebot_plugin_saa import TargetFeishuGroup, TargetTelegramCommon, Image, Text, MessageFactory, enable_auto_select_bot
enable_auto_select_bot()

from typing import List, Union
from pydantic import BaseModel, Field


class Land(BaseModel):
    """即将使用 bridge 连接起来的土地
    """
    name: str
    id_: str = Field(alias="id")
    bot_name: str


class BridgeConfig(BaseModel):
    """bridge 配置
    """
    name: str
    lands: list[Land]


class BotConfig(BaseModel):
    """机器人配置
    """
    name: str
    id_: str = Field(alias="id")
    type_: str = Field(alias="type")


class Config(BaseModel):
    """配置
    """
    nonebot_bridges: list[BridgeConfig]
    nonebot_bridge_bots: list[BotConfig]


plugin_config = get_plugin_config(Config)
where_ami = on_command("where", priority=1, block=True)
any_message = on_message(priority=100)


@where_ami.handle()
async def handle_function(event: Union[Event, TelegramEvent]):
    print(event)
    if isinstance(event, TelegramEvent):
        message = f"{event.get_session_id()} 发送了: {event.get_message()}"
        await where_ami.finish(f"我在....{message}")
    await where_ami.finish(f"我在....{event.model_dump_json()}")

@any_message.handle()
async def brodcast(event: Union[Event, TelegramMessageEvent, FeishuMessageEvent]):
    message = event.get_message()
    sender = event.get_user_id()
    if isinstance(event, TelegramEvent):
        chat_id = str(event.chat.id)
    elif isinstance(event, FeishuEvent):
        chat_id = str(event.event.message.chat_id)
    else:
        chat_id = str(event.get_session_id())
    # 获取和 chat_id 相关的 bridge
    print(chat_id)
    bridge = get_bridge_by_chat_id(chat_id)
    if not bridge:
        await any_message.finish(f"未配置, 无法服务")
    # 发送到除了自己的 land
    for land in bridge.lands:
        if land.id_ == chat_id:
            continue
        bot_config = get_bot_by_name(land.bot_name)
        if not bot_config:
            await any_message.finish(f"未配置相关机器人, 无法服务")
        if bot_config.type_ == "telegram":
            target = TargetTelegramCommon(chat_id=land.id_)
        elif bot_config.type_ == "feishu":
            target = TargetFeishuGroup(chat_id=land.id_)
        else:
            await any_message.finish(f"未知机器人类型, 无法服务")
        bot = get_bot(bot_config.id_)
        print(f"即将发送到: {land.id_}, bot: {land.bot_name}")
        await MessageFactory([Text(f"{message}")]).send_to(target, bot=bot)


def get_bridge_by_chat_id(chat_id: str):
    """根据 chat_id 获取 bridge
    """
    for bridge in plugin_config.nonebot_bridges:
        for land in bridge.lands:
            if land.id_ == chat_id:
                return bridge
    return None

def get_bot_by_name(name: str):
    """根据 bot_name 获取 bot
    """
    for bot in plugin_config.nonebot_bridge_bots:
        if bot.name == name:
            return bot
    return None
