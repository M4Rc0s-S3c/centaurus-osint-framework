"""
Evidence Manager domain service.
"""

from centaurus.evidence.evidence import Evidence


class EvidenceManager:
    """
    Domain service responsible for transforming raw observations
    into Evidence objects.

    Responsibilities:
        - Transform raw observations into Evidence.
        - Preserve traceability of collected knowledge.
        - Isolate the normalization process from the rest of
          the domain.

    This service never:
        - Executes plugins.
        - Applies rules.
        - Generates findings.
        - Produces reports.
    """

    def create_evidence(
        self,
        raw_observation,
    ) -> Evidence:
        """
        Create an Evidence object from a raw observation.

        The normalization strategy is intentionally left
        undefined at this stage and will be implemented
        incrementally.
        """

        raise NotImplementedError