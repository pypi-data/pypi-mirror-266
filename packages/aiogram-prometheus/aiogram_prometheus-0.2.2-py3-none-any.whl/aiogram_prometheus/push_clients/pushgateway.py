import base64
import logging
import time
from typing import List
from urllib.parse import quote_plus, urlparse, urlunparse

import aiohttp
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from aiogram_prometheus.push_clients.base import BasePushClient

logger = logging.getLogger('prometheus_client')


def _escape_grouping_key(key: str, value: str):
    if not value:
        return key + '@base64', '='

    if '/' in value:
        return key + '@base64', base64.urlsafe_b64encode(value.encode('utf-8')).decode('utf-8')

    return key, quote_plus(value)


def normalize_url(base_url: str, adding_path: List[str]) -> str:
    parsed_url = urlparse(base_url)

    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()

    assert netloc, f'Can`t parse base url: {base_url}'

    if scheme not in ['http', 'https']:
        scheme = 'http'

    path = parsed_url.path + '/'.join(adding_path)

    return urlunparse((scheme, netloc, path, parsed_url.params, parsed_url.query, parsed_url.fragment))


class PushGatewayClient(BasePushClient):
    @property
    def url(self) -> str:
        path_params = [('job', self.job)] + sorted(list(self.grouping_key.items()))
        path_normalize_params = [
            item for sublist in [_escape_grouping_key(k, v) for k, v in path_params] for item in sublist
        ]

        path_normalize_params = ['metrics'] + path_normalize_params

        return normalize_url(self.base_address, path_normalize_params)

    async def push(self):
        logger.debug(f'Started pushing "{self.__class__.__name__}"')

        data = generate_latest(self.registry)

        start_time = time.time()
        response = None

        async with aiohttp.ClientSession(headers={'Content-Type': CONTENT_TYPE_LATEST}) as session:
            try:
                response = await session.put(self.url, data=data)

            except BaseException as ex:
                logger.error('push gateway error: ', ex)

        if response is None:
            self.collector.was_push(None, time.time() - start_time)
            return

        self.collector.was_push(response.status, time.time() - start_time)

        if response.status != 200:
            text = await response.text()
            logger.error(f'push gateway error: code={response.status} text={text}')
            return

        logger.debug('Success pushed')

        # push_to_gateway(self.base_address, self.job, self.registry)
