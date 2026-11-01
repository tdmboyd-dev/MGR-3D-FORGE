"""MGR original CPU audio-reactive jaw: real PCM wave contract, not phoneme AI."""
import io,math,struct,unittest,wave
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from forge.audio_motion import _wav_features,create_audio_motion_timeline
from forge.human_lipsync import build_human_lipsync

def synthetic_audio(seconds=1.4,rate=16000,amplitude=0.7):
    buffer=io.BytesIO()
    with wave.open(buffer,"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
        values=[]
        for sample in range(round(seconds*rate)):
            t=sample/rate
            voice=amplitude*math.sin(2*math.pi*195*t) if .3<t<1.1 else 0
            values.append(round(32767*voice))
        out.writeframes(struct.pack("<"+("h"*len(values)),*values))
    return buffer.getvalue()

class AudioMotionTests(unittest.TestCase):
    def test_sound_produces_bounded_jaw_but_not_false_phoneme_alignment(self):
        with TemporaryDirectory() as t:
            data=synthetic_audio()
            result=create_audio_motion_timeline(data,Path(t)/"timeline",
                       actor_id="mgr-human",fps=24)
            self.assertEqual(result["status"],"AUDIO_REACTIVE_NOT_PHONEME_ALIGNED")
            self.assertTrue(result["audio_file_used"])
            self.assertFalse(result["automatic_audio_alignment_verified"])
            self.assertEqual(result["events"],[])
            self.assertGreater(max(frame["weights"]["jawOpen"] for frame in result["frames"]),.30)
            self.assertEqual(result["frames"][0]["weights"]["jawOpen"],0)
            self.assertTrue(all(0<=v<=1 for frame in result["frames"] for v in frame["weights"].values()))
            self.assertGreater(result["speech_activity_ratio_estimate"],0.15)
            with self.assertRaises(FileExistsError):
                create_audio_motion_timeline(data,Path(t)/"timeline")

    def test_silence_does_not_claim_speech(self):
        with TemporaryDirectory() as t:
            quiet=synthetic_audio(amplitude=0)
            result=create_audio_motion_timeline(quiet,Path(t)/"silent")
            self.assertEqual(result["speech_activity_ratio_estimate"],0)
            self.assertEqual(max(x["weights"]["jawOpen"] for x in result["frames"]),0)

    def test_invalid_audio_declined_without_creating_output(self):
        for data in (b"",b"\0"*150,synthetic_audio()[:50],
                     b"RIFF"+b"\0"*300):
            with self.subTest(kind=data[:12]),TemporaryDirectory() as t:
                with self.assertRaises(ValueError):
                    create_audio_motion_timeline(data,Path(t)/"target")
                self.assertFalse((Path(t)/"target").exists())
        with TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                create_audio_motion_timeline(synthetic_audio(),Path(t)/"bad",fps=1)
            with self.assertRaises(ValueError):
                create_audio_motion_timeline(synthetic_audio(),Path(t)/"bad",actor_id="../../etc")

    def test_missing_blender_denied_before_editing_audio_inputs(self):
        with TemporaryDirectory() as t:
            wav=Path(t)/"authored.wav";wav.write_bytes(synthetic_audio())
            with patch("forge.human_lipsync.shutil.which",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Blender"):
                    build_human_lipsync({"actor_id":"mgr-native"},Path(t)/"project",
                                        audio_wav=wav,blender="not-blender")
            self.assertFalse((Path(t)/"project").exists())
