#!/usr/bin/env python3
"""
NanoBot GitHub Sync Script
Sincronizza dati tra locale e GitHub repository
Funziona con Python 3.9+
"""

import json
import os
import sys
import urllib.request
import urllib.error
import base64
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "nanobot-ecosystem")
API_BASE = "https://api.github.com"

def github_request(method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "NanoBot-Local/1.0"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None

def get_open_issues():
    """Legge i task aperti dal repository GitHub"""
    issues = github_request("GET", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues?state=open&labels=task")
    if issues:
        print(f"Task aperti trovati: {len(issues)}")
        for issue in issues:
            print(f"  #{issue['number']}: {issue['title']}")
    return issues

def create_issue(title, body, labels=None):
    """Crea un nuovo task/issue su GitHub"""
    data = {
        "title": title,
        "body": body,
        "labels": labels or ["task", "local"]
    }
    result = github_request("POST", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues", data)
    if result:
        print(f"Issue creata: #{result['number']} - {result['title']}")
    return result

def sync_status():
    """Aggiorna lo stato del bot locale su GitHub"""
    status = {
        "agent_id": "nanobot-local-mac",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "online",
        "platform": "darwin",
        "python_version": sys.version
    }
    body = f"**Status Update**\n\n```json\n{json.dumps(status, indent=2)}\n```"
    return create_issue(f"[STATUS] Local Bot Online - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}", body, ["status", "local"])

def upload_file(local_path, remote_path):
    """Carica un file sul repository GitHub"""
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    # Controlla se il file esiste già
    existing = github_request("GET", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{remote_path}")

    data = {
        "message": f"Update {remote_path} from local bot",
        "content": content,
        "committer": {
            "name": "NanoBot Local",
            "email": "nanobot@local"
        }
    }
    if existing and "sha" in existing:
        data["sha"] = existing["sha"]

    result = github_request("PUT", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{remote_path}", data)
    if result:
        print(f"File caricato: {remote_path}")
    return result

if __name__ == "__main__":
    if not GITHUB_TOKEN or not GITHUB_OWNER:
        print("ERROR: Imposta GITHUB_TOKEN e GITHUB_OWNER come variabili ambiente")
        print("  export GITHUB_TOKEN='il_tuo_token'")
        print("  export GITHUB_OWNER='il_tuo_username'")
        sys.exit(1)

    print("=== NanoBot GitHub Sync ===")
    print(f"Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
    print()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        sync_status()
    elif cmd == "tasks":
        get_open_issues()
    elif cmd == "upload" and len(sys.argv) == 4:
        upload_file(sys.argv[2], sys.argv[3])
    else:
        print("Uso: python3 github_sync.py [status|tasks|upload <local> <remote>]")
