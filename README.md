# HDMI Grabber Manager

> **Language:** [English](#english) | [Polski](#polski)

---

## <a name="english"></a>English (default)

**HDMI Grabber Manager** is a simple tool for managing HDMI capture devices. It allows you to easily view, record, and manage HDMI input sources on your system.

### Features

* Detect and list HDMI capture devices
* Live preview of HDMI input
* Easy recording to local storage
* Lightweight and fast

### Screenshots

![App Screenshot EN](ugreenEN.png)

### Installation

You can install directly from this repository:

```bash
# Clone the repository
git clone https://github.com/hattimon/hdmi-grabber-manager.git
cd hdmi-grabber-manager

# Install dependencies (example for Python project)
pip install -r requirements.txt

# Run the application
python app.py
```

Or download the latest release from GitHub and run the binary (if provided).

### Usage

```bash
# Start the app
python app.py

# Show available devices
python app.py --list

# Record from a specific device
python app.py --record 0 --output capture.mp4
```

---

## <a name="polski"></a>Polski

**HDMI Grabber Manager** to proste narzędzie do zarządzania urządzeniami do przechwytywania HDMI. Pozwala łatwo przeglądać, nagrywać i zarządzać źródłami HDMI w systemie.

### Funkcje

* Wykrywanie i lista urządzeń HDMI
* Podgląd na żywo HDMI
* Proste nagrywanie na dysk lokalny
* Lekki i szybki

### Zrzuty ekranu

![App Screenshot PL](ugreenPL.png)

### Instalacja

Możesz zainstalować bezpośrednio z repozytorium:

```bash
# Sklonuj repozytorium
git clone https://github.com/hattimon/hdmi-grabber-manager.git
cd hdmi-grabber-manager

# Zainstaluj zależności (przykład dla projektu Python)
pip install -r requirements.txt

# Uruchom aplikację
python app.py
```

Lub pobierz najnowszą wersję z GitHub i uruchom binarkę (jeśli jest dostępna).

### Użytkowanie

```bash
# Uruchom aplikację
python app.py

# Pokaż dostępne urządzenia
python app.py --list

# Nagrywaj z wybranego urządzenia
python app.py --record 0 --output capture.mp4
```

---

**License:** MIT
**Repository:** [https://github.com/hattimon/hdmi-grabber-manager](https://github.com/hattimon/hdmi-grabber-manager)
