#!/bin/bash
# install.sh - Tworzy pakiet .deb dla HDMI Grabber Manager

APP_NAME="hdmi-grabber-manager"
APP_VERSION="1.0"
APP_ARCH="all"
APP_DESC="UGREEN HDMI Grabber Manager - zarządzanie urządzeniem HDMI w Linux MX"

# Ścieżki tymczasowe
BUILD_DIR="./${APP_NAME}_deb"
DEBIAN_DIR="${BUILD_DIR}/DEBIAN"
BIN_DIR="${BUILD_DIR}/usr/bin"

# Usuń stare buildy
rm -rf "$BUILD_DIR"

# Tworzenie struktury pakietu
mkdir -p "$DEBIAN_DIR"
mkdir -p "$BIN_DIR"

# Kopiowanie pliku głównego
cp ./hdmi-grabber-manager.py "$BIN_DIR/$APP_NAME"
chmod +x "$BIN_DIR/$APP_NAME"

# Tworzenie pliku kontrolnego DEBIAN/control
cat <<EOF > "$DEBIAN_DIR/control"
Package: $APP_NAME
Version: $APP_VERSION
Section: utils
Priority: optional
Architecture: $APP_ARCH
Maintainer: Twoje Imię <twoj@email.com>
Description: $APP_DESC
Depends: python3, python3-pyqt5, v4l-utils, ffmpeg
EOF

# Opcjonalnie: skrypt preinst / postinst
# mkdir -p "$DEBIAN_DIR"
# echo -e "#!/bin/bash\nexit 0" > "$DEBIAN_DIR/postinst"
# chmod 755 "$DEBIAN_DIR/postinst"

# Budowanie pakietu .deb
dpkg-deb --build "$BUILD_DIR"

# Przeniesienie paczki do katalogu bieżącego
mv "${BUILD_DIR}.deb" ./

echo "Pakiet ${APP_NAME}.deb został wygenerowany w katalogu bieżącym."
