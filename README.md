# HDMI Grabber Manager (UGREEN) – Linux MX

GUI application for controlling UGREEN HDMI USB grabbers on Linux using **V4L2** and **ffplay**.  
Includes brightness/contrast controls, resolution presets, live preview, and device selection.

---

## ✨ Features

- 🎥 Live HDMI preview using **ffplay (MJPEG low‑latency mode)**
- 🎛 Brightness / Contrast / Saturation / Hue controls (via v4l2-ctl)
- 📺 Resolution & FPS presets (720p / 1080p @ 30/60fps)
- 🔌 Video device selector (`/dev/video*`)
- 💾 Saves last used device, language and settings
- 🌍 English & Polish interface
- 📦 Easy installation via generated **.deb package**

---

## 🐧 Supported Systems

Tested on:
- **MX Linux**
- Debian-based distributions (Ubuntu, Mint, etc.)

---

## 🔧 Build the .deb Package

### 1️⃣ Requirements (only for building)
Make sure you have:

```bash
sudo apt update
sudo apt install dpkg-dev
```

### 2️⃣ Put files in one folder

You must have:

```
install.sh
hdmi-grabber-manager.py
```

### 3️⃣ Build package

```bash
chmod +x install.sh
sudo ./install.sh
```

After completion you will get:

```
hdmi-grabber-manager_3.0.0_all.deb
```

---

## 📦 Install the Application

```bash
sudo dpkg -i hdmi-grabber-manager_3.0.0_all.deb
```

If dependencies are missing:

```bash
sudo apt -f install
```

---

## 🚀 Run the App

From menu:
```
Menu → Multimedia → HDMI Grabber Manager
```

Or terminal:
```bash
hdmi-grabber-manager
```

---

## 🎛 Controls

| Control | Description |
|--------|-------------|
| Brightness | Adjust video brightness |
| Contrast | Adjust contrast |
| Saturation | Adjust color intensity |
| Hue | Adjust color tone |
| Presets | Choose resolution and FPS |
| Device | Select HDMI capture device |

---

## 🧠 Tips

- Double‑click the preview window to toggle fullscreen
- If video is black, verify correct `/dev/videoX` device
- Use 1080p30 for best stability on slower systems

---

## 🛠 Dependencies (installed automatically via .deb)

- python3
- python3-pyqt5
- ffmpeg
- v4l-utils

---

## 👨‍💻 Author

HDMI Grabber Manager Project  
Optimized for **UGREEN HDMI Capture Cards**

---

## 📜 License

Free for personal and educational use.
