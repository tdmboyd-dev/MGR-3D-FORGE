"""MGR-native segmentation adapter contract.

This module defines the *interface* every segmentation backend (manual mask,
SAM3, or any future model) must satisfy before its output can feed
`forge.multiview` or `forge.unclothe_3d`. It ships **no neural model** and
makes no availability claim: a backend is usable only after it passes
`available()` on this machine and its licence is cleared by the owner.

The design goal is honesty, not convenience: a mask that cannot be traced to a
named adapter with a measured `available()` result must never be treated as
machine-inferred.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, runtime_checkable

SCHEMA = "mgr.forge.segmentation-adapter.v1"
EVIDENCE_LEVEL_MANUAL = "MANUAL_OWNER_MASK"
EVIDENCE_LEVEL_INFERRED = "MODEL_INFERRED_MASK"
EVIDENCE_LEVEL_UNAVAILABLE = "UNAVAILABLE"


class SegmentationError(ValueError):
    """Raised when a backend cannot produce a mask honestly."""


@dataclass(frozen=True)
class MaskResult:
    """A segmentation result with full provenance."""
    mask_path: str
    adapter: str
    evidence_level: str
    confidence: float | None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict:
        return {
            "schema": SCHEMA,
            "mask_path": self.mask_path,
            "adapter": self.adapter,
            "evidence_level": self.evidence_level,
            "confidence": self.confidence,
            "notes": list(self.notes),
        }


@runtime_checkable
class SegmentationAdapter(Protocol):
    """Contract every segmentation backend must implement."""

    name: str
    evidence_level: str

    def available(self) -> bool:
        """Return True only if this backend can run on this machine right now."""
        ...

    def segment(self, source_path: str, *, out_path: str) -> MaskResult:
        """Produce a binary mask PNG at out_path and return its provenance."""
        ...


class ManualMaskAdapter:
    """Pass-through for owner-supplied masks. Always available; never claims inference."""

    name = "manual-owner-mask"
    evidence_level = EVIDENCE_LEVEL_MANUAL

    def available(self) -> bool:
        return True

    def segment(self, source_path: str, *, out_path: str) -> MaskResult:
        # Manual adapter does not create pixels; it records that the owner did.
        return MaskResult(
            mask_path=out_path,
            adapter=self.name,
            evidence_level=self.evidence_level,
            confidence=None,
            notes=("owner supplied the mask; no model was invoked",),
        )


class UnavailableAdapter:
    """Placeholder for a backend whose model is not installed or not licensed."""

    def __init__(self, name: str, reason: str):
        self.name = name
        self.reason = reason
        self.evidence_level = EVIDENCE_LEVEL_UNAVAILABLE

    def available(self) -> bool:
        return False

    def segment(self, source_path: str, *, out_path: str) -> MaskResult:
        raise SegmentationError(f"{self.name} is unavailable: {self.reason}")


class AdapterRegistry:
    """Named registry of segmentation backends."""

    def __init__(self):
        self._adapters: dict[str, SegmentationAdapter] = {}

    def register(self, adapter: SegmentationAdapter) -> None:
        if not isinstance(adapter.name, str) or not adapter.name:
            raise ValueError("adapter requires a non-empty name")
        if adapter.name in self._adapters:
            raise ValueError(f"duplicate adapter name: {adapter.name}")
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> SegmentationAdapter:
        if name not in self._adapters:
            raise KeyError(f"unknown segmentation adapter: {name}")
        return self._adapters[name]

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

    def available_names(self) -> tuple[str, ...]:
        return tuple(name for name in self.names()
                    if self._adapters[name].available())

    def require_available(self, name: str) -> SegmentationAdapter:
        try:
            adapter = self.get(name)
        except KeyError as error:
            raise SegmentationError(str(error)) from error
        if not adapter.available():
            raise SegmentationError(f"segmentation adapter not available: {name}")
        return adapter


def build_default_registry() -> AdapterRegistry:
    """Registry with only the always-available manual adapter.

    Neural adapters are deliberately NOT registered here. They must be added by
    an explicit, owner-approved installation step that also records the model
    version and licence under research/external-provenance/.
    """
    registry = AdapterRegistry()
    registry.register(ManualMaskAdapter())
    return registry


def describe_registry(registry: AdapterRegistry) -> dict:
    return {
        "schema": SCHEMA,
        "adapters": [
            {"name": name,
             "available": registry.get(name).available(),
             "evidence_level": registry.get(name).evidence_level}
            for name in registry.names()
        ],
        "neural_adapter_installed": any(
            registry.get(name).evidence_level == EVIDENCE_LEVEL_INFERRED
            for name in registry.names()
        ),
        "honesty": "no neural model is claimed available unless an adapter "
                   "with EVIDENCE_LEVEL_INFERRED is registered and available() is True",
    }
