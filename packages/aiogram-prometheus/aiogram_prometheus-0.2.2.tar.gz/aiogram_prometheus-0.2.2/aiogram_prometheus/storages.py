from typing import Any, Dict, Optional

from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from aiogram_prometheus.collectors.storages import StorageAiogramCollector


class PrometheusMetricStorageMixin(BaseStorage):

    collector: StorageAiogramCollector

    def __init__(self, storage_collector: Optional[StorageAiogramCollector] = None, *args: Any, **kwargs: Any) -> None:
        self.collector = storage_collector if storage_collector is not None else StorageAiogramCollector()
        super().__init__(*args, **kwargs)

        self.collector.set_storage(self)

    async def close(self) -> None:
        async with self.collector.manager('close', None):
            await super().close()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        async with self.collector.manager('set_state', key):
            await super().set_state(key, state)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with self.collector.manager('get_state', key):
            return await super().get_state(key)

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        async with self.collector.manager('set_data', key):
            await super().set_data(key, data)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async with self.collector.manager('get_data', key):
            return await super().get_data(key)
