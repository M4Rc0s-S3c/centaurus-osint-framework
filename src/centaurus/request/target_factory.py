"""Deterministic target extraction and normalization."""

from dataclasses import dataclass
import ipaddress
import re
from urllib.parse import urlparse


_EMAIL_RE = re.compile(
    r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63})(?![\w-])",
    re.IGNORECASE,
)
_DOMAIN_RE = re.compile(
    r"(?<![@\w.-])((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63})(?![\w-])",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[^\s,;()\[\]{}<>]+")


@dataclass(frozen=True, slots=True)
class TargetCandidate:
    """Deterministically detected target before domain construction."""

    value: str
    type: str


class TargetFactory:
    """Build a normalized target candidate without using an LLM."""

    def create(self, user_input: str) -> TargetCandidate:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        text = user_input.strip()
        candidates: list[TargetCandidate] = []

        for match in _EMAIL_RE.finditer(text):
            candidates.append(TargetCandidate(match.group(1).lower(), "EMAIL"))

        for match in _URL_RE.finditer(text):
            parsed = urlparse(match.group(0))
            if parsed.hostname:
                candidates.append(self._from_host(parsed.hostname))

        for token in _TOKEN_RE.findall(text):
            cleaned = token.strip(".:'\"!?/\\")
            if not cleaned or "@" in cleaned:
                continue
            try:
                address = ipaddress.ip_address(cleaned)
            except ValueError:
                continue
            candidates.append(TargetCandidate(str(address), "IP"))

        for match in _DOMAIN_RE.finditer(text):
            candidates.append(self._from_domain(match.group(1)))

        unique = {(candidate.type, candidate.value): candidate for candidate in candidates}
        if not unique:
            raise ValueError("unable to detect a supported target")
        if len(unique) > 1:
            raise ValueError("input contains multiple or ambiguous targets")

        return next(iter(unique.values()))

    def _from_host(self, host: str) -> TargetCandidate:
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return self._from_domain(host)
        return TargetCandidate(str(address), "IP")

    def _from_domain(self, domain: str) -> TargetCandidate:
        normalized = domain.rstrip(".").lower()
        try:
            normalized = normalized.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("invalid domain target") from exc
        return TargetCandidate(normalized, "DOMAIN")
