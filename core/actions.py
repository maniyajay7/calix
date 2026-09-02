"""
CalixGalaxy - Native System Actions Engine
Handles: App launching (native UWP + desktop), file navigation, media, volume, typing
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.parse

try:
    import pyautogui
    import psutil
except ImportError:
    pass

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

VBOX_PATHS = [
    r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe",
    r"C:\Program Files (x86)\Oracle\VirtualBox\VirtualBox.exe",
]

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# Native Windows Store / UWP Apps (launched via shell:AppsFolder)
NATIVE_APPS = {
    "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
}

# Desktop app shortcuts (exe-based)
DESKTOP_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "paint": "mspaint.exe",
    "taskmgr": "taskmgr.exe",
    "task manager": "taskmgr.exe",
    "spotify": "spotify.exe",
}


def get_chrome_path():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    return "chrome.exe"


def get_vbox_path():
    for path in VBOX_PATHS:
        if os.path.exists(path):
            return path
    return "VirtualBox.exe"


# ==========================================
# 1. VirtualBox & Virtual Machine Automation
# ==========================================

def list_vms():
    if not os.path.exists(VBOX_MANAGE):
        return []
    try:
        res = subprocess.run([VBOX_MANAGE, "list", "vms"], capture_output=True, text=True, timeout=10)
        lines = res.stdout.strip().split("\n")
        vms = []
        for line in lines:
            if '"' in line:
                name = line.split('"')[1]
                vms.append(name)
        return vms
    except Exception:
        return []


def start_vm(vm_name="kali"):
    if not os.path.exists(VBOX_MANAGE):
        return "VirtualBox is not installed."
    available = list_vms()
    target_vm = None
    for v in available:
        if vm_name.lower() in v.lower():
            target_vm = v
            break
    if not target_vm and available:
        target_vm = available[0]
    if not target_vm:
        open_app("virtualbox")
        return "Opened VirtualBox GUI (no specific VM found)."
    try:
        subprocess.Popen([VBOX_MANAGE, "startvm", target_vm, "--type", "gui"])
        return f"Launched VM: '{target_vm}'!"
    except Exception as e:
        return f"Failed to start VM {target_vm}: {e}"


def open_virtualbox():
    path = get_vbox_path()
    try:
        subprocess.Popen([path])
        return "Launched Oracle VirtualBox!"
    except Exception as e:
        return f"Could not launch VirtualBox: {e}"


# ==========================================
# 2. Chrome & Web Automation
# ==========================================

def open_chrome_profile(url="https://google.com", profile="Profile 2"):
    chrome_bin = get_chrome_path()
    try:
        cmd = [chrome_bin, f"--profile-directory={profile}", url]
        subprocess.Popen(cmd)
        return f"Opened Chrome at {url}"
    except Exception as e:
        webbrowser.open(url)
        return f"Opened default browser (Fallback: {e})"


def search_google(query, profile="Profile 2"):
    encoded = urllib.parse.quote(query)
    return open_chrome_profile(f"https://www.google.com/search?q={encoded}", profile=profile)


# ==========================================
# 3. Application & Process Launcher (NATIVE FIRST)
# ==========================================

def open_app(app_name):
    app_clean = app_name.lower().strip()
    for filler in ["my ", "the ", "app ", "application ", "program ", "open "]:
        if app_clean.startswith(filler):
            app_clean = app_clean[len(filler):].strip()

    # 1. Check native UWP apps first (WhatsApp, etc.)
    if app_clean in NATIVE_APPS:
        try:
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{NATIVE_APPS[app_clean]}"])
            return f"Launched native {app_name}!"
        except Exception as e:
            return f"Failed to launch native {app_name}: {e}"

    # 2. Check desktop exe apps
    if app_clean in DESKTOP_APPS:
        target = DESKTOP_APPS[app_clean]
    elif app_clean in ["virtualbox", "vbox", "virtual box", "vertual box"]:
        target = get_vbox_path()
    else:
        target = app_clean

    try:
        subprocess.Popen(target, shell=True)
        return f"Launched {app_name}"
    except Exception as e:
        return f"Could not launch {app_name}: {e}"


def close_app(process_name):
    killed = 0
    proc_lower = process_name.lower().replace(".exe", "").strip()
    for proc in psutil.process_iter(["name"]):
        try:
            if proc_lower in proc.info["name"].lower():
                proc.terminate()
                killed += 1
        except Exception:
            pass
    if killed > 0:
        return f"Closed {killed} instance(s) of {process_name}."
    return f"No running instances of {process_name} found."


# ==========================================
# 4. File System Navigation
# ==========================================

def open_folder(path="X:\\"):
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        os.startfile(path)
        return f"Opened folder: {path}"
    except Exception as e:
        return f"Error opening folder {path}: {e}"


def find_project(project_name):
    """Find a project folder on the system."""
    search_roots = [
        "C:\\",
        "D:\\",
        "X:\\Tools\\",
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
    ]
    project_lower = project_name.lower().replace(" ", "")
    
    # Known projects shortcut
    known = {
        "securahub": "C:\\SecuraHub",
        "securehub": "C:\\SecuraHub",
        "secura hub": "C:\\SecuraHub",
        "secure hub": "C:\\SecuraHub",
        "calixgalaxy": "X:\\Tools\\CalixGalaxy",
        "calix galaxy": "X:\\Tools\\CalixGalaxy",
    }
    for k, v in known.items():
        if k in project_lower:
            if os.path.exists(v):
                return v
    
    # Search filesystem
    for root in search_roots:
        if not os.path.exists(root):
            continue
        try:
            for item in os.listdir(root):
                full = os.path.join(root, item)
                if os.path.isdir(full) and project_lower in item.lower().replace(" ", ""):
                    return full
        except PermissionError:
            continue
    return None


# ==========================================
# 5. Media & Hardware Control
# ==========================================

def control_media(action="playpause"):
    try:
        act = action.lower()
        if act in ["play", "pause", "playpause", "toggle"]:
            pyautogui.press("playpause")
            return "Toggled music playback."
        elif act in ["next", "next song", "skip"]:
            pyautogui.press("nexttrack")
            return "Skipped to next song."
        elif act in ["prev", "previous", "previous song"]:
            pyautogui.press("prevtrack")
            return "Previous song."
        elif act in ["stop"]:
            pyautogui.press("stop")
            return "Stopped playback."
        return f"Unknown media command: {action}"
    except Exception as e:
        return f"Media control error: {e}"


def adjust_volume(action="up"):
    try:
        if action.lower() == "up":
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume up."
        elif action.lower() == "down":
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume down."
        elif action.lower() in ["mute", "unmute"]:
            pyautogui.press("volumemute")
            return "Toggled mute."
        return f"Unknown action: {action}"
    except Exception as e:
        return f"Volume error: {e}"


# ==========================================
# 6. GUI Typing & Screen
# ==========================================

def type_text(text, press_enter=False, delay=0.02):
    try:
        time.sleep(0.3)
        pyautogui.write(text, interval=delay)
        if press_enter:
            pyautogui.press("enter")
        return f"Typed: {text[:50]}"
    except Exception as e:
        return f"Typing error: {e}"


def capture_screen(save_path="X:\\Calix\\OmniMemory\\latest_screen.png"):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img = pyautogui.screenshot()
        img.save(save_path)
        return f"Screenshot saved to {save_path}"
    except Exception as e:
        return f"Screenshot error: {e}"


def send_whatsapp(contact, message):
    try:
        import pyautogui
        import time
        # Open WhatsApp
        open_app("whatsapp")
        time.sleep(2)  # Wait for it to load
        
        # Click search or press Ctrl+F
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # Type contact
        pyautogui.write(contact)
        time.sleep(1.5)
        
        # Select first contact (Enter or Tab depending on UI)
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(1)
        
        # Type message and send
        pyautogui.write(message)
        time.sleep(0.5)
        pyautogui.press('enter')
        return f"Sent WhatsApp to {contact}: {message}"
    except Exception as e:
        return f"Failed WhatsApp: {e}"

def play_spotify(song_name):
    import pyautogui
    import time
    try:
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write('spotify')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        pyautogui.write(song_name)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('enter')
        return f"Playing {song_name} on Spotify."
    except Exception as e:
        return f"Failed to play Spotify: {e}"

def set_alarm(seconds, message):
    import threading
    import time
    def _alarm():
        time.sleep(seconds)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(f"ALARM! {message}")
            engine.runAndWait()
        except: pass
    threading.Thread(target=_alarm, daemon=True).start()
    return f"Alarm set for {seconds} seconds."

def get_news():
    import urllib.request
    try:
        import xml.etree.ElementTree as ET
        url = 'https://news.google.com/rss'
        resp = urllib.request.urlopen(url, timeout=5)
        tree = ET.parse(resp)
        root = tree.getroot()
        titles = [item.find('title').text for item in root.findall('./channel/item')[:3]]
        return " Top News: " + " | ".join(titles)
    except Exception as e:
        return "I couldn't fetch the news right now."

def open_maps(destination):
    import webbrowser
    webbrowser.open(f"https://www.google.com/maps/search/{destination}")
    return f"Opened maps for {destination}"
