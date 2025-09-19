import subprocess
import sys
import json
import os
import time
import shutil
from tkinter import messagebox, Tk
from db_utils import get_lock_kiosk_status

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
BASE_DIR = get_app_base_dir()
LOCALDATA = os.getenv("LOCALAPPDATA")

APP_DIR = BASE_DIR   # app install dir (read-only)
DATA_DIR = os.path.join(LOCALDATA, "NizamLab")   # data dir (writable)

LOG_FILE = os.path.join(DATA_DIR, "StudentLogs.csv")
FLAG_FILE = os.path.join(DATA_DIR, "STOP_LAUNCHER.flag")

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
START_SCRIPT = os.path.join(APP_DIR, MAIN_FILE_NAME)
if not os.path.exists(START_SCRIPT): # py script not found
        MAIN_FILE_NAME = "Main.exe"
        START_SCRIPT = os.path.join(APP_DIR, MAIN_FILE_NAME)

FLAG_FILE = os.path.join(DATA_DIR, "STOP_LAUNCHER.flag")

# ---------------- FUNCTIONS ----------------
def check_files():

    if not os.path.exists(START_SCRIPT):
        return False, f"Start file doesn't exists\nCannot find {START_SCRIPT}"

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


# ---------------- LAUNCHER ----------------
def run_kiosk():
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
        if os.path.exists(FLAG_FILE):
            print("Destruct flag detected, stopping launcher.")
            os.remove(FLAG_FILE)  # reset for next launch
            break

        try:
            if START_SCRIPT.lower().endswith('.py'):
                subprocess.run(['python.exe', START_SCRIPT])
            elif START_SCRIPT.lower().endswith('.exe'):
                # Launch Start.exe
                subprocess.run([START_SCRIPT])

        except Exception as e:
            print(f"Error running kiosk: {e}")
            return

        # Short delay before restarting
        time.sleep(0.25)

# ---------------- RUN ----------------
if __name__ == "__main__":
    run_kiosk()
