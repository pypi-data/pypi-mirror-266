"""The `version` module holds the version information for TypedLLM."""
from __future__ import annotations as _annotations

__all__ = 'VERSION', 'version_short'

VERSION = '0.1.2'
"""The version of TypedLLM."""


def version_short() -> str:
    """Return the `major.minor` part of TypedLLM version.

    It returns '2.1' if TypedLLM version is '2.1.1'.
    """
    return '.'.join(VERSION.split('.')[:2])
