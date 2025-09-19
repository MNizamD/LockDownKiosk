import tkinter as tk
from tkinter import messagebox
import csv
import os
import sys
import json
from datetime import datetime
import socket

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

# ================= CONFIG ==================
# PROGRAM_FILES = os.environ.get("ProgramFiles", "C:\\Program Files")
# PROGRAM_DATA = os.environ.get("ProgramData", "C:\\ProgramData")
BASE_DIR = get_app_base_dir()
LOCALDATA = os.getenv("LOCALAPPDATA")

APP_DIR = BASE_DIR   # app install dir (read-only)
DATA_DIR = os.path.join(LOCALDATA, "NizamLab")   # data dir (writable)

STUDENT_CSV = os.path.join(DATA_DIR, "Students.csv")
LOG_FILE = os.path.join(DATA_DIR, "StudentLogs.csv")
FLAG_DESTRUCT_FILE = os.path.join(DATA_DIR, "STOP_LAUNCHER.flag")
FLAG_IDLE_FILE = os.path.join(DATA_DIR, "IDLE.flag")

PC_NAME = socket.gethostname()

### --- Load details.json ---
DETAILS_FILE = os.path.join(BASE_DIR, "details.json")
DETAILS_INFO = {"version": "?", "updated": "?"}
if os.path.exists(DETAILS_FILE):
    try:
        with open(DETAILS_FILE, "r") as f:
            DETAILS_INFO = json.load(f)
    except Exception as e:
        print("Error reading details.json:", e)
# ===========================================


# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["StudentID", "PC_Name", "Login_Time", "Logout_Time"])


# Load student IDs
def load_students():
    students = {"iamadmin": "Admin"}
    if os.path.exists(STUDENT_CSV):
        with open(STUDENT_CSV, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 1:
                    students[row[0]] = row[1] if len(row) > 1 else ""
    return students


ALLOWED_STUDENTS = load_students()

BG_COLOR = "#1f1f1f"
BTN_COLOR = "#353434"
FONT_COLOR = "white"
SECONDARY_FONT_COLOR = "#aaaaaa"


# ================= APP =====================
class KioskApp:
    def __init__(self, master):
        # create idle flag ---
        with open(FLAG_IDLE_FILE, "w") as f:
            f.write("IDLE")

        self.master = master
        self.master.title("Lab Access")
        self.master.attributes('-fullscreen', True)  # Fullscreen at start
        self.master.attributes('-topmost', True)
        self.master.configure(bg=BG_COLOR)
        self.master.attributes("-alpha", 0.95)
        self.master.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.student_id = None
        self.login_time = None

        # --- Outer frame fills the window and centers content ---
        self.frame = tk.Frame(master, bg=BG_COLOR)
        self.frame.pack(fill="both", expand=True)

        # Use grid layout to center everything
        self.frame.grid_rowconfigure(0, weight=1)  # Top spacer
        self.frame.grid_rowconfigure(1, weight=0)  # PC Name
        self.frame.grid_rowconfigure(2, weight=0)  # Instruction
        self.frame.grid_rowconfigure(3, weight=0)  # Entry field
        self.frame.grid_rowconfigure(4, weight=1)  # Bottom spacer
        self.frame.grid_columnconfigure(0, weight=1)  # Center horizontally

        # --- PC Name ---
        self.pc_label = tk.Label(
            self.frame,
            text=PC_NAME,
            font=("Arial", 48, "bold"),
            fg=FONT_COLOR,
            bg=BG_COLOR,
        )
        self.pc_label.grid(row=1, column=0, pady=(0, 20))

        # --- Instruction ---
        self.label = tk.Label(
            self.frame,
            text="Enter Student ID to Access PC",
            font=("Arial", 16),
            fg=FONT_COLOR,
            bg=BG_COLOR,
        )
        self.label.grid(row=2, column=0, pady=(0, 20))

        # --- Entry field ---
        self.entry = tk.Entry(
            self.frame,
            font=("Arial", 22),
            bg="#2e2e2e",
            fg=FONT_COLOR,
            justify="center",
            insertbackground=FONT_COLOR,
        )
        self.entry.grid(row=3, column=0, pady=(0, 20))
        self.entry.focus()

        # Bind Enter key to login
        self.entry.bind("<Return>", lambda event: self.login())
        # Bind key release to dynamically mask non-digit input
        self.entry.bind("<KeyRelease>", self.check_input_mask)

        ### --- Version/Update Info ---
        self.version_label = tk.Label(
            self.frame,
            text=f"v{DETAILS_INFO.get('version','?')}  |  Updated: {DETAILS_INFO.get('updated','?')}",
            font=("Arial", 10),
            fg=SECONDARY_FONT_COLOR,
            bg=BG_COLOR
        )
        self.version_label.grid(row=4, column=0, pady=(10, 5), sticky="s")

    # Disable closing
    def disable_event(self):
        pass

    # Mask input if it contains non-digit characters
    def check_input_mask(self, event=None):
        text = self.entry.get()
        if text and not text.isdigit():
            self.entry.config(show="*")
        else:
            self.entry.config(show="")

    # Login logic
    def login(self):
        sid = self.entry.get().strip()
        if sid == "destruct":
            self.destruct()
            return

        if sid not in ALLOWED_STUDENTS:
            messagebox.showerror("Access Denied", "Invalid Student ID!")
            self.entry.delete(0, tk.END)
            return

        self.student_id = sid
        self.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log login
        with open(LOG_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.student_id, PC_NAME, self.login_time, ""])

        # Switch to logged-in view
        if os.path.exists(FLAG_IDLE_FILE):
            os.remove(FLAG_IDLE_FILE)
        
        self.show_logged_in()

    def destruct(self):
        # remove idle flag
        if os.path.exists(FLAG_IDLE_FILE):
            os.remove(FLAG_IDLE_FILE)
        # create STOP flag
        with open(FLAG_DESTRUCT_FILE, "w") as f:
            f.write("STOP")
        self.master.destroy()

    def show_logged_in(self):
        # Shrink window to normal size
        self.master.attributes("-fullscreen", False)
        self.master.geometry("280x130")
        self.master.resizable(False, False)

        # Clear screen
        for widget in self.frame.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(
            self.frame,
            text=f"Welcome {ALLOWED_STUDENTS[self.student_id] or self.student_id}",
            font=("Arial", 12),
            fg=FONT_COLOR,
            bg=BG_COLOR,
        )
        welcome_label.pack(pady=5)

        self.logout_button = tk.Button(
            self.frame,
            text="Logout",
            font=("Arial", 12),
            fg=FONT_COLOR,
            bg=BTN_COLOR,
            command=self.logout,
        )
        self.logout_button.pack(pady=10)

        # Duration label (starts at 0s)
        self.status_label = tk.Label(
            self.frame,
            text="Logged in: 0s",
            font=("Arial", 10),
            fg=FONT_COLOR,
            bg=BG_COLOR,
        )
        self.status_label.pack(pady=2)

        # Start updating duration
        self.start_time = datetime.now()
        self.update_duration()

    def update_duration(self):
        """Update the duration label every second"""
        elapsed = (datetime.now() - self.start_time).seconds
        mins, secs = divmod(elapsed, 60)
        hrs, mins = divmod(mins, 60)

        if hrs > 0:
            time_str = f"Logged in: {hrs}h {mins}m {secs}s"
        elif mins > 0:
            time_str = f"Logged in: {mins}m {secs}s"
        else:
            time_str = f"Logged in: {secs}s"

        # Keep updating until logout
        if self.logout_button["state"] != "disabled":
            self.status_label.config(text=time_str)
            self.master.after(1000, self.update_duration)

    def logout(self):
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update last empty logout field
        rows = []
        with open(LOG_FILE, mode="r", newline="") as file:
            reader = list(csv.reader(file))
            rows = reader

        for i in range(len(rows) - 1, -1, -1):
            if rows[i][0] == self.student_id and rows[i][3] == "":
                rows[i][3] = logout_time
                break

        with open(LOG_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        # Show logout message instead of timer
        self.status_label.config(text="You have successfully logged out!")

        # Disable the button to prevent double clicks
        self.logout_button.config(state="disabled")

        # After 3 seconds, destroy and rerun
        self.master.after(3000, lambda: self.master.destroy(), run())


def run():
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()


# ================= RUN =====================
if __name__ == "__main__":
    run()

