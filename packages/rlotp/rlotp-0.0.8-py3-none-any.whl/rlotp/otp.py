import base64
import hashlib
import hmac
import string
from typing import Any, Optional
from .steam import STEAM_CHARS, STEAM_DEFAULT_DIGITS
from . import utils


STEAM_CHARS = "23456789BCDFGHJKMNPQRTVWXY"  # steam's custom alphabet
STEAM_DEFAULT_DIGITS = 5  # Steam TOTP code length

class OTP(object):
    """
    Base class for OTP handlers.
    """

    def __init__(
        self,
        secret: str,
        digits: int = 6,
        digest: Any = hashlib.sha1,
        chargroup: Optional[str] = None,
        name: Optional[str] = None,
        issuer: Optional[str] = None,
        encoder: Optional[str] = None,
    ) -> None:
        if digits > 10:
            raise ValueError("Maximum number of digits is 10")
        self.digits = digits
        self.digest = digest
        self.chargroup = chargroup
        self.secret = secret
        self.name = name or "Secret"
        self.issuer = issuer
        self.encoder = encoder
        if self.chargroup and self.chargroup.startswith('alpha'):
            self.chargroup = string.digits + string.ascii_uppercase
        if self.chargroup and  len(self.chargroup) < self.digits:
            raise ValueError("chargroup must be at least the same length as the number of digits")


    def generate_otp(self, input: int) -> str:
        """
        :param input: the HMAC counter value to use as the OTP input.
            Usually either the counter, or the computed integer based on the Unix timestamp
        """
        if input < 0:
            raise ValueError("input must be positive integer")
        hasher = hmac.new(self.byte_secret(), self.int_to_bytestring(input), self.digest)
        hmac_hash = bytearray(hasher.digest())
        offset = hmac_hash[-1] & 0xF
        code = (
            (hmac_hash[offset] & 0x7F) << 24
            | (hmac_hash[offset + 1] & 0xFF) << 16
            | (hmac_hash[offset + 2] & 0xFF) << 8
            | (hmac_hash[offset + 3] & 0xFF)
        )
        v = ""
        if self.encoder == "steam":
            total_chars = len(STEAM_CHARS)
            for _ in range(STEAM_DEFAULT_DIGITS):
                pos = code % total_chars
                char = STEAM_CHARS[int(pos)]
                v += char
                code //= total_chars
        else:
            str_code = str(10_000_000_000 + (code % 10**self.digits))
            v = str_code[-self.digits :]
            if self.chargroup:
                v = utils.pick_chars(v, self.chargroup)
        return v

    def byte_secret(self) -> bytes:
        secret = self.secret
        missing_padding = len(secret) % 8
        if missing_padding != 0:
            secret += "=" * (8 - missing_padding)
        return base64.b32decode(secret, casefold=True)

    @staticmethod
    def int_to_bytestring(i: int, padding: int = 8) -> bytes:
        """
        Turns an integer to the OATH specified
        bytestring, which is fed to the HMAC
        along with the secret
        """
        result = bytearray()
        while i != 0:
            result.append(i & 0xFF)
            i >>= 8
        # It's necessary to convert the final result from bytearray to bytes
        # because the hmac functions in python 2.6 and 3.3 don't work with
        # bytearray
        return bytes(bytearray(reversed(result)).rjust(padding, b"\0"))
