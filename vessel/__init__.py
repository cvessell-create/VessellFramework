"""Compatibility namespace for legacy VesselFramework imports.

New integrations must import ``vessell``.
"""

from pathlib import Path

__path__ = [str(Path(__file__).parents[1] / "vessell")]