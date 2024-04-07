from typing import Iterable, Optional

from prometheus_client import Counter, Histogram
from prometheus_client.metrics_core import Metric
from prometheus_client.registry import Collector


class PushClientsCollector(Collector):
    prefix: str = 'python_prometheus_push'

    def __init__(self) -> None:
        super().__init__()

        self.m_requests = Counter(
            f'{self.prefix}_requests',
            'Count of push requests',
            labelnames=['status_code'],
            registry=None,
        )
        self.m_requests_time = Histogram(
            f'{self.prefix}_requests_time',
            'Histogram about time push requests',
            labelnames=['status_code'],
            registry=None,
        )

    def was_push(self, status_code: Optional[int], execute_time: float):
        self.m_requests.labels(
            status_code=str(status_code),
        ).inc()

        self.m_requests_time.labels(
            status_code=str(status_code),
        ).observe(execute_time)

    def collect(self) -> Iterable[Metric]:
        yield from self.m_requests.collect()
        yield from self.m_requests_time.collect()
