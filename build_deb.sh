#!/bin/bash
set -e

# Configuration
PACKAGE_NAME="kapsulate"
VERSION=$(grep "^Version:" packaging/DEBIAN/control | cut -d' ' -f2)
ARCH="amd64"
BUILD_DIR="build"
PACKAGE_DIR="${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "Building ${PACKAGE_NAME} ${VERSION} for ${ARCH}..."

# Clean previous build
rm -rf "${BUILD_DIR}"

# Create directory structure
mkdir -p "${PACKAGE_DIR}/DEBIAN"
mkdir -p "${PACKAGE_DIR}/usr/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/applications"
mkdir -p "${PACKAGE_DIR}/usr/share/autostart"
mkdir -p "${PACKAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${PACKAGE_DIR}/usr/share/icons/hicolor-dark/scalable/apps"
mkdir -p "${PACKAGE_DIR}/usr/share/icons/hicolor-light/scalable/apps"
mkdir -p "${PACKAGE_DIR}/usr/share/kapsulate"
mkdir -p "${PACKAGE_DIR}/etc/kapsulate"

# Copy DEBIAN control files
cp packaging/DEBIAN/control "${PACKAGE_DIR}/DEBIAN/"
cp packaging/DEBIAN/postinst "${PACKAGE_DIR}/DEBIAN/"
cp packaging/DEBIAN/prerm "${PACKAGE_DIR}/DEBIAN/"

# Make control scripts executable
chmod 755 "${PACKAGE_DIR}/DEBIAN/postinst"
chmod 755 "${PACKAGE_DIR}/DEBIAN/prerm"

# Copy wrapper script
cp packaging/usr/bin/kapsulate "${PACKAGE_DIR}/usr/bin/"
chmod 755 "${PACKAGE_DIR}/usr/bin/kapsulate"

# Copy desktop file
cp kapsulate.desktop "${PACKAGE_DIR}/usr/share/applications/"
cp kapsulate.desktop "${PACKAGE_DIR}/usr/share/autostart/"

# Copy icons
cp assets/hicolor-dark/scalable/apps/kapsulate.svg "${PACKAGE_DIR}/usr/share/icons/hicolor-dark/scalable/apps/"
cp assets/hicolor-light/scalable/apps/kapsulate.svg "${PACKAGE_DIR}/usr/share/icons/hicolor-light/scalable/apps/"
cp assets/hicolor-dark/scalable/apps/kapsulate.svg "${PACKAGE_DIR}/usr/share/icons/hicolor/scalable/apps/"

# Copy icon theme index files
cp assets/hicolor-dark/index.theme "${PACKAGE_DIR}/usr/share/icons/hicolor-dark/"
cp assets/hicolor-light/index.theme "${PACKAGE_DIR}/usr/share/icons/hicolor-light/"

# Copy Python source files
cp -r src/* "${PACKAGE_DIR}/usr/share/kapsulate/"

# Copy default config
cp config/kapsulate.conf "${PACKAGE_DIR}/usr/share/kapsulate/kapsulate.conf"

# Create doc and metainfo directories
mkdir -p "${PACKAGE_DIR}/usr/share/doc/kapsulate"
mkdir -p "${PACKAGE_DIR}/usr/share/metainfo"

# Copy copyright file
cp packaging/DEBIAN/copyright "${PACKAGE_DIR}/usr/share/doc/kapsulate/"

# Copy AppStream metadata
cp packaging/usr/share/metainfo/io.github.darkokuzmanovic.kapsulate.metainfo.xml "${PACKAGE_DIR}/usr/share/metainfo/"

# Calculate installed size
INSTALLED_SIZE=$(du -sk "${PACKAGE_DIR}" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: ${INSTALLED_SIZE}/" "${PACKAGE_DIR}/DEBIAN/control"

# Build the package
dpkg-deb --build "${PACKAGE_DIR}"

echo "Package built successfully: ${PACKAGE_DIR}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${PACKAGE_DIR}.deb"
echo ""
echo "To uninstall:"
echo "  sudo dpkg -r ${PACKAGE_NAME}"
