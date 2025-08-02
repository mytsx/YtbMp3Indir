#!/bin/bash

echo "🔐 Deep Signing Script for MP3Yap"
echo "=================================="

APP_PATH="dist/MP3Yap.app"
IDENTITY="Developer ID Application: Mehmet Yerli (VTVG4G3NFH)"

# First, sign all embedded binaries
echo "📝 Signing embedded binaries..."

# Sign FFmpeg binaries
for binary in $(find "$APP_PATH" -name "ffmpeg" -o -name "ffprobe"); do
    echo "  Signing: $binary"
    codesign --force --sign "$IDENTITY" \
             --options runtime \
             --timestamp \
             --entitlements entitlements.plist \
             "$binary"
done

# Sign all .so and .dylib files
echo "📝 Signing dynamic libraries..."
find "$APP_PATH" -name "*.so" -o -name "*.dylib" | while read lib; do
    echo "  Signing: $(basename $lib)"
    codesign --force --sign "$IDENTITY" \
             --options runtime \
             --timestamp \
             "$lib"
done

# Sign frameworks
echo "📝 Signing frameworks..."
find "$APP_PATH" -name "*.framework" | while read framework; do
    echo "  Signing: $(basename $framework)"
    codesign --force --deep --sign "$IDENTITY" \
             --options runtime \
             --timestamp \
             "$framework"
done

# Finally, sign the app bundle itself
echo "📝 Signing app bundle..."
codesign --force --deep --sign "$IDENTITY" \
         --options runtime \
         --timestamp \
         --entitlements entitlements.plist \
         "$APP_PATH"

# Verify the signature
echo -e "\n✅ Verifying signature..."
codesign --verify --deep --verbose=2 "$APP_PATH"

echo -e "\n✅ Deep signing complete!"