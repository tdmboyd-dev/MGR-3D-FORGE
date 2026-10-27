"""SAM segmentation worker (runs under Python 3.12 with torch installed).

Usage:
    python scripts/sam_segment.py --image INPUT.png --out MASK.png --mode center|auto \
        [--weights PATH] [--model-type vit_b|vit_l|vit_h] [--json-out RECEIPT.json]

Prints a JSON object to stdout with provenance. Writes the mask PNG to --out.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from segment_anything import SamAutomaticMaskGenerator, SamPredictor, sam_model_registry


def infer_model_type(weights):
    name = Path(weights).name.lower()
    if "vit_h" in name:
        return "vit_h"
    if "vit_l" in name:
        return "vit_l"
    return "vit_b"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", choices=("center", "auto"), default="center")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--model-type", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args(argv)

    weights = Path(args.weights)
    if not weights.is_file():
        raise SystemExit(f"missing weights: {weights}")

    model_type = args.model_type or infer_model_type(weights)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    sam = sam_model_registry[model_type](checkpoint=str(weights))
    sam.to(device=device)

    image = Image.open(args.image).convert("RGB")
    arr = np.array(image)
    h, w = arr.shape[:2]

    if args.mode == "auto":
        gen = SamAutomaticMaskGenerator(sam)
        masks = gen.generate(arr)
        if not masks:
            raise SystemExit("SAM produced no masks")
        best = max(masks, key=lambda m: m.get("area", 0))
        mask_arr = best["segmentation"].astype("uint8") * 255
        confidence = float(best.get("predicted_iou", 0.0)) if "predicted_iou" in best else None
        note = f"auto mode: selected largest of {len(masks)} masks (area={best.get('area')})"
    else:
        predictor = SamPredictor(sam)
        predictor.set_image(arr)
        cx, cy = w // 2, h // 2
        masks, scores, _ = predictor.predict(
            point_coords=np.array([[cx, cy]]), point_labels=np.array([1]),
            multimask_output=True)
        if masks is None or len(masks) == 0:
            raise SystemExit("SAM produced no mask")
        idx = int(np.argmax(scores)) if scores is not None and len(scores) else 0
        mask_arr = masks[idx].astype("uint8") * 255
        confidence = float(scores[idx]) if scores is not None and len(scores) else None
        note = f"center mode: selected mask {idx} of {len(masks)} (score={confidence})"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask_arr, mode="L").save(out)

    result = {
        "schema": "mgr.forge.sam-worker.v1",
        "status": "MATERIALIZED",
        "mask_path": str(out.resolve()),
        "mode": args.mode,
        "model_type": model_type,
        "device": device,
        "confidence": confidence,
        "image_size": [w, h],
        "mask_pixels": int((mask_arr > 0).sum()),
        "notes": [note, "licence: Apache 2.0 (SAM); record provenance under research/external-provenance/"],
    }
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    raise SystemExit(main())
