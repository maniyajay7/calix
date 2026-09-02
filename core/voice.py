r"""CalixGalaxy - Thread-Safe Low-Latency Voice Engine
Enhanced microphone sensitivity, extended pause thresholds, and clean speech playback.
"""

import os
import sys
import threading
import queue
import time
import pythoncom
import pyttsx3
import speech_recognition as sr

class VoiceEngine:
    def __init__(self, rate: int = 185):
        self.rate = rate
        self.speech_queue = queue.Queue()
        self.is_running = True
        
        # Start dedicated background TTS worker thread
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

        # Audio listener setup
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2  # Allow 1.2s pause before finalizing speech
        self.recognizer.non_speaking_duration = 0.5

    def _tts_worker(self):
        """Worker thread that serializes all TTS calls safely with COM initialization."""
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
                        try:
                            tts = pyttsx3.init()
                            tts.setProperty("rate", self.rate)
                            voices = tts.getProperty("voices")
                            for v in voices:
                                if "zira" in v.name.lower() or "female" in v.name.lower():
                                    tts.setProperty("voice", v.id)
                                    break
                            tts.say(clean_text)
                            tts.runAndWait()
                        except Exception as e:
                            print(f"[VoiceEngine] Speech error: {e}")
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue

    def speak(self, text: str, block: bool = True) -> None:
        """Speaks text out loud safely without COM loop collision."""
        print(f"\n[Calix]: {text}\n")
        self.speech_queue.put(text)
        if block:
            self.speech_queue.join()

    def listen(self, timeout: int = 8, phrase_time_limit: int = 15) -> str:
        """Listens from the microphone and returns recognized text."""
        try:
            with sr.Microphone() as source:
                print("\n[Listening... Speak to Calix]:", flush=True)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            print("[Processing audio...]", flush=True)
            text = self.recognizer.recognize_google(audio)
            print(f"[Jay (Voice)]: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            print(f"[VoiceEngine] Mic error: {e}")
            return ""

