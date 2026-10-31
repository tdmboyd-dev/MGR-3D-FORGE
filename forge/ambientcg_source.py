"""Official ambientCG v3 public read API adapter; metadata only, no raw download."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .asset_atlas import _is_https_host, _read_bounded, MAX_CATALOG_BYTES


def search_ambientcg(catalog, query, *, kind="textures", limit=6, opener=urlopen):
    if type(query) is not str or not 1 <= len(query.strip()) <= 100:
        raise ValueError("ambientCG query needs 1..100 characters")
    mapping = {"textures": "material", "hdris": "hdri", "models": "3d-model"}
    if kind not in mapping:
        raise ValueError("unsupported ambientCG asset kind")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("ambientCG requests must be bounded to 1..20")
    url = "https://ambientcg.com/api/v3/assets?" + urlencode({
        "type": mapping[kind], "q": query.strip(),
        "limit": limit, "include": "title,tags,downloads"})
    request = Request(url, headers={"User-Agent": "MGR-3D-FORGE-Source-Atlas/1.0",
                                   "Accept": "application/json"})
    with opener(request, timeout=15) as response:
        if not _is_https_host(response.geturl(), "ambientcg.com"):
            raise ValueError("ambientCG API redirected outside approved host")
        doc = json.loads(_read_bounded(response, MAX_CATALOG_BYTES))
    raw = doc.get("assets") if isinstance(doc, dict) else None
    if not isinstance(raw, list) or len(raw) > limit:
        raise ValueError("unrecognized ambientCG v3 response")
    found = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        slug, title = item.get("id"), item.get("title")
        if (type(slug) is not str or not 1 <= len(slug) <= 100 or
            not all(c.isalnum() or c in "-_" for c in slug) or
            type(title) is not str or not 1 <= len(title) <= 200):
            continue
        tags = item.get("tags") if isinstance(item.get("tags"), list) else []
        downloads = item.get("downloads") if isinstance(item.get("downloads"), list) else []
        safe_downloads = []
        for option in downloads[:16]:
            if not isinstance(option, dict):
                continue
            link = option.get("url")
            if (_is_https_host(link, "ambientcg.com") and
                str(link).startswith("https://ambientcg.com/get?file=") and
                option.get("extension") == "zip" and
                type(option.get("size")) is int and 0 < option["size"] <= 75_000_000):
                safe_downloads.append({"attributes": str(option.get("attributes", ""))[:32],
                                       "url": link, "bytes_claimed": option["size"]})
        found.append({
            "id": "ambientcg:" + slug, "provider_id": "ambientcg",
            "slug": slug, "title": title, "category": kind,
            "tags": [tag[:60] for tag in tags[:32] if isinstance(tag, str)],
            "source_url": "https://ambientcg.com/a/" + slug,
            "cdn_url": "", "license": "CC0-1.0",
            "license_url": "https://docs.ambientcg.com/license/",
            "owner": "ambientCG", "bytes_claimed": None, "triangles_claimed": None,
            "ai_generated_claimed": None,
            "rights_status": "OFFICIAL_CC0_METADATA_REVIEW_PENDING",
            "quality_status": "SOURCE_METADATA_ONLY", "download_options": safe_downloads
        })
    catalog.remember(found)
    return {"status": "CACHED_SOURCE_METADATA", "provider": "ambientcg",
            "returned": len(found), "listings": found,
            "assets_downloaded": 0,
            "disclaimer": "Remote metadata is not a preserved, verified material"}
