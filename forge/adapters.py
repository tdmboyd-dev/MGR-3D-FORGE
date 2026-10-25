"""Replaceable generation adapters with explicit offline and resource contracts."""

from dataclasses import dataclass
from pathlib import Path

from .cli import build
from .spec import WorldSpec
from .workflow import Step, approve_plan


@dataclass(frozen=True)
class AdapterCapabilities:
    name: str
    tasks: tuple[str,...]
    network: bool
    estimated_usd: float
    gpu_required: bool
    commercial_license_cleared: bool


class ProceduralWorldAdapter:
    capabilities=AdapterCapabilities("mgr-cpu-world",("world-massing",),False,0.0,False,True)

    def run(self, spec, output):
        if not isinstance(spec,WorldSpec):
            raise ValueError("expected a typed WorldSpec")
        return build(spec,Path(output))


class UnavailableNeuralAdapter:
    """Honest placeholder for future local neural engines; never fakes assets."""
    capabilities=AdapterCapabilities("unavailable-neural",("image-to-mesh",),False,0.0,True,False)

    def run(self, spec, output):
        raise RuntimeError("neural weights/runtime not installed or license approved")


def select_adapter(task, candidates, *, allow_network=False, budget_usd=0,
                   gpu_available=False, approved_step_ids=()):
    """Selection must not silently choose paid, network or uncleared model providers."""
    choices=[]
    for adapter in candidates:
        if not callable(getattr(adapter,"run",None)):
            continue
        capability=adapter.capabilities
        if task not in capability.tasks or not capability.commercial_license_cleared:
            continue
        if capability.network and not allow_network:
            continue
        if capability.gpu_required and not gpu_available:
            continue
        try:
            approve_plan([Step(capability.name,task,
                               estimated_usd=capability.estimated_usd,
                               network_access=capability.network)],budget_usd=budget_usd,
                         approved_step_ids=approved_step_ids)
        except PermissionError:
            continue
        choices.append(adapter)
    if not choices:
        raise LookupError(f"no approved adapter for {task}")
    return sorted(choices,key=lambda item:(item.capabilities.estimated_usd,
                                         item.capabilities.name))[0]
