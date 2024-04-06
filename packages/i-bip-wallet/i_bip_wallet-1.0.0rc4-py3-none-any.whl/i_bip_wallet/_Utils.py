from typing import Union
from Cryptodome.Hash import SHA256, RIPEMD160, keccak
from hexbytes import HexBytes

class Utils:

    @classmethod
    def CheckSum(cls, v: Union[bytes, bytearray, HexBytes]):
        return cls.Doublehash256(v)

    @classmethod
    def Doublehash256(cls, v: Union[bytes, bytearray, HexBytes]):
        return SHA256.new(SHA256.new(v).digest()).digest()[:4]

    @classmethod
    def Sha256(cls, v: Union[bytes, bytearray, HexBytes]):
        return SHA256.new(v).digest()

    @classmethod
    def Ripemd(cls, v: Union[bytes, bytearray, HexBytes]):
        return RIPEMD160.new(cls.Sha256(v)).digest()

    @staticmethod
    def to_checksum_address(address: Union[str, HexBytes]):
        if isinstance(address, str):
            address_hash = HexBytes(keccak.new(data=address.lower()[2:].encode(), digest_bits=256).digest()).hex()
            return '0x{}'.format("".join((address[i].upper() if int(address_hash[i], 16) > 7 else address[i]) for i in range(2, 42)))
        elif isinstance(address, HexBytes):
            address = address.hex().lower()
            address_hash = HexBytes(keccak.new(data=address[2:].encode(), digest_bits=256).digest()).hex()
            return '0x{}'.format("".join((address[i].upper() if int(address_hash[i], 16) > 7 else address[i]) for i in range(2, 42)))