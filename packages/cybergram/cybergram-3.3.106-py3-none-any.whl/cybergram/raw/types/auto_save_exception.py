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


class AutoSaveException(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~cybergram.raw.base.AutoSaveException`.

    Details:
        - Layer: ``158``
        - ID: ``81602D47``

    Parameters:
        peer (:obj:`Peer <cybergram.raw.base.Peer>`):
            N/A

        settings (:obj:`AutoSaveSettings <cybergram.raw.base.AutoSaveSettings>`):
            N/A

    """

    __slots__: List[str] = ["peer", "settings"]

    ID = 0x81602d47
    QUALNAME = "types.AutoSaveException"

    def __init__(self, *, peer: "raw.base.Peer", settings: "raw.base.AutoSaveSettings") -> None:
        self.peer = peer  # Peer
        self.settings = settings  # AutoSaveSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AutoSaveException":
        # No flags
        
        peer = TLObject.read(b)
        
        settings = TLObject.read(b)
        
        return AutoSaveException(peer=peer, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.settings.write())
        
        return b.getvalue()
