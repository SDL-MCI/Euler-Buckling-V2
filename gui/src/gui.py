from pathlib import Path
from tkinter import Tk, Canvas, PhotoImage, Label, Button
import math
import serial
import threading
import time  

# ---------- CONFIGURATION ----------
SERIAL_PORT = "COM3" # Anpassen an den verwendeten Port
BAUD_RATE = 9600

# ---------- PATHS ----------
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(
    r"C:\Users\max-n\OneDrive\Dokumente\Projektmitarbeit\Mikrocontroller_Skript\Figma\GUI\build\assets\frame0"
)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# ---------- DRAWING FUNCTIONS ----------
def draw_needle(canvas, center_x, center_y, angle_deg, length, tag, color="black"):
    angle_rad = math.radians(angle_deg)
    end_x = center_x + length * math.cos(angle_rad)
    end_y = center_y - length * math.sin(angle_rad)
    canvas.create_line(center_x, center_y, end_x, end_y, fill=color, width=4, tags=tag)

def update_needle(canvas, tag, center_x, center_y, angle_deg, length):
    angle_rad = math.radians(angle_deg)
    end_x = center_x + length * math.cos(angle_rad)
    end_y = center_y - length * math.sin(angle_rad)
    canvas.coords(tag, center_x, center_y, end_x, end_y)

# ---------- GUI SETUP ----------
window = Tk()
window.geometry("923x573")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=573,
    width=923,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# Titles
canvas.create_text(686.0, 29.0, anchor="nw", text="Euler Fall 4", fill="#000000", font=("Arial", 20))
canvas.create_text(384.0, 29.0, anchor="nw", text="Euler Fall 3", fill="#000000", font=("Arial", 20))
canvas.create_text(82.0, 29.0, anchor="nw", text="Euler Fall 2", fill="#000000", font=("Arial", 20))

# Kraftanzeige-Felder (Labels statt Textboxen)
entries = []
entry_positions = [(55.0, 401.0), (361.0, 401.0), (668.0, 401.0)]
entry_images = ["entry_1.png", "entry_2.png", "entry_3.png"]
entry_imgs = []

for i, (x, y) in enumerate(entry_positions):
    img = PhotoImage(file=relative_to_assets(entry_images[i]))
    canvas.create_image(x + 101, y + 41, image=img)
    entry_imgs.append(img)
    entry = Label(
        bg="#D9D9D9",
        fg="#000716",
        font=("Arial", 20),
        anchor="center",
        justify="center"
    )
    entry.place(x=x, y=y, width=202.0, height=80.0)
    entry.config(text="0.00 N")
    entries.append(entry)

# Background images (Zifferblätter etc.)
bg_images_data = [
    ("Außenring1.png", 154, 227),
    ("Außenring2.png", 461, 227),
    ("Außenring3.png", 767, 228),
    ("image_2.png", 154, 230),
    ("image_3.png", 153.646, 226.646),
    ("image_4.png", 153.0, 230.5),
    ("image_7.png", 461.0, 230.0),
    ("image_8.png", 460.646, 226.646),
    ("image_9.png", 460.0, 230.5),
    ("image_12.png", 767.0, 234.0),
    ("image_13.png", 766.646, 230.646),
    ("image_14.png", 766.0, 234.5)
]
bg_refs = []
for img_name, x, y in bg_images_data:
    img = PhotoImage(file=relative_to_assets(img_name))
    canvas.create_image(x, y, image=img)
    bg_refs.append(img)

# Create needles (unter dem Zentrum)
needle_centers = [(154, 238), (461, 238), (767, 242)]
needle_tags = ["needle1", "needle2", "needle3"]
for (x, y), tag in zip(needle_centers, needle_tags):
    draw_needle(canvas, x, y, 240, 90, tag)

# Vordergrund (Zentrum-Images über den Nadeln)
front_image_data = [
    ("image_5.png", 154.0, 238.0),
    ("image_10.png", 461.0, 238.0),
    ("image_15.png", 767.0, 242.0)
]
for img_name, x, y in front_image_data:
    img = PhotoImage(file=relative_to_assets(img_name))
    canvas.create_image(x, y, image=img)
    bg_refs.append(img)  # damit sie nicht gelöscht werden

# ---------- LOGIC ----------
def update_gauges(values):
    """Aktualisiert die 3 Anzeigen und Zeiger. Werte werden auf 0–70 begrenzt."""
    for i in range(3):
        v = max(0, min(values[i], 70))      # Clamp 0–70
        angle = 240 - (v * 4.2857)          # Start bei 240°, 1 N = 4.2857°
        update_needle(canvas, needle_tags[i], *needle_centers[i], angle, 90)
        entries[i].config(text=f"{v:.2f} N")

# --- Messsteuerung (Start/Reset) ---
running_event = threading.Event()  # False = pausiert, True = läuft
ser = None                         # wird im Thread initialisiert

def start_measurement():
    """Startet die Messung (aktiviert das Einlesen)."""
    global ser
    running_event.set()
    # Eingangs-Puffer leeren
    try:
        if ser and ser.is_open:
            ser.reset_input_buffer()
    except Exception:
        pass

def reset_measurement():
    """
    Setzt Anzeigen auf 0.00 N und stoppt die Messung.
    Die Werte bleiben auf 0, bis wieder Start gedrückt wird.
    """
    running_event.clear()              # Messung anhalten
    update_gauges([0.0, 0.0, 0.0])     # Anzeigen zurücksetzen
    try:
        if ser and ser.is_open:
            ser.reset_input_buffer()   # optional: Puffer leeren
    except Exception:
        pass

def read_serial_loop():
    """Liest seriell; verarbeitet Daten nur, wenn running_event gesetzt ist."""
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        while True:
            if not running_event.is_set():
                # pausiert: auf Start warten
                time.sleep(0.1)
                continue
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) == 3:
                    values = [float(p) for p in parts]
                    window.after(0, update_gauges, values)
            except ValueError:
                
                continue
            except Exception:
                # Kurz warten bei temporären Problemen
                time.sleep(0.05)
    except Exception as e:
        print("Serial error:", e)

# ---------- BUTTONS ----------
start_btn = Button(window, text="Start", font=("Arial", 14), bg="#4CAF50", fg="white",
                   activebackground="#45A049", activeforeground="white",
                   relief="flat", cursor="hand2", command=start_measurement)
reset_btn = Button(window, text="Reset", font=("Arial", 14), bg="#F44336", fg="white",
                   activebackground="#E53935", activeforeground="white",
                   relief="flat", cursor="hand2", command=reset_measurement)

# Position 
canvas.create_window(380, 525, window=start_btn, width=120, height=40)
canvas.create_window(525, 525, window=reset_btn, width=120, height=40)

# ---------- START SERIAL THREAD ----------
threading.Thread(target=read_serial_loop, daemon=True).start()

# ---------- MAINLOOP ----------
window.resizable(False, False)
window.mainloop()
