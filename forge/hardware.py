"""MGR resource-aware model admission; no automatic GPU/vendor assumptions."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ComputeProfile:
    physical_ram_gb: float
    reported_gpu_memory_gb: float | None
    gpu_name: str
    cuda_available: bool
    gpu_memory_is_shared_or_unknown: bool = False


@dataclass(frozen=True)
class ModelRequirement:
    name: str
    min_ram_gb: float
    min_vram_gb: float
    requires_cuda: bool
    cpu_supported: bool
    commercial_license_verified: bool


def assess_local_model(profile: ComputeProfile, candidate: ModelRequirement):
    """Conservative admission: unknown/shared VRAM never proves dedicated capacity."""
    for number in (profile.physical_ram_gb, candidate.min_ram_gb,candidate.min_vram_gb):
        if type(number) not in (int,float) or not math.isfinite(number) or number<0:
            raise ValueError("invalid memory requirement")
    if profile.reported_gpu_memory_gb is not None and (
        type(profile.reported_gpu_memory_gb) not in (int,float) or
        not math.isfinite(profile.reported_gpu_memory_gb) or profile.reported_gpu_memory_gb<0):
        raise ValueError("invalid reported GPU memory")
    blockers=[]
    if not candidate.commercial_license_verified:
        blockers.append("model license not commercially cleared")
    if profile.physical_ram_gb<candidate.min_ram_gb:
        blockers.append("insufficient installed RAM")
    if candidate.requires_cuda and not profile.cuda_available:
        blockers.append("CUDA GPU runtime unavailable")
    if candidate.min_vram_gb>0:
        if profile.reported_gpu_memory_gb is None or profile.gpu_memory_is_shared_or_unknown:
            blockers.append("verified dedicated GPU memory unavailable")
        elif profile.reported_gpu_memory_gb<candidate.min_vram_gb:
            blockers.append("insufficient reported dedicated GPU memory")
    if not candidate.cpu_supported and candidate.min_vram_gb==0 and not candidate.requires_cuda:
        blockers.append("candidate has no verified execution backend")
    return {"model":candidate.name,"local_admitted":not blockers,
            "blockers":blockers,"recommended_path":"LOCAL" if not blockers else "OPTIONAL_REVIEWED_REMOTE_OR_CPU_ALTERNATIVE",
            "note":"This is a prerequisite gate, not an actual inference benchmark or license opinion."}
