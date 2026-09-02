"""
CalixGalaxy - Voice Engine v8 (Ultra-Low Latency Faster-Whisper)
- Full-duplex continuous background listening
- Interrupts speech instantly mid-sentence
- 0ms network latency STT (runs on local RTX 3050 via faster-whisper)
"""

import os
import re
import sys
import threading
import queue
import time
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import numpy as np
from faster_whisper import WhisperModel

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

VOICE_PROFILES = {
    "neerja": "en-IN-NeerjaNeural",
    "ava": "en-US-AvaNeural",
    "jenny": "en-US-JennyNeural",
    "emma": "en-US-EmmaNeural",
    "sonia": "en-GB-SoniaNeural",
}

VOICE_ALIASES = {
    "neerja": "neerja", "neeja": "neerja", "nirja": "neerja",
    "ava": "ava", "eva": "ava",
    "jenny": "jenny", "jen": "jenny", "jenni": "jenny",
    "emma": "emma", "ema": "emma",
    "sonia": "sonia", "sonya": "sonia",
}

AUDIO_CACHE_DIR = r"X:\Calix\OmniMemory\audio_cache"
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

def find_active_microphone():
    try:
        names = sr.Microphone.list_microphone_names()
        for i, n in enumerate(names):
            if any(k in n.lower() for k in ["airdopes", "buds", "headset", "bluetooth"]) and "output" not in n.lower():
                try:
                    with sr.Microphone(device_index=i) as _: pass
                    return i, n
                except Exception: pass
        for i, n in enumerate(names):
            if "microphone array" in n.lower():
                try:
                    with sr.Microphone(device_index=i) as _: pass
                    return i, n
                except Exception: pass
    except Exception:
        pass
    return None, "Default System Microphone"


def strip_emojis(text):
    return re.sub(r"[^\x00-\x7F]+", "", text).strip()


def safe_print(text):
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        clean = text.encode("ascii", "ignore").decode("ascii")
        print(clean, flush=True)


class WakeVoiceEngine:
    def __init__(self, voice_profile="ava", rate="+5%", pitch="+2Hz"):
        self.active_profile = voice_profile.lower()
        self.voice_name = VOICE_PROFILES.get(self.active_profile, "en-US-AvaNeural")
        self.rate = rate
        self.pitch = pitch
        
        self.speech_queue = queue.Queue()       
        self.recognized_queue = queue.Queue()   
        
        self.is_running = True
        self.is_speaking = False
        self.interrupt_flag = False

        self.mic_index, self.mic_name = find_active_microphone()

        try:
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)
        except Exception:
            try:
                pygame.mixer.init()
            except Exception:
                pass

        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 95
        self.recognizer.dynamic_energy_threshold = False
        # Ultra-low latency VAD settings
        self.recognizer.pause_threshold = 0.25      
        self.recognizer.non_speaking_duration = 0.1

        mic_args = {"device_index": self.mic_index} if self.mic_index is not None else {}
        self.mic = sr.Microphone(**mic_args)
        
        # FIX: Hardcode a safe energy threshold so she never goes deaf from ambient noise spikes.
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
            
        self.stop_listening_func = None

        # ==== FAST LOCAL STT INITIALIZATION ====
        safe_print("[Calix] Loading Ultra-Fast Local Voice Model into GPU...")
        try:
            try:
                self.whisper_model = WhisperModel("tiny.en", device="cuda", compute_type="float16")
                # Dummy transcription to force CUDA DLL loading
                import numpy as np
                dummy = np.zeros(16000, dtype=np.float32)
                segments, info = self.whisper_model.transcribe(dummy, beam_size=1)
                list(segments)  # Must exhaust generator to trigger CUDA load!
                safe_print("[Calix] Whisper initialized on CUDA GPU! 0ms latency mode active.")
            except Exception as e:
                self.whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
                safe_print("[Calix] Whisper initialized on CPU! 0ms latency mode active.")
        except Exception as e:
            safe_print(f"[Calix] Whisper Error: {e}")
            self.whisper_model = None

    def _audio_to_numpy(self, audio_data):
        wav_bytes = audio_data.get_wav_data(convert_rate=16000, convert_width=2)
        return np.frombuffer(wav_bytes[44:], dtype=np.int16).astype(np.float32) / 32768.0

    def start_background_listening(self):
        if self.stop_listening_func:
            return
            
        self._bg_listening_active = True
        
        def _listen_loop():
            while self._bg_listening_active:
                try:
                    with self.mic as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=15)
                    
                    def _recognize_task(a):
                        if self.whisper_model:
                            try:
                                audio_np = self._audio_to_numpy(a)
                                segments, info = self.whisper_model.transcribe(audio_np, beam_size=1)
                                text = " ".join([s.text for s in segments]).strip()
                                if text and len(text) > 1:
                                    if self.is_speaking:
                                        self.stop_speaking()
                                        safe_print(f"\n[Barge-in Detected!]: Jay interrupted with -> '{text}'")
                                    self.recognized_queue.put(text)
                            except Exception as e:
                                print(f'Whisper Error: {e}')
                        else:
                            try:
                                text = self.recognizer.recognize_google(a, language="en-US")
                                if text and text.strip():
                                    if self.is_speaking:
                                        self.stop_speaking()
                                    self.recognized_queue.put(text.strip())
                            except:
                                pass
                    threading.Thread(target=_recognize_task, args=(audio,), daemon=True).start()
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    safe_print(f"[Calix] Mic reconnecting... ({e})")
                    import time
                    time.sleep(2)
                    try:
                        self.mic_index, self.mic_name = find_active_microphone()
                        mic_args = {"device_index": self.mic_index} if self.mic_index is not None else {}
                        self.mic = sr.Microphone(**mic_args)
                        with self.mic as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    except:
                        pass

        t = threading.Thread(target=_listen_loop, daemon=True)
        t.start()
        
        def stop_func(wait_for_stop=False):
            self._bg_listening_active = False
            
        self.stop_listening_func = stop_func
        safe_print("[Calix] Background Live Listening activated (Resilient Mode).")

    def stop_background_listening(self):
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None

    def stop_speaking(self):
        self.interrupt_flag = True
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        self.is_speaking = False

    def _generate_and_play(self, text):
        ts = int(time.time() * 1000)
        mp3_path = os.path.join(AUDIO_CACHE_DIR, f"speech_{ts}.mp3")

        async def _gen():
            tts = edge_tts.Communicate(text, self.voice_name, rate=self.rate, pitch=self.pitch)
            await tts.save(mp3_path)

        try:
            asyncio.run(_gen())
        except Exception:
            return False

        if self.interrupt_flag:
            try: os.remove(mp3_path)
            except: pass
            return False

        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 100:
            try:
                pygame.mixer.music.load(mp3_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    if self.interrupt_flag:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        break
                    time.sleep(0.02)
                else:
                    pygame.mixer.music.unload()
            except Exception:
                pass
            try: os.remove(mp3_path)
            except: pass
            return True
        return False

    def _speech_worker(self):
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.1)
                if text and not self.interrupt_flag:
                    self.is_speaking = True
                    clean_text = strip_emojis(text)
                    clean_text = clean_text.replace("[CALIX_AI]", "").replace("[Thinking...]", "").strip()

                    if clean_text and not self.interrupt_flag:
                        self._generate_and_play(clean_text)

                    self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                self.is_speaking = False

    def speak(self, text):
        safe_print(f"\n[Calix ({self.active_profile.title()})]: {text}\n")
        self.interrupt_flag = False
        self.speech_queue.put(text)
