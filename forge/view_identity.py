"""MGR View Identity — cautious identity decisions across views and poses.

The module deliberately separates verified asset provenance from appearance
similarity. Two pixels/images alone cannot prove the same 3D character.
"""

from dataclasses import dataclass
import math

from .visualqa import read_png


@dataclass(frozen=True)
class AssetView:
    """Evidence from an approved asset registry and a particular scene pose."""

    asset_id: str | None
    canonical_asset_sha256: str | None
    rest_mesh_sha256: str | None
    pose_id: str | None = None
    camera_id: str | None = None


def _digest(value):
    return isinstance(value, str) and len(value)==64 and all(c in "0123456789abcdef" for c in value)


def compare_asset_views(left: AssetView, right: AssetView):
    """Prove provenance agreement where possible; never infer identity from name."""
    for item in (left, right):
        for value in (item.canonical_asset_sha256,item.rest_mesh_sha256):
            if value is not None and not _digest(value):
                raise ValueError("asset hashes must be SHA-256")
    same_canonical=(left.canonical_asset_sha256 is not None and
                    left.canonical_asset_sha256==right.canonical_asset_sha256)
    same_rest=(left.rest_mesh_sha256 is not None and
               left.rest_mesh_sha256==right.rest_mesh_sha256)
    conflicting=(left.canonical_asset_sha256 is not None and
                 right.canonical_asset_sha256 is not None and
                 left.canonical_asset_sha256!=right.canonical_asset_sha256)
    if same_canonical or same_rest:
        verdict="SAME_VERIFIED_SOURCE_ASSET"
        basis="matching cryptographic asset or neutral-rest-mesh digest"
    elif conflicting:
        verdict="DIFFERENT_SOURCE_ARTIFACTS"
        basis="different canonical artifact digests do not prove different characters"
    else:
        verdict="IDENTITY_UNDETERMINED"
        basis="insufficient trusted common asset evidence"
    return {"schema":"mgr.forge.asset-view-identity.v1",
            "verdict":verdict,"basis":basis,
            "asset_id_matches":bool(left.asset_id and left.asset_id==right.asset_id),
            "different_pose":left.pose_id!=right.pose_id,
            "different_camera":left.camera_id!=right.camera_id,
            "limitations":["a matching name alone is not identity proof",
                           "equal rest meshes do not prove same clothing or face texture",
                           "separately generated models can represent the same person"]}


def _foreground_mask(png, *, background=None, tolerance=12):
    if background is None:
        background=tuple(png["rows"][0][:3])
    transparent=(png["channels"]==4 and
                 any(row[x*4+3]<255 for row in png["rows"]
                     for x in range(png["width"])))
    coords=[]
    channels=png["channels"]
    for y,row in enumerate(png["rows"]):
        for x in range(png["width"]):
            rgb=row[x*channels:x*channels+3]
            present=(row[x*channels+3]>tolerance) if transparent else any(
                abs(rgb[i]-background[i])>tolerance for i in range(3))
            if present:
                coords.append((x,y))
    if not coords:
        return set()
    left=min(x for x,y in coords)
    top=min(y for x,y in coords)
    width=max(x for x,y in coords)-left+1
    height=max(y for x,y in coords)-top+1
    # Sample on an even 0..30 coordinate lattice, avoiding the half-pixel
    # ambiguity that appears when rotating a 0..31 raster about its center.
    return {(round((x-left)*30/max(1,width-1)), round((y-top)*30/max(1,height-1)))
            for x,y in coords}


def _turn(mask,rotations):
    for _ in range(rotations):
        mask={(30-y,x) for x,y in mask}
    return mask


def compare_view_silhouettes(first_png,second_png,*,allow_quarter_turns=True,
                             acceptance_iou=0.92):
    """Translation/scale-tolerant silhouette comparison, **not** identity proof.

    Optional 90-degree image-plane rotation tolerance. Does not solve arbitrary
    3D camera rotation, depth ambiguity, limb posing, or occlusion.
    """
    if not isinstance(acceptance_iou,(int,float)) or not math.isfinite(acceptance_iou) or not 0<=acceptance_iou<=1:
        raise ValueError("acceptance_iou must be in [0,1]")
    a=_foreground_mask(read_png(first_png))
    b=_foreground_mask(read_png(second_png))
    if not a or not b:
        return {"verdict":"INSUFFICIENT_FOREGROUND","best_iou":None,
                "identity_proven":False}
    scores=[]
    for turns in range(4 if allow_quarter_turns else 1):
        trial=_turn(b,turns)
        intersection=len(a & trial)
        union=len(a | trial)
        scores.append((intersection/union,turns))
    best,rotation=max(scores)
    return {"schema":"mgr.forge.view-silhouette.v1",
            "verdict":"APPEARANCE_CONSISTENT" if best>=acceptance_iou else "APPEARANCE_DIFFERENT_OR_VIEW_CHANGED",
            "best_iou":round(best,6),"image_plane_quarter_turns":rotation,
            "identity_proven":False,
            "limitations":["binary silhouette only; lighting/background affect masks",
                           "translation and image-plane quarter turns tolerated",
                           "3D rotation and different poses can change silhouette",
                           "appearance similarity is never proof of character identity"]}
