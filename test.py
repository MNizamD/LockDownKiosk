import tkinter as tk
from PIL import Image, ImageDraw
import pystray
import threading

def create_image():
    # Simple blue circle tray icon
    image = Image.new("RGB", (64, 64), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=(0, 128, 255))
    return image

def on_quit(icon, item):
    icon.stop()
    root.destroy()

def restore_window(icon=None, item=None):
    root.deiconify()
    if tray_icon:
        tray_icon.visible = False   # Hide tray icon when restored

def minimize_to_tray():
    root.withdraw()
    if tray_icon:
        tray_icon.visible = True    # Show tray icon only when minimized

root = tk.Tk()
root.title("Tkinter Tray Example")
root.geometry("400x300")

root.overrideredirect(True)   # Removes title bar completely


# --- Create tray icon once ---
tray_icon = pystray.Icon(
    "MyApp",
    create_image(),
    "My Tkinter App",
    menu=pystray.Menu(
        pystray.MenuItem("Restore", restore_window),
        pystray.MenuItem("Quit", on_quit)
    )
)

# Run tray in background thread
threading.Thread(target=tray_icon.run, daemon=True).start()

# --- GUI button ---
btn = tk.Button(root, text="Minimize to Tray", command=minimize_to_tray)
btn.pack(pady=20)

root.mainloop()
