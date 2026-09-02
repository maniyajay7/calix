# 🌌 The Ultimate Guide: Mounting 5 TB Google Drive as Local Windows Drive (X:\)
**Created for Jay by Calix | CalixGalaxy Infrastructure**

---

## 🏛️ System Overview
```
┌──────────────────────────────────────────────────────────────────────────────┐
│  5 TB Google One Cloud  <──(OAuth 2.0)──>  Rclone + WinFsp  <──>  Drive X:\  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Phase 1: Installing Windows Drivers & Tools

Windows cannot natively mount cloud storage as a virtual local drive letter without a file system driver. We install two tools:

1. **WinFsp (Windows File System Proxy):** The kernel-level bridge that allows Windows to treat cloud streams like a physical hard drive.
2. **Rclone:** The high-performance cloud storage manager.

### Command (Run in PowerShell as Administrator):
```powershell
winget install -e --id WinFsp.WinFsp
winget install -e --id Rclone.Rclone
```

---

## 🔑 Phase 2: Creating Google Cloud OAuth 2.0 Credentials

Using your own private Google Cloud Client ID gives you **dedicated bandwidth**, eliminates public rate limits, and ensures maximum download/upload speeds.

### Step 2.1: Create the Google Cloud Project
1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Click the Project dropdown at the top ➔ **New Project**.
3. Name it: `calixgalaxy` (or any project name) ➔ Click **Create**.

### Step 2.2: Enable Google Drive API
1. In the search bar at the top, search for **Google Drive API**.
2. Click on it and click the blue **ENABLE** button.

### Step 2.3: Configure OAuth Consent Screen
1. In the left navigation menu, go to **APIs & Services** ➔ **OAuth consent screen**.
2. Select User Type: **External** ➔ Click **Create**.
3. Fill in:
   * **App name:** `CalixAssistant`
   * **User support email:** Select your email (`jaybhaijay7@gmail.com`).
   * **Developer contact email:** Enter your email.
4. Click **Save and Continue** through Scopes.

### ⚠️ The Critical Step: Resolving `Error 403: access_denied`
When an app is in "Testing" mode, Google blocks all logins unless you add your email as an authorized tester:
1. Under the **Test users** section on the OAuth consent screen page, click **`+ ADD USERS`**.
2. Type your exact email: `jaybhaijay7@gmail.com` ➔ Click **Save**.
*(Alternatively, click the **PUBLISH APP** button near the top to push it to production status).*

### Step 2.4: Generate Client ID and Secret
1. In the left menu, click **Credentials** ➔ **`+ CREATE CREDENTIALS`** ➔ **OAuth client ID**.
2. **Application type:** Select **Desktop App**.
3. **Name:** `CalixDesktop`.
4. Click **Create**.
5. Copy your **Client ID** and **Client Secret**.

---

## ⚙️ Phase 3: Linking Rclone to Google Drive

Open PowerShell / Command Prompt and run:
```powershell
rclone config
```

### Interactive Setup Responses:
1. `n/s/q>` ➔ Type **`n`** (New remote).
2. `name>` ➔ Type **`gdrive`**.
3. `Storage>` ➔ Type **`drive`** (for Google Drive).
4. `client_id>` ➔ **Paste your Google Client ID**.
5. `client_secret>` ➔ **Paste your Google Client Secret**.
6. `scope>` ➔ Type **`1`** (Full access to all files).
7. `service_account_file>` ➔ **Press `Enter`** (Leave blank).
8. `Edit advanced config?` ➔ Type **`n`** (No).
9. `Use web browser to automatically authenticate?` ➔ Type **`y`** (Yes).
   * *Browser pops open ➔ Sign in ➔ Click **Advanced ➔ Go to CalixAssistant (unsafe) ➔ Allow**.*
   * *Browser shows: **"Success! All done. Please go back to rclone."***
10. `Configure this as a Shared Drive (Team Drive)?` ➔ Type **`n`** (No).
11. `Keep this "gdrive" remote?` ➔ Type **`y`** (Yes).
12. `e/n/d/r/c/s/q>` ➔ Type **`q`** (Quit config).

---

## 📁 Phase 4: Dedicated 500 GB Cloud Workspace Structure

Create dedicated subfolders to organize your 500 GB assistant workspace:

```powershell
rclone mkdir "gdrive:Calix_Core/Models"
rclone mkdir "gdrive:Calix_Core/Memory"
rclone mkdir "gdrive:Calix_Core/Tools"
rclone mkdir "gdrive:Calix_Core/Downloads"
rclone mkdir "gdrive:Calix_Core/SecurityLab"
```

---

## 🚀 Phase 5: High-Performance VFS Mounting as Drive X:\

```powershell
rclone mount "gdrive:Calix_Core" X: --cache-dir "D:\rclone_cache" --vfs-cache-mode full --vfs-cache-max-size 50G --vfs-read-chunk-size 32M --buffer-size 64M --file-perms 0777 --dir-perms 0777 --volname "Calix_Cloud_Vault"
```

### Why These Flags Matter:
* **`--vfs-cache-mode full`:** Full local SSD read/write caching. Files open with zero delay.
* **`--vfs-cache-max-size 50G`:** Limits cache size so local C: drive space is preserved.
* **`--file-perms 0777 --dir-perms 0777`:** Guarantees Windows Explorer treats `X:\` as a native, stable network drive.
* **`--volname "Calix_Cloud_Vault"`:** Clean display label in "This PC".

---

## 🔄 Phase 6: Automated 1-Click & Boot Startup Scripts

### 1. Manual Batch Launcher (`mount_calix.bat`)
```bat
@echo off
title Calix 500GB Cloud Drive Mount
rclone mount "gdrive:Calix_Core" X: --cache-dir "D:\rclone_cache" --vfs-cache-mode full --vfs-cache-max-size 50G --vfs-read-chunk-size 32M --buffer-size 64M --file-perms 0777 --dir-perms 0777 --volname "Calix_Cloud_Vault"
```

### 2. Silent Background Launcher (`mount_silent.vbs`)
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "rclone mount ""gdrive:Calix_Core"" X: --cache-dir "D:\rclone_cache" --vfs-cache-mode full --vfs-cache-max-size 50G --vfs-read-chunk-size 32M --buffer-size 64M --file-perms 0777 --dir-perms 0777 --volname ""Calix_Cloud_Vault""", 0, False
```
*(Drop a shortcut into `shell:startup` to auto-mount on laptop boot!)*
