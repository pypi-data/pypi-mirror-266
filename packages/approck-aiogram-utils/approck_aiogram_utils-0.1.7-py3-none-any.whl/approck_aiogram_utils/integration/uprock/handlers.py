from aiogram import Bot
from approck_messaging.models.message import TransportMessage
from faststream import Context
from faststream.exceptions import NackMessage
from uprock_sdk import terms

from approck_aiogram_utils.message import send_message


async def send_message_handler(message: TransportMessage, bot: Bot = Context()):
    if message.caption:
        message.caption = terms.sanitize(message.caption)

    try:
        await send_message(bot=bot, chat_id=message.recipient.telegram_id, message=message)
    except Exception as exc:
        raise NackMessage() from exc
