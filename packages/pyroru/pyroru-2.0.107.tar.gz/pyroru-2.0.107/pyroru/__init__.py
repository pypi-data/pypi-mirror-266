__version__ = "2.0.107"
__license__ = "Меньшая стандартная общественная лицензия GNU v3.0 (LGPL-3.0)"
__copyright__ = "Авторские права (C) Дэн, 2017 г. <https://github.com/delivrance>"

from concurrent.futures.thread import ThreadPoolExecutor


class StopTransmission(Exception):
    pass


class StopPropagation(StopAsyncIteration):
    pass


class ContinuePropagation(StopAsyncIteration):
    pass


from . import raw, types, filters, handlers, emoji, enums
from .client import Client
from .sync import idle, compose

crypto_executor = ThreadPoolExecutor(1, thread_name_prefix="CryptoWorker")
