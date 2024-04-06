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

from uuid import uuid4

import pyroru
from pyroru import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~pyroru.types.InlineQueryResultCachedAudio`
    - :obj:`~pyroru.types.InlineQueryResultCachedDocument`
    - :obj:`~pyroru.types.InlineQueryResultCachedAnimation`
    - :obj:`~pyroru.types.InlineQueryResultCachedPhoto`
    - :obj:`~pyroru.types.InlineQueryResultCachedSticker`
    - :obj:`~pyroru.types.InlineQueryResultCachedVideo`
    - :obj:`~pyroru.types.InlineQueryResultCachedVoice`
    - :obj:`~pyroru.types.InlineQueryResultArticle`
    - :obj:`~pyroru.types.InlineQueryResultAudio`
    - :obj:`~pyroru.types.InlineQueryResultContact`
    - :obj:`~pyroru.types.InlineQueryResultDocument`
    - :obj:`~pyroru.types.InlineQueryResultAnimation`
    - :obj:`~pyroru.types.InlineQueryResultLocation`
    - :obj:`~pyroru.types.InlineQueryResultPhoto`
    - :obj:`~pyroru.types.InlineQueryResultVenue`
    - :obj:`~pyroru.types.InlineQueryResultVideo`
    - :obj:`~pyroru.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "pyroru.Client"):
        pass
