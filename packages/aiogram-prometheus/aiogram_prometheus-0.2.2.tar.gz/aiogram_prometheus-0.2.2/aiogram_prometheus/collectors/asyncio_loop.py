import asyncio
from typing import Iterable, Optional

from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.metrics_core import Metric
from prometheus_client.registry import Collector


class AsyncioCollector(Collector):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super().__init__()
        self.loop = loop

    def collect(self) -> Iterable[Metric]:
        if self.loop is None:
            try:
                self.loop = asyncio.get_running_loop()

            except RuntimeError:
                return

        yield InfoMetricFamily(
            'python_asyncio_loops',
            'Count of active asyncio loops',
            {
                'id': str(id(self.loop)),
                'is_running': str(self.loop.is_running()),
                'is_debug': str(self.loop.get_debug()),
            },
        )

        c = GaugeMetricFamily(
            'python_asyncio_tasks',
            'Count of active asyncio tasks',
            labels=['loop_id'],
        )

        c.add_metric(
            [str(id(self.loop))],
            len(asyncio.all_tasks(self.loop)),
        )

        yield c
