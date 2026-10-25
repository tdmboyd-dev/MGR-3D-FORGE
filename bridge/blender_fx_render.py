"""Render MGR-authored emissive effect GLB on dark background using CPU Cycles."""

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:
        raise ValueError("expected effect.glb output.png report.json")
    source,image,report=map(Path,args)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    objects=[obj for obj in bpy.data.objects if obj.type=="MESH"]
    if not objects:
        raise ValueError("no effect geometry")
    verts=[o.matrix_world @ Vector(corner) for o in objects for corner in o.bound_box]
    minimum=Vector(tuple(min(v[i] for v in verts) for i in range(3)))
    maximum=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
    center=(minimum+maximum)/2
    span=max(maximum-minimum)
    cam_data=bpy.data.cameras.new("MGR_FX_Camera")
    camera=bpy.data.objects.new("MGR_FX_Camera",cam_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location=center+Vector((span*.1,-span*2,span*.3))
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    cam_data.type="ORTHO"
    cam_data.ortho_scale=span*1.6
    scene=bpy.context.scene
    scene.camera=camera
    scene.world=bpy.data.worlds.new("MGR_FX_Dark_Stage")
    scene.world.use_nodes=True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.007,.009,.02,1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.15
    # MGR Light Sculptor: real authored lights, distinct from emissive material
    # shader color. Warm/cool lights deliberately illuminate a matte witness.
    for label,color,energy,offset in (
        ("MGR_FX_Cool_Light",(.10,.65,1.0),600,(-span*.5,-span*.3,span*.5)),
        ("MGR_FX_Warm_Light",(1.0,.24,.05),380,(span*.5,-span*.4,-span*.2)),
    ):
        lamp_data=bpy.data.lights.new(label,"POINT")
        lamp_data.energy=energy
        lamp_data.color=color
        lamp_data.shadow_soft_size=max(.1,span*.1)
        lamp=bpy.data.objects.new(label,lamp_data)
        scene.collection.objects.link(lamp)
        lamp.location=center+Vector(offset)
    # A physical witness mesh makes light interaction testable; there is no
    # attempt to misrepresent the GLB's self-emission as lighting other assets.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(center.x+span*.65,center.y-span*.22,center.z-span*.38))
    witness=bpy.context.object
    witness.name="MGR_FX_Light_Witness"
    witness.scale=(span*.13,span*.13,span*.13)
    witness_material=bpy.data.materials.new("MGR_FX_Matte_Witness")
    witness_material.diffuse_color=(.22,.22,.22,1)
    witness.data.materials.append(witness_material)
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=8
    scene.render.resolution_x=600
    scene.render.resolution_y=600
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.view_settings.view_transform="Standard"
    # Blender 5.2 compositor glare is a node-based, optional optical effect;
    # it is not equivalent to physically simulated atmosphere or volumes.
    comp=bpy.data.node_groups.new("MGR_FX_Optical_Glow", "CompositorNodeTree")
    scene.compositing_node_group=comp
    render_layers=comp.nodes.new("CompositorNodeRLayers")
    glare=comp.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value="Fog Glow"
    composite=comp.nodes.new("CompositorNodeComposite")
    comp.links.new(render_layers.outputs["Image"],glare.inputs["Image"])
    comp.links.new(glare.outputs["Image"],composite.inputs["Image"])
    scene.render.film_transparent=False
    image.parent.mkdir(parents=True,exist_ok=True)
    report.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(image.resolve())
    bpy.ops.render.render(write_still=True)
    emissive=[]
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type=="BSDF_PRINCIPLED":
                        socket=node.inputs.get("Emission Color")
                        if socket:
                            emissive.append(list(socket.default_value))
    result={"schema":"mgr.forge.fx-blender-render.v2","blender_version":bpy.app.version_string,
            "status":"PASS" if image.exists() and image.stat().st_size>0 else "FAIL",
            "source":source.name,"mesh_count":len(objects),
            "emission_socket_colors":emissive,"camera":"MGR_FX_Camera",
            "render_engine":"CYCLES","render_device":"CPU",
            "point_light_count":2,"light_witness":witness.name,
            "compositor_glare":glare.inputs["Type"].default_value,
            "image_bytes":image.stat().st_size if image.exists() else 0,
            "limitations":["basic emissive geometry, not physically simulated effects",
                           "optical glare is not physical volume scattering",
                           "no collision-driven particles or fluid simulation"]}
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if result["status"]!="PASS":
        raise RuntimeError("FX render failed")
    print("MGR_FANTASY_RENDER_PASS")


if __name__=="__main__":
    main()
