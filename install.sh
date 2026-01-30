#!/bin/bash
# HDMI Grabber Manager - UGREEN Optimized Install Script (v3.0)
# Automatycznie tworzy pakiet .deb
set -e

APP_NAME="hdmi-grabber-manager"
APP_VERSION="3.0.0"
DEB_BUILD_DIR="/tmp/hdmi-grabber-manager-deb"
LANG_CHOICE="EN"

declare -A MESSAGES_EN=(
    [TITLE]="===== UGREEN HDMI Grabber Manager .deb Builder v$APP_VERSION ====="
    [CHOOSE_LANG]="Choose installation language / Wybierz język instalacji"
    [LANG_SELECT]="1) English (EN)"
    [LANG_SELECT2]="2) Polski (PL)"
    [LANG_PROMPT]="Language [1-2, default EN]: "
    [CHECK_ROOT]="❌ Script must be run as root (use sudo)"
    [CREATE_DEB]="📦 Creating .deb package..."
    [DEB_DONE]="✅ .deb created: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]=" Install: sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_ONLY_COMPLETE]="✅ .deb package ready!"
    [CHECK_FILES]="❌ Missing hdmi-grabber-manager.py!"
)

declare -A MESSAGES_PL=(
    [TITLE]="===== Kreator paczki .deb HDMI Grabber Manager v$APP_VERSION ====="
    [CHOOSE_LANG]="Wybierz język instalacji"
    [LANG_SELECT]="1) English (EN)"
    [LANG_SELECT2]="2) Polski (PL)"
    [LANG_PROMPT]="Język [1-2, domyślnie EN]: "
    [CHECK_ROOT]="❌ Uruchom jako root (sudo)"
    [CREATE_DEB]="📦 Tworzę paczkę .deb..."
    [DEB_DONE]="✅ .deb: ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_INSTALL]=" sudo dpkg -i ${APP_NAME}_${APP_VERSION}_all.deb"
    [DEB_ONLY_COMPLETE]="✅ Paczka .deb gotowa!"
    [CHECK_FILES]="❌ Brak hdmi-grabber-manager.py!"
)

msg(){ [ "$LANG_CHOICE" = "PL" ] && echo "${MESSAGES_PL[$1]}" || echo "${MESSAGES_EN[$1]}"; }

choose_language(){
    echo "$(msg CHOOSE_LANG)"
    echo "1) $(msg LANG_SELECT)"
    echo "2) $(msg LANG_SELECT2)"
    read -p "$(msg LANG_PROMPT)" lang_input
    case $lang_input in 2|PL|pl) LANG_CHOICE="PL";; *) LANG_CHOICE="EN";; esac
    echo ""; echo "$(msg TITLE)"; echo ""
}

check_root(){ [ "$EUID" -ne 0 ] && echo "$(msg CHECK_ROOT)" && exit 1; }
check_files(){ [ ! -f "hdmi-grabber-manager.py" ] && echo "$(msg CHECK_FILES)" && exit 1; }

create_deb_package(){
    echo "$(msg CREATE_DEB)"
    rm -rf "$DEB_BUILD_DIR"
    mkdir -p "$DEB_BUILD_DIR/DEBIAN" \
             "$DEB_BUILD_DIR/opt/hdmi-grabber-manager" \
             "$DEB_BUILD_DIR/usr/local/bin" \
             "$DEB_BUILD_DIR/usr/share/applications"

    cp hdmi-grabber-manager.py "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/"
    chmod 755 "$DEB_BUILD_DIR/opt/hdmi-grabber-manager/hdmi-grabber-manager.py"

    # ✅ POPRAWIONY LINK
    ln -sfr /opt/hdmi-grabber-manager/hdmi-grabber-manager.py \
           "$DEB_BUILD_DIR/usr/local/bin/$APP_NAME"

    cat > "$DEB_BUILD_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Version=$APP_VERSION
Type=Application
Name=HDMI Grabber Manager
Comment=UGREEN HDMI grabber control
Exec=$APP_NAME
Icon=video-display
Terminal=false
Categories=Multimedia;Utility;
EOF

    cat > "$DEB_BUILD_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: HDMI Grabber <dev@local>
Depends: python3 (>= 3.9), python3-pyqt5, ffmpeg, v4l-utils
Description: UGREEN HDMI Grabber Manager GUI for HDMI capture devices
EOF

    dpkg-deb --build "$DEB_BUILD_DIR" "${APP_NAME}_${APP_VERSION}_all.deb"
    rm -rf "$DEB_BUILD_DIR"

    echo "$(msg DEB_DONE)"
    echo "$(msg DEB_INSTALL)"
}

main(){
    clear
    choose_language
    check_root
    check_files
    create_deb_package
    echo ""; echo "$(msg DEB_ONLY_COMPLETE)"
}
main "$@"
