import customtkinter as ctk
from tkinter import filedialog, messagebox
from modules.watcher import FolderWatcher
from modules.sorter import DESTINATIONS, clear_destination_folder, clear_all_destinations
import time
import os
import threading
import pystray
import json
import logging
import sys
import winreg
from PIL import Image, ImageDraw

REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "SmartFileManager"

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=os.path.join("logs", "app.log"),
    level=logging.INFO,
    format="[%Y-%m-%d %H:%M:%S] %(message)s",
    encoding="utf-8"
)

watcher = None
selected_folder = os.path.join(os.path.expanduser("~"), "Downloads")
tray_icon = None

stats_counters = {
    "Total": 0, "Images": 0, "Videos": 0, "Audio": 0, 
    "Documents": 0, "Archives": 0, "Developpement": 0, 
    "Applications": 0, "Divers": 0
}
stats_labels = {}

def load_config():
    global selected_folder, stats_counters
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                selected_folder = data.get("selected_folder", selected_folder)
                saved_stats = data.get("stats_counters", {})
                for k in stats_counters:
                    if k in saved_stats:
                        stats_counters[k] = saved_stats[k]
        except Exception as e:
            logging.error(f"Erreur chargement config : {e}")

def save_config():
    data = {
        "selected_folder": selected_folder,
        "stats_counters": stats_counters
    }
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Erreur sauvegarde config : {e}")

def update_log_box(text):
    log_box.configure(state="normal")
    current_time = time.strftime("%H:%M:%S")
    formatted_text = f"[{current_time}] {text}"
    log_box.insert("end", f"{formatted_text}\n")
    log_box.configure(state="disabled")
    log_box.see("end")
    logging.info(text)

def log_message(text):
    app.after(0, lambda: update_log_box(text))

def update_stat_ui(category):
    stats_counters["Total"] += 1
    if category in stats_counters:
        stats_counters[category] += 1
    
    for cat, val in stats_counters.items():
        if cat in stats_labels:
            stats_labels[cat].configure(text=f"{cat}: {val}")
    save_config()

def trigger_stat_update(category):
    app.after(0, lambda: update_stat_ui(category))

def init_stats_ui_values():
    for cat, val in stats_counters.items():
        if cat in stats_labels:
            stats_labels[cat].configure(text=f"{cat}: {val}")

def choose_folder():
    global selected_folder
    folder = filedialog.askdirectory(initialdir=selected_folder)
    if folder:
        selected_folder = folder
        folder_label.configure(text=f"Dossier cible : {selected_folder}")
        log_message(f"Nouveau dossier cible selectionne : {selected_folder}")
        save_config()

def start_watch():
    global watcher
    if watcher is None:
        watcher = FolderWatcher(selected_folder, log_message, trigger_stat_update)
        watcher.start()
        log_message(f"Surveillance active sur : {selected_folder}")

def stop_watch():
    global watcher
    if watcher:
        watcher.stop()
        watcher = None
        log_message("Surveillance arretee")

def clean_selected_dest():
    category = category_dropdown.get()
    confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer tout le contenu du dossier {category} ? Cette action est irreversible.")
    if confirm:
        result = clear_destination_folder(category)
        log_message(result)

def clean_all_dests():
    confirm = messagebox.askyesno("CONFIRMATION GLOBALE", "ATTENTION : Voulez-vous vraiment supprimer TOUT le contenu de TOUS les dossiers de destination Windows ? Cette action effacera tout de maniere definitive.")
    if confirm:
        result = clear_all_destinations()
        log_message(result)

def check_windows_boot_status():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, REG_APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def toggle_windows_boot():
    is_checked = boot_checkbox.get()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_SET_VALUE)
        if is_checked == 1:
            exe_path = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
            logging.info("Demarrage automatique avec Windows active")
        else:
            try:
                winreg.DeleteValue(key, REG_APP_NAME)
                logging.info("Demarrage automatique avec Windows desactive")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        logging.error(f"Erreur modification registre Windows : {e}")

def create_tray_image():
    img = Image.new("RGB", (64, 64), color="indigo")
    d = ImageDraw.Draw(img)
    d.rectangle([(16, 16), (48, 48)], fill="white")
    return img

def on_tray_click(icon, item):
    if str(item) == "Ouvrir":
        icon.stop()
        app.after(0, app.deiconify)
    elif str(item) == "Quitter":
        icon.stop()
        stop_watch()
        app.after(0, app.destroy)

def run_tray():
    global tray_icon
    menu = pystray.Menu(
        pystray.Menu.item("Ouvrir", on_tray_click),
        pystray.Menu.item("Quitter", on_tray_click)
    )
    tray_icon = pystray.Icon("SmartFileManager", create_tray_image(), "Smart File Manager", menu)
    tray_icon.run()

def minimize_to_tray():
    app.withdraw()
    threading.Thread(target=run_tray, daemon=True).start()

load_config()

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("900x820")
app.title("Smart File Manager")
app.protocol("WM_DELETE_WINDOW", minimize_to_tray)

title = ctk.CTkLabel(app, text="Smart File Manager", font=("Arial", 24))
title.pack(pady=10)

stats_frame = ctk.CTkFrame(app)
stats_frame.pack(pady=10, fill="x", padx=40)

stats_title = ctk.CTkLabel(stats_frame, text="Statistiques globales (sauvegardées)", font=("Arial", 12, "bold"))
stats_title.grid(row=0, column=0, columnspan=5, pady=5, padx=10, sticky="w")

categories_list = list(stats_counters.keys())
for index, cat in enumerate(categories_list):
    row_idx = 1 if index < 5 else 2
    col_idx = index % 5
    lbl = ctk.CTkLabel(stats_frame, text=f"{cat}: 0", font=("Arial", 11), width=150, anchor="w")
    lbl.grid(row=row_idx, column=col_idx, padx=15, pady=5)
    stats_labels[cat] = lbl

init_stats_ui_values()

config_frame = ctk.CTkFrame(app)
config_frame.pack(pady=10, fill="x", padx=40)

folder_label = ctk.CTkLabel(config_frame, text=f"Dossier cible : {selected_folder}", font=("Arial", 12))
folder_label.pack(side="left", padx=15, pady=10)

browse_button = ctk.CTkButton(config_frame, text="Choisir un dossier", command=choose_folder, width=150)
browse_button.pack(side="right", padx=15, pady=10)

boot_frame = ctk.CTkFrame(app)
boot_frame.pack(pady=5, fill="x", padx=40)

boot_checkbox = ctk.CTkCheckBox(boot_frame, text="Lancer automatiquement avec Windows (Démarrage)", command=toggle_windows_boot)
boot_checkbox.pack(side="left", padx=15, pady=10)
if check_windows_boot_status():
    boot_checkbox.select()

control_frame = ctk.CTkFrame(app)
control_frame.pack(pady=10, fill="x", padx=40)

start_button = ctk.CTkButton(control_frame, text="Démarrer la surveillance", command=start_watch, fg_color="green", hover_color="darkgreen")
start_button.pack(side="left", padx=15, pady=10, expand=True)

stop_button = ctk.CTkButton(control_frame, text="Arrêter la surveillance", command=stop_watch, fg_color="red", hover_color="darkred")
stop_button.pack(side="left", padx=15, pady=10, expand=True)

clean_frame = ctk.CTkFrame(app)
clean_frame.pack(pady=10, fill="x", padx=40)

clean_label = ctk.CTkLabel(clean_frame, text="Nettoyage :", font=("Arial", 12))
clean_label.pack(side="left", padx=15, pady=10)

clean_categories = [k for k in DESTINATIONS.keys()]
category_dropdown = ctk.CTkOptionMenu(clean_frame, values=clean_categories, width=150)
category_dropdown.pack(side="left", padx=10, pady=10)

clean_button = ctk.CTkButton(clean_frame, text="Vider ce dossier", command=clean_selected_dest, fg_color="purple", hover_color="indigo", width=130)
clean_button.pack(side="left", padx=10, pady=10)

clean_all_button = ctk.CTkButton(clean_frame, text="Tout vider", command=clean_all_dests, fg_color="darkred", hover_color="black", width=130)
clean_all_button.pack(side="right", padx=15, pady=10)

log_box = ctk.CTkTextbox(app, width=820, height=240, font=("Courier", 12))
log_box.pack(pady=15)
log_box.configure(state="disabled")

app.mainloop()