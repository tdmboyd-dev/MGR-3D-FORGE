"""Timed voice cue and Human Forge source-backed 3D lip-sync tests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.lipsync import create_lipsync_timeline, _validate, PHONEMES, CHANNELS
from forge.human_lipsync import build_human_lipsync

SPEC={"schema":"mgr.forge.phoneme-timeline.v1","actor_id":"mgr-proxy-human",
      "language":"en-US","duration_ms":900,
      "phonemes":[{"phoneme":"M","start_ms":0,"end_ms":170},
                  {"phoneme":"AA","start_ms":170,"end_ms":450},
                  {"phoneme":"TH","start_ms":450,"end_ms":610},
                  {"phoneme":"OW","start_ms":610,"end_ms":900}]}

class LipSyncTests(unittest.TestCase):
    def test_real_timed_viseme_weights_are_bounded_and_different(self):
        with TemporaryDirectory() as t:
            target=Path(t)/"timeline"
            one=create_lipsync_timeline(SPEC,target)
            self.assertEqual(one["status"],"EXPLICIT_PHONEME_TIMING_NO_AUDIO_ALIGNMENT")
            self.assertEqual(set(one["channels"]),set(CHANNELS))
            self.assertFalse(one["automatic_audio_alignment_verified"])
            values={k:max(frame["weights"][k] for frame in one["frames"]) for k in CHANNELS}
            for key in ("jawOpen","lipsPress","tongueOut","mouthFunnel"):
                self.assertGreater(values[key],0.12)
            self.assertTrue(all(0<=value<=1 for frame in one["frames"] for value in frame["weights"].values()))
            self.assertTrue((target/"lipsync.json").is_file())
            with self.assertRaises(FileExistsError):
                create_lipsync_timeline(SPEC,target)

    def test_invalid_timing_or_unsupported_phonemes_refused(self):
        cases=[
          {**SPEC,"duration_ms":1},
          {**SPEC,"language":"unknown"},
          {**SPEC,"phonemes":[{"phoneme":"DELETE","start_ms":0,"end_ms":70}]},
          {**SPEC,"phonemes":[{"phoneme":"M","start_ms":300,"end_ms":200}]},
          {**SPEC,"phonemes":[{"phoneme":"M","start_ms":10,"end_ms":250},
                              {"phoneme":"AA","start_ms":200,"end_ms":650}]},
          {**SPEC,"actor_id":"invalid/../../"},
        ]
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):
                _validate(case)

    def test_no_faked_blender_when_binary_missing(self):
        with TemporaryDirectory() as t:
            dest=Path(t)/"output"
            with patch("forge.human_lipsync.shutil.which",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Blender"):
                    build_human_lipsync(SPEC,dest,blender="not-installed")
            self.assertFalse(dest.exists())

    def test_original_mannequin_and_timeline_are_written_before_blender(self):
        with TemporaryDirectory() as t:
            dest=Path(t)/"project"
            def fail(*args,**kwargs):
                raise RuntimeError("intentional Blender failure")
            with patch("forge.human_lipsync.shutil.which",return_value="blender"),patch(
                    "forge.human_lipsync._blender",side_effect=fail):
                with self.assertRaisesRegex(RuntimeError,"intentional"):
                    build_human_lipsync(SPEC,dest)
            self.assertTrue((dest/"existing-human-forge"/"mannequin.glb").is_file())
            self.assertTrue((dest/"phoneme-timeline"/"lipsync.json").is_file())
            self.assertTrue((dest/"needs-reconciliation.txt").is_file())
            self.assertFalse((dest/"human-lipsync-receipt.json").exists())
