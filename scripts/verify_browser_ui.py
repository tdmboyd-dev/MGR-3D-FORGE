"""Reproduce actual owner Windows Chrome Studio workflows on a fresh Forge instance.

Requires optional playwright-core installed in scripts/browser-qa and Chrome.
Creates only private test GLBs/workspaces/screenshot and a safe JSON receipt.
Never runs against a public user website or uploads secrets or model binaries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import threading

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import start_server


def verify(mode,out,blender):
    if mode not in ("creature","human"):
        raise ValueError("browser mode must be creature or human")
    private=Path(out)
    private.mkdir(parents=True,exist_ok=True)
    if not private.is_dir():
        raise ValueError("private browser evidence directory is unavailable")
    repo_script=ROOT/"scripts"/"browser-qa"/(mode+".mjs")
    if not repo_script.is_file():
        raise FileNotFoundError("MGR Forge browser QA source absent")
    if mode=="human" and blender=="blender" and shutil.which("blender") is None:
        # Owner Windows Blender 5.2 installation; source stays portable when
        # installed Blender is already in PATH or an exact --blender is given.
        known=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
        if known.is_file():
            blender=str(known)
    with tempfile.TemporaryDirectory(prefix="mgr-browser-owner-") as temp:
        target=Path(temp)
        build(WorldSpec(seed=24,columns=2,rows=2,buildings=2),target/"world")
        service,studio=start_server(target/"world",target/"workspace",blender=blender)
        worker=threading.Thread(target=service.serve_forever,daemon=True)
        worker.start()
        try:
            process=subprocess.run(
                ["node",str(repo_script),
                 "http://127.0.0.1:"+str(service.server_port)+"/",str(private)],
                cwd=repo_script.parent,capture_output=True,text=True,timeout=190
            )
            if process.returncode:
                print("MGR_CHROME_RUN_FAILED",process.stderr[-1500:])
                for path in (target/"workspace"/"jobs").rglob("human-error.json"):
                    try:
                        item=json.loads(path.read_text(encoding="utf8"))
                        print("PRIVATE_WORKER_FAILURE_TYPE",item.get("error_type","UNKNOWN"))
                    except (ValueError,OSError):
                        print("PRIVATE_WORKER_FAILURE_RECEIPT_UNREADABLE")
                raise RuntimeError("Actual Forge Chrome QA failed; do not record success")
            marker="FORGE_BROWSER_QA=" if mode=="creature" else "MGR_HUMAN_CHROME_PROOF="
            matching=[line.split(marker,1)[1] for line in process.stdout.splitlines()
                      if line.startswith(marker)]
            if len(matching)!=1:
                raise RuntimeError("Missing actual Chrome acceptance output")
            proof=json.loads(matching[0])
            if proof.get("status") not in ("PASS","REAL_CHROME_HUMAN_FACE_CREATION_PASS"):
                raise RuntimeError("Chrome result did not claim successful observed behavior")
            if proof.get("browser_errors") or proof.get("page_errors"):
                raise RuntimeError("Actual browser reported JavaScript error")
            if mode=="creature":
                rows=json.loads((target/"workspace"/"creature-requests.json").read_text(encoding="utf8"))
                biome=json.loads((target/"workspace"/"biome-requests.json").read_text(encoding="utf8"))
                expected={row["sha256"] for row in rows.values()}
                expected|={row["sha256"] for row in biome.values()}
                received={proof["glb_sha256"],proof["morph_revision_sha256"],proof["biome_glb_sha256"]}
                if not expected.issubset(received) or len(rows)!=2 or len(biome)!=1 or (
                   not proof.get("original_biome_and_edit_job_passed")):
                    raise RuntimeError("Browser fixture output differs from actual Forge job files")
            else:
                rows=json.loads((target/"workspace"/"human-lipsync-requests.json").read_text(encoding="utf8"))
                if len(rows)!=1 or next(iter(rows.values()))["sha256"]!=proof["real_human_glb_sha256"]:
                    raise RuntimeError("Browser Human GLB SHA differs from real Blender worker")
            receipt={"schema":"mgr.forge.owner-browser-reproduction.v1",
                     "mode":mode,"status":"REAL_CHROME_ACCEPTANCE_PASS",
                     "source":"same Forge Studio viewer + existing Python Forge workers",
                     "public_hosted_consumer_verified":False,
                     "gpu_neural_inference_used":False,"owner_visual_art_accepted":False,
                     "actual_browser_result":proof}
            destination=private/("browser-"+mode+"-receipt.json")
            if destination.exists():
                raise FileExistsError("Never overwrite existing owner browser proof")
            destination.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
            return destination
        finally:
            service.shutdown()
            service.server_close()
            worker.join(timeout=2)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("creature","human"),required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--blender",default="blender")
    args=parser.parse_args()
    print("MGR_BROWSER_SOURCE_VERIFIED",verify(args.mode,args.out,args.blender))
