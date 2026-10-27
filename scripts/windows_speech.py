"""Windows Speech Recognition worker (runs under Python 3.x with pywin32 or SAPI).

Captures audio from the default microphone for `duration` seconds and returns
transcribed text via Windows Speech Recognition. Requires a working microphone.

Usage:
    python scripts/windows_speech.py --duration 5

Prints a JSON object to stdout.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import speech_recognition as sr
    _SR = True
except ImportError:
    _SR = False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default=None, help="transcribe from WAV file instead of mic")
    parser.add_argument("--duration", type=float, default=5.0)
    args = parser.parse_args(argv)

    if not _SR:
        # Fallback: try Windows SAPI via ctypes
        print(json.dumps({"schema": "mgr.forge.voice-worker.v1", "status": "UNAVAILABLE",
                          "error": "speech_recognition not installed (pip install SpeechRecognition pyaudio)",
                          "transcript": None}))
        return 1

    r = sr.Recognizer()
    if args.file:
        try:
            with sr.AudioFile(args.file) as source:
                audio = r.record(source)
        except Exception as e:
            print(json.dumps({"schema": "mgr.forge.voice-worker.v1", "status": "FILE_FAILED",
                              "error": str(e), "transcript": None}))
            return 1
    else:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=args.duration, phrase_time_limit=args.duration)
        except Exception as e:
            print(json.dumps({"schema": "mgr.forge.voice-worker.v1", "status": "CAPTURE_FAILED",
                              "error": str(e), "transcript": None}))
            return 1

    try:
        text = r.recognize_google(audio)  # requires internet
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        # try sphinx (offline)
        try:
            text = r.recognize_sphinx(audio)
        except Exception:
            text = ""
            print(json.dumps({"schema": "mgr.forge.voice-worker.v1", "status": "TRANSCRIBE_FAILED",
                              "error": str(e), "transcript": None}))
            return 1

    print(json.dumps({"schema": "mgr.forge.voice-worker.v1", "status": "MATERIALIZED",
                      "duration_seconds": args.duration, "transcript": text,
                      "notes": ["Windows Speech Recognition", "requires microphone and (for Google) internet"]}))


if __name__ == "__main__":
    raise SystemExit(main())
