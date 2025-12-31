#!/bin/bash
set -e

# Release helper script for Kapsulate
# This script helps prepare and create a new release

if [ -z "$1" ]; then
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 1.0.1"
    exit 1
fi

VERSION="$1"
TAG="v${VERSION}"

echo "Preparing release ${VERSION}..."

# Update version in control file
sed -i "s/^Version: .*/Version: ${VERSION}/" packaging/DEBIAN/control

# Update version in main.py
sed -i "s/^APP_VERSION = \".*\"/APP_VERSION = \"${VERSION}\"/" src/main.py

# Update CHANGELOG.md (you'll need to edit this manually)
echo ""
echo "Please update CHANGELOG.md with the changes for version ${VERSION}"
echo "Then run:"
echo "  git add -A"
echo "  git commit -m \"Release ${VERSION}\""
echo "  git tag ${TAG}"
echo "  git push origin main"
echo "  git push origin ${TAG}"
echo ""
echo "GitHub Actions will build and publish the release automatically."
