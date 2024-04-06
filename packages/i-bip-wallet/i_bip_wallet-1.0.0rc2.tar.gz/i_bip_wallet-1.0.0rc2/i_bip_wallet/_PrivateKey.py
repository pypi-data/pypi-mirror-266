import secrets
from typing import Union

from hexbytes import HexBytes

class PrivateKey:

    def __init__(self, Keys: Union[str, bytes, bytearray, HexBytes, int]) -> None:
        if isinstance(Keys, str): 
            self.__keys__ = HexBytes(Keys)
        elif isinstance(Keys, (bytes, bytearray, HexBytes)):
            self.__keys__ = HexBytes(Keys)
        elif isinstance(Keys, int):
            self.__keys__ = HexBytes(hex(Keys))

    def __str__(self) -> str:
        return self.__keys__.hex()
    
    def __bytes__(self) -> bytes:
        return HexBytes(self.__keys__)
    
    @classmethod
    def generate(cls):
        return cls(HexBytes(secrets.token_hex(32))) # Generate random PrivateKey
    
    @classmethod
    def FromHex(cls, Keys: str):
        return cls(Keys)
    
    @classmethod
    def FromBytes(cls, Keys: Union[bytes, bytearray, HexBytes]):
        return cls(Keys)
    
    @classmethod
    def FromInt(cls, Keys: int):
        return cls(Keys)
    
    @classmethod
    def FromWif(cls):
        return 'Not Found'