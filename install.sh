#!/bin/bash

# HDMI Grabber Manager - UGREEN Optimized Install Script (v4.2)
# Opcje: stwórz .deb, zainstaluj z .deb, odinstaluj

set -e

# ============================================================================
# KONFIGURACJA
# ============================================================================

APP_NAME="hdmi-grabber-manager"
APP_VERSION="3.0.0"
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
    [CREATE_DEB]="📦 Creating .deb package..."
    [DEB_DONE]="✅ .deb created: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]="   Install with: sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [INSTALL_DEB]="📥 Installing from .deb..."
    [INSTALL_COMPLETE]="✅ HDMI Grabber Manager installed from .deb!"
    [OPT1]="1) Create .deb package"
    [OPT2]="2) Install from .deb"
    [OPT3]="3) Uninstall HDMI Grabber Manager"
    [OPTION_PROMPT]="Option [1-3]: "
    [UNINSTALL_COMPLETE]="✅ HDMI Grabber Manager uninstalled!"
    [INVALID_OPTION]="❌ Invalid option"
    [CHECK_FILES]="❌ Missing hdmi-grabber-manager.py!"
    [CHECK_FILES_PATH]="Put script in same dir as install.sh"
)

declare -A MESSAGES_PL=(
    [TITLE]="===== Instalator UGREEN HDMI Grabber Manager v$APP_VERSION ====="
    [CHOOSE_LANG]="Wybierz język instalacji"
    [LANG_SELECT]="1) English (EN)"
    [LANG_SELECT2]="2) Polski (PL)"
    [LANG_PROMPT]="Język [1-2, domyślnie EN]: "
    [CHECK_ROOT]="❌ Uruchom jako root (sudo)"
    [CREATE_DEB]="📦 Tworzę paczkę .deb..."
    [DEB_DONE]="✅ .deb: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]="   Instalacja: sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [INSTALL_DEB]="📥 Instalacja z .deb..."
    [INSTALL_COMPLETE]="✅ HDMI Grabber Manager zainstalowany z .deb!"
    [OPT1]="1) Utwórz paczkę .deb"
    [OPT2]="2) Zainstaluj z .deb"
    [OPT3]="3) Odinstaluj HDMI Grabber Manager"
    [OPTION_PROMPT]="Opcja [1-3]: "
    [UNINSTALL_COMPLETE]="✅ HDMI Grabber Manager odinstalowany!"
    [INVALID_OPTION]="❌ Błędna opcja"
    [CHECK_FILES]="❌ Brak hdmi-grabber-manager.py!"
    [CHECK_FILES_PATH]="Umieść w tym samym folderze co install.sh"
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

create_deb_package() {
    echo "$(msg CREATE_DEB)"
    rm -rf "$DEB_BUILD_DIR" 2>/dev/null || true
    mkdir -p "$DEB_BUILD_DIR/DEBIAN" "$DEB_BUILD_DIR/opt/hdmi-grabber-manager" \
             "$DEB_BUILD_DIR/usr/local/bin" "$DEB_BUILD_DIR/usr/share/applications"

    cp -f hdmi-grabber-manager.py "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/"
    chmod 755 "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/hdmi-grabber-manager.py"
    ln -s "$APP_DIR/hdmi-grabber-manager.py" "$DEB_BUILD_DIR/usr/local/bin/$APP_NAME"

    cat > "$DEB_BUILD_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Version=$APP_VERSION
Type=Application
Name=HDMI Grabber Manager
Comment=UGREEN HDMI grabber control
Exec=$APP_DIR/hdmi-grabber-manager.py
Icon=video-display
Terminal=false
Categories=Multimedia;Utility;Video;
StartupNotify=true
EOF

    cat > "$DEB_BUILD_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: HDMI Grabber <dev@local>
Depends: python3 (>= 3.9), python3-pyqt5, ffmpeg, v4l-utils, libv4l-0 | libv4l2-0
Recommends: libv4lconvert0
Description: UGREEN HDMI Grabber Manager
 GUI application to control UGREEN HDMI USB grabber (/dev/video2).
EOF

    cat > "$DEB_BUILD_DIR/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
set -e
update-desktop-database 2>/dev/null || true
update-mime-database /usr/share/mime 2>/dev/null || true
POSTINST
    chmod 755 "$DEB_BUILD_DIR/DEBIAN/postinst"

    cat > "$DEB_BUILD_DIR/DEBIAN/prerm" << 'PRERM'
#!/bin/bash
set -e
rm -rf /opt/hdmi-grabber-manager
rm -f /usr/local/bin/hdmi-grabber-manager
rm -f /usr/share/applications/hdmi-grabber-manager.desktop
update-desktop-database 2>/dev/null || true
PRERM
    chmod 755 "$DEB_BUILD_DIR/DEBIAN/prerm"

    dpkg-deb --build "$DEB_BUILD_DIR" "${APP_NAME}_${APP_VERSION}_all.deb"
    rm -rf "$DEB_BUILD_DIR"
    echo "$(msg DEB_DONE)"
    echo "$(msg DEB_INSTALL)"
}

install_from_deb() {
    echo "$(msg INSTALL_DEB)"
    if [ ! -f "${APP_NAME}_${APP_VERSION}_all.deb" ]; then
        echo "❌ .deb file not found! Run option 1 first."
        exit 1
    fi
    sudo dpkg -i "${APP_NAME}_${APP_VERSION}_all.deb"
    sudo apt-get install -f -y
    echo "$(msg INSTALL_COMPLETE)"
}

uninstall_application() {
    echo "❌ Uninstalling HDMI Grabber Manager..."
    rm -rf "$APP_DIR" "$BIN_DIR/$APP_NAME" "$DESKTOP_FILE"
    update-desktop-database >/dev/null 2>&1 || true
    echo "$(msg UNINSTALL_COMPLETE)"
}

# ============================================================================
# GŁÓWNY PROGRAM
# ============================================================================

main() {
    clear
    choose_language
    check_root
    check_files

    echo "$(msg CHOOSE_OPTION)"
    echo "$(msg OPT1)"
    echo "$(msg OPT2)"
    echo "$(msg OPT3)"
    echo ""
    read -p "$(msg OPTION_PROMPT)" choice

    case $choice in
        1)
            create_deb_package
            ;;
        2)
            install_from_deb
            ;;
        3)
            uninstall_application
            ;;
        *)
            echo "$(msg INVALID_OPTION)"
            exit 1
            ;;
    esac

    echo ""
    echo "🎉 Done!"
    echo "📱 Menu Start > Multimedia > HDMI Grabber Manager"
}

main "$@"
