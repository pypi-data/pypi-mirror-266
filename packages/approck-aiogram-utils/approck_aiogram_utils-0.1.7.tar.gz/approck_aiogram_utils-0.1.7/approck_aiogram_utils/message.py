import asyncio
import uuid
from typing import Union, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError
from aiogram.types import (
    URLInputFile,
    InputMediaVideo,
    InputMediaPhoto,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)
from approck_messaging.models.message import Message, MessageType, MessageMedia
from loguru import logger


async def _send_message_generic(
    bot: Bot,
    chat_id: Union[int, str],
    message: Message,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    if message.media:
        if len(message.media) > 1:
            media_group = []
            is_caption_added = False

            for media in message.media or []:
                caption = None

                if not is_caption_added:
                    caption = message.caption

                if media.type.startswith("image"):
                    media_group.append(InputMediaPhoto(media=URLInputFile(url=str(media.url)), caption=caption))
                    is_caption_added = True
                elif media.type.startswith("video"):
                    media_group.append(InputMediaVideo(media=URLInputFile(url=str(media.url)), caption=caption))
                    is_caption_added = True

            # NOTE:
            #  pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: PyErr { type: <class 'KeyError'>, value: KeyError('parse_mode'), traceback: None }
            # if media:
            #     media[0].caption = dto.caption

            await bot.send_media_group(chat_id=chat_id, media=media_group)
        else:
            media = message.media[0]

            if media.type.startswith("image"):
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=URLInputFile(url=str(media.url)),
                    caption=message.caption,
                    reply_markup=reply_markup,
                )
            elif media.type.startswith("video"):
                await bot.send_video(
                    chat_id=chat_id,
                    video=URLInputFile(url=str(media.url)),
                    caption=message.caption,
                    reply_markup=reply_markup,
                )
    else:
        if message.caption:
            await bot.send_message(
                chat_id=chat_id, text=message.caption, disable_web_page_preview=True, reply_markup=reply_markup
            )


async def _send_message_video_note(
    bot: Bot,
    chat_id: Union[int, str],
    message: Message,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    await bot.send_video_note(
        chat_id=chat_id, video_note=URLInputFile(url=str(message.video_note.url)), reply_markup=reply_markup
    )


async def _send_message_impl(
    bot: Bot,
    chat_id: Union[int, str],
    message: Message,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    send_message_impl_map = {
        MessageType.GENERIC: _send_message_generic,
        MessageType.VIDEO_NOTE: _send_message_video_note,
    }

    send_message_func = send_message_impl_map.get(message.type)

    if not send_message_func:
        raise NotImplementedError(f"Message type '{message.type}' is not supported")

    return await send_message_func(bot=bot, chat_id=chat_id, message=message, reply_markup=reply_markup)


async def send_message(
    bot: Bot,
    chat_id: Union[int, str],
    message: Message,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    # noinspection PyBroadException
    try:
        await _send_message_impl(bot=bot, chat_id=chat_id, message=message, reply_markup=reply_markup)
    except TelegramForbiddenError as exc:
        logger.info("Forbidden: {}", exc.message)
    except TelegramBadRequest as exc:
        if "USER_IS_BLOCKED" in exc.message:
            logger.info("Forbidden: {}", exc.message)
        elif "VOICE_MESSAGES_FORBIDDEN" in exc.message:
            logger.info("Voice messages forbidden: {}", exc.message)
        else:
            logger.exception("Unable to send message")
            raise
    except TelegramRetryAfter as exc:
        await asyncio.sleep(exc.retry_after)
        await send_message(bot=bot, chat_id=chat_id, message=message, reply_markup=reply_markup)  # Recursive call
    except Exception:
        logger.exception("Unable to send message")
        raise


async def send_simple_message(
    bot: Bot,
    chat_id: Union[str, int],
    caption: Optional[str] = None,
    cover: Optional[str] = None,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    media = (
        [MessageMedia(id=uuid.uuid4().hex, type="image/png", name="", url=caption, status="finished")]
        if cover
        else None
    )

    await send_message(
        bot=bot,
        chat_id=chat_id,
        message=Message(type=MessageType.GENERIC, caption=caption, media=media),
        reply_markup=reply_markup,
    )
