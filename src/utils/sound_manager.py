import os
import wave
import math
import struct

# Initialize pygame mixer safely
HAS_AUDIO = False
try:
    import pygame
    pygame.mixer.init()
    HAS_AUDIO = True
except Exception as e:
    print(f"Audio warning: Could not initialize pygame mixer ({e}). The game will run silently.")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "sounds")

def generate_tone(filepath, frequency, duration, wave_type='sine', sweep_end=None):
    """
    Generates a WAV file using the standard library wave module.
    wave_type: 'sine', 'square', 'sawtooth', 'triangle', 'noise'
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
            
            for i in range(num_samples):
                t = float(i) / sample_rate
                
                # Handle frequency sweeps
                if sweep_end is not None:
                    freq = frequency + (sweep_end - frequency) * (t / duration)
                else:
                    freq = frequency
                
                # Generate waveform
                angle = 2.0 * math.pi * freq * t
                if wave_type == 'sine':
                    val = math.sin(angle)
                elif wave_type == 'square':
                    val = 1.0 if math.sin(angle) >= 0 else -1.0
                elif wave_type == 'sawtooth':
                    val = 2.0 * (t * freq - math.floor(t * freq + 0.5))
                elif wave_type == 'triangle':
                    val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
                else:
                    val = math.sin(angle)
                
                # Apply envelope to prevent click sounds
                envelope = 1.0
                fade_samples = 1500
                if i < fade_samples:
                    envelope = i / fade_samples
                elif i > num_samples - fade_samples:
                    envelope = (num_samples - i) / fade_samples
                
                scaled_val = int(val * envelope * 16384.0)
                wav_file.writeframes(struct.pack('<h', scaled_val))
    except Exception as e:
        print(f"Failed to generate sound file {filepath}: {e}")

def create_default_sounds():
    """Generates all standard sound effects as WAV files if they do not exist."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    sound_configs = {
        "click.wav": {"freq": 800, "dur": 0.04, "type": "sine"},
        "correct.wav": {"freq": 1000, "dur": 0.15, "type": "sine", "sweep": 1300},
        "incorrect.wav": {"freq": 220, "dur": 0.25, "type": "square", "sweep": 180},
        "powerup.wav": {"freq": 440, "dur": 0.4, "type": "sine", "sweep": 880},
    }
    
    for filename, config in sound_configs.items():
        path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(path):
            generate_tone(path, config["freq"], config["dur"], config["type"], config.get("sweep"))
            
    # Generate multi-tone sounds: win.wav (rising chime) and lose.wav (falling chime)
    win_path = os.path.join(ASSETS_DIR, "win.wav")
    if not os.path.exists(win_path):
        # We merge 3 short tones: C5, E5, G5, C6
        notes = [523.25, 659.25, 783.99, 1046.50]
        sample_rate = 44100
        duration_per_note = 0.12
        total_samples = int(sample_rate * duration_per_note * len(notes))
        
        try:
            with wave.open(win_path, 'w') as wav_file:
                wav_file.setparams((1, 2, sample_rate, total_samples, 'NONE', 'not compressed'))
                for note_idx, freq in enumerate(notes):
                    samples = int(sample_rate * duration_per_note)
                    for i in range(samples):
                        t = float(i) / sample_rate
                        angle = 2.0 * math.pi * freq * t
                        val = math.sin(angle)
                        
                        # Envelope for each note
                        envelope = 1.0
                        fade = 800
                        if i < fade:
                            envelope = i / fade
                        elif i > samples - fade:
                            envelope = (samples - i) / fade
                            
                        scaled_val = int(val * envelope * 16384.0)
                        wav_file.writeframes(struct.pack('<h', scaled_val))
        except Exception as e:
            print(f"Failed to generate win.wav: {e}")

    lose_path = os.path.join(ASSETS_DIR, "lose.wav")
    if not os.path.exists(lose_path):
        # We merge 4 short tones descending: C4, Ab3, F3, D3
        notes = [261.63, 207.65, 174.61, 146.83]
        sample_rate = 44100
        duration_per_note = 0.18
        total_samples = int(sample_rate * duration_per_note * len(notes))
        
        try:
            with wave.open(lose_path, 'w') as wav_file:
                wav_file.setparams((1, 2, sample_rate, total_samples, 'NONE', 'not compressed'))
                for note_idx, freq in enumerate(notes):
                    samples = int(sample_rate * duration_per_note)
                    for i in range(samples):
                        t = float(i) / sample_rate
                        angle = 2.0 * math.pi * freq * t
                        val = 0.7 * math.sin(angle) + 0.3 * math.sin(2.0 * angle) # square-ish sine combo
                        
                        # Envelope for each note
                        envelope = 1.0
                        fade = 800
                        if i < fade:
                            envelope = i / fade
                        elif i > samples - fade:
                            envelope = (samples - i) / fade
                            
                        scaled_val = int(val * envelope * 16384.0)
                        wav_file.writeframes(struct.pack('<h', scaled_val))
        except Exception as e:
            print(f"Failed to generate lose.wav: {e}")

# Sound playback manager class
class SoundManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.muted = False
            cls._instance.sounds = {}
            cls._instance.volume = 0.5
            # Generate sounds first
            create_default_sounds()
            cls._instance.load_sounds()
        return cls._instance
        
    def load_sounds(self):
        if not HAS_AUDIO:
            return
        
        sound_files = ["click.wav", "correct.wav", "incorrect.wav", "powerup.wav", "win.wav", "lose.wav"]
        for f in sound_files:
            name = f.split(".")[0]
            path = os.path.join(ASSETS_DIR, f)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.volume)
                except Exception as e:
                    print(f"Error loading sound {f}: {e}")
                    
    def play(self, sound_name):
        if self.muted or not HAS_AUDIO:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Play sound error: {e}")
                
    def set_volume(self, val):
        """val: float between 0.0 and 1.0"""
        self.volume = max(0.0, min(1.0, val))
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.volume)
            except Exception:
                pass
                
    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted
