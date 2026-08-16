"""
Evidence Manager domain service.
"""

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.evidence.raw_observation import RawObservation
from centaurus.normalization.dnsrecon_normalizer import normalize_dnsrecon_data
from centaurus.normalization.rdap_normalizer import normalize_rdap_data
from centaurus.normalization.sublist3r_normalizer import normalize_sublist3r_data
from centaurus.normalization.whois_normalizer import normalize_whois_data


class EvidenceManager:
    """
    Domain service responsible for transforming RawObservation
    objects into immutable, normalized Evidence Value Objects.
    """

    def create_evidence(
        self,
        raw_observation: RawObservation,
    ) -> Evidence:
        """
        Normalize a RawObservation and build an immutable Evidence.

        The RawObservation is never modified. Normalization is selected
        according to the observation source and remains tool-specific.
        """

        if raw_observation is None:
            raise ValueError("RawObservation cannot be None.")

        if not isinstance(raw_observation, RawObservation):
            raise ValueError("Expected a RawObservation instance.")

        normalized_data = self._normalize(
            raw_observation.source,
            raw_observation.data,
        )

        return Evidence(
            source=raw_observation.source,
            data=normalized_data,
            collected_at=raw_observation.collected_at,
        )

    @staticmethod
    def _normalize(
        source: EvidenceSource,
        data: dict,
    ) -> dict:
        """
        Apply the normalizer registered for a supported evidence source.

        A source without a defined normalizer is rejected instead of
        allowing RAW data to bypass the normalization boundary.
        """

        if source is EvidenceSource.WHOIS:
            return normalize_whois_data(data)

        if source is EvidenceSource.RDAP:
            return normalize_rdap_data(data)

        if source is EvidenceSource.DNSRECON:
            return normalize_dnsrecon_data(data)

        if source is EvidenceSource.SUBLIST3R:
            return normalize_sublist3r_data(data)

        raise ValueError(
            f"No normalizer registered for evidence source: {source.value}"
        )
