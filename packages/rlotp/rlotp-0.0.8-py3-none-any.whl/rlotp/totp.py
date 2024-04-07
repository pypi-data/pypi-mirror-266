import calendar
import datetime
import hashlib
import time
import secrets
from typing import Any, Optional, Union, Tuple

from . import utils
from .otp import OTP


class TOTP():
    """
    Handler for time-based OTP counters.
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
        period: int = 30,
        encoder: Optional[str] = None,
    ) -> None:
        """
        :param secret: secret in base32 format
        :param digits: number of integers in the OTP. Some apps expect this to be 6 digits, others support more.
        :param digest: digest function to use in the HMAC (expected to be SHA1)
        :param name: account name
        :param issuer: issuer
        :param period: the time period in seconds for OTP. This defaults to 30.
        """
        self.rdigits = None
        if rdigits:
            if rdigits[0] < 6 or rdigits[1] > 10:
                raise ValueError("rdigits must be between 6 and 10")
            self.rdigits = rdigits
        if digest is None:
            digest = hashlib.sha1

        self.secret = secret
        self.digits = digits
        self.digest = digest
        self.name = name or 'Secret'
        self.issuer = issuer
        self.period = period
        self.chargroup = chargroup
        self.encoder = encoder

    def at(self, for_time: Union[int, datetime.datetime], counter_offset: int = 0) -> str:
        """
        Accepts either a Unix timestamp integer or a datetime object.

        To get the time until the next timecode change (seconds until the current OTP expires), use this instead:

        .. code:: python

            totp = rlotp.TOTP(...)
            time_remaining = totp.period - datetime.datetime.now().timestamp() % totp.period

        :param for_time: the time to generate an OTP for
        :param counter_offset: the amount of ticks to add to the time counter
        :returns: OTP value
        """
        if self.rdigits:
            ns = range(self.rdigits[0], self.rdigits[1] + 1)
            n = len(str(len(ns)))
            otp1 = OTP(self.secret, digits=n, digest=self.digest, name=self.name, issuer=self.issuer)
            digits = utils.normalize(int(otp1.generate_otp(self.timecode(for_time) + counter_offset) if for_time else counter_offset), ns)
        else:
            digits = self.digits

        otp = OTP(self.secret, digits=digits, digest=self.digest, name=self.name, issuer=self.issuer, chargroup=self.chargroup, encoder=self.encoder)

        if for_time:
            if not isinstance(for_time, datetime.datetime):
                for_time = datetime.datetime.fromtimestamp(int(for_time))
            return otp.generate_otp(self.timecode(for_time) + counter_offset)
        # else it's a HOTP, counter_offset is the counter
        return otp.generate_otp(counter_offset)

    def now(self) -> str:
        """
        Generate the current time OTP

        :returns: OTP value
        """
        return self.at(datetime.datetime.now())

    def verify(self, otp: str, for_time: Optional[datetime.datetime] = None, valid_window: int = 0) -> bool:
        """
        Verifies the OTP passed in against the current time OTP.

        :param otp: the OTP to check against
        :param for_time: Time to check OTP at (defaults to now)
        :param valid_window: extends the validity to this many counter ticks before and after the current one
        :returns: True if verification succeeded, False otherwise
        """
        if for_time is None:
            for_time = datetime.datetime.now()

        if valid_window:
            for i in range(-valid_window, valid_window + 1):
                if utils.strings_equal(str(otp), str(self.at(for_time, i))):
                    return True
            return False

        return utils.strings_equal(str(otp), str(self.at(for_time)))

    def provisioning_uri(self,
            name: Optional[str] = None,
            issuer_name: Optional[str] = None,
            image: Optional[str] = None,
            initial_count: Optional[int] = None,
    ) -> str:

        """
        Returns the provisioning URI for the OTP.  This can then be
        encoded in a QR Code and used to provision an OTP app like
        Google Authenticator.

        See also:
            https://github.com/google/google-authenticator/wiki/Key-Uri-Format

        """
        if not initial_count:
            initial_count = self.initial_count if hasattr(self, 'initial_count') else None
        return utils.build_uri(
            self.secret,
            name if name else self.name,
            issuer=issuer_name if issuer_name else self.issuer,
            algorithm=self.digest().name,
            rdigits=self.rdigits,
            chargroup=self.chargroup,
            digits=self.digits,
            period=self.period,
            image=image,
            encoder=self.encoder,
            initial_count=initial_count,
        )

    def timecode(self, for_time: datetime.datetime) -> int:
        """
        Accepts either a timezone naive (`for_time.tzinfo is None`) or
        a timezone aware datetime as argument and returns the
        corresponding counter value (timecode).
        """
        if for_time.tzinfo:
            return int(calendar.timegm(for_time.utctimetuple()) / self.period)
        else:
            return int(time.mktime(for_time.timetuple()) / self.period)
