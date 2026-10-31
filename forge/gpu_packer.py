"""Deterministic CPU-only GPU block packing with bounded shadow backfill.

No provider communication, reservation, cancellation or charge. The schedule
assumes serial jobs and one machine. It cannot prove real runtime duration.
"""
import math


def _check_job(entry, identities):
    if not isinstance(entry, dict) or set(entry) - {"id", "seconds", "min_vram_gb", "shadow"}:
        raise ValueError("unsupported GPU job fields")
    identity, seconds, vram = entry.get("id"), entry.get("seconds"), entry.get("min_vram_gb")
    if not isinstance(identity, str) or not 1 <= len(identity) <= 80 or identity in identities:
        raise ValueError("job id must be unique and 1..80 characters")
    if type(seconds) is not int or not 1 <= seconds <= 86400:
        raise ValueError("job seconds must be a positive integer <= 86400")
    if type(vram) not in (int, float) or not math.isfinite(vram) or not 0 < vram <= 192:
        raise ValueError("job min_vram_gb must be in (0, 192]")
    if type(entry.get("shadow", False)) is not bool:
        raise ValueError("shadow is a boolean")
    identities.add(identity)
    return {"id": identity, "seconds": seconds, "min_vram_gb": float(vram),
            "shadow": entry.get("shadow", False)}


def pack_jobs(jobs, *, block_hours=1.0):
    if type(block_hours) not in (int, float) or not math.isfinite(block_hours) or not 0 < block_hours <= 24:
        raise ValueError("block_hours must be between 0 and 24")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 1000:
        raise ValueError("jobs must be a nonempty list of at most 1000")
    identities = set()
    validated = [_check_job(entry, identities) for entry in jobs]
    seconds_per_block = block_hours * 3600
    bins = []
    placements = []
    unplaced_shadow = []

    def find_gap(length):
        for block in bins:
            for i, (start, end) in enumerate(block):
                if end - start >= length:
                    block[i] = (start + length, end)
                    return start
        return None

    def add_block():
        start = len(bins) * seconds_per_block
        bins.append([(start, start + seconds_per_block)])

    # Primary work pays for blocks. Largest jobs first minimize fragmentation.
    primary = sorted((x for x in validated if not x["shadow"]),
                     key=lambda x: (-x["seconds"], x["id"]))
    shadows = sorted((x for x in validated if x["shadow"]),
                     key=lambda x: (-x["seconds"], x["id"]))
    for job in primary + shadows:
        length = job["seconds"]
        start = find_gap(length) if length <= seconds_per_block else None
        if start is None and job["shadow"]:
            unplaced_shadow.append(job["id"])
            continue
        if start is None:
            if length <= seconds_per_block:
                add_block()
                start = find_gap(length)
            else:
                start = len(bins) * seconds_per_block
                count = math.ceil(length / seconds_per_block)
                for _ in range(count):
                    add_block()
                end = start + length
                last = bins[-1]
                if end < len(bins) * seconds_per_block:
                    last[:] = [(end, len(bins) * seconds_per_block)]
                else:
                    last[:] = []
                for bin_item in bins[-count:-1]:
                    bin_item[:] = []
        placements.append({"id":job["id"],"start_seconds":round(start,4),
                           "end_seconds":round(start+length,4),
                           "seconds":length,"shadow":job["shadow"],
                           "min_vram_gb":job["min_vram_gb"]})
    placements.sort(key=lambda x: (x["start_seconds"], x["id"]))
    primary_seconds=sum(x["seconds"] for x in placements if not x["shadow"])
    shadow_seconds=sum(x["seconds"] for x in placements if x["shadow"])
    billed_seconds=round(len(bins)*seconds_per_block,4)
    return {
        "algorithm":"deterministic-first-fit-decreasing-shadow-backfill-v2",
        "placements":placements,
        "unplaced_shadow":sorted(unplaced_shadow),
        "totals":{"jobs":len(jobs),"placed":len(placements),
                  "blocks":len(bins),"estimated_runtime_seconds":primary_seconds,
                  "shadow_used_seconds":shadow_seconds,
                  "billed_seconds":billed_seconds,
                  "unused_seconds":round(billed_seconds-primary_seconds-shadow_seconds,4),
                  "min_vram_gb":max((x["min_vram_gb"] for x in placements), default=0.0)}
    }
