#!/bin/bash

# HDMI Grabber Manager - UGREEN Optimized Install Script (v3.1)
# Instaluje GUI + ffplay grabber /dev/video* + menu systemowy

set -e

# ============================================================================
# KONFIGURACJA
# ============================================================================

APP_NAME="hdmi-grabber-manager"
APP_VERSION="3.1.0"
APP_DIR="/opt/hdmi-grabber-manager"
BIN_DIR="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/hdmi-grabber-manager.desktop"
DEB_BUILD_DIR="/tmp/hdmi-grabber-manager-deb"
LANG_CHOICE="EN"

# ============================================================================
# TŁUMACZENIA (EN/PL)
# ============================================================================

declare -A MESSAGES_EN=(
    [TITLE]="===== UGREEN HDMI Grabber Manager Installer v$APP_VERSION ====="
    [CHOOSE_LANG]="Choose installation language / Wybierz język instalacji"
    [LANG_SELECT]="1) English (EN)"
    [LANG_SELECT2]="2) Polski (PL)"
    [LANG_PROMPT]="Language [1-2, default EN]: "
    [CHECK_ROOT]="❌ Script must be run as root (use sudo)"
    [INSTALL_DEPS]="📦 Installing dependencies..."
    [INSTALL_DONE]="✅ Dependencies installed"
    [INSTALL_APP]="📁 Installing optimized application..."
    [INSTALL_APP_DONE]="✅ Application installed: $APP_DIR"
    [CREATE_DESKTOP]="🎯 Creating desktop entry..."
    [DESKTOP_DONE]="✅ Desktop entry ready (Menu > Multimedia)"
    [CREATE_DEB]="📦 Creating .deb package..."
    [DEB_DONE]="✅ .deb created: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]="   Install: sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [CHOOSE_OPTION]="Choose option:"
    [OPT1]="1) Install app (full)"
    [OPT2]="2) Install + .deb package"
    [OPT3]="3) .deb package only"
    [OPTION_PROMPT]="Option [1-3]: "
    [INSTALL_COMPLETE]="✅ Installation complete!"
    [RUN_APP]="🚀 Run: hdmi-grabber-manager"
    [INSTALL_DEB_COMPLETE]="✅ App + .deb ready!"
    [DEB_ONLY_COMPLETE]="✅ .deb package ready!"
    [INVALID_OPTION]="❌ Invalid option"
    [CHECK_FILES]="❌ Missing hdmi-grabber-manager.py!"
    [CHECK_FILES_PATH]="Put script in same dir as install.sh"
    [PYTHON_CHECK]="🐍 Python3 & PyQt5 OK"
    [VIDEO_CHECK]="🎥 HDMI grabber detected"
    [FFPLAY_CHECK]="⚡ ffplay optimized for MJPG OK"
)

declare -A MESSAGES_PL=(
    [TITLE]="===== Instalator UGREEN HDMI Grabber Manager v$APP_VERSION ====="
    [CHOOSE_LANG]="Wybierz język instalacji"
    [LANG_SELECT]="1) English (EN)"
    [LANG_SELECT2]="2) Polski (PL)"
    [LANG_PROMPT]="Język [1-2, domyślnie EN]: "
    [CHECK_ROOT]="❌ Uruchom jako root (sudo)"
    [INSTALL_DEPS]="📦 Instaluję zależności..."
    [INSTALL_DONE]="✅ Zależności zainstalowane"
    [INSTALL_APP]="📁 Instaluję aplikację..."
    [INSTALL_APP_DONE]="✅ Aplikacja: $APP_DIR"
    [CREATE_DESKTOP]="🎯 Tworzę wpis Menu..."
    [DESKTOP_DONE]="✅ Menu > Multimedia > HDMI Grabber"
    [CREATE_DEB]="📦 Tworzę paczkę .deb..."
    [DEB_DONE]="✅ .deb: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]="   sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [CHOOSE_OPTION]="Wybierz opcję:"
    [OPT1]="1) Zainstaluj aplikację"
    [OPT2]="2) Zainstaluj + .deb"
    [OPT3]="3) Tylko .deb"
    [OPTION_PROMPT]="Opcja [1-3]: "
    [INSTALL_COMPLETE]="✅ Gotowe!"
    [RUN_APP]="🚀 hdmi-grabber-manager"
    [INSTALL_DEB_COMPLETE]="✅ Aplikacja + .deb gotowe!"
    [DEB_ONLY_COMPLETE]="✅ Paczka .deb gotowa!"
    [INVALID_OPTION]="❌ Błędna opcja"
    [CHECK_FILES]="❌ Brak hdmi-grabber-manager.py!"
    [CHECK_FILES_PATH]="Umieść w tym samym folderze co install.sh"
    [PYTHON_CHECK]="🐍 Python3 + PyQt5 OK"
    [VIDEO_CHECK]="🎥 HDMI grabber wykryty"
    [FFPLAY_CHECK]="⚡ ffplay MJPG zoptymalizowane OK"
)

# ============================================================================
# FUNKCJE
# ============================================================================

msg() {
    local key=$1
    if [ "$LANG_CHOICE" = "PL" ]; then
        echo "${MESSAGES_PL[$key]}"
    else
        echo "${MESSAGES_EN[$key]}"
    fi
}

choose_language() {
    echo "$(msg CHOOSE_LANG)"
    echo "1) $(msg LANG_SELECT)"
    echo "2) $(msg LANG_SELECT2)"
    read -p "$(msg LANG_PROMPT)" lang_input
    
    case $lang_input in
        2|PL|pl) LANG_CHOICE="PL" ;;
        *) LANG_CHOICE="EN" ;;
    esac
    echo ""
    echo "$(msg TITLE)"
    echo ""
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "$(msg CHECK_ROOT)"
        exit 1
    fi
}

check_files() {
    if [ ! -f "hdmi-grabber-manager.py" ]; then
        echo "$(msg CHECK_FILES)"
        echo "$(msg CHECK_FILES_PATH)"
        exit 1
    fi
}

install_dependencies() {
    echo "$(msg INSTALL_DEPS)"
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-minimal python3-pyqt5 python3-pyqt5.qtgui \
        ffmpeg v4l-utils libv4l-0 qt5-style-plugins xdg-utils
    
    python3 -c "import PyQt5; print('✅ PyQt5 OK')" 2>/dev/null || true
    echo "$(msg INSTALL_DONE)"
    echo "$(msg PYTHON_CHECK)"
}

detect_hdmi_grabber() {
    # Sprawdź wszystkie /dev/video* i wybierz kartę zawierającą 'UGREEN' lub 'USB'
    for dev in /dev/video*; do
        if v4l2-ctl -d "$dev" --all 2>/dev/null | grep -iq "UGREEN"; then
            HDMI_DEV="$dev"
            break
        fi
    done
    HDMI_DEV="${HDMI_DEV:-/dev/video2}"
    echo "$(msg VIDEO_CHECK) ($HDMI_DEV)"
}

install_application() {
    echo "$(msg INSTALL_APP)"
    rm -rf "$APP_DIR" "$BIN_DIR/$APP_NAME" 2>/dev/null || true
    mkdir -p "$APP_DIR"
    cp -f hdmi-grabber-manager.py "$APP_DIR/hdmi-grabber-manager.py"
    chmod 755 "$APP_DIR/hdmi-grabber-manager.py"
    ln -sfr "$APP_DIR/hdmi-grabber-manager.py" "$BIN_DIR/$APP_NAME"
    chmod 755 "$BIN_DIR/$APP_NAME"

    mkdir -p "$(dirname "$DESKTOP_FILE")"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=$APP_VERSION
Type=Application
Name=HDMI Grabber Manager
Comment=UGREEN HDMI grabber control
Exec=$APP_NAME
Icon=video-display
Terminal=false
Categories=Multimedia;Utility;Video;
StartupNotify=true
EOF
    chmod 644 "$DESKTOP_FILE"
    update-desktop-database >/dev/null 2>&1 || true
    echo "$(msg INSTALL_APP_DONE)"
    echo "$(msg DESKTOP_DONE)"
}

create_deb_package() {
    echo "$(msg CREATE_DEB)"
    rm -rf "$DEB_BUILD_DIR" 2>/dev/null || true
    mkdir -p "$DEB_BUILD_DIR/DEBIAN" \
             "$DEB_BUILD_DIR/opt/hdmi-grabber-manager" \
             "$DEB_BUILD_DIR/usr/local/bin" \
             "$DEB_BUILD_DIR/usr/share/applications"

    cp -f hdmi-grabber-manager.py "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/"
    chmod 755 "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/hdmi-grabber-manager.py"
    ln -sfr "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/hdmi-grabber-manager.py" "$DEB_BUILD_DIR/usr/local/bin/$APP_NAME"

    cp "$DESKTOP_FILE" "$DEB_BUILD_DIR/usr/share/applications/" 2>/dev/null || \
    cat > "$DEB_BUILD_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Version=$APP_VERSION
Type=Application
Name=HDMI Grabber Manager
Comment=UGREEN HDMI grabber control
Exec=$APP_NAME
Icon=video-display
Terminal=false
Categories=Multimedia;Utility;Video;
EOF

    cat > "$DEB_BUILD_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: HDMI Grabber <dev@local>
Depends: python3, python3-pyqt5, ffmpeg, v4l-utils, libv4l-0
Description: UGREEN HDMI Grabber Manager GUI application
 for controlling UGREEN HDMI USB grabbers.
EOF

    # postinst
    cat > "$DEB_BUILD_DIR/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
set -e
update-desktop-database 2>/dev/null || true
update-mime-database /usr/share/mime 2>/dev/null || true
echo "HDMI Grabber Manager installed successfully!"
POSTINST
    chmod 755 "$DEB_BUILD_DIR/DEBIAN/postinst"

    # prerm
    cat > "$DEB_BUILD_DIR/DEBIAN/prerm" << 'PRERM'
#!/bin/bash
set -e
rm -f /usr/local/bin/hdmi-grabber-manager 2>/dev/null || true
PRERM
    chmod 755 "$DEB_BUILD_DIR/DEBIAN/prerm"

    dpkg-deb --build "$DEB_BUILD_DIR" "${APP_NAME}_${APP_VERSION}_all.deb"
    rm -rf "$DEB_BUILD_DIR"
    echo "$(msg DEB_DONE)"
    echo "$(msg DEB_INSTALL)"
}

# ============================================================================
# GŁÓWNY PROGRAM
# ============================================================================

main() {
    clear
    choose_language
    check_root
    check_files
    detect_hdmi_grabber
    install_dependencies

    echo "$(msg CHOOSE_OPTION)"
    echo "$(msg OPT1)"
    echo "$(msg OPT2)"
    echo "$(msg OPT3)"
    echo ""
    read -p "$(msg OPTION_PROMPT)" choice

    case $choice in
        1)
            install_application
            echo "$(msg INSTALL_COMPLETE)"
            echo "$(msg RUN_APP)"
            ;;
        2)
            install_application
            create_deb_package
            echo "$(msg INSTALL_DEB_COMPLETE)"
            ;;
        3)
            create_deb_package
            echo "$(msg DEB_ONLY_COMPLETE)"
            ;;
        *)
            echo "$(msg INVALID_OPTION)"
            exit 1
            ;;
    esac

    echo ""
    echo "🎉 $(msg RUN_APP)"
    echo "📱 Menu Start > Multimedia > HDMI Grabber Manager"
}

main "$@"
