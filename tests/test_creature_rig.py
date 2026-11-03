import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from forge.imagination import create_original_creature
from forge.creature_rig import rig_creature
from forge.creature_rig_recipe import creature_bones


class CreatureRigLocalTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"dna-creature"
        create_original_creature("invent a winged dragon with a flexible tail",
                                 self.source,seed=11,variants=3)
        self.destination=self.root/"rigged"

    def test_missing_blender_fails_without_partial_output(self):
        with self.assertRaisesRegex(RuntimeError,"Blender"):
            rig_creature(self.source,self.destination,blender="nonexistent-blender-executable")
        self.assertFalse(self.destination.exists())

    def test_wrong_input_fails_before_side_effects(self):
        with self.assertRaises(ValueError):
            rig_creature(self.root/"missing",self.destination)
        self.assertFalse(self.destination.exists())

    def test_existing_output_protected(self):
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            rig_creature(self.source,self.destination)
        self.assertTrue(self.destination.is_dir())

    def test_zero_exit_with_error_output_fails_closed(self):
        class Proc:
            returncode=0
            stdout="Traceback (most recent call last)"
            stderr=""
        with patch("forge.creature_rig.shutil.which",return_value="blender"),patch(
                "forge.creature_rig.subprocess.run",return_value=Proc()):
            with self.assertRaisesRegex(RuntimeError,"reported an error"):
                rig_creature(self.source,self.destination)

    def test_exporter_motion_cannot_substitute_for_receiver_deformation_proof(self):
        manifest=json.loads((self.source/'creature.json').read_text())
        recipe=creature_bones(manifest['selected_genome'],morph=manifest['applied_morph'],
                              axis_extent=manifest['morph_axis_extent'])
        raw=(self.source/'creature.glb').read_bytes()
        # A completed export and receiving import are still insufficient if the
        # imported skin never independently demonstrated animated deformation.
        proof={'status':'LOCAL_BLENDER_REIMPORT_AND_RENDER_PASS',
               'mesh_source_sha256':manifest['artifact']['sha256'],
               'reimported_armature_bones':recipe['bones'], 'reimported_animation_actions':1,
               'max_evaluated_vertex_motion_m':1., 'rigged_glb_sha256':hashlib.sha256(raw).hexdigest(),
               'vertices':123, 'receiver_evaluated_vertices':123,
               'receiver_evaluated_deformation_verified':True,
               'receiver_evaluated_frames':[1,16], 'receiver_max_vertex_motion_m':0.,
               'receiver_moving_vertices':0}
        def witness(binary,script,args,timeout):
            if script=='blender_creature_skin.py':
                self.destination.mkdir()
                (self.destination/'creature-rigged.glb').write_bytes(raw)
                (self.destination/'skin-proof.json').write_text(json.dumps(proof))
                return 'MGR_CREATURE_SKIN='
            return 'MGR_CREATURE_REOPEN='
        with patch('forge.creature_rig.shutil.which',return_value='blender'),patch(
                'forge.creature_rig._run_blender',side_effect=witness):
            with self.assertRaisesRegex(RuntimeError,'receiving-import or animation'):
                rig_creature(self.source,self.destination)
        self.assertTrue((self.destination/'skin-proof.json').is_file())
