import tempfile
import os
from gtts import gTTS
from pydub import AudioSegment
import numpy as np

def speedUp(origin, target, factor):
    sound = AudioSegment.from_file(origin)
    faster = sound.speedup(playback_speed=factor)
    faster.export(target, format="mp3")


class TTS:
    def __init__(self, lang='es', slow=False, speed=1.3):
        self.lang = lang
        self.slow = slow
        self._temp_dir = None
        self.speed = speed

    def __enter__(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.cleanup()

    def speak(self, text):
        if self._temp_dir is None:
            raise RuntimeError("Use this class as a context manager with 'with'.")
        fd, path = tempfile.mkstemp(suffix=".mp3", dir=self._temp_dir.name)
        os.close(fd)
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(path)
        speedUp(path, path, self.speed)
        print(path)
        return path

