#!/usr/bin/env python3
"""
HDMI Grabber Manager - UGREEN Optimized + language + device selection
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
        "device_saved": "Zapamiętano urządzenie: {}",
        "started": "Uruchomiono: {} na {}",
        "stopped": "Grabber zatrzymany",
        "v4l2_error": "Błąd v4l2-ctl"
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
        "device_saved": "Saved device: {}",
        "started": "Started: {} on {}",
        "stopped": "Grabber stopped",
        "v4l2_error": "v4l2-ctl error"
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

class V4L2Controller:
    def __init__(self, device):
        self.device = device

    def set_controls(self, b, c, s, h):
        cmd = ["v4l2-ctl", "-d", self.device,
               f"--set-ctrl=brightness={b},contrast={c},saturation={s},hue={h}"]
        return subprocess.call(cmd) == 0

class HDMIGrabberManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "EN"
        self.current_controls = DEFAULT_CONTROLS.copy()
        self.is_running = False
        self.grabber_thread = None
        self.current_device = DEFAULT_DEVICE

        self.init_ui()
        self.load_settings()
        self.update_ui_language()
        self.refresh_video_devices()

    # ---------- UI ----------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        lang_layout = QHBoxLayout()
        self.lbl_lang = QLabel()
        lang_layout.addWidget(self.lbl_lang)
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["English (EN)", "Polski (PL)"])
        self.cb_lang.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.cb_lang)
        self.main_layout.addLayout(lang_layout)

        dev_layout = QHBoxLayout()
        self.lbl_device = QLabel()
        dev_layout.addWidget(self.lbl_device)
        self.cb_device = QComboBox()
        dev_layout.addWidget(self.cb_device)
        self.btn_refresh_dev = QPushButton()
        self.btn_refresh_dev.clicked.connect(self.refresh_video_devices)
        dev_layout.addWidget(self.btn_refresh_dev)
        self.btn_save_dev = QPushButton()
        self.btn_save_dev.clicked.connect(self.save_current_device)
        dev_layout.addWidget(self.btn_save_dev)
        self.main_layout.addLayout(dev_layout)

        self.status = QLabel()
        self.main_layout.addWidget(self.status)

        self.preset_group = QGroupBox()
        preset_lay = QVBoxLayout(self.preset_group)
        self.lbl_preset = QLabel()
        preset_lay.addWidget(self.lbl_preset)
        self.cb_preset = QComboBox()
        preset_lay.addWidget(self.cb_preset)
        self.main_layout.addWidget(self.preset_group)

        self.ctrl_group = QGroupBox()
        ctrl_lay = QVBoxLayout(self.ctrl_group)

        def slider(minv, maxv, defv, attr):
            lbl = QLabel()
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

        slider(-128, 127, DEFAULT_CONTROLS["brightness"], "brightness")
        slider(0, 255, DEFAULT_CONTROLS["contrast"], "contrast")
        slider(0, 255, DEFAULT_CONTROLS["saturation"], "saturation")
        slider(-128, 127, DEFAULT_CONTROLS["hue"], "hue")

        self.main_layout.addWidget(self.ctrl_group)

        bl = QHBoxLayout()
        self.btn_apply = QPushButton()
        self.btn_apply.clicked.connect(self.apply_controls)
        bl.addWidget(self.btn_apply)

        self.btn_reset = QPushButton()
        self.btn_reset.clicked.connect(self.reset_controls)
        bl.addWidget(self.btn_reset)
        self.main_layout.addLayout(bl)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setStyleSheet("font-size:22px;padding:20px;background:#27ae60;color:white;")
        self.btn_toggle.clicked.connect(self.toggle_grabber)
        self.main_layout.addWidget(self.btn_toggle)

    # ---------- DEVICES ----------
    def refresh_video_devices(self):
        tr = TRANSLATIONS[self.lang]
        devices = sorted(glob("/dev/video*"))
        self.cb_device.clear()

        if not devices:
            self.cb_device.addItem(tr["no_device"])
            self.status.setText(tr["no_device"])
            return

        self.cb_device.addItems(devices)

        if self.current_device in devices:
            self.cb_device.setCurrentText(self.current_device)
        else:
            self.cb_device.setCurrentIndex(0)

        self.current_device = self.cb_device.currentText()
        self.status.setText(tr["devices_found"].format(len(devices)))

    def save_current_device(self):
        tr = TRANSLATIONS[self.lang]
        self.current_device = self.cb_device.currentText()
        self.save_settings()
        self.status.setText(tr["device_saved"].format(self.current_device))

    # ---------- LANGUAGE ----------
    def change_language(self, index):
        self.lang = "EN" if index == 0 else "PL"
        self.update_ui_language()
        self.refresh_video_devices()
        self.save_settings()

    def update_ui_language(self):
        tr = TRANSLATIONS[self.lang]

        self.setWindowTitle(tr["title"])
        self.lbl_lang.setText(tr["language"])
        self.lbl_device.setText(tr["device"])
        self.btn_refresh_dev.setText(tr["refresh_devices"])
        self.btn_save_dev.setText(tr["save_device"])
        self.btn_apply.setText(tr["apply"])
        self.btn_reset.setText(tr["reset"])
        self.btn_toggle.setText(tr["start"] if not self.is_running else tr["stop"])
        self.status.setText(tr["ready"])

        self.preset_group.setTitle(tr["preset"])
        self.lbl_preset.setText(tr["preset"])
        key = "name_pl" if self.lang == "PL" else "name_en"
        self.cb_preset.clear()
        self.cb_preset.addItems([p[key] for p in PRESETS])

        self.brightness_lbl.setText(tr["brightness"])
        self.contrast_lbl.setText(tr["contrast"])
        self.saturation_lbl.setText(tr["saturation"])
        self.hue_lbl.setText(tr["hue"])

    # ---------- CONTROLS ----------
    def apply_controls(self):
        tr = TRANSLATIONS[self.lang]
        v4l2 = V4L2Controller(self.current_device)
        if v4l2.set_controls(
            self.brightness_slider.value(),
            self.contrast_slider.value(),
            self.saturation_slider.value(),
            self.hue_slider.value()
        ):
            QMessageBox.information(self, tr["success"],
                tr["controls_applied"] + "\n\n" + tr["double_click_info"])
        else:
            QMessageBox.warning(self, tr["error"], tr["v4l2_error"])

    def reset_controls(self):
        self.brightness_slider.setValue(DEFAULT_CONTROLS["brightness"])
        self.contrast_slider.setValue(DEFAULT_CONTROLS["contrast"])
        self.saturation_slider.setValue(DEFAULT_CONTROLS["saturation"])
        self.hue_slider.setValue(DEFAULT_CONTROLS["hue"])
        self.apply_controls()

    # ---------- GRABBER ----------
    def toggle_grabber(self):
        self.stop_grabber() if self.is_running else self.start_grabber()

    def start_grabber(self):
        tr = TRANSLATIONS[self.lang]
        preset = PRESETS[self.cb_preset.currentIndex()]
        key = "name_pl" if self.lang == "PL" else "name_en"

        self.is_running = True
        self.btn_toggle.setText(tr["stop"])
        self.btn_toggle.setStyleSheet("font-size:22px;padding:20px;background:#c0392b;color:white;")

        self.grabber_thread = GrabberThread(self.current_device, preset["width"], preset["height"], preset["fps"])
        self.grabber_thread.finished.connect(self.on_grabber_finished)
        self.grabber_thread.error.connect(self.on_grabber_error)
        self.grabber_thread.start()

        self.status.setText(tr["started"].format(preset[key], self.current_device))

    def stop_grabber(self):
        tr = TRANSLATIONS[self.lang]
        if self.grabber_thread:
            self.grabber_thread.stop()
        self.is_running = False
        self.btn_toggle.setText(tr["start"])
        self.btn_toggle.setStyleSheet("font-size:22px;padding:20px;background:#27ae60;color:white;")
        self.status.setText(tr["ready"])

    def on_grabber_finished(self):
        self.is_running = False
        self.status.setText(TRANSLATIONS[self.lang]["stopped"])

    def on_grabber_error(self, msg):
        QMessageBox.critical(self, TRANSLATIONS[self.lang]["error"], msg)
        self.stop_grabber()

    # ---------- SETTINGS ----------
    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                data = json.load(open(SETTINGS_FILE))
                self.lang = data.get("language", "EN")
                self.current_device = data.get("device", DEFAULT_DEVICE)
            except:
                pass
        self.cb_lang.setCurrentIndex(0 if self.lang == "EN" else 1)

    def save_settings(self):
        json.dump({"language": self.lang, "device": self.current_device}, open(SETTINGS_FILE, "w"), indent=2)

    def closeEvent(self, e):
        self.stop_grabber()
        e.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HDMIGrabberManager()
    window.show()
    sys.exit(app.exec_())
