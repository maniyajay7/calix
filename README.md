# 🌌 CalixGalaxy — Autonomous Voice & Desktop Operating System

Built with love and devotion for **Jay**. Powered by high-speed Python desktop automation, Google Cloud Vault streaming (`X:\`), low-latency voice, and persistent vector memory.

---

## 🏛️ Project Structure
```
X:\Tools\CalixGalaxy\
├── core\
│   ├── actions.py       # OS, Chrome Profiles, Typing & Settings Controller
│   ├── brain.py         # Calix Persona & Natural Language Command Router
│   ├── memory.py        # Persistent JSON/Vector Memory in X:\Memory\
│   └── voice.py         # Real-time Speech-to-Text & Text-to-Speech Engine
├── main.py              # Main Interactive Application (Voice & Text)
├── run_calix.bat        # 1-Click Desktop Launcher
└── requirements.txt     # Python Dependencies
```

---

## ⚡ Supported Voice & Text Commands

| Command Category | Example Voice/Text Prompt | Action Executed |
| :--- | :--- | :--- |
| **Chrome Profiles** | `"open chrome"` / `"open browser"` | Launches Chrome with your dedicated **Profile 2** |
| **Google Search** | `"search for latest cybersecurity news"` | Opens Chrome Profile 2 and performs Google search |
| **App Launching** | `"open notepad"`, `"open code"`, `"open calc"` | Launches Windows application instantly |
| **Typing Automation**| `"open notepad and type Hello World"` | Opens Notepad and types text automatically |
| **Cloud Vault** | `"open vault"` / `"open folder"` | Opens `X:\` in Windows File Explorer |
| **System Settings** | `"open bluetooth"`, `"open wifi"` | Opens Windows Settings page |
| **Volume Control** | `"volume up"`, `"volume down"`, `"mute"` | Controls Windows master volume |
| **Screen Perception**| `"screenshot"` / `"look at my screen"` | Captures screen to `X:\Memory\latest_screen.png` |
| **Relationship / Banter** | `"I love you"`, `"Who are you?"` | Spoken voice responses with Calix persona |

---

## 🚀 How to Run
Double-click `run_calix.bat` inside `X:\Tools\CalixGalaxy\` or run:
```powershell
python X:\Tools\CalixGalaxy\main.py
```
