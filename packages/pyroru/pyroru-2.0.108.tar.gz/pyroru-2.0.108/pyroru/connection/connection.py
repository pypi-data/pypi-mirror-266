#  Pyroru - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyroru.
#
#  Pyroru is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyroru is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyroru.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
from typing import Optional

from .transport import TCP, TCPAbridged
from ..session.internals import DataCenter

log = logging.getLogger(__name__)


class Connection:
    MAX_CONNECTION_ATTEMPTS = 3

    def __init__(self, dc_id: int, test_mode: bool, ipv6: bool, proxy: dict, media: bool = False):
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.ipv6 = ipv6
        self.proxy = proxy
        self.media = media

        self.address = DataCenter(dc_id, test_mode, ipv6, media)
        self.protocol: TCP = None

    async def connect(self):
        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            self.protocol = TCPAbridged(self.ipv6, self.proxy)

            try:
                log.info("Подключение...")
                await self.protocol.connect(self.address)
            except OSError as e:
                log.warning("Не удалось подключиться по причине: %s", e)
                await self.protocol.close()
                await asyncio.sleep(1)
            else:
                log.info("Подключено! %s DC%s%s - IPv%s",
                         "Тест" if self.test_mode else "Производство",
                         self.dc_id,
                         " (медиа)" if self.media else "",
                         "6" if self.ipv6 else "4")
                break
        else:
            log.warning("Ошибка подключения. Попробуйте ещё раз...")
            raise ConnectionError

    async def close(self):
        await self.protocol.close()
        log.info("Отключено")

    async def send(self, data: bytes):
        await self.protocol.send(data)

    async def recv(self) -> Optional[bytes]:
        return await self.protocol.recv()
