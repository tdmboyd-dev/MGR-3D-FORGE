"""Independent real Godot import, geometry correspondence and physics witness."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from forge.cli import build
from forge.engine_handoff import export_godot_project
from forge.spec import WorldSpec


WITNESS = '''extends SceneTree

func _initialize() -> void:
    call_deferred("observe")

func refuse(reason: String) -> void:
    push_error("MGR_GODOT_REFUSE: " + reason)
    quit(1)

func point(v: Array) -> Vector3:
    return Vector3(float(v[0]), float(v[1]), float(v[2]))

func observe() -> void:
    var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://qa-expectation.json"))
    var packed := load("res://world.tscn") as PackedScene
    if packed == null or FileAccess.get_sha256("res://assets/world.glb") != expected.sha256:
        refuse("original scene or GLB unavailable")
        return
    var world := packed.instantiate() as Node3D
    root.add_child(world)
    var visual := world.get_node("Visual")
    var vertices: Array[Vector3] = []
    var triangles := 0
    var surfaces := 0
    var mesh_nodes := visual.find_children("*", "MeshInstance3D", true, false)
    if visual is MeshInstance3D:
        mesh_nodes.push_back(visual)
    for node in mesh_nodes:
        var instance := node as MeshInstance3D
        for s in instance.mesh.get_surface_count():
            var arrays := instance.mesh.surface_get_arrays(s)
            var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
            for p in positions:
                vertices.push_back(instance.global_transform * p)
            var indices = arrays[Mesh.ARRAY_INDEX]
            triangles += int((positions.size() if indices == null or indices.is_empty() else indices.size()) / 3.0)
            surfaces += 1
    if triangles != int(expected.triangles) or surfaces < 1 or not world.get_node("PreviewCamera").current:
        refuse("received mesh triangle count or scene camera changed")
        return
    var corner_error := 0.0
    for row in expected.visual_corners:
        var p := point(row)
        var nearest := INF
        for actual in vertices:
            nearest = minf(nearest, p.distance_to(actual))
        corner_error = maxf(corner_error, nearest)
    if corner_error > 0.002:
        refuse("received world vertices no longer match authored collider corners")
        return
    await physics_frame
    await physics_frame
    var rays: Array = []
    for row in expected.rays:
        var at := point(row.point)
        var query := PhysicsRayQueryParameters3D.create(at + Vector3(0, 120, 0), at - Vector3(0, 2, 0))
        var hit := world.get_world_3d().direct_space_state.intersect_ray(query)
        if hit.is_empty() or str(hit.collider.name) != row.body or absf(hit.position.y - at.y) > 0.002:
            refuse("runtime physics did not hit the authored " + row.body)
            return
        rays.push_back({"body":str(hit.collider.name), "surface_y":hit.position.y})
    var drop := RigidBody3D.new()
    drop.position = point(expected.rays.back().point) + Vector3(0, 3, 0)
    var collision := CollisionShape3D.new()
    var sphere := SphereShape3D.new()
    sphere.radius = 0.3
    collision.shape = sphere
    drop.add_child(collision)
    world.add_child(drop)
    for frame in 120:
        await physics_frame
    if absf(drop.global_position.y - 0.3) > 0.05:
        refuse("dynamic sphere did not settle on ground collider")
        return
    print("MGR_GODOT_WITNESS=" + JSON.stringify({"status":"PASS", "engine":Engine.get_version_info().string,
        "glb_sha256":expected.sha256, "mesh_instances":mesh_nodes.size(), "surfaces":surfaces,
        "triangles":triangles, "world_vertices":vertices.size(), "visual_corner_count":expected.visual_corners.size(),
        "max_visual_corner_error_m":corner_error, "physics_rays":rays, "settled_sphere_y_m":drop.global_position.y,
        "headless":true, "rendered_art":false}))
    quit(0)
'''


def check(engine, out):
    engine, out = Path(engine).resolve(strict=True), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    with TemporaryDirectory(prefix='mgr-godot-runtime-') as temporary:
        tmp = Path(temporary)
        for count in (0, 5):
            world, project = tmp/f'world-{count}', tmp/f'engine-{count}'
            manifest = build(WorldSpec(seed=34, columns=4, rows=3, buildings=count), world)
            manifest = json.loads((world/'manifest.json').read_text(encoding='utf8'))
            handoff = export_godot_project(world, project)
            width, depth = (manifest['grounds'][axis] for axis in ('width','depth'))
            corners = [[x,-.55,z] for x in (-width/2,width/2) for z in (-depth/2,depth/2)]
            rays = []
            for i, row in enumerate(manifest['buildings']):
                x, y, z = row['center']; w, h, d = row['size']
                corners.extend([[a,b,c] for a in (x-w/2,x+w/2) for b in (y,y+h) for c in (z-d/2,z+d/2)])
                rays.append({'body':f'BuildingCollider_{i:03d}','point':[x,y+h,z]})
            rays.append({'body':'GroundCollider','point':[width/2-1,0,depth/2-1]})
            (project/'qa-expectation.json').write_text(json.dumps({'sha256':handoff['source_glb_sha256'],
                'triangles':handoff['triangles'],'visual_corners':corners,'rays':rays}), encoding='utf8')
            (project/'qa-observe.gd').write_text(WITNESS, encoding='utf8')
            for phase, args in [('import',['--import']),('physics',['--script','res://qa-observe.gd'])]:
                execution = subprocess.run([str(engine),'--headless','--path',str(project),
                    '--log-file',str(tmp/f'engine-{count}-{phase}.log'),*args],
                    capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                log = execution.stdout + '\n' + execution.stderr
                (out/f'{count}-buildings-{phase}.txt').write_text(log, encoding='utf8')
                if execution.returncode or 'ERROR:' in log:
                    raise RuntimeError(f'Godot {phase} failed; inspect {out}')
                if phase=='physics':
                    matches=[json.loads(line.partition('=')[2]) for line in log.splitlines() if line.startswith('MGR_GODOT_WITNESS=')]
                    if len(matches)!=1 or matches[0]['status']!='PASS':raise RuntimeError('No independent Godot witness')
                    rows.append({**matches[0],'building_count':count})
    result={'schema':'mgr.forge.godot-runtime-proof.v1','status':'PASS','engine_sha256':hashlib.sha256(engine.read_bytes()).hexdigest(),
            'fixtures':rows,'limits':'Actual local headless project import, scene geometry and basic physics. No desktop render, game controls, export templates or production acceptance.'}
    (out/'godot-runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('MGR_GODOT_RUNTIME_PASS',out/'godot-runtime.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--engine',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();check(args.engine,args.out)
