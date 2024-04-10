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


class MessageMediaWebPage(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~cybergram.raw.base.MessageMedia`.

    Details:
        - Layer: ``158``
        - ID: ``A32DD600``

    Parameters:
        webpage (:obj:`WebPage <cybergram.raw.base.WebPage>`):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: cybergram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetWebPagePreview
            messages.UploadMedia
            messages.UploadImportedMedia
    """

    __slots__: List[str] = ["webpage"]

    ID = 0xa32dd600
    QUALNAME = "types.MessageMediaWebPage"

    def __init__(self, *, webpage: "raw.base.WebPage") -> None:
        self.webpage = webpage  # WebPage

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaWebPage":
        # No flags
        
        webpage = TLObject.read(b)
        
        return MessageMediaWebPage(webpage=webpage)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.webpage.write())
        
        return b.getvalue()
