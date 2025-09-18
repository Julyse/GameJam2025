import arcade
from pathlib import Path
from typing import Dict
from audio_controller import SoundController
class SoundController:
    def __init__(self):
        # Dictionary to store loaded sounds
        self.sounds: Dict[str, arcade.Sound] = {}
        # Currently playing sounds (if you want to stop them)
        self.current_playbacks: Dict[str, arcade.SoundPlayback] = {}

    def load_sound(self, name: str, file_path: str, streaming: bool = False):
        sound = arcade.load_sound(file_path, streaming=streaming)
        self.sounds[name] = sound

    def play(self, name: str, volume: float = 1.0, pitch: float = 1.0, loop: bool = False):
        if name in self.sounds:
            playback = self.sounds[name].play(volume=volume, speed=pitch, loop=loop)
            self.current_playbacks[name] = playback
        else:
            #print(f"[SoundController] Sound '{name}' not found!")

    def stop(self, name: str):
        if name in self.current_playbacks:
            self.current_playbacks[name].stop()
            self.current_playbacks[name] = None

    def stop_all(self):
        for name, playback in self.current_playbacks.items():
            if playback:
                playback.stop()
        self.current_playbacks.clear()
