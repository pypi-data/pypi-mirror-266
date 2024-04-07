import logging

from prometheus_client import REGISTRY, CollectorRegistry
from prometheus_client.registry import Collector

logger = logging.getLogger('aiogram_prometheus')


class BaseAiogramCollector(Collector):
    prefix: str
    registry: CollectorRegistry

    def __init__(self, prefix: str = 'aiogram', registry: CollectorRegistry = REGISTRY) -> None:
        super().__init__()

        self.prefix = prefix
        self.registry = registry

    def register(self):
        self.registry.register(self)
