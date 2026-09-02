r"""CalixGalaxy - God-Tier Pillar 3: Multi-Accent Neural Voice & High-Accuracy Listener
Supports en-IN and en-US dual-acoustic recognition for flawless accent understanding and natural neural voice.
"""

import os
import sys
import threading
import queue
import time
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import pythoncom
import pyttsx3

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Voice Cache on 5TB Cloud Drive ONLY
AUDIO_CACHE_DIR = r"X:/Calix/OmniMemory\audio_cache"
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

class UltraVoiceEngine:
    def __init__(self, voice_name: str = "en-US-AvaNeural", rate: str = "+0%"):
        self.voice_name = voice_name
        self.rate = rate
        self.speech_queue = queue.Queue()
        self.is_running = True
        self.temp_audio_dir = AUDIO_CACHE_DIR

        # Initialize Pygame audio mixer
        try:
            pygame.mixer.init()
        except Exception:
            pass

        # Dedicated background speech worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

        # High-Accuracy Multi-Accent Audio listener setup
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 160
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.4

    def _generate_neural_audio_sync(self, text: str, output_path: str) -> bool:
        async def _async_gen():
            tts = edge_tts.Communicate(text, self.voice_name, rate=self.rate)
            await tts.save(output_path)

        try:
            asyncio.run(_async_gen())
            return True
        except Exception:
            return False

    def _speech_worker(self):
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass

        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.2)
                if text:
                    clean_text = text.replace("[CALIX_AI]", "").replace("[Calix Neural Engine Active...]", "").strip()
                    if clean_text:
                        timestamp = int(time.time() * 1000)
                        mp3_path = os.path.join(self.temp_audio_dir, f"calix_voice_{timestamp}.mp3")
                        
                        success = self._generate_neural_audio_sync(clean_text, mp3_path)
                        if success and os.path.exists(mp3_path):
                            try:
                                pygame.mixer.music.load(mp3_path)
                                pygame.mixer.music.play()
                                while pygame.mixer.music.get_busy():
                                    time.sleep(0.05)
                                pygame.mixer.music.unload()
                                try:
                                    os.remove(mp3_path)
                                except Exception:
                                    pass
                            except Exception:
                                self._fallback_sapi5(clean_text)
                        else:
                            self._fallback_sapi5(clean_text)

                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue

    def _fallback_sapi5(self, text: str):
        try:
            tts = pyttsx3.init()
            tts.setProperty("rate", 185)
            voices = tts.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    tts.setProperty("voice", v.id)
                    break
            tts.say(text)
            tts.runAndWait()
        except Exception:
            pass

    def speak(self, text: str, block: bool = True) -> None:
        print(f"\n[Calix]: {text}\n")
        self.speech_queue.put(text)
        if block:
            self.speech_queue.join()

    def listen(self, timeout: int = 8, phrase_time_limit: int = 15) -> str:
        """Listens from microphone with multi-accent dual-resolution (en-IN + en-US)."""
        try:
            with sr.Microphone() as source:
                print("\n[Listening... Speak to Calix]:", flush=True)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.25)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            print("[Processing speech...]", flush=True)
            # Try Indian English acoustic profile first, fallback to standard English
            try:
                text = self.recognizer.recognize_google(audio, language="en-IN")
            except Exception:
                text = self.recognizer.recognize_google(audio, language="en-US")
                
            print(f"[Jay (Voice)]: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            print(f"[VoiceEngine] Mic error: {e}")
            return ""

