import secrets
from typing import Union

from hexbytes import HexBytes
MIN = 0x1
MAX = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class PrivateKey:

    def __init__(self, Keys: Union[str, bytes, bytearray, HexBytes, int]) -> None:
        if isinstance(Keys, str): 
            Keys = HexBytes(Keys)
            if len(Keys) < 32: Keys = HexBytes(bytearray(32 - len(Keys)) + Keys)
            if int.from_bytes(Keys, 'big') < MIN and int.from_bytes(Keys, 'big') > MAX:
                raise Exception('PrivateKey must be in range {} > {}'.format(MIN, MAX))
            self.__keys__ = Keys
        elif isinstance(Keys, (bytes, bytearray, HexBytes)):
            Keys = HexBytes(Keys)
            if len(Keys) < 32: Keys = HexBytes(bytearray(32 - len(Keys)) + Keys)
            if int.from_bytes(Keys, 'big') < MIN and int.from_bytes(Keys, 'big') > MAX:
                raise Exception('PrivateKey must be in range {} > {}'.format(MIN, MAX))
            self.__keys__ = Keys
        elif isinstance(Keys, int):
            Keys = HexBytes(hex(Keys))
            if len(Keys) < 32: Keys = HexBytes(bytearray(32 - len(Keys)) + Keys)
            if int.from_bytes(Keys, 'big') < MIN and int.from_bytes(Keys, 'big') > MAX:
                raise Exception('PrivateKey must be in range {} > {}'.format(MIN, MAX))
            self.__keys__ = Keys

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