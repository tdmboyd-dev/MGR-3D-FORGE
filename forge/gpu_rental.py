"""Dry-run rental planner. Price quotes are caller-supplied, never claimed live."""
from datetime import date
import math
from urllib.parse import urlsplit

from .gpu_packer import pack_jobs


def _valid_offer(offer, *, today):
    if not isinstance(offer, dict) or set(offer) - {"name", "provider", "vram_gb", "hourly_usd",
                                                       "observed_at", "source_url"}:
        raise ValueError("offer contains unsupported fields")
    for field in ("name", "provider"):
        if not isinstance(offer.get(field), str) or not 1 <= len(offer[field].strip()) <= 80:
            raise ValueError("offer name/provider missing")
    capacity, cost = offer.get("vram_gb"), offer.get("hourly_usd")
    if type(capacity) not in (int, float) or not math.isfinite(capacity) or not 0 < capacity <= 192:
        raise ValueError("invalid GPU VRAM offer")
    if type(cost) not in (int, float) or not math.isfinite(cost) or not 0 < cost <= 10000:
        raise ValueError("invalid GPU hourly price")
    source = offer.get("source_url")
    if not isinstance(source, str) or urlsplit(source).scheme != "https":
        raise ValueError("GPU quote requires an HTTPS evidence URL")
    try:
        observed = date.fromisoformat(offer["observed_at"])
    except (TypeError, ValueError, KeyError) as error:
        raise ValueError("GPU quote requires observed_at YYYY-MM-DD") from error
    if observed > today:
        raise ValueError("GPU quote date cannot be in the future")
    return (today - observed).days <= 7


def plan_rental(jobs, *, min_vram_gb=0.0, max_cost_per_hour=1e9,
                prefer="cost", block_hours=1.0, offers=None, today=None):
    """Produce a no-spend quote comparison, requiring explicit recent rates.

    The returned estimate is arithmetic only; does not include storage/egress,
    provisioning, cold starts, failed jobs, taxes or provider commitments.
    """
    if prefer not in ("cost", "performance", "value"):
        raise ValueError("unknown GPU ranking preference")
    if type(min_vram_gb) not in (int, float) or not math.isfinite(min_vram_gb) or min_vram_gb < 0:
        raise ValueError("invalid requested VRAM")
    if type(max_cost_per_hour) not in (int, float) or not math.isfinite(max_cost_per_hour) or max_cost_per_hour <= 0:
        raise ValueError("invalid GPU hourly price ceiling")
    if today is None:
        today = date.today()
    packing = pack_jobs(jobs, block_hours=block_hours)
    minimum = max(float(min_vram_gb), packing["totals"]["min_vram_gb"])
    foundation = {"schema": "mgr.forge.gpu-dry-run.v1",
                  "status": "UNPRICED", "price_proof": "NO_LIVE_QUOTE",
                  "purchase_authorized": False, "provider_called": False, "rental_started": False,
                  "selected_gpu": None, "total_estimated_cost": None,
                  "shadow_use_seconds": packing["totals"]["shadow_used_seconds"],
                  "packing": packing,
                  "estimate_excludes": ["storage", "egress", "cold start", "failures", "taxes"]}
    if offers is None:
        return foundation
    if not isinstance(offers, list) or len(offers) > 200:
        raise ValueError("offers must be a list of at most 200 quoted machines")
    eligible = []
    for offered in offers:
        fresh = _valid_offer(offered, today=today)
        if fresh and offered["vram_gb"] >= minimum and offered["hourly_usd"] <= max_cost_per_hour:
            eligible.append(offered)
    if not eligible:
        return {**foundation, "status": "NO_RECENT_ELIGIBLE_QUOTE"}
    if prefer == "performance":
        ordering = lambda x: (-x["vram_gb"], x["hourly_usd"], x["name"])
    elif prefer == "value":
        ordering = lambda x: (x["hourly_usd"] / x["vram_gb"], x["hourly_usd"], x["name"])
    else:
        ordering = lambda x: (x["hourly_usd"], -x["vram_gb"], x["name"])
    selected = sorted(eligible, key=ordering)[0]
    cost = round(selected["hourly_usd"] * packing["totals"]["blocks"] * block_hours, 6)
    return {**foundation, "status": "DRY_RUN_ESTIMATE", "price_proof": "CALLER_SUPPLIED_WITHIN_7_DAYS",
            "selected_gpu": selected, "total_estimated_cost": cost,
            "quote_as_of": selected["observed_at"]}
