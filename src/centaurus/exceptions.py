"""Framework-level application exceptions."""


class InvalidPluginOutputError(TypeError):
    """Raised when a plugin does not return the required RawObservation."""


class PluginExecutionError(RuntimeError):
    """Stable wrapper for failures occurring inside one plugin execution."""

    def __init__(self, plugin_id: str, detail: str) -> None:
        self.plugin_id = plugin_id
        self.detail = detail
        super().__init__(f"Plugin '{plugin_id}' execution failed: {detail}")
