"""Address sanitization and normalization utilities."""

import re

STREET_TYPES = r"(STREET|ST|AVENUE|AVE|ROAD|RD|DRIVE|DR|PLACE|PL|BOULEVARD|BLVD|LANE|LN|COURT|CT|WAY|TERRACE|TER)"  # noqa: E501


def get_ordinal_suffix(number):
    """Convert a number to its ordinal suffix (1->1st, 2->2nd, 3->3rd, etc.)"""
    number = int(number)
    if 11 <= number % 100 <= 13:
        return f"{number}TH"
    suffix = {1: "ST", 2: "ND", 3: "RD"}.get(number % 10, "TH")
    return f"{number}{suffix}"


def normalize_street_name(address):
    """Convert '3 STREET' to '3RD STREET', etc."""
    pattern = rf"(\d+)\s+{STREET_TYPES}"

    def replace_match(match):
        number = match.group(1)
        street_type = match.group(2)
        return f"{get_ordinal_suffix(number)} {street_type}"

    return re.sub(pattern, replace_match, address, flags=re.IGNORECASE)
