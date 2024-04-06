import binascii
from typing import Union

from hexbytes import HexBytes

import ecdsa

from ._PrivateKey import PrivateKey

class PublicKey:

    def __init__(self, Keys: Union[PrivateKey, str, bytes, bytearray, HexBytes, int], Compressed: bool = True) -> None:
        if isinstance(Keys, str): 
            self.__keys__ = HexBytes(Keys)
        elif isinstance(Keys, (bytes, bytearray, HexBytes)):
            self.__keys__ = HexBytes(Keys)
        elif isinstance(Keys, int):
            self.__keys__ = HexBytes(hex(Keys))
        elif isinstance(Keys, int):
            self.__keys__ = HexBytes(hex(Keys))
        elif isinstance(Keys, PrivateKey):
            if Compressed:
                __keys__ = ecdsa.SigningKey.from_string(HexBytes(bytes(Keys)), curve=ecdsa.SECP256k1).get_verifying_key().to_string()
                x_coord = __keys__[:int(len(__keys__) / 2)]
                if int(binascii.hexlify(__keys__[int(len(__keys__) / 2):]), 16) % 2 == 0:
                    self.__keys__ = HexBytes(b'\x02' + x_coord)
                else:
                    self.__keys__ = HexBytes(b'\x03' + x_coord)
            else:
                self.__keys__ = HexBytes(b'\x04' + ecdsa.SigningKey.from_string(HexBytes(bytes(Keys)), curve=ecdsa.SECP256k1).get_verifying_key().to_string())

    def __str__(self) -> str:
        return self.__keys__.hex()
    
    def __bytes__(self) -> bytes:
        return HexBytes(self.__keys__)
    
    @classmethod
    def FromPrivateKey(cls, Keys: PrivateKey):
        return cls(Keys)
    
    @classmethod
    def FromHex(cls, Keys: str):
        return cls(Keys)
    
    @classmethod
    def FromBytes(cls, Keys: Union[bytes, bytearray, HexBytes]):
        return cls(Keys)
    
    @classmethod
    def FromInt(cls, Keys: int):
        return cls(Keys)
    
    