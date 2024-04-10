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


class ChatlistUpdates(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~cybergram.raw.base.chatlists.ChatlistUpdates`.

    Details:
        - Layer: ``158``
        - ID: ``93BD878D``

    Parameters:
        missing_peers (List of :obj:`Peer <cybergram.raw.base.Peer>`):
            N/A

        chats (List of :obj:`Chat <cybergram.raw.base.Chat>`):
            N/A

        users (List of :obj:`User <cybergram.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: cybergram.raw.functions

        .. autosummary::
            :nosignatures:

            chatlists.GetChatlistUpdates
    """

    __slots__: List[str] = ["missing_peers", "chats", "users"]

    ID = 0x93bd878d
    QUALNAME = "types.chatlists.ChatlistUpdates"

    def __init__(self, *, missing_peers: List["raw.base.Peer"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.missing_peers = missing_peers  # Vector<Peer>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatlistUpdates":
        # No flags
        
        missing_peers = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChatlistUpdates(missing_peers=missing_peers, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.missing_peers))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
