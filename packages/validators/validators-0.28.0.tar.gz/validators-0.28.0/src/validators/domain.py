"""Domain."""

# standard
from pathlib import Path
import re

# local
from .utils import validator


def _iana_tld():
    """Load IANA TLDs."""
    with Path(__file__).parent.joinpath("_tld.txt").open() as tld_f:
        return (line.strip() for line in tld_f.readlines()[1:])


@validator
def domain(
    value: str, /, *, consider_tld: bool = False, rfc_1034: bool = False, rfc_2782: bool = False
):
    """Return whether or not given value is a valid domain.

    Examples:
        >>> domain('example.com')
        # Output: True
        >>> domain('example.com/')
        # Output: ValidationError(func=domain, ...)
        >>> # Supports IDN domains as well::
        >>> domain('xn----gtbspbbmkef.xn--p1ai')
        # Output: True

    Args:
        value:
            Domain string to validate.
        consider_tld:
            Restrict domain to TLDs allowed by IANA.
        rfc_1034:
            Allows optional trailing dot in the domain name.
            Ref: [RFC 1034](https://www.rfc-editor.org/rfc/rfc1034).
        rfc_2782:
            Domain name is of type service record.
            Allows optional underscores in the domain name.
            Ref: [RFC 2782](https://www.rfc-editor.org/rfc/rfc2782).


    Returns:
        (Literal[True]): If `value` is a valid domain name.
        (ValidationError): If `value` is an invalid domain name.

    Raises:
        (UnicodeError): If `value` cannot be encoded into `idna` or decoded into `utf-8`.
    """
    if not value:
        return False

    if consider_tld and value.rstrip(".").rsplit(".", 1)[-1].upper() not in _iana_tld():
        return False

    try:
        return not re.search(r"\s", value) and re.match(
            # First character of the domain
            rf"^(?:[a-z0-9{r'_?'if rfc_2782 else ''}]"
            # Sub-domain
            + rf"(?:[a-z0-9-{r'_?'if rfc_2782 else ''}]{{0,61}}"
            # Hostname
            + rf"[a-z0-9{r'_?'if rfc_2782 else ''}])?\.)"
            # First 61 characters of the gTLD
            + r"+[a-z0-9][a-z0-9-_]{0,61}"
            # Last character of the gTLD
            + rf"[a-z]{r'.?$' if rfc_1034 else r'$'}",
            value.encode("idna").decode("utf-8"),
            re.IGNORECASE,
        )
    except UnicodeError as err:
        raise UnicodeError(f"Unable to encode/decode {value}") from err
