"""Static distribution capability catalog shared by Planner and CLI."""

from __future__ import annotations

from dataclasses import dataclass

from centaurus.executor.execution import ExecutionTask


PUBLIC_EXPOSURE_ASSESSMENT = "public_exposure_assessment"
SUPPORTED_INTENTS = frozenset({PUBLIC_EXPOSURE_ASSESSMENT})


@dataclass(frozen=True, slots=True)
class TaskTemplate:
    """One deterministic task template for an operational target type."""

    plugin_id: str
    target_parameter: str
    fixed_parameters: tuple[tuple[str, str], ...] = ()

    def build(self, target: str) -> ExecutionTask:
        """Build one ephemeral ExecutionTask for the concrete target."""

        parameters = {self.target_parameter: target}
        parameters.update(dict(self.fixed_parameters))
        return ExecutionTask(plugin_id=self.plugin_id, parameters=parameters)


@dataclass(frozen=True, slots=True)
class TargetCapability:
    """Distribution-level target support metadata."""

    target_type: str
    status: str
    description: str
    tasks: tuple[TaskTemplate, ...] = ()

    @property
    def operational(self) -> bool:
        """Return whether this target can produce an execution plan now."""

        return bool(self.tasks)

    @property
    def tools(self) -> tuple[str, ...]:
        """Return distinct tool identifiers in deterministic task order."""

        return tuple(dict.fromkeys(task.plugin_id for task in self.tasks))


DOMAIN_CAPABILITY = TargetCapability(
    target_type="DOMAIN",
    status="full",
    description="Full public-exposure collection supported by the current release.",
    tasks=(
        TaskTemplate("whois", "domain"),
        TaskTemplate("rdap", "domain"),
        TaskTemplate("dnsrecon", "domain"),
        TaskTemplate("dnsrecon", "domain", (("mode", "dmarc"),)),
        TaskTemplate("sublist3r", "domain"),
        TaskTemplate("crtsh", "domain"),
        TaskTemplate("theharvester", "domain"),
    ),
)

IP_CAPABILITY = TargetCapability(
    target_type="IP",
    status="limited",
    description="Limited public-exposure collection through RDAP.",
    tasks=(TaskTemplate("rdap", "ip"),),
)

EMAIL_CAPABILITY = TargetCapability(
    target_type="EMAIL",
    status="future",
    description="Conceptual future target; no operational acquisition plan in this release.",
)

CERTIFICATE_CAPABILITY = TargetCapability(
    target_type="CERTIFICATE",
    status="deferred",
    description="Conceptual target frozen; acquisition remains deferred.",
)

TARGET_CAPABILITIES = (
    DOMAIN_CAPABILITY,
    IP_CAPABILITY,
    EMAIL_CAPABILITY,
    CERTIFICATE_CAPABILITY,
)

OPERATIONAL_TARGET_CAPABILITIES = tuple(
    capability for capability in TARGET_CAPABILITIES if capability.operational
)
DEFERRED_TARGET_CAPABILITIES = tuple(
    capability for capability in TARGET_CAPABILITIES if not capability.operational
)
SUPPORTED_TARGET_TYPES = frozenset(
    capability.target_type for capability in OPERATIONAL_TARGET_CAPABILITIES
)
IMPLEMENTED_TOOLS = tuple(
    dict.fromkeys(
        tool
        for capability in OPERATIONAL_TARGET_CAPABILITIES
        for tool in capability.tools
    )
)


def get_operational_target_capability(target_type: str) -> TargetCapability:
    """Return the operational capability or reject unsupported target types."""

    normalized = target_type.strip().upper() if isinstance(target_type, str) else ""
    for capability in OPERATIONAL_TARGET_CAPABILITIES:
        if capability.target_type == normalized:
            return capability
    raise ValueError(f"unsupported operational target type: {target_type!r}")


__all__ = [
    "CERTIFICATE_CAPABILITY",
    "DEFERRED_TARGET_CAPABILITIES",
    "DOMAIN_CAPABILITY",
    "EMAIL_CAPABILITY",
    "IMPLEMENTED_TOOLS",
    "IP_CAPABILITY",
    "OPERATIONAL_TARGET_CAPABILITIES",
    "PUBLIC_EXPOSURE_ASSESSMENT",
    "SUPPORTED_INTENTS",
    "SUPPORTED_TARGET_TYPES",
    "TARGET_CAPABILITIES",
    "TargetCapability",
    "TaskTemplate",
    "get_operational_target_capability",
]
