"""Independent Blender process validates exported skinned GLB and renders preview."""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def main():
    if "--" not in sys.argv:
        raise ValueError("output dir argument required")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=1:
        raise ValueError("output dir argument required")
    # Blender interprets relative render paths against its own base path,
    # which can be the drive root even while Python reads from the caller cwd.
    root=Path(args[0]).resolve()
    proof=json.loads((root/"skin-proof.json").read_text(encoding="utf-8"))
    target=root/"creature-rigged.glb"
    if hashlib.sha256(target.read_bytes()).hexdigest()!=proof["rigged_glb_sha256"]:
        raise ValueError("exported rigged GLB hash changed")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(target.resolve()))
    rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
    meshes=[o for o in bpy.data.objects if o.type=="MESH"]
    if len(rigs)<1 or len(meshes)<1 or len(bpy.data.actions)<1:
        raise RuntimeError("receiving Blender lost skeleton, mesh or animation")
    rig=rigs[0]
    if len(rig.data.bones)!=proof["bones"]:
        raise RuntimeError("receiving rig bone count changed")
    skinned=[o for o in meshes if any(m.type=="ARMATURE" for m in o.modifiers)]
    # Blender may import glTF rig custom-shape helpers (e.g. Icosphere),
    # so choosing meshes[0] is incorrect. Require exactly one skinned mesh.
    if len(skinned)!=1:
        raise RuntimeError("receiving GLB missing unique deforming skinned mesh")
    mesh=skinned[0]
    # The exporting process moving vertices does not prove an exported skin and
    # animation still deform after import. Evaluate the receiving dependency
    # graph at both authored witness frames and record its own measurements.
    def evaluated_positions(frame):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        received=evaluated.to_mesh()
        try:
            return [evaluated.matrix_world@vertex.co for vertex in received.vertices]
        finally:
            evaluated.to_mesh_clear()
    first,last=evaluated_positions(1),evaluated_positions(16)
    # glTF may split vertices at material/normal seams during export, so the
    # receiver compares its own stable vertex order across frames.
    if not first or len(first)!=len(last) or len(first)!=len(mesh.data.vertices):
        raise RuntimeError('receiving deformation changed imported vertex correspondence')
    displacement=[(a-b).length for a,b in zip(first,last)]
    if any(not math.isfinite(value) for value in displacement) or max(displacement)<.01:
        raise RuntimeError('receiving skin/animation failed to deform imported vertices')
    receiver_motion=max(displacement)
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    for helper in meshes:
        if helper is not mesh:
            helper.hide_render=True
    bounds=[mesh.matrix_world@Vector(corner) for corner in mesh.bound_box]
    center=sum(bounds,Vector((0,0,0)))/len(bounds)
    radius=max((max(p[i] for p in bounds)-min(p[i] for p in bounds)) for i in range(3))
    camera_data=bpy.data.cameras.new("MGR_Creature_Proof_Camera")
    camera=bpy.data.objects.new("MGR_Creature_Proof_Camera",camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location=center+Vector((radius*1.4,-radius*2.1,radius*0.9))
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO"
    camera.data.ortho_scale=radius*2.0
    scene=bpy.context.scene
    scene.camera=camera
    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_x=768
    scene.render.resolution_y=768
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    image=root/"creature-rigged-preview.png"
    scene.render.filepath=str(image)
    bpy.ops.render.render(write_still=True)
    if image.stat().st_size<2000:
        raise RuntimeError("rigged creature preview missing")
    proof.update({"status":"LOCAL_BLENDER_REIMPORT_AND_RENDER_PASS",
                  "reopened_in_second_process":True,
                  "reimported_armature_bones":len(rig.data.bones),
                  "reimported_animation_actions":len(bpy.data.actions),
                  "receiver_evaluated_deformation_verified":True,
                  "receiver_evaluated_frames":[1,16],
                  "receiver_evaluated_vertices":len(first),
                  "receiver_mesh_vertices":len(mesh.data.vertices),
                  "receiver_max_vertex_motion_m":round(receiver_motion,5),
                  "receiver_moving_vertices":sum(value>1e-6 for value in displacement),
                  "preview_png_sha256":hashlib.sha256(image.read_bytes()).hexdigest(),
                  "owner_visual_acceptance":False})
    (root/"skin-proof.json").write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n",
                                        encoding="utf-8")
    print("MGR_CREATURE_REOPEN="+json.dumps(proof))


if __name__=="__main__":
    main()
