import os
import time
import shutil
import subprocess
import requests
import psutil
import zipfile
import json

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCKDOWN_NAME = "LockDown.exe"
MAIN_NAME = "Main.exe"
LAUNCHER_EXE = os.path.join(BASE_DIR, LOCKDOWN_NAME)
START_EXE = os.path.join(BASE_DIR, MAIN_NAME)

# Local details.json (bundled with the app)
LOCAL_DETAILS = os.path.join(BASE_DIR, "details.json")

# Remote details.json (GitHub raw URL)
REMOTE_DETAILS_URL = "https://raw.githubusercontent.com/MNizamD/LockDownKiosk/main/details.json"

TMP_UPDATE = os.path.join(BASE_DIR, "update.zip")
EXTRACT_DIR = os.path.join(BASE_DIR, "_update_tmp")

CHECK_INTERVAL = 60  # seconds

# ---------------- HELPERS ----------------
def get_local_details():
    if os.path.exists(LOCAL_DETAILS):
        with open(LOCAL_DETAILS, "r") as f:
            return json.load(f)
    return {"version": "0.0.0"}

def get_remote_details():
    try:
        r = requests.get(REMOTE_DETAILS_URL, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("Failed to fetch details.json:", e)
    return None

def kill_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name'].lower()
            if LOCKDOWN_NAME in name or MAIN_NAME in name:
                print("Killing:", name)
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def extract_update():
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    with zipfile.ZipFile(TMP_UPDATE, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    # Move extracted files into BASE_DIR
    for item in os.listdir(EXTRACT_DIR):
        src = os.path.join(EXTRACT_DIR, item)
        dst = os.path.join(BASE_DIR, item)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
        else:
            shutil.move(src, dst)

    shutil.rmtree(EXTRACT_DIR)
    os.remove(TMP_UPDATE)

# ---------------- MAIN LOOP ----------------
def updater_loop():
    while True:
        local = get_local_details()
        remote = get_remote_details()

        if remote:
            local_v = local.get("version", "0.0.0")
            remote_v = remote.get("version")
            zip_url = remote.get("zip_url")
            print(local_v)
            print(remote_v)
            print(zip_url)

            if remote_v and zip_url and remote_v != local_v:
                print(f"Update found: {local_v} -> {remote_v}")

                # Download update
                try:
                    r = requests.get(zip_url, stream=True)
                    with open(TMP_UPDATE, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                except Exception as e:
                    print("Download failed:", e)
                    time.sleep(CHECK_INTERVAL)
                    continue

                kill_processes()
                extract_update()

                # Update local details.json
                with open(LOCAL_DETAILS, "w") as f:
                    json.dump(remote, f, indent=4)

                subprocess.Popen([LAUNCHER_EXE])
                print("Update complete, restarted Launcher.")
                break

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    updater_loop()
