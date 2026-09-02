r"""CalixGalaxy - Autonomous Cloud Stream Downloader
Stored in X:/Calix\CloudDownloads\
Downloads 50GB+ large datasets, ISOs, and wordlists straight into X:/Calix/CloudDownloads\ with zero local C: drive exhaustion.
"""

import os
import sys
import time
import threading
import requests
from tqdm import tqdm
from urllib.parse import urlparse

DEFAULT_DOWNLOAD_DIR = r"X:/Calix/CloudDownloads"

class CloudDownloader:
    def __init__(self, download_dir: str = DEFAULT_DOWNLOAD_DIR):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.active_downloads = {}

    def download_file(self, url: str, custom_filename: str = None, callback = None) -> str:
        """Starts a background stream download directly into X:/Calix/CloudDownloads."""
        def _worker():
            try:
                parsed = urlparse(url)
                filename = custom_filename or os.path.basename(parsed.path) or f"download_{int(time.time())}.bin"
                dest_path = os.path.join(self.download_dir, filename)

                print(f"\n[Downloader] Starting background stream: {filename} -> X:\\Calix\\CloudDownloads\\", flush=True)
                
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))

                with open(dest_path, "wb") as f, tqdm(
                    desc=filename,
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in response.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

                msg = f"Finished downloading {filename} directly into your 5TB Cloud Vault (X:\\Calix\\CloudDownloads\\)!"
                print(f"\n[Downloader Success]: {msg}", flush=True)
                if callback:
                    callback(msg)
            except Exception as e:
                err = f"Download failed for {url}: {e}"
                print(f"[Downloader Error]: {err}")
                if callback:
                    callback(err)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return f"Started background download directly into X:\\Calix\\CloudDownloads\\! You can keep using your PC."


