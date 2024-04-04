import hashlib
from enum import Enum
import os
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field


from enum import Enum
import hashlib


class ChecksumTypes(Enum):
    """Enum class representing different types of checksums.

    Attributes:
        SHA1: Represents the SHA-1 checksum algorithm.
        MD5: Represents the MD5 checksum algorithm.
        SHA256: Represents the SHA-256 checksum algorithm.
        SHA512: Represents the SHA-512 checksum algorithm.
    """

    SHA1 = ("SHA-1", hashlib.sha1)
    MD5 = ("MD5", hashlib.md5)
    SHA256 = ("SHA-256", hashlib.sha256)
    SHA512 = ("SHA-512", hashlib.sha512)


class Checksum(BaseModel):
    """Checksum class represents a checksum object with type and value fields.

    Attributes:
        type (str): The type of the checksum.
        value (str): The value of the checksum.
    """

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(..., alias="@type")
    value: str = Field(..., alias="@value")

    @classmethod
    def from_file(
        cls,
        fpath: str,
        hash_fun: Callable,
        hash_algo: str,
    ) -> "Checksum":
        """Takes a file path and returns a checksum object.

        Args:
            fpath (str): The file path to generate the checksum for.
            hash_fun (Callable): The hash function to use for generating the checksum.
            hash_algo (str): The hash algorithm to use for generating the checksum.

        Returns:
            Checksum: A Checksum object with type and value fields.
        """

        value = cls._chunk_checksum(fpath=fpath, hash_fun=hash_fun)
        return cls(type=hash_algo, value=value)  # type: ignore

    @staticmethod
    def _chunk_checksum(fpath: str, hash_fun: Callable, blocksize=2**20) -> str:
        """Chunks a file and returns a checksum.

        Args:
            fpath (str): The file path to generate the checksum for.
            hash_fun (Callable): The hash function to use for generating the checksum.
            blocksize (int): The block size to use for reading the file.

        Returns:
            str: A string representing the checksum of the file.
        """
        m = hash_fun()
        with open(fpath, "rb") as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update(buf)
        return m.hexdigest()
