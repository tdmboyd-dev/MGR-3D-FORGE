"""MGR Forge Model Dock — MGR-native safe model recipe inspection, never execution."""

from dataclasses import dataclass, asdict
import re


_IDENTIFIER = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ModelRecipe:
    id: str
    package_id: str
    version: str
    sha256: str
    license_id: str
    runtime: str
    requires_gpu: bool
    estimated_vram_gb: float
    source_url: str

    def __post_init__(self):
        if not all(_IDENTIFIER.fullmatch(value or "") for value in
                   (self.id,self.package_id,self.version,self.license_id)):
            raise ValueError("invalid recipe identity or license")
        if not _DIGEST.fullmatch(self.sha256):
            raise ValueError("checksum required")
        if self.runtime not in {"python", "onnx", "blender", "binary"}:
            raise ValueError("unsupported runtime")
        if type(self.requires_gpu) is not bool or not (0 <= self.estimated_vram_gb <= 256):
            raise ValueError("invalid resource requirements")
        if self.requires_gpu is False and self.estimated_vram_gb > 0:
            raise ValueError("CPU recipe cannot claim VRAM requirement")
        if not self.source_url.startswith("https://"):
            raise ValueError("secure source URL required")


def inspect_recipe(recipe, *, available_vram_gb=0, approved_licenses=("MGR-native",)):
    """Return security and capacity findings without downloading or running code."""
    problems = []
    if recipe.license_id not in approved_licenses:
        problems.append("license not approved")
    if recipe.requires_gpu and available_vram_gb < recipe.estimated_vram_gb:
        problems.append("insufficient GPU VRAM")
    return {"id": recipe.id, "ready": not problems,
            "reasons": problems, "execute": False,
            "recipe": asdict(recipe)}
