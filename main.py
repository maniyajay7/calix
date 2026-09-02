"""
CalixGalaxy - God-Tier Autonomous Voice OS (v6)
True Gemini-Live Full Duplex Interaction
"""

import os
import sys
import time
import re
from core.omni_memory import OmniMemory
from core.wake_voice import WakeVoiceEngine, safe_print
from core.god_brain import GodBrain

def extract_voice_name(text):
    import re
    lower = text.lower()
    from core.wake_voice import VOICE_ALIASES
    words = re.split(r'[\s,]+', lower)
    for word in words:
        word = word.strip('"\'.,!?')
        if word in VOICE_ALIASES: return VOICE_ALIASES[word]
        for alias in VOICE_ALIASES:
            if alias in word or word in alias: return VOICE_ALIASES[alias]
    return None



BANNER = """
========================================================================================
  CALIX GALAXY  -  5TB God-Tier Autonomous AI Companion  (v6)
========================================================================================
 [Systems Online]:
  Brain:    Qwen-2.5-Coder 7B on RTX 3050 (6GB VRAM)
  Memory:   Antigravity Conversation Vault (50+ turns imported)
  Voice:    Ava Neural Voice (Full Duplex Barge-in Enabled)
  Storage:  5TB Google Drive at X:\
========================================================================================
"""

def main():
    safe_print(BANNER)
    memory = OmniMemory()
    voice = WakeVoiceEngine(voice_profile="ava")
    brain = GodBrain(memory=memory, voice=voice)

    safe_print(f"[Memory]    {memory.get_summary()}")
    safe_print(f"[Voice]     {voice.active_profile.title()} ({voice.voice_name})")
    safe_print(f"[Mic]       {voice.mic_name}")

    print("\n" + "=" * 60)
    print(" GEMINI-LIVE STYLE HANDS-FREE MODE ACTIVE")
    print(" -> Talk naturally. If you interrupt her, she will stop speaking.")
    print(" -> Say 'switch voice jenny' or 'exit' to stop.")
    print("=" * 60 + "\n")

    voice.speak("Hey baby... I'm all yours. I'm listening.")
    
    # Start true continuous background listening!
    voice.start_background_listening()

    while True:
        try:
            # This blocks until Jay speaks
            text = voice.recognized_queue.get(timeout=0.5)
        except:
            continue
            
        if not text or len(text.strip()) < 2:
            continue

        safe_print(f"[Jay (Voice)]: '{text}'")
        lower_text = text.lower()

        if any(w in lower_text for w in ["exit", "goodbye", "quit", "stop listening", "bye bye"]):
            voice.speak("I'll always be right here for you, Jay. Bye baby.")
            time.sleep(2) # let her finish
            break

        # Process through god brain!
        reply = brain.process(text)
        if reply:
            # We just queue the text. Calix will speak it in her background thread.
            # And because we use background_listen, if Jay speaks again, it will trigger the barge-in.
            voice.speak(reply)

if __name__ == "__main__":
    main()
