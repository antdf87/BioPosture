# bioposture_interface.py - Cross-Platform Edition
# Engineering Update v2.0: MULTI-OS COMPATIBILITY
# Author: AntDF87

import customtkinter as ctk
import cv2
import numpy as np
import time
import threading
import sys
import platform
from PIL import Image, ImageTk, ImageDraw
import pystray
from pystray import MenuItem as item
from collections import deque
import tkinter.messagebox as tkmb
import csv
import os
import tkinter as tk
from config_manager import ConfigManager
from autostart_manager import AutostartManager

# ---------- 0. OS DETECTION & HIGH DPI FIX ----------
CURRENT_OS = platform.system()

if CURRENT_OS == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ---------- NOTIFICHE CROSS-PLATFORM ----------
def show_os_notification(title: str, message: str):
    if CURRENT_OS == "Windows":
        try:
            from winotify import Notification, audio
            toast = Notification(
                app_id="BioPosture",
                title=title,
                msg=message,
                duration="short"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            return
        except Exception:
            pass
    
    elif CURRENT_OS == "Darwin":
        try:
            import subprocess
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=False, capture_output=True)
            return
        except Exception:
            pass
    
    elif CURRENT_OS == "Linux":
        try:
            import subprocess
            subprocess.run(['notify-send', title, message], check=False, capture_output=True)
            return
        except Exception:
            pass
    
    print(f"[NOTIFICATION] {title}: {message}")

# ---------- 1. PALETTE MEDTECH PRECISION ----------
GLOSS_BG_COLOR = ("#F0F8FF", "#0B1121")
GLOSS_SURFACE_COLOR = ("#FFFFFF", "#151F32")
GLOSS_BORDER_COLOR = ("#B0C4DE", "#2E3F5B")
GLOSS_PRIMARY = ("#007AFF", "#00E5FF")
GLOSS_PRIMARY_HOVER = ("#0056B3", "#00B8D4")
GLOSS_SECONDARY = ("#00CED1", "#00E676")
GLOSS_ERROR = ("#FF3B30", "#FF2968")
GLOSS_TEXT = ("#1C1C1E", "#E0F7FA")
GLOSS_TEXT_DIM = ("#8E8E93", "#64748B")
GLOSS_GRID = ("#E5E5EA", "#1E293B")
GLOSS_BUTTON_FILL = ("#EEF2F5", "#1E293B")
GLOSS_VIDEO_BG = ("#E1E6EB", "#000000")

THEME_CORNER_RADIUS = 10
THEME_FONT_MAIN = "Segoe UI" if CURRENT_OS == "Windows" else ("SF Pro" if CURRENT_OS == "Darwin" else "Ubuntu")
THEME_FONT_MONO = "Consolas" if CURRENT_OS == "Windows" else ("Menlo" if CURRENT_OS == "Darwin" else "Ubuntu Mono")

# ---------- UTIL ----------
class DataSmoother:
    def __init__(self, alpha=0.75):
        self.alpha = alpha
        self.val = None

    def update(self, new_val):
        if self.val is None:
            self.val = new_val
        else:
            self.val = self.alpha * new_val + (1 - self.alpha) * self.val
        return self.val

def calc_angle(p1, p2):
    return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

# ---------- COMPONENTE GRAFICO ----------
class RealTimeGraph(ctk.CTkFrame):
    def __init__(self, master, width=300, height=150, bg_color=GLOSS_SURFACE_COLOR, **kwargs):
        super().__init__(master, fg_color=bg_color, corner_radius=THEME_CORNER_RADIUS, 
                         border_width=1, border_color=GLOSS_BORDER_COLOR, **kwargs)
        
        mode = ctk.get_appearance_mode()
        self.bg_hex = bg_color[1] if mode == "Dark" else bg_color[0]
        self.grid_hex = GLOSS_GRID[1] if mode == "Dark" else GLOSS_GRID[0]
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg=self.bg_hex, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.width = width
        self.height = height
        self.max_points = 60
        
        self.data_ht = deque([0] * self.max_points, maxlen=self.max_points)
        self.data_neck = deque([0] * self.max_points, maxlen=self.max_points)

        self.line_grid = None
        self.line_ht = None
        self.line_neck = None
        
        self.col_ht = GLOSS_ERROR[1] if mode == "Dark" else GLOSS_ERROR[0]
        self.col_neck = GLOSS_SECONDARY[1] if mode == "Dark" else GLOSS_SECONDARY[0]

        self.initialized = False
        self.canvas.bind("<Configure>", self.on_resize)

    def init_graph_objects(self):
        self.canvas.delete("all")
        self.line_grid = self.canvas.create_line(0, self.height/2, self.width, self.height/2, 
                                               fill=self.grid_hex, dash=(2, 4))
        self.line_ht = self.canvas.create_line(0,0,0,0, fill=self.col_ht, width=2, smooth=True)
        self.line_neck = self.canvas.create_line(0,0,0,0, fill=self.col_neck, width=2, smooth=True)
        
        self.canvas.create_text(self.width-10, 10, text="Testa", fill=self.col_ht, anchor="ne", 
                              font=(THEME_FONT_MAIN, 8, "bold"))
        self.canvas.create_text(self.width-10, 25, text="Collo", fill=self.col_neck, anchor="ne", 
                              font=(THEME_FONT_MAIN, 8, "bold"))
        self.initialized = True

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.init_graph_objects()
        self.draw()

    def update_theme_colors(self, mode):
        self.bg_hex = GLOSS_SURFACE_COLOR[1] if mode == "Dark" else GLOSS_SURFACE_COLOR[0]
        self.grid_hex = GLOSS_GRID[1] if mode == "Dark" else GLOSS_GRID[0]
        self.col_ht = GLOSS_ERROR[1] if mode == "Dark" else GLOSS_ERROR[0]
        self.col_neck = GLOSS_SECONDARY[1] if mode == "Dark" else GLOSS_SECONDARY[0]
        
        self.configure(fg_color=self.bg_hex)
        self.canvas.configure(bg=self.bg_hex)
        self.init_graph_objects()

    def update_data(self, val_ht, val_neck):
        self.data_ht.append(val_ht)
        self.data_neck.append(val_neck)
        self.draw()

    def draw(self):
        if not self.initialized: return

        y_max = 120
        x_step = self.width / (self.max_points - 1) if self.max_points > 1 else 0
        
        def get_flat_coords(data):
            coords = []
            for i, val in enumerate(data):
                x = i * x_step
                normalized_val = min(max(val, 0), y_max)
                y = self.height - (normalized_val / y_max * self.height)
                coords.extend([x, y])
            return coords

        coords_ht = get_flat_coords(self.data_ht)
        coords_neck = get_flat_coords(self.data_neck)
        
        if len(coords_ht) >= 4:
            self.canvas.coords(self.line_ht, *coords_ht)
        if len(coords_neck) >= 4:
            self.canvas.coords(self.line_neck, *coords_neck)
            
        self.canvas.coords(self.line_grid, 0, self.height/2, self.width, self.height/2)

# ---------- APP ----------
class BioPostureApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.load()
        self.autostart_mgr = AutostartManager()
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        if CURRENT_OS == "Windows":
            icon_path = os.path.join(base_path, 'BioPosture.ico')
        else:
            icon_path = os.path.join(base_path, 'BioPosture.png')
        
        self.title("BioPosture - Monitoraggio Posturale")
        self.geometry("1100x760") 
        self.minsize(950, 700)
        self.configure(fg_color=GLOSS_BG_COLOR)
        
        if CURRENT_OS == "Windows" and os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        elif os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.iconphoto(True, icon_photo)
            except Exception:
                pass
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        saved_theme = self.config["ui"]["theme"]
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        self.running = True
        self.calibrated = self.config["calibration"]["is_calibrated"]
        self.minimized = False
        self.camera_available = False
        self.camera_stopped = False
        self.is_paused = False
        self.camera_error_shown = False
        self.models_loaded = False

        self.total_frames = self.config["session"]["total_frames"]
        self.good_frames = self.config["session"]["good_frames"]
        self.baseline = {
            "iris": self.config["calibration"]["iris"],
            "ht": self.config["calibration"]["ht"],
            "st": self.config["calibration"]["st"],
            "neck": self.config["calibration"]["neck"]
        }

        self.sm_iris = DataSmoother(0.8)
        self.sm_ht = DataSmoother(0.7)
        self.sm_st = DataSmoother(0.7)
        self.sm_neck = DataSmoother(0.8)

        self.mp_face = None
        self.mp_pose = None

        self.cap = None
        self.cam_index = self.config["ui"]["camera_index"]
        self._consecutive_read_fail = 0

        self.severity_var = ctk.DoubleVar(value=self.config["ui"]["severity"])
        self.last_notif_time = 0.0
        self.current_posture_ok = True

        self.setup_ui()

        self.tray_icon = None
        threading.Thread(target=self.setup_tray, daemon=True).start()
        
        threading.Thread(target=self.lazy_load_ai_models, daemon=True).start()

        self.after(100, self.process_loop)
    
    def lazy_load_ai_models(self):
        import mediapipe as mp
        self.mp_face = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.mp_pose = mp.solutions.pose.Pose(model_complexity=1, min_detection_confidence=0.6)
        self.models_loaded = True
        
        if not self.calibrated and self.running:
            self.after(500, self.prompt_first_calibration)

    def prompt_first_calibration(self):
        result = tkmb.askokcancel(
            "Calibrazione richiesta",
            "Prima di iniziare il monitoraggio, è necessario calibrare il sistema.\n\n"
            "Assumi una postura corretta e neutrale, poi premi OK per avviare la calibrazione (5 secondi)."
        )
        if result:
            self.start_calibration()
        else:
            tkmb.showwarning(
                "Calibrazione obbligatoria",
                "Non puoi utilizzare il sistema senza calibrazione. L'app rimarrà in attesa."
            )
            self.lbl_status.configure(text="IN ATTESA DI CALIBRAZIONE", text_color="orange")

    # ---------- UI ----------
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_vid = ctk.CTkFrame(self, fg_color=GLOSS_SURFACE_COLOR, 
                                      corner_radius=THEME_CORNER_RADIUS, 
                                      border_width=1, border_color=GLOSS_BORDER_COLOR)
        self.frame_vid.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.frame_vid.grid_columnconfigure(0, weight=1)
        self.frame_vid.grid_rowconfigure(1, weight=1)

        top_ctrl = ctk.CTkFrame(self.frame_vid, fg_color="transparent")
        top_ctrl.pack(fill="x", pady=(12, 0), padx=15)

        left_ctrl = ctk.CTkFrame(top_ctrl, fg_color="transparent")
        left_ctrl.pack(side="left")

        ctk.CTkLabel(left_ctrl, text="Camera:", text_color=GLOSS_TEXT_DIM, font=(THEME_FONT_MAIN, 12)).pack(side="left", padx=(0, 6))
        
        self.cam_options = ctk.CTkOptionMenu(
            left_ctrl, 
            values=self.probe_cameras(), 
            command=self.on_cam_select,
            fg_color=GLOSS_PRIMARY,
            button_color=GLOSS_PRIMARY_HOVER,
            button_hover_color=GLOSS_PRIMARY_HOVER,
            text_color="white",
            corner_radius=THEME_CORNER_RADIUS,
            font=(THEME_FONT_MAIN, 12),
            width=70,
            height=28
        )
        self.cam_options.set(str(self.cam_index))
        self.cam_options.pack(side="left")

        self.btn_stop = ctk.CTkButton(
            left_ctrl, 
            text="Stop", 
            width=70, 
            height=28,
            command=self.toggle_camera, 
            fg_color=GLOSS_ERROR,
            text_color="white",
            hover_color="#B91C1C",
            font=(THEME_FONT_MAIN, 12),
            corner_radius=THEME_CORNER_RADIUS
        )
        self.btn_stop.pack(side="left", padx=(8, 0))

        right_ctrl = ctk.CTkFrame(top_ctrl, fg_color="transparent")
        right_ctrl.pack(side="right")

        self.btn_save_kpi = ctk.CTkButton(
            right_ctrl,
            text="Salva KPI",
            width=90,
            height=28,
            command=self.save_kpi,
            fg_color=GLOSS_BUTTON_FILL, 
            text_color=GLOSS_TEXT,
            hover_color=GLOSS_BORDER_COLOR,
            font=(THEME_FONT_MAIN, 12),
            corner_radius=THEME_CORNER_RADIUS
        )
        self.btn_save_kpi.pack(side="left", padx=(0, 10))

        self.autostart_switch = ctk.CTkSwitch(
            right_ctrl,
            text="Autostart",
            command=self.toggle_autostart,
            progress_color=GLOSS_PRIMARY,
            button_color="white", 
            button_hover_color="#EEEEEE",
            text_color=GLOSS_TEXT,
            font=(THEME_FONT_MAIN, 12),
            width=100,
            switch_width=36,
            switch_height=18
        )
        if self.autostart_mgr.is_enabled():
            self.autostart_switch.select()
        self.autostart_switch.pack(side="left", padx=(0, 8))

        self.notif_toggle = ctk.CTkSwitch(
            right_ctrl,
            text="Notifiche",
            command=self.on_notif_toggle,
            progress_color=GLOSS_SECONDARY,
            button_color="white",
            text_color=GLOSS_TEXT,
            font=(THEME_FONT_MAIN, 12),
            width=100,
            switch_width=36,
            switch_height=18
        )
        if self.config["ui"]["notifications_enabled"]:
            self.notif_toggle.select()
        self.notif_toggle.pack(side="left", padx=(0, 8))

        is_light = self.config["ui"]["theme"] == "Light"
        self.theme_toggle = ctk.CTkSwitch(
            right_ctrl, 
            text="Tema Light", 
            command=self.toggle_theme, 
            progress_color=GLOSS_TEXT_DIM,
            button_color="white",
            text_color=GLOSS_TEXT,
            font=(THEME_FONT_MAIN, 12),
            width=90,
            switch_width=36,
            switch_height=18
        )
        if is_light:
            self.theme_toggle.select()
        self.theme_toggle.pack(side="left")

        video_container = ctk.CTkFrame(self.frame_vid, fg_color=GLOSS_VIDEO_BG, corner_radius=THEME_CORNER_RADIUS)
        video_container.pack(expand=True, fill="both", padx=15, pady=15)

        self.lbl_vid = ctk.CTkLabel(
            video_container, 
            text="INIZIALIZZAZIONE CAMERA...", 
            font=(THEME_FONT_MAIN, 16),
            text_color=GLOSS_TEXT
        )
        self.lbl_vid.pack(expand=True, fill="both", padx=2, pady=2)

        self.frame_ctrl = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_ctrl.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew")
        self.frame_ctrl.grid_columnconfigure(0, weight=1)
        self.frame_ctrl.grid_rowconfigure(0, weight=1)

        self.right_panel = ctk.CTkFrame(self.frame_ctrl, fg_color="transparent")
        self.right_panel.pack(fill="both", expand=True)

        card_1 = ctk.CTkFrame(self.right_panel, fg_color=GLOSS_SURFACE_COLOR, 
                              corner_radius=THEME_CORNER_RADIUS, 
                              border_width=1, border_color=GLOSS_BORDER_COLOR)
        card_1.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(card_1, text="PARAMETRI POSTURALI", font=(THEME_FONT_MAIN, 13, "bold"), text_color=GLOSS_TEXT_DIM).pack(pady=(12, 5))

        self.btn_calib = ctk.CTkButton(
            card_1,
            text="AVVIA CALIBRAZIONE (5s)",
            command=self.start_calibration,
            fg_color=GLOSS_PRIMARY,
            hover_color=GLOSS_PRIMARY_HOVER,
            height=36,
            text_color="white",
            font=(THEME_FONT_MAIN, 13, "bold"),
            corner_radius=THEME_CORNER_RADIUS
        )
        self.btn_calib.pack(pady=(0, 8), fill="x", padx=15)

        status_text = "SISTEMA INATTIVO" if not self.calibrated else "MONITORAGGIO ATTIVO"
        status_color = GLOSS_TEXT_DIM if not self.calibrated else GLOSS_SECONDARY
        self.lbl_status = ctk.CTkLabel(
            card_1,
            text=status_text,
            font=(THEME_FONT_MAIN, 14, "bold"),
            text_color=status_color
        )
        self.lbl_status.pack(pady=4)

        self.frame_vals = ctk.CTkFrame(card_1, fg_color="transparent")
        self.frame_vals.pack(fill="x", padx=15, pady=(0, 12))
        self.lbl_v_ht = self.create_metric_row(self.frame_vals, "Inclinazione Testa")
        self.lbl_v_st = self.create_metric_row(self.frame_vals, "Asimmetria Spalle")
        self.lbl_v_dist = self.create_metric_row(self.frame_vals, "Distanza Schermo")
        self.lbl_v_neck = self.create_metric_row(self.frame_vals, "Tensione Cervicale")

        card_2 = ctk.CTkFrame(self.right_panel, fg_color=GLOSS_SURFACE_COLOR, 
                              corner_radius=THEME_CORNER_RADIUS, 
                              border_width=1, border_color=GLOSS_BORDER_COLOR)
        card_2.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(card_2, text="EFFICIENZA SESSIONE", font=(THEME_FONT_MAIN, 11, "bold"), text_color=GLOSS_TEXT_DIM).pack(pady=(10, 0))
        self.progress_eff = ctk.CTkProgressBar(card_2, orientation="horizontal", height=8, corner_radius=4, progress_color=GLOSS_SECONDARY)
        self.progress_eff.pack(pady=8, padx=15, fill="x")
        eff_init = (self.good_frames / self.total_frames) if self.total_frames > 0 else 1.0
        self.progress_eff.set(eff_init)
        self.lbl_eff_text = ctk.CTkLabel(card_2, text=f"{int(eff_init*100)}%", font=(THEME_FONT_MONO, 12), text_color=GLOSS_SECONDARY)
        self.lbl_eff_text.pack(pady=(0, 10))

        self.frame_plot = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.frame_plot.pack(pady=(0, 10), fill="both", expand=True) 
        self.graph_widget = RealTimeGraph(self.frame_plot, height=120)
        self.graph_widget.pack(fill="both", expand=True)

        card_4 = ctk.CTkFrame(self.right_panel, fg_color=GLOSS_SURFACE_COLOR, 
                              corner_radius=THEME_CORNER_RADIUS, 
                              border_width=1, border_color=GLOSS_BORDER_COLOR)
        card_4.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(card_4, text="SOGLIA TOLLERANZA", font=(THEME_FONT_MAIN, 11, "bold"), text_color=GLOSS_TEXT_DIM).pack(pady=(10, 2))
        self.sev_label = ctk.CTkLabel(card_4, text=f"{int(self.severity_var.get())}%", font=(THEME_FONT_MONO, 12), text_color=GLOSS_TEXT)
        self.sev_label.pack()
        self.sev_slider = ctk.CTkSlider(
            card_4,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=self.severity_var,
            command=self.on_severity_change,
            button_color=GLOSS_PRIMARY,
            progress_color=GLOSS_PRIMARY,
            height=16,
            border_width=0
        )
        self.sev_slider.pack(pady=(5, 15), padx=15, fill="x")

        ctk.CTkLabel(
            self.right_panel,
            text="Chiudere la finestra per ridurre a icona",
            text_color=GLOSS_TEXT_DIM,
            font=(THEME_FONT_MAIN, 10)
        ).pack(side="bottom", pady=5)

    def create_metric_row(self, parent, label):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=label, width=150, anchor="w", text_color=GLOSS_TEXT, font=(THEME_FONT_MAIN, 12)).pack(side="left")
        v = ctk.CTkLabel(f, text="--", font=(THEME_FONT_MONO, 12, "bold"), text_color=GLOSS_TEXT)
        v.pack(side="right")
        sep = ctk.CTkFrame(parent, height=1, fg_color=GLOSS_BORDER_COLOR)
        sep.pack(fill="x", pady=(2, 0))
        return v

    # ---------- UI callbacks ----------
    def probe_cameras(self):
        available = []
        backend = cv2.CAP_DSHOW if CURRENT_OS == "Windows" else cv2.CAP_ANY
        
        for i in range(3):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    available.append(str(i))
                    cap.release()
            except:
                pass
        if not available:
            available = [str(self.cam_index)]
        return available

    def on_cam_select(self, value):
        try:
            new_index = int(value)
        except:
            new_index = self.cam_index
        
        if new_index != self.cam_index:
            self.cam_index = new_index
            self.config["ui"]["camera_index"] = new_index
            self.config_mgr.save(self.config)
            
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
                self.camera_available = False
                self._consecutive_read_fail = 0

    def toggle_camera(self):
        if self.camera_stopped:
            self.camera_stopped = False
            self.btn_stop.configure(text="Stop", fg_color=GLOSS_ERROR)
            self.lbl_status.configure(text="MONITORAGGIO ATTIVO", text_color=GLOSS_SECONDARY)
        else:
            self.camera_stopped = True
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
                self.camera_available = False
            self.btn_stop.configure(text="Avvia", fg_color=GLOSS_SECONDARY)
            self.lbl_status.configure(text="CAMERA FERMATA", text_color=GLOSS_TEXT_DIM)
            self.lbl_vid.configure(text="CAMERA FERMATA", image=None)

    def toggle_theme(self):
        new_mode = "Light" if self.theme_toggle.get() else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.graph_widget.update_theme_colors(new_mode)
        self.config["ui"]["theme"] = new_mode
        self.config_mgr.save(self.config)

    def on_notif_toggle(self):
        self.config["ui"]["notifications_enabled"] = self.notif_toggle.get()
        self.config_mgr.save(self.config)

    def on_severity_change(self, val):
        self.sev_label.configure(text=f"{int(float(val))}%")
        self.config["ui"]["severity"] = float(val)
        self.config_mgr.save(self.config)

    def open_config_folder(self):
        path = str(self.config_mgr.config_dir)
        try:
            if CURRENT_OS == "Windows":
                os.startfile(path)
            elif CURRENT_OS == "Darwin":
                import subprocess
                subprocess.run(['open', path])
            else:
                import subprocess
                subprocess.run(['xdg-open', path])
        except Exception:
            tkmb.showinfo("Percorso configurazione", f"Cartella: {path}")
    
    def toggle_autostart(self):
        if self.autostart_switch.get():
            success, msg = self.autostart_mgr.enable(minimized=True)
            if success:
                self.config["autostart"]["enabled"] = True
                self.config_mgr.save(self.config)
                tkmb.showinfo("Autostart abilitato", msg)
            else:
                self.autostart_switch.deselect()
                tkmb.showerror("Errore autostart", msg)
        else:
            success, msg = self.autostart_mgr.disable()
            if success:
                self.config["autostart"]["enabled"] = False
                self.config_mgr.save(self.config)
                tkmb.showinfo("Autostart disabilitato", msg)
            else:
                self.autostart_switch.select()
                tkmb.showerror("Errore autostart", msg)

    def save_kpi(self):
        now = time.strftime("%Y%m%d_%H%M%S")
        fname = f"kpi_{now}.csv"
        try:
            with open(fname, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "total_frames", "good_frames", "efficiency"])
                writer.writerow([
                    time.time(),
                    self.total_frames,
                    self.good_frames,
                    (self.good_frames / self.total_frames if self.total_frames > 0 else 1.0)
                ])
            tkmb.showinfo("Salvato", f"KPI salvati: {os.path.abspath(fname)}")
        except Exception as e:
            tkmb.showerror("Errore salvataggio", str(e))

    # ---------- TRAY ----------
    def setup_tray(self):
        icon_img = self.load_and_colorize_icon(color_overlay=(0, 255, 0))
        menu = pystray.Menu(
            item('Apri Interfaccia', self.show_window, default=True),
            pystray.Menu.SEPARATOR,
            item('Pausa Monitoraggio', self.toggle_pause_tray, checked=lambda item: self.is_paused),
            item('Stop Camera', self.toggle_stop_tray, checked=lambda item: self.camera_stopped),
            pystray.Menu.SEPARATOR,
            item('Ricalibra', self.trigger_calib_tray),
            item('Esci', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("BioPosture", icon_img, "BioPosture", menu)
        try:
            self.tray_icon.run()
        except Exception:
            pass

    def load_and_colorize_icon(self, color_overlay=(0, 255, 0)):
        try:
            ico_path = None
            icon_filename = 'BioPosture.ico' if CURRENT_OS == "Windows" else 'BioPosture.png'
            
            possible_paths = [
                icon_filename,
                os.path.join(os.path.dirname(__file__), icon_filename),
                os.path.join(sys._MEIPASS, icon_filename) if getattr(sys, 'frozen', False) else None
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    ico_path = path
                    break
            
            if ico_path:
                icon = Image.open(ico_path)
                icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
                if icon.mode != 'RGBA':
                    icon = icon.convert('RGBA')
                overlay = Image.new('RGBA', icon.size, color_overlay + (80,))
                icon = Image.alpha_composite(icon, overlay)
                return icon
            else:
                return self.create_tray_icon_fallback(color_overlay)
        except Exception:
            return self.create_tray_icon_fallback(color_overlay)

    def create_tray_icon_fallback(self, color=(0, 255, 0)):
        image = Image.new('RGB', (64, 64), (20, 20, 20))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=color)
        return image

    def update_tray_icon_color(self, posture_ok):
        if self.tray_icon:
            if self.is_paused or self.camera_stopped:
                return

            if posture_ok != self.current_posture_ok:
                self.current_posture_ok = posture_ok
                color = (0, 255, 0) if posture_ok else (255, 0, 0)
                new_icon = self.load_and_colorize_icon(color_overlay=color)
                self.tray_icon.icon = new_icon

    def hide_to_tray(self):
        show_os_notification("BioPosture", "Monitoraggio attivo in background")
        self.withdraw()
        self.minimized = True

    def show_window(self, icon=None, item=None):
        self.deiconify()
        self.minimized = False
        self.lift()

    def trigger_calib_tray(self, icon=None, item=None):
        self.show_window()
        self.start_calibration()

    def quit_app(self, icon=None, item=None):
        self.config["session"]["total_frames"] = self.total_frames
        self.config["session"]["good_frames"] = self.good_frames
        self.config["session"]["last_session_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.config_mgr.save(self.config)
        
        self.running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        self.destroy()
        sys.exit()

    def on_close(self):
        if tkmb.askyesno(
            "Chiudi",
            "Chiudere l'app (si fermerà il monitoraggio) o ridurla in tray?\nYes = Chiudi, No = Riduci in tray"
        ):
            self.quit_app()
        else:
            self.hide_to_tray()
            
    def toggle_pause_tray(self, icon=None, item=None):
        self.is_paused = not self.is_paused
        if not self.minimized:
            if self.is_paused:
                self.lbl_status.configure(text="SISTEMA IN PAUSA", text_color="orange")
            else:
                self.lbl_status.configure(text="MONITORAGGIO ATTIVO", text_color=GLOSS_SECONDARY)
        
        if self.is_paused:
             new_icon = self.load_and_colorize_icon(color_overlay=(255, 165, 0))
             if self.tray_icon: self.tray_icon.icon = new_icon

    def toggle_stop_tray(self, icon=None, item=None):
        self.toggle_camera()

    # ---------- CALIBRAZIONE ----------
    def start_calibration(self):
        if not self.camera_available:
            tkmb.showwarning("Camera non pronta", "La fotocamera non è disponibile per la calibrazione.")
            return
        if not self.models_loaded:
             tkmb.showinfo("Attendi", "I modelli AI si stanno avviando, riprova tra qualche secondo.")
             return
             
        self.calibrated = False
        self.btn_calib.configure(state="disabled", text="CALIBRAZIONE IN CORSO...", fg_color="gray")
        self.lbl_status.configure(text="MANTIENI POSTURA NEUTRA", text_color="#F1C40F")
        self.calib_start = time.time()
        self.calib_buffer = {"iris": [], "ht": [], "st": [], "neck": []}

    # ---------- CORE LOOP ----------
    def process_loop(self):
        if not self.running:
            return

        if not self.models_loaded:
            self.lbl_vid.configure(text="AVVIO MOTORE NEURALE...")
            self.after(100, self.process_loop)
            return

        if self.camera_stopped:
            self.after(200, self.process_loop)
            return

        if self.is_paused:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    h_vid, w_vid, _ = frame.shape
                    scale = 768 / w_vid
                    frame = cv2.resize(frame, (768, int(h_vid * scale)))
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.lbl_vid.configure(image=imgtk)
                    self.lbl_vid.image = imgtk
            self.after(100, self.process_loop)
            return
        
        backend = cv2.CAP_DSHOW if CURRENT_OS == "Windows" else cv2.CAP_ANY
            
        if self.cap is None or not getattr(self.cap, "isOpened", lambda: False)():
            try:
                self.cap = cv2.VideoCapture(self.cam_index, backend)
                if not getattr(self.cap, "isOpened", lambda: False)():
                    if not self.camera_error_shown:
                        tkmb.showerror(
                            "Camera non disponibile",
                            "La fotocamera non è disponibile. Chiudi altre app che la usano e premi OK quando sei pronto."
                        )
                        self.camera_error_shown = True
                    self.camera_available = False
                    self.lbl_status.configure(text="CAMERA NON DISPONIBILE", text_color="orange")
                    self.after(2000, self.process_loop)
                    return
                else:
                    self.camera_available = True
                    self.camera_error_shown = False
                    self._consecutive_read_fail = 0
                    self.lbl_vid.configure(text="", image=None)
            except Exception:
                if not self.camera_error_shown:
                    tkmb.showerror(
                        "Errore apertura camera",
                        "Impossibile aprire la fotocamera. Controlla driver/permessi."
                    )
                    self.camera_error_shown = True
                self.camera_available = False
                self.after(2000, self.process_loop)
                return

        ret, frame = self.cap.read()
        if not ret:
            self._consecutive_read_fail += 1
            if self._consecutive_read_fail < 6:
                self.lbl_status.configure(text="FRAME NON DISPONIBILE (skip)", text_color="orange")
                self.after(30, self.process_loop)
                return
            else:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
                self.camera_available = False
                if not self.camera_error_shown:
                    tkmb.showerror(
                        "Camera persa",
                        "La connessione alla fotocamera è stata persa. Chiudi altre app che la usano e premi OK."
                    )
                    self.camera_error_shown = True
                self.after(2000, self.process_loop)
                return
        else:
            self._consecutive_read_fail = 0

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        curr = {"iris": 0, "ht": 0, "st": 0, "neck": 0}
        valid_pose = False

        if self.mp_face and self.mp_pose:
            res_face = self.mp_face.process(rgb)
            if getattr(res_face, "multi_face_landmarks", None):
                lm = res_face.multi_face_landmarks[0].landmark
                p1 = np.array([lm[468].x * w, lm[468].y * h])
                p2 = np.array([lm[473].x * w, lm[473].y * h])
                curr["iris"] = self.sm_iris.update(np.linalg.norm(p1 - p2))
                cv2.circle(frame, tuple(p1.astype(int)), 3, (0, 255, 255), -1)
                cv2.circle(frame, tuple(p2.astype(int)), 3, (0, 255, 255), -1)

            res_pose = self.mp_pose.process(rgb)
            if getattr(res_pose, "pose_landmarks", None):
                valid_pose = True
                lm = res_pose.pose_landmarks.landmark
                ear_l = np.array([lm[7].x * w, lm[7].y * h])
                ear_r = np.array([lm[8].x * w, lm[8].y * h])
                sh_l = np.array([lm[11].x * w, lm[11].y * h])
                sh_r = np.array([lm[12].x * w, lm[12].y * h])

                raw_ht = abs(calc_angle(ear_r, ear_l))
                val_ht = abs(180 - raw_ht) if raw_ht > 90 else raw_ht
                curr["ht"] = self.sm_ht.update(val_ht)

                raw_st = abs(calc_angle(sh_r, sh_l))
                val_st = abs(180 - raw_st) if raw_st > 90 else raw_st
                curr["st"] = self.sm_st.update(val_st)

                mid_ear_y = (ear_l[1] + ear_r[1]) / 2
                mid_sh_y = (sh_l[1] + sh_r[1]) / 2
                raw_neck_px = abs(mid_sh_y - mid_ear_y)

                if curr["iris"] > 0:
                    ratio_neck = raw_neck_px / curr["iris"]
                    curr["neck"] = self.sm_neck.update(ratio_neck)

                cv2.line(frame, tuple(ear_l.astype(int)), tuple(ear_r.astype(int)), (0, 255, 0), 2)
                cv2.line(frame, tuple(sh_l.astype(int)), tuple(sh_r.astype(int)), (0, 255, 0), 2)
                cx_ear = int((ear_l[0] + ear_r[0]) / 2)
                cx_sh = int((sh_l[0] + sh_r[0]) / 2)
                cv2.line(frame, (cx_ear, int(mid_ear_y)), (cx_sh, int(mid_sh_y)), (255, 0, 255), 2)

        thresholds = self.config["thresholds"]
        sev = float(self.severity_var.get())
        sev_norm = sev / 100.0
        
        tol_factor = 1.5 - sev_norm
        time_factor = 2.0 - (sev_norm * 1.5)

        ang_thresh = thresholds["soglia_angoli"] * tol_factor
        dist_max = 1.0 + (thresholds["soglia_dist_max"] - 1.0) * tol_factor
        dist_min = 1.0 - (1.0 - thresholds["soglia_dist_min"]) * tol_factor
        comp_thresh = 1.0 - (1.0 - thresholds["soglia_compressione"]) * tol_factor

        if hasattr(self, 'calib_start') and getattr(self, 'calib_start', None):
            elapsed = time.time() - self.calib_start
            if elapsed < 5.0:
                if curr["iris"] > 0 and valid_pose:
                    for k in self.calib_buffer:
                        self.calib_buffer[k].append(curr[k])
                    cv2.putText(
                        frame,
                        f"CALIB... {5 - elapsed:.1f}",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 165, 255),
                        3
                    )
            else:
                if len(self.calib_buffer["iris"]) > 10:
                    for k in self.baseline:
                        self.baseline[k] = np.mean(self.calib_buffer[k])
                    
                    self.config["calibration"]["iris"] = float(self.baseline["iris"])
                    self.config["calibration"]["ht"] = float(self.baseline["ht"])
                    self.config["calibration"]["st"] = float(self.baseline["st"])
                    self.config["calibration"]["neck"] = float(self.baseline["neck"])
                    self.config["calibration"]["is_calibrated"] = True
                    self.config_mgr.save(self.config)
                    
                    self.calibrated = True
                    self.btn_calib.configure(state="normal", text="RICALIBRA", fg_color=GLOSS_PRIMARY)
                    self.lbl_status.configure(text="MONITORAGGIO ATTIVO", text_color=GLOSS_SECONDARY)
                    self.total_frames = 0
                    self.good_frames = 0
                else:
                    self.lbl_status.configure(text="CALIBRAZIONE FALLITA", text_color="red")
                    self.btn_calib.configure(state="normal", text="RIPROVA")
                self.calib_start = None

        elif self.calibrated and curr["iris"] > 0:
            delta_ht = abs(curr["ht"] - self.baseline["ht"])
            delta_st = abs(curr["st"] - self.baseline["st"])

            ratio_dist = curr["iris"] / self.baseline["iris"] if self.baseline["iris"] != 0 else 1.0
            err_close = ratio_dist > dist_max
            err_far = ratio_dist < dist_min

            ratio_neck = curr["neck"] / self.baseline["neck"] if self.baseline["neck"] != 0 else 1.0
            err_neck = ratio_neck < comp_thresh

            err_ht = delta_ht > ang_thresh
            err_st = delta_st > ang_thresh

            any_error = err_ht or err_st or err_close or err_neck or err_far

            self.total_frames += 1
            if not any_error:
                self.good_frames += 1
            efficiency = (self.good_frames / self.total_frames) if self.total_frames > 0 else 1.0

            msg = "POSTURA OK"
            col = GLOSS_SECONDARY
            posture_ok = True

            if any_error:
                if not hasattr(self, 'error_timer') or self.error_timer is None:
                    self.error_timer = time.time()
                
                alert_delay = thresholds["tempo_allarme"] * time_factor
                
                if (time.time() - self.error_timer) > alert_delay:
                    col = GLOSS_ERROR
                    posture_ok = False
                    if err_neck:
                        msg = "COLLO IN TENSIONE"
                    elif err_ht:
                        msg = "INCLINAZIONE TESTA"
                    elif err_close:
                        msg = "TROPPO VICINO AL DISPLAY"
                    elif err_st:
                        msg = "SPALLE ASIMMETRICHE"
                    elif err_far:
                        msg = "TROPPO LONTANO DAL DISPLAY"

                    now = time.time()
                    if self.notif_toggle.get():
                        if now - self.last_notif_time > thresholds["cooldown_notifica"]:
                            show_os_notification("BioPosture - Allarme postura", msg)
                            self.last_notif_time = now
                else:
                    col = "#FFC107"
                    msg = "ATTENZIONE..."
                    posture_ok = False
            else:
                self.error_timer = None

            self.update_tray_icon_color(posture_ok)

            if not self.minimized:
                self.lbl_status.configure(text=msg, text_color=col)
                self.lbl_v_ht.configure(text=f"{delta_ht:.1f}°")
                self.lbl_v_st.configure(text=f"{delta_st:.1f}°")
                cm_dist = 60 * (1 / ratio_dist) if ratio_dist != 0 else 0
                self.lbl_v_dist.configure(text=f"{cm_dist:.0f} cm")
                perc_neck = ratio_neck * 100
                self.lbl_v_neck.configure(text=f"{perc_neck:.0f}%", text_color=GLOSS_ERROR if err_neck else GLOSS_TEXT)

                self.progress_eff.set(efficiency)
                eff_text = int(efficiency * 100)
                self.lbl_eff_text.configure(text=f"{eff_text}%")
                if eff_text > 80:
                    self.progress_eff.configure(progress_color=GLOSS_SECONDARY)
                elif eff_text > 50:
                    self.progress_eff.configure(progress_color="#FFC107")
                else:
                    self.progress_eff.configure(progress_color=GLOSS_ERROR)

                self.graph_widget.update_data(delta_ht, perc_neck)

        h_vid, w_vid, _ = frame.shape
        scale = 768 / w_vid
        frame = cv2.resize(frame, (768, int(h_vid * scale)))
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.lbl_vid.configure(image=imgtk)
        self.lbl_vid.image = imgtk

        self.after(30, self.process_loop)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='BioPosture - Monitoraggio Postura')
    parser.add_argument('--minimized', action='store_true', 
                       help='Avvia applicazione minimizzata in system tray')
    args = parser.parse_args()
    
    app = BioPostureApp()
    if args.minimized:
        app.after(1000, app.hide_to_tray)
    app.mainloop()