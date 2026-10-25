"""Blender CPU render witness for MGR studio materials, lights, curves and volume.

This is an original controlled scene fixture. Not a production character,
animated hair simulation, measured BSDF, game runtime or 10-system acceptance.
"""

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def principled(name,color,metallic,roughness,subsurface=0):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value=(*color,1)
    shader.inputs["Metallic"].default_value=metallic
    shader.inputs["Roughness"].default_value=roughness
    if subsurface:
        shader.inputs["Subsurface Weight"].default_value=subsurface
    return mat


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:
        raise ValueError("expected unique output.blend image.png report.json")
    blend,image,report=map(Path,args)
    for target in (blend,image,report):
        if target.exists():
            raise FileExistsError("studio witness outputs must be new")
        target.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=12
    scene.render.resolution_x=420
    scene.render.resolution_y=280
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(image.resolve())
    scene.world=bpy.data.worlds.new("MGR_Studio_World")
    scene.world.use_nodes=True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.03,.04,.08,1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.24

    specs=(
        ("MGR_Material_Skin_Witness",(-1.7,0,.85),(.52,.22,.13),0.0,.42,.12),
        ("MGR_Material_Metal_Witness",(0,0,.85),(.64,.7,.8),.95,.21,0),
        ("MGR_Material_Wax_Witness",(1.7,0,.85),(.85,.47,.27),0,.35,.24),
    )
    authored=[]
    for name,position,color,metallic,roughness,sss in specs:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.72,location=position)
        sphere=bpy.context.object
        sphere.name=name
        bpy.ops.object.shade_smooth()
        mat=principled(name+"_Shader",color,metallic,roughness,sss)
        sphere.data.materials.append(mat)
        authored.append({"object":name,"material":mat.name,"metallic":metallic,
                         "roughness":roughness,"subsurface_weight":sss})

    floor=principled("MGR_Floor_Matte",(.065,.07,.10),.0,.82)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.13))
    ground=bpy.context.object
    ground.name="MGR_Studio_Floor"
    ground.scale=(5.2,3.2,.16)
    ground.data.materials.append(floor)

    # Geometry witness: a controllable hair strand, NOT a hair physics solver.
    curve=bpy.data.curves.new("MGR_Hair_Stroke_Path","CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=.035
    curve.bevel_resolution=3
    strand=curve.splines.new("POLY")
    strand.points.add(5)
    for point,xyz in zip(strand.points,((-1.8,0,1.49),(-1.96,0,1.76),(-1.84,0,1.98),(-1.67,0,2.11),(-1.56,0,2.24),(-1.45,0,2.31))):
        point.co=(*xyz,1)
    hair=bpy.data.objects.new("MGR_Hair_Strand_Witness",curve)
    scene.collection.objects.link(hair)
    hair.data.materials.append(principled("MGR_Hair_Black",(.018,.012,.008),0,.39))

    lights=[]
    for name,color,energy,position in (
        ("MGR_Light_Key",(.65,.82,1),550,(-2.5,-3.2,4.0)),
        ("MGR_Light_Rim",(1,.35,.12),380,(2.5,1.1,3.2)),
    ):
        data=bpy.data.lights.new(name,"POINT")
        data.energy=energy
        data.color=color
        obj=bpy.data.objects.new(name,data)
        scene.collection.objects.link(obj)
        obj.location=position
        lights.append({"name":name,"energy":energy})

    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1))
    volume=bpy.context.object
    volume.name="MGR_Atmosphere_Reference"
    volume.scale=(3.6,2.2,2.0)
    material=bpy.data.materials.new("MGR_Atmosphere_Low_Density")
    material.use_nodes=True
    nodes=material.node_tree.nodes
    nodes.clear()
    output=nodes.new("ShaderNodeOutputMaterial")
    medium=nodes.new("ShaderNodeVolumePrincipled")
    medium.inputs["Density"].default_value=.009
    medium.inputs["Color"].default_value=(.25,.42,.8,1)
    material.node_tree.links.new(medium.outputs["Volume"],output.inputs["Volume"])
    volume.data.materials.append(material)

    camera_data=bpy.data.cameras.new("MGR_Studio_Camera")
    camera=bpy.data.objects.new("MGR_Studio_Camera",camera_data)
    scene.collection.objects.link(camera)
    camera.location=Vector((0,-9,4))
    camera.rotation_euler=(Vector((0,0,.85))-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=camera
    camera_data.type="PERSP"
    camera_data.lens=42
    scene.render.film_transparent=False
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
    bpy.ops.render.render(write_still=True)
    receipt={"schema":"mgr.forge.studio-blender-witness.v1","status":"PASS",
             "blender_version":bpy.app.version_string,"renderer":"CYCLES",
             "device":"CPU","samples":scene.cycles.samples,
             "image_resolution":[420,280],"materials":authored,
             "point_lights":lights,"hair_curve_points":len(strand.points),
             "atmosphere_density":.009,"camera_type":"PERSP",
             "blend":str(blend.resolve()),"image":str(image.resolve()),
             "limitations":["controlled 3-material/2-light render only; not photometric/material fit",
                            "hair stroke is static curve geometry, not dynamics or groom",
                            "uniform low-density medium is not animated fluid or fog simulation",
                            "not Tevin or an approved photoreal human"]}
    report.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","report":str(report.resolve()),"image":str(image.resolve())}))


if __name__=="__main__":
    main()
