#  cybergram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2024-present Dan <https://github.com/rizaldevs>
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

from io import BytesIO

from cybergram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from cybergram.raw.core import TLObject
from cybergram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class ChatInvitePeek(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~cybergram.raw.base.ChatInvite`.

    Details:
        - Layer: ``158``
        - ID: ``61695CB0``

    Parameters:
        chat (:obj:`Chat <cybergram.raw.base.Chat>`):
            N/A

        expires (``int`` ``32-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: cybergram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.CheckChatInvite
    """

    __slots__: List[str] = ["chat", "expires"]

    ID = 0x61695cb0
    QUALNAME = "types.ChatInvitePeek"

    def __init__(self, *, chat: "raw.base.Chat", expires: int) -> None:
        self.chat = chat  # Chat
        self.expires = expires  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatInvitePeek":
        # No flags
        
        chat = TLObject.read(b)
        
        expires = Int.read(b)
        
        return ChatInvitePeek(chat=chat, expires=expires)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.chat.write())
        
        b.write(Int(self.expires))
        
        return b.getvalue()
