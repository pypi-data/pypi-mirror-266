import hashlib
from typing import Any, Optional, Tuple, Union

from . import utils
from .totp import TOTP


class HOTP(TOTP):
    """
    Handler for HMAC-based OTP counters.
    """

    def __init__(
        self,
        secret: str,
        rdigits: Union[Tuple[int, int], None] = None,
        chargroup: str = None,
        digits: int = 6,
        digest: Any = None,
        name: Optional[str] = None,
        issuer: Optional[str] = None,
        initial_count: int = 0,
        encoder: Optional[str] = None,
    ) -> None:
        """
        :param secret: secret in base32 format
        :param initial_count: starting HMAC counter value, defaults to 0
        :param digits: number of integers in the OTP. Some apps expect this to be 6 digits, others support more.
        :param digest: digest function to use in the HMAC (expected to be SHA1)
        :param name: account name
        :param issuer: issuer
        """
        self.initial_count = initial_count
        super().__init__(secret, rdigits=rdigits, chargroup=chargroup, digits=digits, digest=digest, name=name, issuer=issuer, encoder=encoder)

    def at(self, count: int) -> str:
        """
        Generates the OTP for the given count.

        :param count: the OTP HMAC counter
        :returns: OTP
        """
        return super().at(0, count)

    def verify(self, otp: str, counter: int) -> bool:
        """
        Verifies the OTP passed in against the current counter OTP.

        :param otp: the OTP to check against
        :param counter: the OTP HMAC counter
        """
        return utils.strings_equal(str(otp), str(self.at(counter)))

    def now(self):
        raise NotImplementedError("HOTP does not support now() method, use at() instead")
