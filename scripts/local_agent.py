#!/usr/bin/env python3
"""
NanoBot Local Agent - macOS
Automazione desktop, file management, git operations
Funziona con Python 3.9+
"""

import os
import sys
import json
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "nanobot-ecosystem"
DB_PATH = WORKSPACE / "data" / "local_agent.db"
LOG_PATH = WORKSPACE / "logs" / "agent.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_issue_id INTEGER,
            title TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            completed_at TEXT,
            result TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            details TEXT
        )
    """)
    conn.commit()
    return conn

# === Desktop Automation (macOS) ===

def run_applescript(script):
    """Esegue AppleScript su macOS"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    return result.stdout.strip(), result.returncode

def take_screenshot(output_path=None):
    """Screenshot dello schermo"""
    if not output_path:
        output_path = WORKSPACE / "data" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    result = subprocess.run(["screencapture", "-x", str(output_path)])
    if result.returncode == 0:
        log(f"Screenshot salvato: {output_path}")
        return str(output_path)
    return None

def open_application(app_name):
    """Apre un'applicazione macOS"""
    script = f'tell application "{app_name}" to activate'
    _, code = run_applescript(script)
    log(f"App aperta: {app_name} (exit: {code})")
    return code == 0

def show_notification(title, message):
    """Mostra notifica macOS"""
    script = f'display notification "{message}" with title "{title}"'
    run_applescript(script)
    log(f"Notifica: {title} - {message}")

# === Git Operations ===

def git_status(repo_path=None):
    """Status del repository git"""
    cwd = repo_path or os.getcwd()
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=cwd
    )
    return result.stdout

def git_pull(repo_path=None):
    """Pull dal remote"""
    cwd = repo_path or os.getcwd()
    result = subprocess.run(
        ["git", "pull"],
        capture_output=True, text=True, cwd=cwd
    )
    log(f"Git pull in {cwd}: {result.stdout.strip()}")
    return result.returncode == 0

def git_commit_push(message, repo_path=None):
    """Commit e push automatico"""
    cwd = repo_path or os.getcwd()
    subprocess.run(["git", "add", "-A"], cwd=cwd)
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True, cwd=cwd
    )
    if result.returncode == 0:
        push = subprocess.run(["git", "push"], capture_output=True, text=True, cwd=cwd)
        log(f"Commit+Push: {message}")
        return push.returncode == 0
    return False

# === File Management ===

def scan_directory(path, extensions=None):
    """Scansiona directory e restituisce file"""
    path = Path(path)
    files = []
    for f in path.rglob("*"):
        if f.is_file():
            if not extensions or f.suffix in extensions:
                files.append({
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
    return files

def organize_downloads():
    """Organizza la cartella Downloads"""
    downloads = Path.home() / "Downloads"
    organized = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "documents": [".pdf", ".doc", ".docx", ".txt", ".md"],
        "code": [".py", ".js", ".ts", ".html", ".css", ".json"],
        "archives": [".zip", ".tar", ".gz", ".dmg", ".pkg"]
    }
    moved = 0
    for folder, exts in organized.items():
        dest = downloads / folder
        dest.mkdir(exist_ok=True)
        for f in downloads.iterdir():
            if f.is_file() and f.suffix.lower() in exts:
                new_path = dest / f.name
                if not new_path.exists():
                    f.rename(new_path)
                    moved += 1
    log(f"Downloads organizzati: {moved} file spostati")
    return moved

# === Main ===

def status_report():
    """Report dello stato del sistema"""
    report = {
        "agent": "nanobot-local-mac",
        "timestamp": datetime.now().isoformat(),
        "workspace": str(WORKSPACE),
        "db_exists": DB_PATH.exists(),
        "python": sys.version
    }

    # Disk usage
    result = subprocess.run(["df", "-h", str(Path.home())], capture_output=True, text=True)
    report["disk"] = result.stdout.strip()

    # Running processes count
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    report["processes"] = len(result.stdout.strip().split("\n")) - 1

    return report

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        report = status_report()
        print(json.dumps(report, indent=2))
    elif cmd == "screenshot":
        path = take_screenshot()
        print(f"Screenshot: {path}")
    elif cmd == "notify":
        title = sys.argv[2] if len(sys.argv) > 2 else "NanoBot"
        msg = sys.argv[3] if len(sys.argv) > 3 else "Test notifica"
        show_notification(title, msg)
    elif cmd == "organize":
        n = organize_downloads()
        print(f"Organizzati {n} file")
    elif cmd == "init":
        conn = init_db()
        log("Database inizializzato")
        conn.close()
        print("Agent inizializzato!")
    else:
        print("Uso: python3 local_agent.py [status|screenshot|notify|organize|init]")
