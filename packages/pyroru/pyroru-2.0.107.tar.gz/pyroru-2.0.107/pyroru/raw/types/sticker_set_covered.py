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

from io import BytesIO

from pyroru.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyroru.raw.core import TLObject
from pyroru import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class StickerSetCovered(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroru.raw.base.StickerSetCovered`.

    Details:
        - Layer: ``158``
        - ID: ``6410A5D2``

    Parameters:
        set (:obj:`StickerSet <pyroru.raw.base.StickerSet>`):
            N/A

        cover (:obj:`Document <pyroru.raw.base.Document>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroru.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetAttachedStickers
    """

    __slots__: List[str] = ["set", "cover"]

    ID = 0x6410a5d2
    QUALNAME = "types.StickerSetCovered"

    def __init__(self, *, set: "raw.base.StickerSet", cover: "raw.base.Document") -> None:
        self.set = set  # StickerSet
        self.cover = cover  # Document

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StickerSetCovered":
        # No flags
        
        set = TLObject.read(b)
        
        cover = TLObject.read(b)
        
        return StickerSetCovered(set=set, cover=cover)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.set.write())
        
        b.write(self.cover.write())
        
        return b.getvalue()
