"""MGR wardrobe part taxonomy and source/skin separation gate."""


GARMENTS={"shirt":"torso", "coat":"torso", "left_pant_leg":"left_leg",
          "right_pant_leg":"right_leg", "left_boot":"left_leg", "right_boot":"right_leg",
          "left_elbow_sleeve":"left_upper_arm", "right_elbow_sleeve":"right_upper_arm"}
ACCESSORIES={"chain":"torso"}
BODY={"head","torso","left_upper_arm","right_upper_arm","left_forearm",
      "right_forearm","left_hand","right_hand","left_leg","right_leg","hair"}


def wardrobe_inventory(character_manifest, rig_receipt=None):
    """Separate physical wardrobe pieces from the anonymous body mesh.

    This verifies independent GLB parts and bone assignment *metadata* only.
    It does not prove garment fit, clipping, physics or texture quality.
    """
    parts=character_manifest.get("editable_parts")
    if not isinstance(parts,list) or len(parts)!=len(set(parts)):
        raise ValueError("unique editable part names required")
    present=set(parts)
    errors=[]
    for name in (*GARMENTS,*ACCESSORIES,*BODY):
        if name not in present:
            errors.append(f"missing independently editable part: {name}")
    for item in present-(set(GARMENTS)|set(ACCESSORIES)|BODY):
        errors.append(f"unknown wardrobe/body part: {item}")
    if rig_receipt is not None:
        assignments=rig_receipt.get("attachments",{})
        for name,bone in {**GARMENTS,**ACCESSORIES}.items():
            if assignments.get(name)!=bone:
                errors.append(f"wrong garment bone attachment: {name}")
    return {"schema":"mgr.forge.wardrobe-inventory.v1",
            "status":"PASS" if not errors else "FAIL", "errors":errors,
            "detachable_garments":sorted(present & set(GARMENTS)),
            "detachable_accessories":sorted(present & set(ACCESSORIES)),
            "body_components":sorted(present & BODY),
            "checks":["detachable mesh manifest", "unique part IDs", "garment bone mapping"],
            "limitations":["rigid 1.0 skin weights, no cloth simulation",
                           "no physical fit or self-intersection proof",
                           "generic anonymous mannequin, not Tevin"]}
