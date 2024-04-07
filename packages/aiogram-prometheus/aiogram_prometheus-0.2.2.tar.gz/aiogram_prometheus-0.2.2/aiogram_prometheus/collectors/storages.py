from __future__ import annotations

import logging
import time
from inspect import Traceback
from typing import Any, Iterable, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram
from prometheus_client.metrics_core import GaugeMetricFamily, InfoMetricFamily, Metric

from aiogram_prometheus.collectors.base import BaseAiogramCollector

logger = logging.getLogger('aiogram_prometheus')


class StorageAiogramCollector(BaseAiogramCollector):
    """Storage for metric Storages action

    Need use with PrometheusMetricStorageMixin

    ### Example

    ```
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram_prometheus import StorageAiogramCollector, PrometheusMetricStorageMixin

    # Use mixin
    class _Storage(PrometheusMetricStorageMixin, MemoryStorage):
        pass

    storage_collector = StorageAiogramCollector()
    storage = _Storage(storage_collector)

    dp = Dispatcher(storage=storage)
    ```
    """

    LABELS: list[str] = ['bot_id', 'action', 'error_type']
    uniq_sets: dict[str, set[Any]]

    def __init__(self, prefix: str = 'aiogram_storage', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__(prefix, registry)

        self.storage = None

        self.m_storage_actinos = Counter(
            f'{self.prefix}_actions',
            'Aiogram`s received messages',
            self.LABELS,
            registry=None,
        )

        self.m_storage_actinos_time = Histogram(
            f'{self.prefix}_actions_time',
            'Aiogram`s received messages',
            self.LABELS,
            registry=None,
        )

        self.uniq_sets = {
            'chat_id': set(),
            'thread_id': set(),
            'destiny': set(),
            'user_id': set(),
        }

        self.register()

    def set_storage(self, storage: BaseStorage):
        self.storage = storage

    def manager(self, action: str, key: Optional[StorageKey]) -> ActionStorageManager:
        return ActionStorageManager(self, action, key)

    def was_action(self, action: str, key: Optional[StorageKey], delta_time: float, ex: Optional[BaseException] = None):
        labels = {'action': action, 'bot_id': 'None', 'error_type': 'None'}

        if key is not None:
            labels['bot_id'] = key.bot_id

            self.uniq_sets['chat_id'].add(key.chat_id)
            self.uniq_sets['thread_id'].add(key.thread_id)
            self.uniq_sets['destiny'].add(key.destiny)
            self.uniq_sets['user_id'].add(key.user_id)

        if ex is not None:
            labels['error_type'] = ex.__class__.__name__

        self.m_storage_actinos.labels(**labels).inc()

        self.m_storage_actinos_time.labels(**labels).observe(delta_time)

    def collect(self) -> Iterable[Metric]:
        if self.storage is None:
            return

        yield InfoMetricFamily(
            self.prefix,
            'Info about aiogram storage',
            value={
                'type': self.storage.__class__.__name__,
            },
        )

        yield GaugeMetricFamily(
            f'{self.prefix}_chats',
            'Count of uniq chats in storage',
            len(self.uniq_sets['chat_id']),
        )

        yield GaugeMetricFamily(
            f'{self.prefix}_threads',
            'Count of uniq threads in storage',
            len(self.uniq_sets['thread_id']),
        )

        yield GaugeMetricFamily(
            f'{self.prefix}_destinies',
            'Count of uniq destinies in storage',
            len(self.uniq_sets['destiny']),
        )

        yield GaugeMetricFamily(
            f'{self.prefix}_users',
            'Count of uniq users in storage',
            len(self.uniq_sets['user_id']),
        )

        yield from self.m_storage_actinos.collect()
        yield from self.m_storage_actinos_time.collect()


class ActionStorageManager(object):
    started_at: float

    def __init__(self, collector: StorageAiogramCollector, action: str, key: Optional[StorageKey]):
        self.collector = collector
        self.action = action
        self.key = key

    async def __aenter__(self):
        self.started_at = time.time()
        return self

    async def __aexit__(self, exc_type: type[BaseException], exc_value: BaseException, traceback: Traceback):
        if exc_value is not None:
            pass

        return False
