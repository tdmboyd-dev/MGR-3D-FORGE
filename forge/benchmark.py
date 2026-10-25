"""Local reproducible CPU geometry and GLB exporter benchmark receipts."""

import json
from pathlib import Path
import platform
import time
import tracemalloc

from .geometry import create_neighborhood
from .glb import export_glb,inspect_glb
from .quality import validate_neighborhood
from .spec import WorldSpec


def run_benchmark(sizes=(10,100,1000)):
    results=[]
    for size in sizes:
        if type(size) is not int or not 0 <= size <= 10000:
            raise ValueError("unsupported benchmark size")
        columns=max(1,min(100,size))
        rows=max(1,(size+columns-1)//columns)
        spec=WorldSpec(columns=columns,rows=rows,buildings=size)
        tracemalloc.start()
        start=time.perf_counter()
        meshes,scene=create_neighborhood(spec)
        payload=export_glb(meshes)
        elapsed=time.perf_counter()-start
        _,peak=tracemalloc.get_traced_memory()
        tracemalloc.stop()
        qc=validate_neighborhood(scene)
        glb=inspect_glb(payload)
        if not qc["passed"] or not glb["valid"]:
            raise RuntimeError("benchmark output invalid")
        results.append({"buildings":size,"seconds":round(elapsed,6),
                        "python_peak_bytes":peak,"glb_bytes":len(payload),
                        "triangles":glb["triangles"],"status":"PASS"})
    return {"schema":"mgr.forge.benchmark.v1","compute":"CPU",
            "implementation":platform.python_implementation(),
            "python_version":platform.python_version(),
            "machine":platform.machine(),"external_api_calls":0,"results":results,
            "note":"Local Python timings, not cross-device or competitor benchmarks"}


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    results=run_benchmark()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    print(json.dumps(results,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
