r"""CalixGalaxy - SecurityLab & Penetration Testing Engine
Stored in X:/Calix/securityLab\
Manages wordlists (SecLists, RockYou), CVE lookups, payloads, and SecuraHub integration.
"""

import os
import sys
import requests
import json
from typing import Dict, Any, List

SECURITY_LAB_DIR = r"X:/Calix/SecurityLab"
WORDLISTS_DIR = os.path.join(SECURITY_LAB_DIR, "wordlists")
PAYLOADS_DIR = os.path.join(SECURITY_LAB_DIR, "payloads")

os.makedirs(WORDLISTS_DIR, exist_ok=True)
os.makedirs(PAYLOADS_DIR, exist_ok=True)

# Common wordlists download URLs
WORDLIST_URLS = {
    "common_passwords": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt",
    "common_subdomains": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt",
    "common_directories": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt",
    "fuzzing_params": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt",
}

class SecurityLab:
    def __init__(self):
        self.wordlists_dir = WORDLISTS_DIR
        self.payloads_dir = PAYLOADS_DIR

    def download_starter_wordlists(self) -> str:
        """Downloads essential SecLists wordlists directly into X:/Calix/SecurityLab/wordlists."""
        downloaded = []
        for name, url in WORDLIST_URLS.items():
            dest = os.path.join(self.wordlists_dir, f"{name}.txt")
            if not os.path.exists(dest):
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        with open(dest, "w", encoding="utf-8") as f:
                            f.write(r.text)
                        downloaded.append(name)
                except Exception as e:
                    print(f"[SecurityLab] Error downloading {name}: {e}")
        return f"SecLists wordlists downloaded to X:\\Calix/securityLab/wordlists\\ ({len(downloaded)} new lists)."

    def lookup_cve(self, cve_id: str) -> str:
        """Looks up a CVE vulnerability summary via public NIST / CVE API."""
        clean_id = cve_id.upper().strip()
        if not clean_id.startswith("CVE-"):
            clean_id = f"CVE-{clean_id}"
        
        url = f"https://cveawg.mitre.org/api/cve/{clean_id}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                containers = data.get("containers", {}).get("cna", {})
                title = containers.get("title", "No title")
                desc = containers.get("descriptions", [{}])[0].get("value", "No description available.")
                return f"[{clean_id}] {title}\n{desc[:300]}..."
            return f"Could not find CVE records for {clean_id}."
        except Exception as e:
            return f"CVE lookup error: {e}"

    def get_payload(self, payload_type: str = "sqli") -> str:
        """Returns standard security testing payloads."""
        payloads = {
            "sqli": ["' OR '1'='1", "admin' --", "' UNION SELECT null, username, password FROM users --"],
            "xss": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)"],
            "jwt_none": '{"alg": "none", "typ": "JWT"}',
            "ssrf": ["http://127.0.0.1:80", "http://169.254.169.254/latest/meta-data/"],
        }
        p = payloads.get(payload_type.lower(), ["' OR 1=1 --"])
        return f"Testing payloads for {payload_type}: {', '.join(p)}"


