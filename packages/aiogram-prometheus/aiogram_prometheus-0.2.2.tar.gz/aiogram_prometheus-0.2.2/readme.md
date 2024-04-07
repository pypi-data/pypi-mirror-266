# aiogram Prometheus Exporter

Module for exporting monitoring values for Prometheus

[![PyPI](https://img.shields.io/pypi/v/aiogram-prometheus)](https://pypi.org/project/aiogram-prometheus/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiogram-prometheus)](https://pypi.org/project/aiogram-prometheus/)
[![GitLab last commit](https://img.shields.io/gitlab/last-commit/rocshers/python/aiogram-prometheus)](https://gitlab.com/rocshers/python/aiogram-prometheus)
[![Docs](https://img.shields.io/badge/docs-exist-blue)](https://rocshers.gitlab.io/python/aiogram-prometheus/)

[![Test coverage](https://codecov.io/gitlab/rocshers:python/aiogram-prometheus/graph/badge.svg?token=3C6SLDPHUC)](https://codecov.io/gitlab/rocshers:python/aiogram-prometheus)
[![Downloads](https://static.pepy.tech/badge/aiogram-prometheus)](https://pepy.tech/project/aiogram-prometheus)
[![GitLab stars](https://img.shields.io/gitlab/stars/rocshers/python/aiogram-prometheus)](https://gitlab.com/rocshers/python/aiogram-prometheus)

## Installation

`pip install aiogram-prometheus`

## Quick start

- **aiogram.BotAiogramCollector** - base `info` abut started bot
- **aiogram.PrometheusMetricRequestMiddleware** - tracking `requests` from bot to server
- **aiogram.DispatcherAiogramCollector** - base `info` abut started app
- **aiogram.PrometheusMetricMessageMiddleware** - tracking `event` for app processing
- **aiogram.StorageAiogramCollector** - tracking `actions` with fsm storage
- **aiogram.PushGatewayClient** - easy way to push your metrics to `pushgateway` server

```python
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from decouple import config

from aiogram_prometheus import (
    BotAiogramCollector,
    DispatcherAiogramCollector,
    PrometheusMetricMessageMiddleware,
    PrometheusMetricStorageMixin,
    PrometheusMetricRequestMiddleware,
    PushGatewayClient,
    StorageAiogramCollector,
)

logging.basicConfig(level='DEBUG')

logger = logging.getLogger(__name__)

bot = Bot('TOKEN')

# Bot info metrics
BotAiogramCollector().add_bot(bot)

# Metric requests
# which are made by the target bot
bot.session.middleware(PrometheusMetricRequestMiddleware())

# Metric storage
# Change "MemoryStorage" to your storage
class _Storage(PrometheusMetricStorageMixin, MemoryStorage):
    pass

storage_collector = StorageAiogramCollector()
storage = _Storage(storage_collector)

dp = Dispatcher(storage=storage)

# Metric message
# which are processed by the dispatcher
dp.message.middleware(PrometheusMetricMessageMiddleware())


# Metric base info
DispatcherAiogramCollector(dp)

push_gateway_client = PushGatewayClient('http://localhost:9091/', 'job-name')

@dp.startup()
async def on_startup(bot: Bot):
    push_gateway_client.schedule_push(5)

@dp.message()
async def handle(message: Message) -> None:
    await message.reply('Ok')

asyncio.run(dp.start_polling(bot))

```

## Functionality

### aiogram.BotAiogramCollector

You should use this collector if you want to track information about running bots. The metrics include most of the available information about the bot, including its `id`, `username` and `full_name`

```python
from aiogram import Bot
from aiogram_prometheus import BotAiogramCollector

bot = Bot(TOKEN)

BotAiogramCollector(bot)
```

### aiogram.PrometheusMetricRequestMiddleware

This is an intermediate layer for requests that are sent to telegram servers on behalf of a specific bot. Use this middleware to track `requests`, their `types`, and their `execution times`.

```python
from aiogram import Bot
from aiogram_prometheus import PrometheusMetricRequestMiddleware

bot = Bot(TOKEN)
bot.session.middleware(PrometheusMetricRequestMiddleware())
```

### aiogram.DispatcherAiogramCollector

You should use this collector if you want to track general application information. This will be useful if you want to keep the `aiogram_version` and `telegram_api` up to date

```python
from aiogram import Dispatcher
from aiogram_prometheus import DispatcherAiogramCollector

dp = Dispatcher()

DispatcherAiogramCollector(dp)
```

### aiogram.PrometheusMetricMessageMiddleware

this intermediate layer is needed to track the events that the dispatcher processes. You will receive information about the `event`, the `execution times` (by your application), and the `message` (if the event is a message).

Note: if there is no handler for a message, then the message will not be tracked

```python
from aiogram import Dispatcher
from aiogram_prometheus import PrometheusMetricMessageMiddleware

dp = Dispatcher()
dp.message.middleware(PrometheusMetricMessageMiddleware())
```

### aiogram.StorageAiogramCollector

This collector is used inside a storage mixin. You should use it if you need transparency when working with storage. You will be able to see how `often` and how `much data` you `save and read`.

note. To use this collector you must use a mixin (`aiogram.PrometheusMetricStorageMixin`)

```python
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_prometheus import PrometheusMetricStorageMixin, StorageAiogramCollector

class _Storage(PrometheusMetricStorageMixin, MemoryStorage):
    pass

storage = _Storage(StorageAiogramCollector())

dp = Dispatcher(storage=storage)
```

### aiogram.PushGatewayClient

Collecting metrics from application software is not an easy task. You can run a web application in parallel or use `pushgateway`. If everything is clear with the first, then there may be problems with the second. You can use the client implemented here, which starts when the application starts and sends metrics to the server every X seconds.

```python
from aiogram import Dispatcher, Bot
from aiogram_prometheus import PushGatewayClient

dp = Dispatcher()

push_gateway_client = PushGatewayClient('http://localhost:9091/', 'job-name')

@dp.startup()
async def on_startup(bot: Bot):
    push_gateway_client.schedule_push(5)
```


## Contribute

Issue Tracker: <https://gitlab.com/rocshers/python/aiogram-prometheus/-/issues>  
Source Code: <https://gitlab.com/rocshers/python/aiogram-prometheus>

Before adding changes:

```bash
make install-dev
```

After changes:

```bash
make format test
```
