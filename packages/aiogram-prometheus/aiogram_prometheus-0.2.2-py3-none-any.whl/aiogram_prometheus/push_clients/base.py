import abc
import asyncio
import logging
import time
from asyncio import AbstractEventLoop
from typing import Dict, Optional

from prometheus_client import REGISTRY, CollectorRegistry

from aiogram_prometheus.collectors import PushClientsCollector

logger = logging.getLogger('aiogram_prometheus')


class BasePushClient(abc.ABC):
    base_address: str
    job: str
    registry: CollectorRegistry
    grouping_key: Dict[str, str]

    _schedule_task: Optional[asyncio.Task]

    def __init__(
        self,
        base_address: str,
        job: str,
        grouping_key: Optional[Dict[str, str]] = None,
        registry: CollectorRegistry = REGISTRY,
    ) -> None:
        self.base_address = base_address
        self.job = job
        self.grouping_key = grouping_key if grouping_key is not None else {}
        self.registry = registry

        self.collector = PushClientsCollector()
        registry.register(self.collector)

        self._schedule_task = None

    @abc.abstractmethod
    async def push(self):
        pass

    async def __schedule_push(self, on_time: int = 15):
        _on_time_original = on_time

        while True:
            await asyncio.sleep(on_time)

            _start_time = time.time()

            try:
                await self.push()

            except asyncio.CancelledError as ex:
                raise ex

            except BaseException as ex:
                logger.error(f'"{self.__class__.__name__}" pushing error: {ex}')

                on_time += _on_time_original

            else:
                on_time = _on_time_original

            self.collector.was_push(200, time.time() - _start_time)

    def schedule_push(self, on_time: int = 15, loop: Optional[AbstractEventLoop] = None):
        """Sending metrics once every on_time seconds

        Args:
            on_time (int, optional): Seconds

        """

        if self._schedule_task is not None and not self._schedule_task.cancelled():
            logger.warning(f'"{self.__class__.__name__}" schedule already started')
            return

        if loop is None:
            loop = asyncio.get_event_loop()

        self._schedule_task = loop.create_task(self.__schedule_push(on_time))
