"""Address normalization utilities for NYC street names."""

import re

_STREET_TYPES = (
    r"(STREET|ST|AVENUE|AVE|ROAD|RD|DRIVE|DR|PLACE|PL"
    r"|BOULEVARD|BLVD|LANE|LN|COURT|CT|WAY|TERRACE|TER)"
)

_NUMBERED_STREET = re.compile(
    rf"(?<![\d]-)(\b\d+)\s+{_STREET_TYPES}",
    re.IGNORECASE,
)

ORDINAL_SUFFIXES = {1: "ST", 2: "ND", 3: "RD"}


def get_ordinal_suffix(number):
    """Return the ordinal form of *number* (1 -> '1ST', 12 -> '12TH')."""
    value = int(number)
    if 11 <= value % 100 <= 13:
        return f"{value}TH"
    return f"{value}{ORDINAL_SUFFIXES.get(value % 10, 'TH')}"


def normalize_street_name(address):
    """Convert bare numbered streets to ordinal form.

    ``'3 STREET'`` becomes ``'3RD STREET'``, while house numbers
    like ``'21-83'`` and named streets like ``'BROADWAY'`` are
    left unchanged.
    """
    def _ordinalize(match):
        number = match.group(1)
        street_type = match.group(2)
        return f"{get_ordinal_suffix(number)} {street_type}"

    return _NUMBERED_STREET.sub(_ordinalize, address)
