import subprocess
import sys
import os
import time
import shutil
import psutil
from tkinter import messagebox, Tk
from lock_down_utils import get_lock_kiosk_status, run_if_not_running, duplicate_file

def get_app_base_dir():
    """
    Return the directory that contains the running application.
    Works for:
      - dev mode (python script): returns folder of this .py file
      - frozen mode (PyInstaller one-dir or one-file): returns folder of the exe
    """
    if getattr(sys, "frozen", False):
        # Frozen by PyInstaller: sys.executable -> path to the running .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as plain python script
        return os.path.dirname(os.path.abspath(__file__))

# ---------------- CONFIG ----------------
# PROGRAM_FILES = os.environ.get("ProgramFiles", "C:\\Program Files")
# PROGRAM_DATA = os.environ.get("ProgramData", "C:\\ProgramData")
LOCALDATA = os.getenv("LOCALAPPDATA")

APP_DIR = get_app_base_dir()   # app install dir (read-only)
DATA_DIR = os.path.join(LOCALDATA, "NizamLab")   # data dir (writable)

LOG_FILE = os.path.join(DATA_DIR, "StudentLogs.csv")
FLAG_DESTRUCT_FILE = os.path.join(DATA_DIR, "STOP_LAUNCHER.flag")
FLAG_IDLE_FILE = os.path.join(DATA_DIR, "IDLE.flag")

# ### --- Load details.json ---
# DETAILS_FILE = os.path.join(BASE_DIR, "details.json")
# DETAILS_INFO = {}
# if os.path.exists(DETAILS_FILE):
#     try:
#         with open(DETAILS_FILE, "r") as f:
#             DETAILS_INFO = json.load(f)
#     except Exception as e:
#         print("Error reading details.json:", e)
# # ===========================================

lock_status = get_lock_kiosk_status()

MAIN_FILE_NAME = "Main.py"
MAIN_SCRIPT = os.path.join(APP_DIR, MAIN_FILE_NAME)
if not os.path.exists(MAIN_SCRIPT): # py script not found
        MAIN_FILE_NAME = "Main.exe"
        MAIN_SCRIPT = os.path.join(APP_DIR, MAIN_FILE_NAME)

UPDATER_SCRIPT = os.path.join(APP_DIR, "Updater.exe")
UPDATER_SCRIPT_COPY = os.path.join(DATA_DIR, "Updater_copy.exe")
DETAILS_FILE = os.path.join(APP_DIR, "details.json")
DETAILS_FILE_COPY = os.path.join(DATA_DIR, "details.json")

# ---------------- FUNCTIONS ----------------
def check_files():

    if not os.path.exists(MAIN_SCRIPT):
        return False, f"Start file doesn't exists\nCannot find {MAIN_SCRIPT}"

    """Check that the log file is writable and that its drive has at least 1GB free"""
    print("Checking Log file: ", LOG_FILE)
    folder = os.path.dirname(LOG_FILE)

    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    # Check writable
    try:
        with open(LOG_FILE, "a") as f:
            f.write("")  # just a test append
    except Exception as e:
        messagebox.showerror("Error", f"Log file {LOG_FILE} is not writable.\n"
                                      f"Please contact the administrator.\n\n"
                                      f"{e}")
        return False, f"Log file {LOG_FILE} is not writable"

    # Check free space
    total, used, free = shutil.disk_usage(folder)
    if free < 1 * 1024 * 1024 * 1024:  # 1 GB
        return False, f"Not enough free space ({free / (1024**3):.2f} GB available)"

    return True, ""

def clean_destruction(msg):
    print(f"Destruct flag detected, {msg}.")
    os.remove(FLAG_DESTRUCT_FILE)

# ---------------- LAUNCHER ----------------
def run_kiosk():
    if os.path.exists(FLAG_DESTRUCT_FILE):
        clean_destruction("app may have crashed")

    if not bool(lock_status["ENABLED"]):
        print(lock_status)
        print("Disabled on server")
        return

    # Pre-check folder and disk
    ok, msg = check_files()
    if not ok:
        root = Tk()
        root.withdraw()  # hide main window
        messagebox.showwarning("Launcher Warning", f"Cannot start kiosk:\n\n{msg}")
        return

    while True:
        # Exit if destruct flag exists
        if os.path.exists(FLAG_DESTRUCT_FILE):
            clean_destruction("stopping launcher.")
            break

        try:
            # Replace the copy every time to ensure fresh
            # duplicate_file(UPDATER_SCRIPT, UPDATER_SCRIPT_COPY)

            run_if_not_running(UPDATER_SCRIPT, is_background=True, arg=APP_DIR)
            run_if_not_running(MAIN_SCRIPT)

        except Exception as e:
            print(f"Error running kiosk: {e}")
            return

        # Short delay before restarting

# ---------------- RUN ----------------
if __name__ == "__main__":
    run_kiosk()
