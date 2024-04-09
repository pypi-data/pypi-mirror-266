from functools import partial
from typing import Any, List, Optional

import uprock_sdk.telegram_bots
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from approck_messaging.subscriber import Subscriber
from redis.asyncio.client import Redis

from approck_aiogram_utils.integration.uprock.handlers import send_message_handler


class TelegramDispatcher(Dispatcher):
    def __init__(self, token: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.bot = Bot(token=token, parse_mode="HTML")

    def run(self, **kwargs: Any) -> None:
        super().run_polling(self.bot, **kwargs)

    async def start(self, **kwargs: Any) -> None:
        await super().start_polling(self.bot, **kwargs)


async def commands_on_startup(bot: Bot, commands: List[BotCommand]) -> None:
    await bot.set_my_commands(commands)


async def create_app(
    id_: int, router: Router, commands: Optional[List[BotCommand]] = None, message_channels: Optional[List[str]] = None
) -> TelegramDispatcher:
    telegram_bot = await uprock_sdk.telegram_bots.get(id_)

    storage = RedisStorage(Redis.from_url(str(telegram_bot.redis_uri)))

    dispatcher = TelegramDispatcher(token=telegram_bot.token, storage=storage)
    dispatcher.include_router(router)

    # Register startup hook to initialize commands webhook
    if commands:
        dispatcher.startup.register(partial(commands_on_startup, commands=commands))

    # Register startup hook to initialize message processing webhook
    if message_channels:
        subscriber = Subscriber.from_uri(redis_uri=telegram_bot.redis_uri, bot=dispatcher.bot)
        for message_channel in message_channels:
            subscriber.message(message_channel)(send_message_handler)

        dispatcher.startup.register(subscriber.broker.start)
        dispatcher.shutdown.register(subscriber.broker.close)

    return dispatcher
