import logging
from typing import Any, Iterable, List, Optional

from aiogram import Bot
from aiogram.methods import Response, TelegramMethod
from prometheus_client import REGISTRY, CollectorRegistry, Histogram
from prometheus_client.metrics_core import InfoMetricFamily, Metric

from aiogram_prometheus.collectors.base import BaseAiogramCollector

logger = logging.getLogger('aiogram_prometheus')


class BotAiogramCollector(BaseAiogramCollector):
    """Collector for main info about bot

    Args:
        bot [aiogram.Bot]: Object of target bot

    """

    bots: List[Bot]

    def __init__(self, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.bots = []

        self.register()

    def add_bot(self, bot: Bot):
        self.bots.append(bot)

    def collect(self) -> Iterable[Metric]:
        for bot in self.bots:
            bot_user = bot._me

            if bot_user is None:
                return

            yield InfoMetricFamily(
                f'{self.prefix}_bot',
                'Info about bot',
                {
                    'id': str(bot.id),
                    'username': str(bot_user.username),
                    'is_bot': str(bot_user.is_bot),
                    'first_name': str(bot_user.first_name),
                    'last_name': str(bot_user.last_name),
                    'language_code': str(bot_user.language_code),
                    'is_premium': str(bot_user.is_premium),
                    'added_to_attachment_menu': str(bot_user.added_to_attachment_menu),
                    'can_join_groups': str(bot_user.can_join_groups),
                    'can_read_all_group_messages': str(bot_user.can_read_all_group_messages),
                    'supports_inline_queries': str(bot_user.supports_inline_queries),
                    'parse_mode': str(bot.parse_mode),
                    'disable_web_page_preview': str(bot.disable_web_page_preview),
                    'protect_content': str(bot.protect_content),
                },
            )


class RequestsBotAiogramCollector(BaseAiogramCollector):
    """Collector for requests from bot to server

    Used inside aiogram_prometheus.middlewares.PrometheusMetricRequestMiddleware

    """

    prefix: str
    m_requests_histogram: Histogram
    LABELS = ['method_type', 'bot_username', 'error']

    def __init__(self, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.m_requests_histogram = Histogram(
            f'{self.prefix}_requests',
            'Aiogram`s requests',
            self.LABELS,
            registry=None,
        )

        self.register()

    def add_request(
        self,
        bot: Bot,
        method: Optional[TelegramMethod[Any]],
        response: Optional[Response[Any]],
        executing_time: float,
        error: Optional[BaseException] = None,
    ):
        labels = {
            'method_type': method.__class__.__name__,
            'bot_username': getattr(bot._me, 'username', 'None'),
            'error': error.__class__.__name__,
        }

        if response is not None:
            pass

        self.m_requests_histogram.labels(**labels).observe(executing_time)

    def collect(self) -> Iterable[Metric]:
        yield from self.m_requests_histogram.collect()
