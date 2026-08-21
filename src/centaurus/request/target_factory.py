"""Deterministic target extraction, normalization and validation."""

from dataclasses import dataclass
import ipaddress
import re
from urllib.parse import urlparse


_DOMAIN_RE = re.compile(
    r"(?<![@\w.-])((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63})(?![\w-])",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[^\s,;()\[\]{}<>]+")
_DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


@dataclass(frozen=True, slots=True)
class TargetCandidate:
    """Deterministically detected target before domain construction."""

    value: str
    type: str


class TargetFactory:
    """Build and validate normalized operational target candidates."""

    def create(self, user_input: str) -> TargetCandidate:
        """Extract exactly one supported target from natural-language input."""

        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        text = user_input.strip()
        candidates: list[TargetCandidate] = []

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
            candidates.append(self.normalize(str(address), "IP"))

        for match in _DOMAIN_RE.finditer(text):
            candidates.append(self._from_domain(match.group(1)))

        unique = {(candidate.type, candidate.value): candidate for candidate in candidates}
        if not unique:
            raise ValueError("unable to detect a supported target")
        if len(unique) > 1:
            raise ValueError("input contains multiple or ambiguous targets")

        return next(iter(unique.values()))

    @staticmethod
    def normalize(target: str, target_type: str) -> TargetCandidate:
        """Normalize and validate one target against its declared operational type."""

        if not isinstance(target, str) or not target.strip():
            raise ValueError("target must be a non-empty string")
        if not isinstance(target_type, str) or not target_type.strip():
            raise ValueError("target_type must be a non-empty string")

        normalized_type = target_type.strip().upper()
        value = target.strip()

        if normalized_type == "IP":
            try:
                address = ipaddress.ip_address(value)
            except ValueError as exc:
                raise ValueError("invalid IP target") from exc
            if "%" in value:
                raise ValueError("scoped IP targets are not supported")
            return TargetCandidate(str(address), "IP")

        if normalized_type == "DOMAIN":
            normalized = value.rstrip(".").lower()
            try:
                normalized = normalized.encode("idna").decode("ascii")
            except UnicodeError as exc:
                raise ValueError("invalid domain target") from exc

            if len(normalized) > 253:
                raise ValueError("invalid domain target")

            labels = normalized.split(".")
            if len(labels) < 2 or any(
                not _DOMAIN_LABEL_RE.fullmatch(label)
                for label in labels
            ):
                raise ValueError("invalid domain target")

            tld = labels[-1]
            if len(tld) < 2:
                raise ValueError("invalid domain target")
            if not (tld.isalpha() or tld.startswith("xn--")):
                raise ValueError("invalid domain target")

            return TargetCandidate(normalized, "DOMAIN")

        raise ValueError(f"unsupported target_type: {target_type!r}")

    def _from_host(self, host: str) -> TargetCandidate:
        try:
            ipaddress.ip_address(host)
        except ValueError:
            return self._from_domain(host)
        return self.normalize(host, "IP")

    def _from_domain(self, domain: str) -> TargetCandidate:
        return self.normalize(domain, "DOMAIN")
