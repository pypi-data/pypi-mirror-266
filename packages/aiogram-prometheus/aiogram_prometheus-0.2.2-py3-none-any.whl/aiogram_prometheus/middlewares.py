import logging
import time
from typing import Any, Awaitable, Callable, Coroutine, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.client.bot import Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware, NextRequestMiddlewareType
from aiogram.methods import Response, TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import Message, TelegramObject

from aiogram_prometheus.collectors import MessageMiddlewareAiogramCollector, RequestsBotAiogramCollector

logger = logging.getLogger('aiogram_prometheus')

__all__ = ('PrometheusMetricMessageMiddleware', 'PrometheusMetricRequestMiddleware')


class PrometheusMetricMessageMiddleware(BaseMiddleware):
    """Middleware for metrics messages in Dispatcher

    ### Args

    - collector [MessageMiddlewareAiogramCollector] optional

    ### Usage

    Need add to `dp.message.middleware`

    ### Example:

    ```
    from aiogram import Bot
    from from aiogram_prometheus import PrometheusMetricMessageMiddleware

    dp = Dispatcher()
    dp.message.middleware(PrometheusMetricMessageMiddleware())

    ```
    """

    collector: MessageMiddlewareAiogramCollector

    def __init__(self, collector: Optional[MessageMiddlewareAiogramCollector] = None) -> None:
        self.collector = collector if collector is not None else MessageMiddlewareAiogramCollector()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Coroutine[Any, Any, Any]:
        start_time = time.time()

        try:
            res = await handler(event, data)

        except BaseException as ex:
            delta_time = time.time() - start_time
            self.collector.add_event(event, delta_time, ex)
            raise ex

        delta_time = time.time() - start_time
        self.collector.add_event(event, delta_time)
        return res


class PrometheusMetricRequestMiddleware(BaseRequestMiddleware):
    """Middleware for metric requests from Bot

    ### Args

    - collector [RequestsBotAiogramCollector] optional

    ### Usage

    Need add to `bot.session.middleware`

    ### Example:

    ```python
    from aiogram import Bot
    from from aiogram_prometheus import PrometheusMetricRequestMiddleware

    bot = Bot(TOKEN)
    bot.session.middleware(PrometheusMetricRequestMiddleware())

    ```

    """

    def __init__(self, collector: Optional[RequestsBotAiogramCollector] = None) -> None:
        self.collector = collector if collector is not None else RequestsBotAiogramCollector()

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Coroutine[Any, Any, Response[TelegramType]]:
        start_time = time.time()

        try:
            response = await make_request(bot, method)

        except BaseException as ex:
            delta_time = time.time() - start_time
            self.collector.add_request(bot, method, None, delta_time, ex)
            raise ex

        delta_time = time.time() - start_time
        self.collector.add_request(bot, method, response, delta_time, None)

        return response
