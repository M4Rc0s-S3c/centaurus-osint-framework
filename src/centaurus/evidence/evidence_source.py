"""
Enumeration of evidence sources.

Represents the logical origin of normalized observations.
"""

from enum import Enum


class EvidenceSource(str, Enum):
    """
    Logical origin of an Evidence or RawObservation.
    """

    WHOIS = "whois"
    RDAP = "rdap"
    DNSRECON = "dnsrecon"
    SUBLIST3R = "sublist3r"
    THEHARVESTER = "theharvester"
    CRTSH = "crtsh"