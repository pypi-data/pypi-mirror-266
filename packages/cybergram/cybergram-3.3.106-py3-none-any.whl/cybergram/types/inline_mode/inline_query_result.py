#  cybergram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2024-present Dan <https://github.com/delivrance>
#
#  This file is part of cybergram.
#
#  cybergram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cybergram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with cybergram.  If not, see <http://www.gnu.org/licenses/>.

from uuid import uuid4

import cybergram
from cybergram import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~cybergram.types.InlineQueryResultCachedAudio`
    - :obj:`~cybergram.types.InlineQueryResultCachedDocument`
    - :obj:`~cybergram.types.InlineQueryResultCachedAnimation`
    - :obj:`~cybergram.types.InlineQueryResultCachedPhoto`
    - :obj:`~cybergram.types.InlineQueryResultCachedSticker`
    - :obj:`~cybergram.types.InlineQueryResultCachedVideo`
    - :obj:`~cybergram.types.InlineQueryResultCachedVoice`
    - :obj:`~cybergram.types.InlineQueryResultArticle`
    - :obj:`~cybergram.types.InlineQueryResultAudio`
    - :obj:`~cybergram.types.InlineQueryResultContact`
    - :obj:`~cybergram.types.InlineQueryResultDocument`
    - :obj:`~cybergram.types.InlineQueryResultAnimation`
    - :obj:`~cybergram.types.InlineQueryResultLocation`
    - :obj:`~cybergram.types.InlineQueryResultPhoto`
    - :obj:`~cybergram.types.InlineQueryResultVenue`
    - :obj:`~cybergram.types.InlineQueryResultVideo`
    - :obj:`~cybergram.types.InlineQueryResultVoice`
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

    async def write(self, client: "cybergram.Client"):
        pass
