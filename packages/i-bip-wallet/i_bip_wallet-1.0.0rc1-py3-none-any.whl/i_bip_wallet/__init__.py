from typing import Union

from hexbytes import HexBytes
from ._PrivateKey import PrivateKey as __PK__
from ._PublicKey import PublicKey as __PB__
from ._Ripemd import Ripemd as __R__
from ._Utils import Utils as __U__

class BIP_Wallet:

    @staticmethod
    def PrivateKey(Keys: Union[str, bytes, bytearray, HexBytes, int]):
        return __PK__(Keys)

    @staticmethod
    def PublicKey(Keys: Union[__PK__, str, bytes, bytearray, HexBytes, int], Compressed: bool = True):
        return __PB__(Keys, Compressed)

    @staticmethod
    def Ripemd(Keys: Union[__PK__, __PB__, str, bytes, bytearray, HexBytes, int], Compressed: bool = True):
        return __R__(Keys, Compressed)

    @staticmethod
    def Utils():
        return __U__()