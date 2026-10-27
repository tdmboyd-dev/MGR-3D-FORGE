"""Optional SAM (Segment Anything) adapter behind the F108 contract.

This module is **import-safe**: if torch / segment_anything are not installed in
the running interpreter it still imports and `SamAdapter.available()` returns
False *unless* a Python 3.12 worker with torch + weights is available, in which
case segmentation is delegated to `scripts/sam_segment.py`.

SAM is free (Apache 2.0) but heavy: PyTorch + model weights (~375 MB for
ViT-B, ~2.4 GB for ViT-H) and a GPU is strongly recommended. On CPU it works
but is slow (seconds to tens of seconds per image).

Honest scope of what this adapter does today:
- `mode="center"` : segment the subject around the image centre (useful for
  isolating a character from a clean reference).
- `mode="auto"`    : run SAM's automatic mask generator and return the largest
  mask (useful for exploration; not part-level).
Full part-level segmentation (hair/face/body/clothing) is NOT implemented:
it requires prompted masks or a downstream classifier and is open work.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import torch
    from PIL import Image
    from segment_anything import (
        SamAutomaticMaskGenerator,
        SamPredictor,
        sam_model_registry,
    )

    _IMPORT_OK = True
except Exception:  # pragma: no cover - depends on environment
    _IMPORT_OK = False
    np = None
    torch = None
    Image = None
    SamAutomaticMaskGenerator = None
    SamPredictor = None
    sam_model_registry = None

from .segmentation import (
    EVIDENCE_LEVEL_INFERRED,
    MaskResult,
    SegmentationAdapter,
    SegmentationError,
)

SCHEMA = "mgr.forge.sam-adapter.v1"
DEFAULT_WEIGHTS_ENV = "MGR_SAM_WEIGHTS"
DEFAULT_WEIGHTS_CANDIDATES = (
    "models/sam_vit_b_01ec64.pth",
    "models/sam_vit_h_4b8939.pth",
    "models/sam_vit_l_0b3195.pth",
)
WORKER_SCRIPT = "scripts/sam_segment.py"
DEFAULT_WORKER_PYTHON_CANDIDATES = (
    "python3.12",
    r"C:\Users\cool\.local\bin\python3.12.exe",
)


def _resolve_weights(weights_path: Optional[str]) -> Optional[Path]:
    if weights_path:
        p = Path(weights_path)
        return p if p.is_file() else None
    env = os.environ.get(DEFAULT_WEIGHTS_ENV)
    if env:
        p = Path(env)
        if p.is_file():
            return p
    for candidate in DEFAULT_WEIGHTS_CANDIDATES:
        p = Path(candidate)
        if p.is_file():
            return p
    for root in (Path("."), Path("models"), Path.home() / ".cache" / "sam"):
        for name in ("sam_vit_b_01ec64.pth", "sam_vit_h_4b8939.pth", "sam_vit_l_0b3195.pth"):
            p = root / name
            if p.is_file():
                return p
    return None


def _resolve_worker_python() -> Optional[str]:
    env = os.environ.get("MGR_SAM_PYTHON")
    if env and Path(env).is_file():
        return env
    for candidate in DEFAULT_WORKER_PYTHON_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
        # try on PATH
        import shutil
        found = shutil.which(candidate)
        if found:
            return found
    return None


def _infer_model_type(weights: Optional[Path]) -> str:
    if weights is None:
        return "vit_b"
    name = weights.name.lower()
    if "vit_h" in name:
        return "vit_h"
    if "vit_l" in name:
        return "vit_l"
    return "vit_b"


class SamAdapter:
    """SAM-backed segmentation adapter. Gated on install + weights + licence."""

    name = "sam"
    evidence_level = EVIDENCE_LEVEL_INFERRED

    def __init__(self, weights_path: Optional[str] = None, model_type: Optional[str] = None,
                 device: Optional[str] = None, mode: str = "center"):
        self.weights_path = weights_path
        self.mode = mode if mode in ("center", "auto") else "center"
        self._weights = _resolve_weights(weights_path)
        self._model_type = model_type or _infer_model_type(self._weights)
        self._device = device
        self._model = None
        self._predictor = None
        self._mask_generator = None

    def available(self) -> bool:
        if self._weights is None:
            return False
        if _IMPORT_OK:
            try:
                return self._weights.stat().st_size > 1_000_000
            except OSError:
                return False
        # worker mode: need python 3.12 + torch + weights
        worker = _resolve_worker_python()
        if worker is None:
            return False
        worker_script = Path(WORKER_SCRIPT)
        if not worker_script.is_file():
            return False
        try:
            return self._weights.stat().st_size > 1_000_000
        except OSError:
            return False

    def _ensure_loaded(self):
        if self._predictor is not None or self._mask_generator is not None:
            return
        if not self.available():
            raise SegmentationError(
                "SAM is unavailable: install torch + segment_anything and provide "
                "weights (env MGR_SAM_WEIGHTS or models/sam_vit_*.pth), and clear the licence")
        if _IMPORT_OK:
            if self._device is None:
                self._device = "cuda" if (torch is not None and torch.cuda.is_available()) else "cpu"
            sam = sam_model_registry[self._model_type](checkpoint=str(self._weights))
            sam.to(device=self._device)
            if self.mode == "auto":
                self._mask_generator = SamAutomaticMaskGenerator(sam)
            else:
                self._predictor = SamPredictor(sam)

    def _segment_inprocess(self, source_path: str, out_path: str):
        self._ensure_loaded()
        if Image is None:
            raise SegmentationError("PIL is required for SAM adapter")
        image = Image.open(source_path).convert("RGB")
        import numpy as np
        arr = np.array(image)
        h, w = arr.shape[:2]

        if self.mode == "auto":
            masks = self._mask_generator.generate(arr)
            if not masks:
                raise SegmentationError("SAM produced no masks")
            best = max(masks, key=lambda m: m.get("area", 0))
            mask_arr = best["segmentation"].astype("uint8") * 255
            note = f"auto mode: selected largest of {len(masks)} masks (area={best.get('area')})"
            confidence = float(best.get("predicted_iou", 0.0)) if "predicted_iou" in best else None
        else:
            self._predictor.set_image(arr)
            cx, cy = w // 2, h // 2
            masks, scores, _ = self._predictor.predict(
                point_coords=__import__("numpy").array([[cx, cy]]),
                point_labels=__import__("numpy").array([1]),
                multimask_output=True)
            if masks is None or len(masks) == 0:
                raise SegmentationError("SAM produced no mask")
            idx = int(np.argmax(scores)) if scores is not None and len(scores) else 0
            mask_arr = masks[idx].astype("uint8") * 255
            note = f"center mode: selected mask {idx} of {len(masks)} (score={float(scores[idx]) if scores is not None else None})"
            confidence = float(scores[idx]) if scores is not None and len(scores) else None

        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(mask_arr, mode="L").save(out)

        return MaskResult(
            mask_path=str(out.resolve()),
            adapter=self.name,
            evidence_level=self.evidence_level,
            confidence=confidence,
            notes=(note, f"model_type={self._model_type}", f"device={self._device}",
                   "licence: Apache 2.0 (SAM); owner must record provenance under research/external-provenance/"),
        )

    def _segment_worker(self, source_path: str, out_path: str):
        worker = _resolve_worker_python()
        if worker is None:
            raise SegmentationError("no Python 3.12 worker available (set MGR_SAM_PYTHON)")
        script = Path(WORKER_SCRIPT)
        if not script.is_file():
            raise SegmentationError(f"missing worker script: {script}")
        cmd = [worker, str(script), "--image", source_path, "--out", out_path,
               "--mode", self.mode, "--weights", str(self._weights)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            raise SegmentationError("SAM worker timed out")
        if proc.returncode != 0:
            raise SegmentationError(f"SAM worker failed: {proc.stderr.strip() or proc.stdout.strip()}")
        try:
            data = json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            raise SegmentationError(f"SAM worker returned invalid JSON: {proc.stdout[:500]}")
        return MaskResult(
            mask_path=data["mask_path"],
            adapter=self.name,
            evidence_level=self.evidence_level,
            confidence=data.get("confidence"),
            notes=tuple(data.get("notes", [])) + (f"worker_python={worker}",),
        )

    def segment(self, source_path: str, *, out_path: str) -> MaskResult:
        src = Path(source_path)
        if not src.is_file():
            raise SegmentationError(f"missing source image: {src.name}")
        if not self.available():
            raise SegmentationError(
                "SAM is unavailable: install torch + segment_anything and provide "
                "weights (env MGR_SAM_WEIGHTS or models/sam_vit_*.pth), and clear the licence")
        if _IMPORT_OK:
            return self._segment_inprocess(source_path, out_path)
        return self._segment_worker(source_path, out_path)


def register_sam_if_available(registry, weights_path: Optional[str] = None,
                              mode: str = "center") -> bool:
    adapter = SamAdapter(weights_path=weights_path, mode=mode)
    if not adapter.available():
        return False
    try:
        registry.register(adapter)
    except ValueError:
        return False
    return True


def describe_sam() -> dict:
    adapter = SamAdapter()
    return {
        "schema": SCHEMA,
        "import_ok": _IMPORT_OK,
        "worker_python": _resolve_worker_python(),
        "available": adapter.available(),
        "weights": str(adapter._weights) if adapter._weights else None,
        "model_type": adapter._model_type,
        "mode": adapter.mode,
        "honesty": "SAM is optional and gated; manual masks remain the default and primary path",
    }
