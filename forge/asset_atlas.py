"""MGR Source Atlas: source discovery, bounded CC0 GLB intake, honest rights gates.

The 3DAssets.dev public read API supports bounded search and explicit download;
Poly Haven supports live metadata search only. Other sources are rights-labeled
directory candidates, not installed integrations.
The Forge-owned object store remains forge.assets.AssetRegistry.
"""

import hashlib
import json
from pathlib import Path
import struct
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from .assets import AssetRegistry


ATLAS_PATH = Path(__file__).resolve().parent / "data" / "asset_sources.json"
API_ORIGIN = "https://3dassets.dev"
CDN_HOST = "cdn.3dassets.dev"
MAX_CATALOG_BYTES = 2_000_000
MAX_ASSET_BYTES = 25_000_000


def _is_https_host(value, host):
    if type(value) is not str:
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    return (parsed.scheme == "https" and parsed.hostname == host and
            port in (None, 443) and not parsed.username and
            not parsed.password and not parsed.fragment)


def _read_bounded(response, maximum):
    length = response.headers.get("Content-Length")
    if length is not None:
        try:
            size = int(length)
        except ValueError as error:
            raise ValueError("invalid upstream content length") from error
        if size < 0 or size > maximum:
            raise ValueError("upstream response exceeds byte budget")
    payload = response.read(maximum + 1)
    if len(payload) > maximum:
        raise ValueError("upstream response exceeds byte budget")
    return payload


def inspect_import_glb(blob):
    """Structural safety check, NOT a Blender import, quality or rigging proof."""
    if not 28 <= len(blob) <= MAX_ASSET_BYTES:
        raise ValueError("GLB size outside bounded source intake")
    magic, version, length = struct.unpack_from("<4sII", blob, 0)
    if (magic, version, length) != (b"glTF", 2, len(blob)):
        raise ValueError("invalid GLB 2.0 header")
    cursor = 12
    chunks = []
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            raise ValueError("truncated GLB chunk")
        size, kind = struct.unpack_from("<I4s", blob, cursor)
        cursor += 8
        if size % 4 or cursor + size > len(blob):
            raise ValueError("invalid GLB chunk length")
        chunks.append((kind, blob[cursor:cursor + size]))
        cursor += size
    if len(chunks) != 2 or chunks[0][0] != b"JSON" or chunks[1][0] != b"BIN\0":
        raise ValueError("expected self-contained JSON and BIN GLB")
    try:
        doc = json.loads(chunks[0][1])
        if doc["asset"]["version"] != "2.0":
            raise ValueError("GLB is not glTF 2.0")
        buffers = doc["buffers"]
        meshes = doc["meshes"]
        if (len(buffers) != 1 or not 1 <= len(meshes) <= 10_000 or
                type(buffers[0]["byteLength"]) is not int or
                not 0 <= buffers[0]["byteLength"] <= len(chunks[1][1])):
            raise ValueError("GLB buffer or mesh inventory invalid")
        if any("uri" in value for value in buffers + doc.get("images", [])):
            raise ValueError("external or embedded URI references not admitted")
        extensions = doc.get("extensionsRequired", [])
        if not isinstance(extensions, list) or any(not isinstance(x, str) for x in extensions):
            raise ValueError("invalid required GLB extensions")
        return {"status": "STRUCTURE_INSPECTED", "meshes": len(meshes),
                "extensions_required": extensions,
                "limitations": ["Full accessor/texture/geometry validation not performed",
                                "Blender, Godot, rigging and likeness unverified"]}
    except (KeyError, TypeError, IndexError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("malformed GLB JSON document") from error


class MGRSourceAtlas:
    def __init__(self, file=ATLAS_PATH):
        document = json.loads(Path(file).read_text(encoding="utf-8"))
        if document.get("schema") != "mgr.forge.source-atlas.v1":
            raise ValueError("unsupported Source Atlas schema")
        sources = document.get("sources")
        if not isinstance(sources, list) or len({s["id"] for s in sources}) != len(sources):
            raise ValueError("source directory must have unique ids")
        self.sources = sources

    def find(self, *, category="", text="", kind=""):
        needle = text.casefold().strip()
        return [entry for entry in self.sources
                if (not category or category in entry["categories"])
                and (not kind or kind == entry["kind"])
                and (not needle or needle in (entry["name"] + " " + entry["id"] + " " +
                                               " ".join(entry["categories"])).casefold())]


class MGRAssetCatalog:
    """A recoverable metadata cache. Only explicit acquisition touches assets."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "catalog.json"

    def _read(self):
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("schema") != "mgr.forge.asset-catalog.v1" or not isinstance(data.get("items"), dict):
            raise ValueError("invalid local Source Atlas catalog")
        return data["items"]

    def remember(self, listings):
        if len(listings) > 100 or any(record.get("provider_id") not in ("3dassets", "polyhaven")
                                      for record in listings):
            raise ValueError("unsupported provider catalog batch")
        items = self._read()
        for record in listings:
            key = record["id"]
            prior = items.get(key)
            if prior is not None and (prior["cdn_url"] != record["cdn_url"] or
                                       prior["license"] != record["license"]):
                raise ValueError("upstream URL/rights changed; review before replacing source record")
            items[key] = record
        if len(items) > 10_000:
            raise ValueError("asset catalog size limit reached")
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps({"schema": "mgr.forge.asset-catalog.v1", "items": items},
                                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp.replace(self.path)
        return len(items)

    def search(self, *, text="", category="", provider=""):
        needle = text.casefold().strip()
        records = self._read().values()
        return sorted((entry for entry in records
                       if (not provider or entry["provider_id"] == provider)
                       and (not category or entry["category"] == category)
                       and (not needle or needle in (entry["title"] + " " + " ".join(entry["tags"])).casefold())),
                      key=lambda x: x["id"])

    def search_live_3dassets(self, query, *, category="", limit=20, opener=urlopen):
        if type(query) is not str or not 1 <= len(query.strip()) <= 120:
            raise ValueError("search must have 1..120 characters")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("search page limit must be 1..100")
        if category and (type(category) is not str or len(category) > 48 or
                         not all(ch.isalnum() or ch == "-" for ch in category)):
            raise ValueError("invalid source category filter")
        parameters = {"q": query.strip(), "limit": limit}
        if category:
            parameters["category"] = category
        url = f"{API_ORIGIN}/api/v1/assets?{urlencode(parameters)}"
        request = Request(url, headers={"User-Agent": "MGR-3D-FORGE-Source-Atlas/1.0",
                                         "Accept": "application/json"})
        with opener(request, timeout=12) as response:
            if not _is_https_host(response.geturl(), "3dassets.dev"):
                raise ValueError("catalog request redirected outside approved source")
            payload = json.loads(_read_bounded(response, MAX_CATALOG_BYTES))
        raw = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(raw, list) or len(raw) > 100:
            raise ValueError("unrecognized upstream source response")
        results = []
        for item in raw:
            if not isinstance(item, dict) or item.get("status") != "published":
                continue
            license_info = item.get("license") or {}
            stats = item.get("stats") or {}
            cdn = item.get("cdnUrl")
            source_url = item.get("url")
            slug = item.get("slug")
            size = stats.get("fileSize")
            if (license_info.get("slug") != "cc0-1.0" or
                    not _is_https_host(cdn, CDN_HOST) or
                    not _is_https_host(source_url, "3dassets.dev") or
                    type(size) is not int or not 28 <= size <= MAX_ASSET_BYTES or
                    type(slug) is not str or not 1 <= len(slug) <= 160 or
                    not all(ch.isalnum() or ch == "-" for ch in slug)):
                continue
            cat = item.get("category") or {}
            title = item.get("title")
            if type(title) is not str or not title.strip() or len(title) > 240:
                continue
            tags = item.get("tags") or []
            contributor = item.get("contributor") or {}
            entry = {"id": "3dassets:" + slug, "provider_id": "3dassets",
                     "slug": slug, "title": title, "category": str(cat.get("slug", "unknown"))[:60],
                     "tags": [t["slug"] for t in tags[:32] if isinstance(t, dict) and
                              isinstance(t.get("slug"), str)],
                     "source_url": source_url, "cdn_url": cdn, "license": "CC0-1.0",
                     "license_url": license_info.get("url") or "https://creativecommons.org/publicdomain/zero/1.0/",
                     "owner": str(contributor.get("name") or contributor.get("username") or "3DAssets.dev")[:100],
                     "bytes_claimed": size, "triangles_claimed": stats.get("triangles"),
                     "ai_generated_claimed": item.get("aiGenerated"),
                     "rights_status": "SOURCE_CC0_CLAIM_REVIEW_PENDING",
                     "quality_status": "SOURCE_METADATA_ONLY"}
            results.append(entry)
        self.remember(results)
        return {"status": "CACHED_SOURCE_METADATA", "provider": "3dassets",
                "returned": len(results), "skipped_unadmittable": len(raw) - len(results),
                "listings": results, "assets_downloaded": 0}

    def search_live_polyhaven(self, query, *, kind="models", limit=6, opener=urlopen):
        """Use official free semantic search; receive metadata only, not paid files.

        The Poly Haven live API requires visible source credit even though
        the assets themselves are CC0. We persist that usage obligation.
        """
        if type(query) is not str or not 1 <= len(query.strip()) <= 100:
            raise ValueError("Poly Haven search needs 1..100 characters")
        if kind not in ("models", "textures", "hdris"):
            raise ValueError("unknown Poly Haven asset family")
        if type(limit) is not int or not 1 <= limit <= 10:
            raise ValueError("Poly Haven source search must request 1..10 assets")
        parameters = urlencode({"q": query.strip().lower(), "t": kind, "limit": limit})
        url = f"https://api.polyhaven.com/search?{parameters}"
        headers = {"User-Agent": "MGR-3D-FORGE-Source-Atlas/1.0", "Accept": "application/json"}
        with opener(Request(url, headers=headers), timeout=12) as response:
            if not _is_https_host(response.geturl(), "api.polyhaven.com"):
                raise ValueError("Poly Haven search redirected outside official API")
            data = json.loads(_read_bounded(response, MAX_CATALOG_BYTES))
        results = data.get("results") if isinstance(data, dict) else None
        if not isinstance(results, list) or len(results) > limit:
            raise ValueError("invalid Poly Haven search response")
        found = []
        for match in results:
            slug = match.get("slug") if isinstance(match, dict) else None
            if type(slug) is not str or not 1 <= len(slug) <= 100 or not all(
                    ch.isalnum() or ch in "_-" for ch in slug):
                continue
            info_url = f"https://api.polyhaven.com/info/{slug}"
            with opener(Request(info_url, headers=headers), timeout=12) as response:
                if not _is_https_host(response.geturl(), "api.polyhaven.com"):
                    raise ValueError("Poly Haven metadata redirected outside official API")
                info = json.loads(_read_bounded(response, MAX_CATALOG_BYTES))
            if not isinstance(info, dict) or info.get("type") != {"hdris": 0, "textures": 1, "models": 2}[kind]:
                continue
            title = info.get("name")
            if type(title) is not str or not 1 <= len(title) <= 240:
                continue
            authors = info.get("authors") or {}
            if not isinstance(authors, dict):
                authors = {}
            tags = info.get("tags") or []
            found.append({"id": "polyhaven:" + slug, "provider_id": "polyhaven",
                          "slug": slug, "title": title, "category": kind,
                          "tags": [tag[:60] for tag in tags[:32] if isinstance(tag, str)],
                          "source_url": f"https://polyhaven.com/a/{slug}", "cdn_url": "",
                          "license": "CC0-1.0", "license_url": "https://polyhaven.com/license",
                          "owner": ", ".join(authors)[:100] or "Poly Haven",
                          "bytes_claimed": None, "triangles_claimed": info.get("polycount"),
                          "ai_generated_claimed": None,
                          "rights_status": "PROVIDER_CC0_CLAIM_API_CREDIT_REQUIRED",
                          "quality_status": "SOURCE_METADATA_ONLY",
                          "api_credit": "Powered by Poly Haven"})
        self.remember(found)
        return {"status": "CACHED_SOURCE_METADATA", "provider": "polyhaven",
                "returned": len(found), "skipped_unadmittable": len(results) - len(found),
                "listings": found, "assets_downloaded": 0,
                "api_credit": "Powered by Poly Haven"}

    def acquire_3dassets(self, slug, store_root, *, opener=urlopen):
        """Explicitly download to local quarantine; never advertise as usable/cleared."""
        record = self._read().get("3dassets:" + slug)
        if record is None:
            raise ValueError("source must first be discovered in this catalog")
        if record["provider_id"] != "3dassets" or record["license"] != "CC0-1.0":
            raise ValueError("only reviewed source family is eligible for bounded fetch")
        if not _is_https_host(record["cdn_url"], CDN_HOST):
            raise ValueError("remote asset host not allowlisted")
        request = Request(record["cdn_url"], headers={"User-Agent": "MGR-3D-FORGE-Source-Atlas/1.0"})
        with opener(request, timeout=30) as response:
            if not _is_https_host(response.geturl(), CDN_HOST):
                raise ValueError("asset request redirected outside approved CDN")
            payload = _read_bounded(response, MAX_ASSET_BYTES)
        if len(payload) != record["bytes_claimed"]:
            raise ValueError("download length differs from published metadata")
        glb = inspect_import_glb(payload)
        owner = record["owner"]
        metadata = AssetRegistry(store_root).add(payload, owner=owner, license_id="CC0-1.0",
            source=record["source_url"], extra={"title": record["title"],
                "category": record["category"], "provider_id": "3dassets", "source_slug": slug,
                "rights_reviewed": False, "geometry_status": glb["status"]})
        return {"status": "QUARANTINED_RIGHTS_AND_QUALITY", "asset": metadata,
                "container_inspection": glb, "source_claimed_triangles": record["triangles_claimed"],
                "source_claimed_ai_generated": record["ai_generated_claimed"],
                "license_note": "Provider claims CC0; asset-level rights and independent engine quality not verified",
                "external_cost_usd": 0, "external_api_writes": 0}
