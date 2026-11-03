"""Reproducible offline CLI qualification; no providers, model downloads or paid calls.

Run from the repository: python scripts/verify_forge_path_matrix.py --out NEW_DIRECTORY
Fixtures are disposable. Receipts retain exact commands, exit codes and observations.
This is bounded CPU qualification, not Blender/Godot/browser/production acceptance.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def run_remaining_blender(output, blender):
    """Run original render/facial/creature CLI receivers once on bounded fixtures."""
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    files=[*sorted((ROOT/'forge').rglob('*.py')),*sorted((ROOT/'bridge').glob('*.py'))]
    def snapshot():return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    before=snapshot()
    cases=[]
    def cli(name,args):
        command=[sys.executable,'-m','forge.cli',*map(str,args)]
        started=time.monotonic()
        try:
            run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf8',timeout=640)
            row={'case':name,'command':command,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'status':'PASS' if run.returncode==0 else 'FAIL'}
        except subprocess.TimeoutExpired:
            row={'case':name,'command':command,'status':'FAIL','reason':'640-second CLI deadline'}
        row['seconds']=round(time.monotonic()-started,3)
        cases.append(row)
        print(f"{name}: {row['status']} ({row['seconds']}s)",flush=True)
    if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
    from tests.test_human_lipsync import SPEC
    from tests.test_audio_motion import synthetic_audio
    with tempfile.TemporaryDirectory(prefix='mgr-forge-render-paths-') as temp:
        p=Path(temp)
        world=p/'world'
        cli('build-render-fixture',['build','--buildings','3','--out',world])
        cli('actual-workbench-world-render',['blender-render',world/'world.glb','--image',p/'world-render.png','--report',p/'world-render.json','--binary',blender])
        director=p/'director.blend'
        cli('actual-cinematic-reel',['blender-cinematic',world/'world.glb','--tour',world/'camera_tour.json','--blend',director,'--image',p/'director.png','--report',p/'director.json','--binary',blender])
        cli('actual-director-timeline-audit',['blender-director-audit',director,'--report',p/'director-audit.json','--binary',blender])
        cli('actual-director-frame-receivers',['blender-director-frames',director,'--out',p/'director-frames','--report',p/'director-frames.json','--binary',blender])
        fx=p/'fx'
        cli('native-portal-render-fixture',['fantasy-effect','--kind','portal','--particles','12','--out',fx])
        for name,density in (('control','0'),('volume','0.12')):
            cli('actual-fx-'+name,['blender-fx-render',fx/'effect.glb','--image',p/f'fx-{name}.png','--report',p/f'fx-{name}.json','--binary',blender,'--volume-density',density])
        cli('actual-matched-atmosphere-judge',['judge-atmosphere',p/'fx-control.png',p/'fx-volume.png',p/'fx-control.json',p/'fx-volume.json','--out',p/'atmosphere.json'])
        cli('actual-studio-material-light-hair-witness',['blender-studio-witness','--blend',p/'studio-witness.blend','--image',p/'studio-witness.png','--report',p/'studio-witness.json','--binary',blender])
        character=p/'character'
        cli('native-pose-fixture',['character','--pose','T','--out',character])
        cli('actual-skin-pose-fixture',['blender-rig',character,'--blend',p/'rig.blend','--report',p/'rig.json','--binary',blender,'--skin'])
        cli('actual-pose-frames',['blender-pose-render',p/'rig.blend','--first',p/'pose-a.png','--second',p/'pose-b.png','--report',p/'pose-render.json','--binary',blender])
        (p/'timings.json').write_text(json.dumps(SPEC),encoding='utf8')
        (p/'owned.wav').write_bytes(synthetic_audio())
        cli('actual-human-timed-cli',['human-lipsync','--timings',p/'timings.json','--out',p/'human-timed','--blender',blender])
        cli('actual-human-audio-cli',['human-audio-motion','--wav',p/'owned.wav','--actor-id','mgr-synthetic-cli-audio','--out',p/'human-audio','--blender',blender])
        cli('native-creature-rig-fixture',['imagine-creature','--prompt','invent a winged dragon with a flexible tail','--seed','11','--variants','3','--out',p/'creature'])
        cli('actual-creature-rig-cli',['rig-creature','--source',p/'creature','--out',p/'creature-rig','--blender',blender])
        for file in p.glob('*.json'):shutil.copyfile(file,output/file.name)
    after=snapshot()
    result={'schema':'mgr.forge.remaining-blender-cli.v1','cases':cases,'status':'PASS' if all(c['status']=='PASS' for c in cases) else 'FAIL',
            'source_checkpoints':{'before':before,'after':after,'changed':[k for k in before if before[k]!=after[k]]},
            'limits':['Original synthetic assets, installed Blender, no neural/providers/spend','Fixed existing bridge render bounds; no art/production quality claim']}
    (output/'matrix.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return int(result['status']=='FAIL')


def run_blender_inspections(output, blender):
    """New CLI receiver qualifications only; no repeated render or provider jobs."""
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    cases=[]
    def cli(name,args):
        command=[sys.executable,"-m","forge.cli",*map(str,args)]
        try:
            result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding="utf8",timeout=190)
            cases.append({"case":name,"command":command,"exit_code":result.returncode,"stdout":result.stdout,"stderr":result.stderr,"status":"PASS" if result.returncode==0 else "FAIL"})
            return result.returncode==0
        except subprocess.TimeoutExpired:
            cases.append({"case":name,"command":command,"status":"FAIL","reason":"190-second timeout"})
            return False
    with tempfile.TemporaryDirectory(prefix="mgr-forge-blender-paths-") as temp:
        p=Path(temp)
        world=p/"world"
        cli("fresh-native-world",["build","--buildings","3","--out",world])
        cli("native-world-independent-import",["blender-verify",world/"world.glb","--report",p/"import.json","--binary",blender])
        cli("native-world-independent-facts",["blender-facts",world/"world.glb","--report",p/"facts.json","--binary",blender])
        cli("native-world-material-sockets",["blender-material-audit",world/"world.glb","--report",p/"materials.json","--binary",blender])
        character=p/"character"
        cli("fresh-native-mannequin",["character","--pose","T","--out",character])
        cli("mannequin-candidate-admission",["character-intake","--source",character/"mannequin.glb","--out",p/"candidate"])
        blend=p/"character.blend"
        cli("candidate-editable-blender",["character-blender","--candidate",p/"candidate","--blend",blend,"--report",p/"character-blender.json","--binary",blender])
        if blend.is_file():
            # Reopen checks the admitted GLB lineage stored on scene/meshes,
            # rather than treating the editable .blend bytes as that identity.
            digest=hashlib.sha256((character/"mannequin.glb").read_bytes()).hexdigest()
            cli("candidate-independent-blend-reopen",["character-reopen","--blend",blend,"--sha256",digest,"--report",p/"character-reopen.json","--binary",blender])
            cli("candidate-material-separation",["character-separate","--blend",blend,"--out",p/"separated.blend","--report",p/"separated.json","--binary",blender])
        rig=p/"rig.blend"
        cli("actual-mannequin-skin-rig",["blender-rig",character,"--blend",rig,"--report",p/"rig.json","--binary",blender,"--skin"])
        if rig.is_file():
            cli("actual-mannequin-pose-audit",["blender-pose-audit",rig,"--report",p/"pose.json","--binary",blender])
            motion=p/"motion.glb"
            cli("actual-deforming-motion-export",["character-motion-export","--blend",rig,"--out",motion,"--report",p/"motion-export.json","--binary",blender])
            if motion.is_file():
                digest=hashlib.sha256(motion.read_bytes()).hexdigest()
                cli("independent-motion-glb-reimport",["character-motion-reimport","--glb",motion,"--sha256",digest,"--report",p/"motion-reimport.json","--binary",blender])
        if (world/"manifest.json").is_file():
            manifest=json.loads((world/"manifest.json").read_text(encoding="utf8"))
            edits={"schema":"mgr.forge.world-edit.v1","asset_sha256":manifest["artifact"]["sha256"],"buildings":[{k:b[k] for k in ("id","center","size","material")} for b in manifest["buildings"]]}
            edits["buildings"][0]["size"][1]+=1
            (p/"edits.json").write_text(json.dumps(edits),encoding="utf8")
            cli("world-edit-source-for-blender",["apply-world-edits","--world",world,"--edits",p/"edits.json","--out",p/"edited"])
            live=p/"live.blend"
            cli("world-individually-editable-blender",["blender-live-scene","--world",p/"edited","--blend",live,"--report",p/"live.json","--binary",blender])
            if live.is_file():
                cli("blender-world-back-to-native-edits",["blender-to-forge","--blend",live,"--original",world,"--out",p/"roundtrip.json","--report",p/"roundtrip-report.json","--binary",blender])
        for file in p.glob("*.json"):
            shutil.copyfile(file,output/file.name)
    result={"schema":"mgr.forge.blender-cli-paths.v1","status":"FAIL" if any(c["status"]=="FAIL" for c in cases) else "PASS_SCOPED_BLENDER_RECEIVERS","cases":cases,
            "limits":["Fresh original fixtures, actual local Blender receivers, no paid/provider calls or repeated Cycles renders","No actual Godot runtime, arbitrary imported rig, likeness, cloth or human art acceptance"],
            "summary":{"cases":len(cases),"commands_executed":len({c['command'][3] for c in cases}),"failures":sum(c['status']=='FAIL' for c in cases)}}
    (output/"matrix.json").write_text(json.dumps(result,indent=2)+'\n',encoding="utf8")
    print(json.dumps(result["summary"],indent=2))
    return int(result["status"]=="FAIL")


def run_matrix(output, *, blender=None, extended=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    cases = []
    tracked=[ROOT / "forge/cli.py",*sorted((ROOT / "forge").glob("*.py")),ROOT / "forge/security/rambler.py"]
    def checkpoints():
        return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    initial_sources=checkpoints()

    def save(path, payload):
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf8")
        return path

    def check(name, assertion, detail):
        cases.append({"case": name, "kind": "artifact_assertion", "status": "PASS" if assertion else "FAIL", "detail": detail})

    def cli(name, args, *, reject=False):
        command = [sys.executable, "-m", "forge.cli", *map(str, args)]
        started = time.monotonic()
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf8", timeout=90)
            passed = result.returncode != 0 if reject else result.returncode == 0
            row = {"case": name, "kind": "cli", "command": command, "exit_code": result.returncode,
                   "expected_rejection": reject, "status": ("EXPECTED_REJECTION" if reject else "PASS") if passed else "FAIL",
                   "seconds": round(time.monotonic()-started, 4), "stdout": result.stdout,
                   "stderr": result.stderr}
            cases.append(row)
            try: return json.loads(result.stdout)
            except json.JSONDecodeError: return {}
        except subprocess.TimeoutExpired:
            cases.append({"case": name, "kind": "cli", "command": command, "status": "FAIL", "reason": "90-second timeout"})
            return {}

    with tempfile.TemporaryDirectory(prefix="mgr-forge-path-matrix-") as temp:
        fixture = Path(temp)
        world = fixture / "world"
        spec = save(fixture / "spec.json", {"seed": 8964, "columns": 3, "rows": 3, "buildings": 4, "name": "MGR Native Path Matrix"})
        cli("world-from-spec", ["build", "--spec", spec, "--out", world])
        if not (world / "manifest.json").is_file():
            raise RuntimeError("world fixture failed; dependent checks cannot execute")
        manifest = json.loads((world / "manifest.json").read_text(encoding="utf8"))
        source_hash = hashlib.sha256((world / "world.glb").read_bytes()).hexdigest()
        cli("world-integrity", ["verify-bundle", world])
        inspected = cli("world-glb-structure", ["inspect", world / "world.glb"])
        check("real-geometry", inspected.get("triangles", 0) > 0, inspected)
        check("world-main-lineage", source_hash == manifest["artifact"]["sha256"], {"sha256": source_hash})
        check("camera-clearance", manifest["cinematic_camera_clearance"]["status"] == "PASS", manifest["cinematic_camera_clearance"])
        check("no-provider-in-world", manifest["execution"]["external_api_calls"] == 0 and not manifest["execution"]["model_inference"], manifest["execution"])
        blob=(world / "world.glb").read_bytes()
        doc=json.loads(blob[20:20+int.from_bytes(blob[12:16],"little")].decode("utf8"))
        check("world-authored-pbr", any(m.get("pbrMetallicRoughness",{}).get("metallicFactor",0)>0 for m in doc["materials"]), {"materials":doc["materials"],"limit":"GLB values only, not rendered material fidelity"})
        cli("glb-obj-parity", ["audit-export", "--glb", world / "world.glb", "--obj", world / "world.obj", "--out", fixture / "parity.json"])
        repeated = fixture / "repeat"
        cli("world-deterministic-repeat", ["build", "--spec", spec, "--out", repeated])
        check("world-byte-repeat", (repeated / "world.glb").read_bytes() == (world / "world.glb").read_bytes(), "same spec and seed produce exact GLB bytes")
        cli("world-prompt-native", ["build", "--prompt", "build 3 houses", "--out", fixture / "prompt"])
        badspec = save(fixture / "bad-spec.json", {"seed": True})
        cli("world-invalid-spec", ["build", "--spec", badspec, "--out", fixture / "bad-world"], reject=True)
        cli("world-zero-buildings", ["build", "--buildings", "0", "--out", fixture / "empty-world"])
        cli("world-zero-integrity", ["verify-bundle", fixture / "empty-world"])
        cli("world-fully-occupied", ["build", "--columns", "2", "--rows", "2", "--buildings", "4", "--out", fixture / "full-world"])
        full=json.loads((fixture / "full-world" / "manifest.json").read_text(encoding="utf8"))
        check("no-invalid-empty-park-glb", full.get("omitted_empty_layers")==["parks"] and not (fixture / "full-world" / "parks.glb").exists(), "empty optional layers omitted; no empty primitive GLB presented as a usable asset")
        cli("world-flight-package", ["world-flight", "--world", world, "--out", fixture / "flight.html"])
        handoff = fixture / "godot"
        result = cli("godot-collision-package", ["godot-handoff", "--world", world, "--out", handoff])
        check("godot-not-fake-runtime", result.get("engine_import_verified") is False and result.get("building_colliders") == 4, result)
        check("godot-visual-corner-witness", result.get("collision_visual_witness",{}).get("status")=="AUTHORED_BOX_CORNERS_VERIFIED", result.get("collision_visual_witness"))
        if (handoff / "world.tscn").is_file():
            scene = (handoff / "world.tscn").read_text(encoding="utf8")
            check("godot-authored-collision-bodies", scene.count('type="StaticBody3D"') == 5, "four buildings and one ground collider; engine import remains unrun")
        shifted=json.loads(json.dumps(manifest))
        shifted["buildings"][0]["center"][0]+=1.25
        save(world / "manifest.json",shifted)
        cli("godot-shifted-collider-manifest", ["godot-handoff","--world",world,"--out",fixture / "bad-godot"], reject=True)
        save(world / "manifest.json",manifest)
        ids = [b["id"] for b in manifest["buildings"]]
        walk = fixture / "walk.json"
        cli("road-collision-rehearsal", ["rehearse-walk", world / "manifest.json", "--from-building", ids[0], "--to-building", ids[-1], "--out", walk])
        if walk.is_file():
            path = json.loads(walk.read_text(encoding="utf8"))
            check("walk-has-positions", len(path["frames"]) > 1 and path["status"] == "PASS_OFFLINE_ROAD_GRAPH", {"frames":len(path["frames"]),"status":path["status"]})
        biome = fixture / "biome"
        cli("native-terrain-layer", ["world-biome", "--world", world, "--out", biome, "--biome", "alien", "--resolution", "12"])
        check("biome-source-unchanged", source_hash == hashlib.sha256((world / "world.glb").read_bytes()).hexdigest(), source_hash)
        if extended:
            from PIL import Image,ImageDraw
            reference=fixture / "reference.png"
            im=Image.new("RGBA",(128,128),(0,0,0,0))
            ImageDraw.Draw(im).rectangle((32,32,95,95),fill=(100,180,230,255))
            im.save(reference)
            mask=fixture / "mask.png"
            im=Image.new("RGB",(128,128),(0,0,0))
            ImageDraw.Draw(im).rectangle((32,32,95,95),fill=(255,255,255))
            im.save(mask)
            cli("image-derived-relief",["image-relief","--image",reference,"--out",fixture / "relief","--grid","8"])
            cli("relief-integrity",["verify-bundle",fixture / "relief"])
            cli("native-creature",["imagine-creature","--prompt","a horned creature with four legs and one tail","--variants","2","--out",fixture / "creature"])
            recipe=save(fixture / "morph.json",{"width":1.1,"bend_degrees":5})
            cli("imported-static-morph",["morph-model","--source",world / "world.glb","--out",fixture / "morphed","--morph",recipe,"--expected-sha256",source_hash])
            cli("native-uv-atlas",["uv-atlas","--source",world / "world.glb","--out",fixture / "uv","--atlas-size","256","--padding","2","--expected-sha256",source_hash])
            cli("mannequin-character",["character","--pose","A","--out",fixture / "character"])
            mannequin=fixture / "character" / "mannequin.glb"
            cli("character-candidate-admit",["character-intake","--source",mannequin,"--out",fixture / "candidate"])
            cli("character-structural-readiness",["character-readiness","--source",mannequin,"--out",fixture / "readiness.json"])
            view=json.loads((fixture / "character" / "character.json").read_text(encoding="utf8"))["asset_view"]
            identity=save(fixture / "identity.json",view)
            cli("same-asset-source-identity",["compare-asset-identity",identity,identity])
            cli("same-raster-pixels",["compare-renders",reference,reference])
            cli("same-raster-silhouette",["compare-views",reference,reference])
            references=save(fixture / "references.json",{"schema":"mgr.forge.reference-input.v1","character":"synthetic-fixture","images":[{"asset":"body","view":"front","file":"reference.png"}]})
            cli("reference-pack-admission",["character-reference-pack","--spec",references,"--out",fixture / "reference-pack.json"])
            proposal=save(fixture / "parts.json",{"schema":"mgr.forge.unclothe.v1","source":"reference.png","parts":[{"id":"coat","kind":"coat","decision":"approved","mask":"mask.png"}]})
            cli("visible-part-review",["unclothe-review","--spec",proposal])
            cli("visible-part-extraction",["unclothe-extract","--spec",proposal,"--out",fixture / "parts"])
            cli("visible-part-proxy",["unclothe-proxy","--parts",fixture / "parts","--out",fixture / "proxies","--grid","8"])
            small=Image.new("RGB",(128,128),(0,0,0))
            ImageDraw.Draw(small).rectangle((32,32,47,47),fill=(255,255,255))
            small.save(fixture / "small-mask.png")
            smallproposal=save(fixture / "small-parts.json",{"schema":"mgr.forge.unclothe.v1","source":"reference.png","parts":[{"id":"coat","kind":"coat","decision":"approved","mask":"small-mask.png"}]})
            cli("small-visible-part-extraction",["unclothe-extract","--spec",smallproposal,"--out",fixture / "small-parts"])
            cli("small-visible-part-proxy",["unclothe-proxy","--parts",fixture / "small-parts","--out",fixture / "small-proxies","--grid","8"])
            reconstruction=save(fixture / "reconstruction.json",{"bounds":{"width":2,"height":2,"depth":2},"grid":16,"views":[{"axis":"front","mask":"mask.png"},{"axis":"left","mask":"mask.png"}]})
            cli("orthographic-reconstruction",["reconstruct-silhouette","--spec",reconstruction,"--out",fixture / "hull"])
            truth=save(fixture / "truth.json",{"boxes":[{"min":[-.5,.5,-.5],"max":[.5,1.5,.5]}]})
            cli("reconstruction-analytic-score",["reconstruct-score","--spec",reconstruction,"--truth",truth,"--out",fixture / "score.json"])
            quad=save(fixture / "quad.json",[[0,0],[127,0],[127,127],[0,127]])
            cli("planar-mask-rectification",["rectify-mask","--image",mask,"--src-quad",quad,"--dst-quad",quad,"--size","128","128","--out",fixture / "rectified.png"])
            edits={"schema":"mgr.forge.world-edit.v1","asset_sha256":source_hash,"buildings":[{k:b[k] for k in ("id","center","size","material")} for b in manifest["buildings"]]}
            edits["buildings"][0]["size"][1]+=1
            changes=save(fixture / "edits.json",edits)
            cli("authored-world-edit-export",["apply-world-edits","--world",world,"--edits",changes,"--out",fixture / "edited"])
            cli("cpu-workflow-pipeline",["pipeline","--buildings","3","--out",fixture / "pipeline"])
        if blender:
            composed=fixture / "composed"
            cli("real-blender-world-composition", ["world-compose", "--world", world, "--biome", biome, "--out", composed, "--blender", blender])
            cli("composed-bundle-integrity", ["verify-bundle",composed])
            for name in ("world-composed-proof.json","world-composed-preview.png","composition-receipt.json"):
                if (composed/name).is_file():shutil.copyfile(composed/name,output/name)
        for kind in ("portal", "spell-orbit", "aura"):
            fxout = fixture / kind
            cli("fx-"+kind, ["fantasy-effect", "--kind", kind, "--phase", "0.35", "--particles", "12", "--out", fxout])
            if (fxout / "effect.glb").is_file():
                blob = (fxout / "effect.glb").read_bytes()
                size = int.from_bytes(blob[12:16], "little")
                doc = json.loads(blob[20:20+size].decode("utf8"))
                check("fx-emissive-"+kind, any("emissiveFactor" in m for m in doc.get("materials", [])), {"materials": doc.get("materials", [])})
        cli("fx-invalid-radius", ["fantasy-effect", "--radius", "nan", "--out", fixture / "bad-fx"], reject=True)
        layers = save(fixture / "layers.json", {"layers":[{"id":"base", "objects":{"/world/rock":{"kind":"mesh", "material":"stone"}}},{"id":"art", "objects":{"/world/rock":{"material":"moss"}}}]})
        sceneout = fixture / "scene.json"
        cli("layer-composition", ["compose-scene", "--layers", layers, "--out", sceneout])
        if sceneout.is_file():
            composed = json.loads(sceneout.read_text(encoding="utf8"))
            check("layer-field-provenance", composed["field_sources"]["/world/rock"] == {"kind":"base", "material":"art"}, composed)
        cli("composition-overwrite", ["compose-scene", "--layers", layers, "--out", sceneout], reject=True)
        cli("spatial-math-contract", ["spatial-proof", "--out", fixture / "spatial.json"])
        cli("studio-quality-contracts", ["studio-proof", "--out", fixture / "studio.json"])
        cli("asset-source-index", ["asset-sources", "--query", "Kenney"])
        cli("asset-cache-empty", ["asset-search", "--catalog", fixture / "catalog", "--query", "dragon"])
        save(fixture / "catalog" / "catalog.json", {"schema":"mgr.forge.asset-catalog.v1", "items":{"3dassets:fixture-dragon":{"id":"3dassets:fixture-dragon","provider_id":"3dassets","title":"Synthetic cache fixture dragon","tags":["dragon"],"category":"creatures","license":"cc0-1.0","cdn_url":"https://example.invalid/fixture.glb"}}})
        cached=cli("asset-cache-persisted-search", ["asset-search", "--catalog", fixture / "catalog", "--query", "dragon"])
        check("cached-metadata-read", cached.get("count")==1 and cached.get("assets_downloaded")==0, "synthetic fixture metadata only; no asset or upstream rights acceptance")
        cli("asset-acquire-unknown-no-network", ["asset-acquire", "--catalog", fixture / "catalog", "--slug", "not-discovered", "--store", fixture / "store"], reject=True)
        engines = cli("model-engine-status", ["model-engines"])
        check("native-only-engine-readiness", all(not e["runtime_ready"] for e in engines.get("engines", []) if e["id"] != "mgr-native-imagination"), {"ready":engines.get("ready")})
        jobs = save(fixture / "jobs.json", [{"id":"cpu-study", "seconds":60, "min_vram_gb":24}])
        cost = fixture / "gpu-plan.json"
        cli("gpu-unpriced-dry-run", ["gpu-plan", "--jobs", jobs, "--out", cost])
        if cost.is_file():
            plan = json.loads(cost.read_text(encoding="utf8"))
            check("no-rental-without-prices", plan["status"] == "UNPRICED" and not plan["provider_called"] and not plan["rental_started"], plan)
        cells = fixture / "cells"
        cells.mkdir()
        shutil.copyfile(world / "world.glb", cells / "world.glb")
        cellmeta = save(fixture / "cells.json", {"world":{"sha256":source_hash, "bytes":(cells / "world.glb").stat().st_size}})
        cellplan = save(fixture / "cell-plan.json", {"status":"PLAN_ONLY", "active":["world"], "prefetch":[], "evict":[]})
        cli("cell-real-glb-load", ["load-cells", "--root", cells, "--manifest", cellmeta, "--plan", cellplan, "--out", fixture / "loaded.json"])
        (cells / "world.glb").write_bytes(b"tampered")
        cli("cell-tamper", ["load-cells", "--root", cells, "--manifest", cellmeta, "--plan", cellplan, "--out", fixture / "corrupt.json"], reject=True)
        release = fixture / "release"
        release.mkdir()
        (release / "app.txt").write_text("MGR-owned fixture", encoding="utf8")
        files = save(fixture / "release-files.json", ["app.txt"])
        roster = fixture / "release-roster.json"
        cli("release-seal", ["rambler-seal", "--root", release, "--files-json", files, "--out", roster])
        cli("release-internal-roster-destination", ["rambler-seal", "--root", release, "--files-json", files, "--out", release / "roster.json"], reject=True)
        cli("release-byte-verify", ["rambler-verify", "--root", release, "--manifest", roster])
        (release / "unlisted.txt").write_text("unlisted", encoding="utf8")
        cli("release-unlisted-file", ["rambler-verify", "--root", release, "--manifest", roster], reject=True)
        (release / "unlisted.txt").unlink()
        (release / "app.txt").write_text("changed", encoding="utf8")
        cli("release-tamper", ["rambler-verify", "--root", release, "--manifest", roster], reject=True)
        inconsistent=fixture / "inconsistent-bundle"
        inconsistent.mkdir()
        (inconsistent / "side.txt").write_bytes(b"safe")
        save(inconsistent / "manifest.json", {"artifact":{"path":"missing.glb","sha256":"0"*64,"bytes":20},"artifact_inventory":{"side.txt":{"sha256":hashlib.sha256(b"safe").hexdigest(),"bytes":4}}})
        cli("bundle-missing-declared-primary", ["verify-bundle", inconsistent], reject=True)
        source_manifest=json.loads((world / "manifest.json").read_text(encoding="utf8"))
        del source_manifest["artifact_inventory"]["parks.json"]
        save(world / "manifest.json",source_manifest)
        cli("bundle-declared-sidecar-omitted", ["verify-bundle",world], reject=True)
        save(world / "manifest.json",manifest)
        (world / "parks.json").write_text("tampered", encoding="utf8")
        cli("world-sidecar-tamper", ["verify-bundle", world], reject=True)

    tree = ast.parse((ROOT / "forge/cli.py").read_text(encoding="utf8"))
    commands = sorted({node.args[0].value for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_parser" and node.args and isinstance(node.args[0], ast.Constant)})
    exercised = {row["command"][3] for row in cases if row["kind"] == "cli"}
    coverage = [{"command": c, "state":"EXECUTED_SCOPED_FIXTURE" if c in exercised else "NOT_RUN_IN_THIS_OFFLINE_MATRIX", "reason": "Actual subprocess fixture receipts present" if c in exercised else "Excluded from this bounded CPU matrix; requires separate specific fixture/runtime/source qualification, not assumed unavailable", "limit":"See named receipts; command execution does not qualify all parameter branches or clients."} for c in commands]
    result = {"schema":"mgr.forge.offline-path-matrix.v1", "status":"FAIL" if any(c["status"] == "FAIL" for c in cases) else "PASS_SCOPED_OFFLINE",
              "cases":cases, "cli_coverage":coverage, "summary":{"cli_declared":len(commands),"cli_exercised":len(exercised),"cases":len(cases),"failures":sum(c["status"] == "FAIL" for c in cases)},
              "blender_requested":str(blender) if blender else None,
              "extended_cpu_cases_requested":extended,
              "limits":["Fresh disposable fixtures only; no model weights, generation APIs, purchases or network workflows.","Only the explicit composition case uses independent Blender when --blender is supplied. Godot runtime, browser interaction and mobile remain outside this matrix.","Unrun commands remain unassessed, not failures or successes. Existing separate receipts require current source reconciliation."]}
    save(output / "matrix.json", result)
    final_sources=checkpoints()
    save(output / "source-checkpoints.json", {"before":initial_sources,"after":final_sources,
         "changed_during_run":[path for path in initial_sources if initial_sources[path]!=final_sources[path]],
         "scope":"Per-run source snapshots; changed source requires scoped reconciliation, not assumed current acceptance"})
    print(json.dumps(result["summary"], indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--blender",type=Path,help="optional actual installed Blender binary for two-process city/biome composition and render")
    parser.add_argument("--extended",action="store_true",help="also exercise original image/reference/character/morph/reconstruction/edit/pipeline CPU paths")
    parser.add_argument("--blender-inspections-only",action="store_true",help="with --blender, qualify actual independent import/material/rig/edit receivers without rerunning renders")
    parser.add_argument('--remaining-blender-only',action='store_true',help='with --blender, qualify render/FX/human/creature CLI receivers once')
    args=parser.parse_args()
    if args.remaining_blender_only:
        if not args.blender:parser.error('--remaining-blender-only requires --blender')
        raise SystemExit(run_remaining_blender(args.out,args.blender))
    if args.blender_inspections_only:
        if not args.blender:parser.error('--blender-inspections-only requires --blender')
        raise SystemExit(run_blender_inspections(args.out,args.blender))
    raise SystemExit(run_matrix(args.out,blender=args.blender,extended=args.extended))
