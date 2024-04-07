import logging
from typing import Iterable, Optional

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.types import Message, TelegramObject
from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram
from prometheus_client.metrics_core import GaugeMetricFamily, InfoMetricFamily, Metric

from aiogram_prometheus.collectors.base import BaseAiogramCollector

logger = logging.getLogger('aiogram_prometheus')


class DispatcherAiogramCollector(BaseAiogramCollector):
    dp: Dispatcher

    def __init__(self, dp: Dispatcher, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.dp = dp

        self.mf_aiogram_info = InfoMetricFamily(
            self.prefix,
            'Info about aiogram',
            value={
                'version': aiogram.__version__,
                'api_version': aiogram.__api_version__,
            },
        )

        self.mf_dispatcher_info = InfoMetricFamily(
            f'{self.prefix}_dispatcher',
            'Info about aiogram dispatcher',
            value={
                # 'version': self.dp.errors,
                # 'api_version': aiogram.__api_version__,
            },
        )

        self.register()

    def collect(self) -> Iterable[Metric]:
        yield self.mf_aiogram_info
        yield self.mf_dispatcher_info

        c = GaugeMetricFamily(
            f'{self.prefix}_observers',
            'Aiogram`s Dispatcher`s observers',
            labels=['name'],
        )

        c.add_metric(['shutdown'], len(self.dp.shutdown.handlers))
        c.add_metric(['startup'], len(self.dp.startup.handlers))

        for observer_name, observer in self.dp.observers.items():
            c.add_metric([observer_name], len(observer.handlers))

        yield c

        yield InfoMetricFamily(
            f'{self.prefix}_fsm',
            'Info about aiogram`s dispatcher`s fsm',
            {
                'storage': self.dp.fsm.storage.__class__.__name__,
                'strategy': self.dp.fsm.strategy.__class__.__name__,
                'events_isolation': str(self.dp.fsm.events_isolation),
            },
        )


class ReceivedMessagesAiogramCollector(BaseAiogramCollector):
    prefix: str
    messages_counter: Counter

    def __init__(self, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.messages_counter = Counter(
            f'{self.prefix}_received_messages',
            'Aiogram`s received messages',
            self.labels,
            registry=None,
        )

        self.register()

    def add_messages(self, bot: Bot, message: Message):
        labels = [
            bot.id,
            getattr(bot._me, 'username', 'None'),
            'is_audio' if message.audio is not None else 'no_audio',
            'is_file' if message.media_group_id is not None else 'no_file',
            'is_reply' if message.reply_to_message is not None else 'no_reply',
        ]

        self.messages_counter.labels(*labels).inc()

    def collect(self) -> Iterable[Metric]:
        yield from self.messages_counter.collect()


class MessageMiddlewareAiogramCollector(BaseAiogramCollector):
    LABELS = ['bot_id', 'bot_username', 'event_type', 'error', 'message_type']

    prefix: str

    def __init__(self, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.m_events = Counter(
            f'{self.prefix}_events',
            'Aiogram`s events',
            self.LABELS,
            registry=None,
        )

        self.m_events_time = Histogram(
            f'{self.prefix}_events_time',
            'Aiogram`s events',
            self.LABELS,
            registry=None,
        )

        self.register()

    def add_event(self, event: TelegramObject, executing_time: float, error: Optional[BaseException] = None):
        if event.bot is None or event.bot._me is None:
            return

        labels = {
            'bot_id': event.bot.id,
            'bot_username': getattr(event.bot._me, 'username', 'None'),
            'event_type': event.__class__.__name__,
            'error': 'None',
            'message_type': 'Text',
        }

        if error is not None:
            labels['error'] = error.__class__.__name__

        if isinstance(event, Message):
            for message_type in [
                event.animation,
                event.audio,
                event.document,
                event.photo,
                event.sticker,
                event.story,
                event.video,
                event.video_note,
                event.voice,
                event.caption,
                event.game,
                event.poll,
            ]:
                if message_type is not None:
                    labels['message_type'] = message_type.__class__.__name__

        self.m_events.labels(**labels).inc()
        self.m_events_time.labels(**labels).observe(executing_time)

    def collect(self) -> Iterable[Metric]:
        yield from self.m_events.collect()
