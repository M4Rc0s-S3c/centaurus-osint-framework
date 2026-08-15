"""Reporting domain components."""

from .report import Report

__all__ = ["Report", "ReportManager"]


def __getattr__(name: str):
    if name == "ReportManager":
        from .report_manager import ReportManager
        return ReportManager
    raise AttributeError(name)
