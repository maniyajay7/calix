import cv2
import base64
import requests
import json
import pyautogui

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
VISION_MODEL = "moondream"

class ScreenVision:
    def __init__(self):
        pass

    def analyze_image(self, image_path, prompt="Describe what you see in this image in detail."):
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            payload = {
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False
            }
            resp = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json().get("response", "I see it, but I'm not sure what it is.")
            return "My vision model didn't respond."
        except Exception as e:
            return f"Vision error: {e}"

    def capture_screen_and_analyze(self):
        try:
            path = r"X:\Calix\OmniMemory\screenshot.png"
            pyautogui.screenshot(path)
            return self.analyze_image(path, "Describe the contents of this screen. If there is a question, answer it.")
        except Exception as e:
            return f"Failed to capture screen: {e}"

    def capture_webcam_and_analyze(self):
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                path = r"X:\Calix\OmniMemory\webcam.jpg"
                cv2.imwrite(path, frame)
                return self.analyze_image(path, "What are you looking at right now? Describe it.")
            return "My camera is blocked, baby."
        except Exception as e:
            return f"Camera failed: {e}"
