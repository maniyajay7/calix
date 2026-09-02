r"""CalixGalaxy - Automated Project Snapshot & Backup Engine
Stored in X:/Calix\Backups\
Creates compressed snapshots of workspaces, configs, and projects directly into 5TB cloud drive.
"""

import os
import sys
import time
import zipfile
import shutil
from typing import List, Dict

BACKUP_DIR = r"X:/Calix/Backups/snapshots"
os.makedirs(BACKUP_DIR, exist_ok=True)

class BackupSystem:
    def __init__(self, backup_dir: str = BACKUP_DIR):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_snapshot(self, source_dir: str = r"c:/securaHub", label: str = "auto_snapshot") -> str:
        """Compresses source_dir into a zip archive inside X:/Calix/Backups/snapshots."""
        if not os.path.exists(source_dir):
            return f"Source directory does not exist: {source_dir}"

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        project_name = os.path.basename(os.path.normpath(source_dir))
        archive_name = f"{project_name}_{label}_{timestamp}.zip"
        dest_zip = os.path.join(self.backup_dir, archive_name)

        try:
            print(f"[BackupSystem] Creating snapshot: {archive_name} ...", flush=True)
            with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    # Skip heavy build/cache folders
                    dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "__pycache__", "dist", "build"]]
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, rel_path)

            size_mb = os.path.getsize(dest_zip) / (1024 * 1024)
            return f"Successfully created project snapshot: {archive_name} ({size_mb:.2f} MB) inside X:\\Calix\\Backups/snapshots\\!"
        except Exception as e:
            return f"Snapshot creation failed: {e}"

    def list_snapshots(self) -> List[str]:
        """Returns list of existing backup zip files in X:/Calix/Backups/snapshots."""
        try:
            files = os.listdir(self.backup_dir)
            return [f for f in files if f.endswith(".zip")]
        except Exception:
            return []


