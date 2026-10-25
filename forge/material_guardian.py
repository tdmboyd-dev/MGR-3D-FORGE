"""MGR material round-trip acceptance, separate from cosmetic visual quality."""

import math


def validate_imported_materials(report, *, minimum_materials=1):
    entries=report.get("materials",[]) if isinstance(report,dict) else []
    errors=[]
    if not isinstance(entries,list) or len(entries)<minimum_materials:
        errors.append("missing imported materials")
    else:
        names=set()
        for item in entries:
            name=item.get("name") if isinstance(item,dict) else None
            if not isinstance(name,str) or not name or name in names:
                errors.append("missing/duplicate material name")
                continue
            names.add(name)
            for field in ("metallic","roughness"):
                value=item.get(field)
                if type(value) not in (float,int) or not math.isfinite(value) or not 0<=value<=1:
                    errors.append(f"{name}: invalid imported {field}")
            rgba=item.get("base_color")
            if not isinstance(rgba,list) or len(rgba)!=4 or not all(
                type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in rgba):
                errors.append(f"{name}: invalid imported base color")
    return {"schema":"mgr.forge.material-guardian.v1","status":"PASS" if not errors else "FAIL",
            "count":len(entries) if isinstance(entries,list) else 0,"errors":errors,
            "limitations":["Principled socket inspection, not full shader graph or texture fidelity",
                           "does not prove photorealism or appearance under another engine"]}
