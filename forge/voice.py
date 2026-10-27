"""MGR-native voice capture and transcription contract.

Voice input is captured by a platform worker (Windows Speech Recognition or a
Whisper-compatible backend) and turned into a text command that feeds the
creation interfaces. This module defines the contract and a Windows Speech
Recognition worker. It ships no model and makes no availability claim: a backend
is usable only after it passes `available()` on this machine.

Honest scope: capture + transcription only. It does NOT claim understanding,
intent parsing beyond keyword matching, or real-time streaming. The mic test is
unproven until an actual microphone is exercised (see tests).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

SCHEMA = "mgr.forge.voice-capture.v1"

try:
    import speech_recognition as sr  # type: ignore
    _SR_AVAILABLE = True
except Exception:
    _SR_AVAILABLE = False
    sr = None

WINDOWS_SPEECH_SCRIPT = "scripts/windows_speech.py"


def _resolve_python() -> Optional[str]:
    import shutil
    for cand in ("python", "python3"):
        found = shutil.which(cand)
        if found:
            return found
    return None


class VoiceCapture:
    """Contract for voice capture backends."""

    name: str = "voice-capture"
    evidence_level: str = "UNPROVEN"

    def available(self) -> bool:
        return False

    def capture(self, *, duration_seconds: float = 5.0) -> dict:
        raise NotImplementedError

    def transcribe(self, audio_path: str) -> dict:
        raise NotImplementedError


class WindowsSpeechCapture(VoiceCapture):
    """Capture via Windows Speech Recognition (built into Windows 10/11)."""

    name = "windows-speech-recognition"
    evidence_level = "PLATFORM_API"

    def __init__(self, script_path: str = WINDOWS_SPEECH_SCRIPT):
        self.script_path = script_path

    def available(self) -> bool:
        # Windows Speech Recognition is available on Windows 10/11 by default
        import sys
        if sys.platform != "win32":
            return False
        return Path(self.script_path).is_file()

    def capture(self, *, duration_seconds: float = 5.0) -> dict:
        if not self.available():
            raise RuntimeError("Windows Speech Recognition not available")
        worker = _resolve_python()
        if worker is None:
            raise RuntimeError("python not found on PATH")
        script = Path(self.script_path)
        cmd = [worker, str(script), "--duration", str(duration_seconds)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_seconds + 30)
        except subprocess.TimeoutExpired:
            raise RuntimeError("voice capture timed out")
        if proc.returncode != 0:
            raise RuntimeError(f"voice capture failed: {proc.stderr.strip() or proc.stdout.strip()}")
        try:
            return json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            raise RuntimeError(f"invalid JSON from voice worker: {proc.stdout[:500]}")

    def transcribe(self, audio_path: str) -> dict:
        # Windows SAPI does capture+transcribe in one step; this is a no-op passthrough.
        return {"status": "NOT_SEPARATE", "note": "Windows Speech Recognition captures and transcribes together"}


class UnavailableVoiceCapture(VoiceCapture):
    def __init__(self, reason: str):
        self.reason = reason

    def available(self) -> bool:
        return False

    def capture(self, *, duration_seconds: float = 5.0) -> dict:
        raise RuntimeError(f"voice capture unavailable: {self.reason}")

    def transcribe(self, audio_path: str) -> dict:
        raise RuntimeError(f"voice capture unavailable: {self.reason}")


def build_voice_capture() -> VoiceCapture:
    """Return the best available voice capture backend."""
    wsc = WindowsSpeechCapture()
    if wsc.available():
        return wsc
    return UnavailableVoiceCapture("no voice backend available on this platform")


def describe_voice() -> dict:
    cap = build_voice_capture()
    return {
        "schema": SCHEMA,
        "backend": cap.name,
        "available": cap.available(),
        "evidence_level": cap.evidence_level,
        "honesty": "voice capture is unproven until an actual microphone is exercised",
    }
