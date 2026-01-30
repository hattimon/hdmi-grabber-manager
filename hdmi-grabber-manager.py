#!/usr/bin/env python3
"""
HDMI Grabber Manager - UGREEN Optimized + wybór języka + wybór urządzenia
+ automatyczne wykrywanie grabbera po nazwie karty
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from glob import glob

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QLabel, QPushButton, QMessageBox, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

CONFIG_DIR = Path.home() / ".config" / "hdmi-grabber"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
DEFAULT_DEVICE = "/dev/video2"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

TRANSLATIONS = {
    "PL": {
        "title": "UGREEN HDMI Grabber Manager",
        "language": "Język",
        "start": "START Grabber",
        "stop": "STOP",
        "apply": "Zastosuj",
        "reset": "Domyślne",
        "brightness": "Jasność",
        "contrast": "Kontrast",
        "saturation": "Nasycenie",
        "hue": "Barwa",
        "preset": "Wybierz preset",
        "device": "Urządzenie video",
        "refresh_devices": "Odśwież urządzenia",
        "save_device": "Zapisz urządzenie",
        "success": "Sukces!",
        "error": "Błąd",
        "controls_applied": "Kontrolki zastosowane!",
        "grabber_running": "Grabber już działa!",
        "ready": "Gotowy",
        "confirm_reset": "Reset do domyślnych?",
        "no_device": "Nie znaleziono urządzeń video!",
        "double_click_info": "Podwójne kliknięcie na oknie podglądu maksymalizuje / minimalizuje je",
        "devices_found": "Wykryto {} urządzeń video",
        "device_saved": "Zapamiętano urządzenie: {}"
    },
    "EN": {
        "title": "UGREEN HDMI Grabber Manager",
        "language": "Language",
        "start": "START Grabber",
        "stop": "STOP",
        "apply": "Apply",
        "reset": "Reset",
        "brightness": "Brightness",
        "contrast": "Contrast",
        "saturation": "Saturation",
        "hue": "Hue",
        "preset": "Select Preset",
        "device": "Video Device",
        "refresh_devices": "Refresh Devices",
        "save_device": "Save Device",
        "success": "Success!",
        "error": "Error",
        "controls_applied": "Controls applied!",
        "grabber_running": "Grabber is running!",
        "ready": "Ready",
        "confirm_reset": "Reset to defaults?",
        "no_device": "No video devices found!",
        "double_click_info": "Double-click on the preview window to maximize / minimize it",
        "devices_found": "Detected {} video devices",
        "device_saved": "Saved device: {}"
    }
}

DEFAULT_CONTROLS = {
    "brightness": -11,
    "contrast": 148,
    "saturation": 180,
    "hue": 0
}

PRESETS = [
    {"name_pl": "1080p @ 30 fps", "name_en": "1080p @ 30 fps", "width": 1920, "height": 1080, "fps": "30"},
    {"name_pl": "1080p @ 60 fps", "name_en": "1080p @ 60 fps", "width": 1920, "height": 1080, "fps": "60"},
    {"name_pl": "720p @ 30 fps",  "name_en": "720p @ 30 fps",  "width": 1280, "height": 720,  "fps": "30"},
    {"name_pl": "720p @ 60 fps",  "name_en": "720p @ 60 fps",  "width": 1280, "height": 720,  "fps": "60"},
]

# ===================== GRABBER THREAD =====================
class GrabberThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, device, width, height, fps):
        super().__init__()
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.process = None
        self._stop = False

    def run(self):
        try:
            cmd = [
                "ffplay", "-f", "v4l2",
                "-input_format", "mjpeg",
                "-video_size", f"{self.width}x{self.height}",
                "-framerate", self.fps,
                "-fflags", "nobuffer",
                "-flags", "low_delay",
                "-probesize", "32",
                "-analyzeduration", "0",
                self.device,
                "-noborder", "-window_title", "UGREEN HDMI Live"
            ]
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process.wait()
        except Exception as e:
            if not self._stop:
                self.error.emit(str(e))
        finally:
            self.finished.emit()

    def stop(self):
        self._stop = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(2)
            except:
                self.process.kill()

# ===================== V4L2 CONTROLLER =====================
class V4L2Controller:
    def __init__(self, device):
        self.device = device

    def run_cmd(self, cmd, timeout=5):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def set_controls(self, b, c, s, h):
        cmd = ["v4l2-ctl", "-d", self.device,
               f"--set-ctrl=brightness={b},contrast={c},saturation={s},hue={h}"]
        return self.run_cmd(cmd)[0]

    def test_device(self):
        return os.path.exists(self.device)

# ===================== MAIN APP =====================
class HDMIGrabberManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "EN"
        self.current_controls = DEFAULT_CONTROLS.copy()
        self.is_running = False
        self.grabber_thread = None
        self.current_device = self.detect_grabber_device()  # <- AUTO DETECTION

        self.init_ui()
        self.load_settings()
        self.update_ui_language()
        self.refresh_video_devices()

    # ---------- AUTO DETEKCJA URZĄDZENIA ----------
    def detect_grabber_device(self):
        for dev in sorted(glob("/dev/video*")):
            try:
                output = subprocess.check_output(["v4l2-ctl", "--all", "-d", dev],
                                                 text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    if "Device name" in line and "UGREEN" in line:
                        return dev
            except:
                continue
        return DEFAULT_DEVICE

    # ---------- UI INIT ----------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        # Language selection
        lang_layout = QHBoxLayout()
        self.lbl_lang = QLabel("...")
        lang_layout.addWidget(self.lbl_lang)
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["English (EN)", "Polski (PL)"])
        self.cb_lang.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.cb_lang)
        self.main_layout.addLayout(lang_layout)

        # Device selection
        dev_layout = QHBoxLayout()
        self.lbl_device = QLabel("...")
        dev_layout.addWidget(self.lbl_device)
        self.cb_device = QComboBox()
        dev_layout.addWidget(self.cb_device)
        self.btn_refresh_dev = QPushButton("...")
        self.btn_refresh_dev.clicked.connect(self.refresh_video_devices)
        dev_layout.addWidget(self.btn_refresh_dev)
        self.btn_save_dev = QPushButton("...")
        self.btn_save_dev.clicked.connect(self.save_current_device)
        dev_layout.addWidget(self.btn_save_dev)
        self.main_layout.addLayout(dev_layout)

        self.status = QLabel("...")
        self.main_layout.addWidget(self.status)

        # Preset selection
        self.preset_group = QGroupBox("...")
        preset_lay = QVBoxLayout(self.preset_group)
        self.lbl_preset = QLabel("...")
        preset_lay.addWidget(self.lbl_preset)
        self.cb_preset = QComboBox()
        preset_lay.addWidget(self.cb_preset)
        self.preset_group.setLayout(preset_lay)
        self.main_layout.addWidget(self.preset_group)

        # Control sliders
        self.ctrl_group = QGroupBox("...")
        ctrl_lay = QVBoxLayout(self.ctrl_group)

        def slider(key, minv, maxv, defv, attr):
            lbl = QLabel("...")
            s = QSlider(Qt.Horizontal)
            s.setRange(minv, maxv)
            s.setValue(defv)
            val = QLabel(str(defv))
            s.valueChanged.connect(lambda v: val.setText(str(v)))
            hbox = QHBoxLayout()
            hbox.addWidget(s)
            hbox.addWidget(val)
            ctrl_lay.addWidget(lbl)
            ctrl_lay.addLayout(hbox)
            setattr(self, f"{attr}_slider", s)
            setattr(self, f"{attr}_lbl", lbl)

        slider("brightness", -128, 127, DEFAULT_CONTROLS["brightness"], "brightness")
        slider("contrast", 0, 255, DEFAULT_CONTROLS["contrast"], "contrast")
        slider("saturation", 0, 255, DEFAULT_CONTROLS["saturation"], "saturation")
        slider("hue", -128, 127, DEFAULT_CONTROLS["hue"], "hue")

        self.main_layout.addWidget(self.ctrl_group)

        # Apply / Reset buttons
        bl = QHBoxLayout()
        self.btn_apply = QPushButton("...")
        self.btn_apply.clicked.connect(self.apply_controls)
        bl.addWidget(self.btn_apply)

        self.btn_reset = QPushButton("...")
        self.btn_reset.clicked.connect(self.reset_controls)
        bl.addWidget(self.btn_reset)
        self.main_layout.addLayout(bl)

        # Toggle grabber
        self.btn_toggle = QPushButton("...")
        self.btn_toggle.setStyleSheet("font-size: 22px; padding: 20px; background: #27ae60; color: white;")
        self.btn_toggle.clicked.connect(self.toggle_grabber)
        self.main_layout.addWidget(self.btn_toggle)

        self.main_layout.addStretch()

    # ---------- VIDEO DEVICES ----------
    def refresh_video_devices(self):
        devices = sorted(glob("/dev/video*"))
        self.cb_device.clear()
        if not devices:
            self.cb_device.addItem("Brak urządzeń")
            self.status.setText(TRANSLATIONS[self.lang]["no_device"])
            return

        for dev in devices:
            self.cb_device.addItem(dev)

        # Restore last device if available
        if self.current_device in devices:
            self.cb_device.setCurrentText(self.current_device)
        else:
            self.cb_device.setCurrentIndex(0)

        self.current_device = self.cb_device.currentText()
        self.status.setText(TRANSLATIONS[self.lang]["devices_found"].format(len(devices)))

    def save_current_device(self):
        self.current_device = self.cb_device.currentText()
        self.save_settings()
        # <-- POPRAWIONE: użycie TRANSLATIONS w zależności od języka
        self.status.setText(TRANSLATIONS[self.lang]["device_saved"].format(self.current_device))

    # ---------- LANGUAGE ----------
    def change_language(self, index):
        self.lang = "EN" if index == 0 else "PL"
        self.update_ui_language()
        self.save_settings()

    def update_ui_language(self):
        tr = TRANSLATIONS[self.lang]

        self.setWindowTitle(tr["title"])
        self.lbl_lang.setText(tr["language"])
        self.btn_toggle.setText(tr["start"] if not self.is_running else tr["stop"])
        self.btn_apply.setText(tr["apply"])
        self.btn_reset.setText(tr["reset"])
        self.preset_group.setTitle(tr["preset"])
        self.lbl_preset.setText(tr["preset"])
        self.lbl_device.setText(tr["device"])
        self.btn_refresh_dev.setText(tr["refresh_devices"])
        self.btn_save_dev.setText(tr["save_device"])

        self.brightness_lbl.setText(tr["brightness"])
        self.contrast_lbl.setText(tr["contrast"])
        self.saturation_lbl.setText(tr["saturation"])
        self.hue_lbl.setText(tr["hue"])

        self.cb_preset.clear()
        key = "name_pl" if self.lang == "PL" else "name_en"
        self.cb_preset.addItems([p[key] for p in PRESETS])

        self.status.setText(tr["ready"] if not self.is_running else tr["grabber_running"])

    # ---------- CONTROLS ----------
    def apply_controls(self):
        b = self.brightness_slider.value()
        c = self.contrast_slider.value()
        s = self.saturation_slider.value()
        h = self.hue_slider.value()

        v4l2 = V4L2Controller(self.current_device)
        if v4l2.set_controls(b, c, s, h):
            self.current_controls = {"brightness": b, "contrast": c, "saturation": s, "hue": h}
            self.save_settings()
            QMessageBox.information(self, 
                TRANSLATIONS[self.lang]["success"], 
                TRANSLATIONS[self.lang]["controls_applied"] + "\n\n" + TRANSLATIONS[self.lang]["double_click_info"])
        else:
            QMessageBox.warning(self, TRANSLATIONS[self.lang]["error"], "v4l2-ctl error")

    def reset_controls(self):
        self.brightness_slider.setValue(DEFAULT_CONTROLS["brightness"])
        self.contrast_slider.setValue(DEFAULT_CONTROLS["contrast"])
        self.saturation_slider.setValue(DEFAULT_CONTROLS["saturation"])
        self.hue_slider.setValue(DEFAULT_CONTROLS["hue"])
        self.apply_controls()

    # ---------- GRABBER ----------
    def toggle_grabber(self):
        if self.is_running:
            self.stop_grabber()
        else:
            self.start_grabber()

    def start_grabber(self):
        if self.is_running:
            return

        preset_idx = self.cb_preset.currentIndex()
        preset = PRESETS[preset_idx]

        w = preset["width"]
        h = preset["height"]
        fps = preset["fps"]

        self.is_running = True
        self.btn_toggle.setText(TRANSLATIONS[self.lang]["stop"])
        self.btn_toggle.setStyleSheet("font-size: 22px; padding: 20px; background: #c0392b; color: white;")

        self.apply_controls()

        self.grabber_thread = GrabberThread(self.current_device, w, h, fps)
        self.grabber_thread.finished.connect(self.on_grabber_finished)
        self.grabber_thread.error.connect(self.on_grabber_error)
        self.grabber_thread.start()

        preset_key = "name_pl" if self.lang == "PL" else "name_en"
        self.status.setText(f"Started: {preset[preset_key]} on {self.current_device}")

    def stop_grabber(self):
        if not self.is_running or not self.grabber_thread:
            return

        self.grabber_thread.stop()
        self.grabber_thread.wait(5000)

        self.is_running = False
        self.btn_toggle.setText(TRANSLATIONS[self.lang]["start"])
        self.btn_toggle.setStyleSheet("font-size: 22px; padding: 20px; background: #27ae60; color: white;")
        self.status.setText(TRANSLATIONS[self.lang]["ready"])

    def on_grabber_finished(self):
        self.is_running = False
        self.btn_toggle.setText(TRANSLATIONS[self.lang]["start"])
        self.btn_toggle.setStyleSheet("font-size: 22px; padding: 20px; background: #27ae60; color: white;")
        self.status.setText("Grabber stopped")

    def on_grabber_error(self, msg):
        QMessageBox.critical(self, TRANSLATIONS[self.lang]["error"], msg)
        self.stop_grabber()

    # ---------- SETTINGS ----------
    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.current_controls.update(data.get('controls', {}))
                    self.lang = data.get('language', 'EN')
                    self.cb_lang.setCurrentIndex(0 if self.lang == 'EN' else 1)
                    self.current_device = data.get('device', self.current_device)
            except:
                pass

        self.brightness_slider.setValue(self.current_controls["brightness"])
        self.contrast_slider.setValue(self.current_controls["contrast"])
        self.saturation_slider.setValue(self.current_controls["saturation"])
        self.hue_slider.setValue(self.current_controls["hue"])

    def save_settings(self):
        data = {
            'controls': self.current_controls,
            'language': self.lang,
            'device': self.current_device
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def closeEvent(self, event):
        self.stop_grabber()
        event.accept()

# ===================== MAIN =====================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HDMIGrabberManager()
    window.show()
    sys.exit(app.exec_())
