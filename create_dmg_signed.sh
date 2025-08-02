#!/bin/bash

echo "📦 Signed DMG Oluşturma Script"
echo "=============================="

APP_NAME="MP3Yap"
DMG_NAME="MP3Yap-2.1.1-signed.dmg"
VOLUME_NAME="YouTube MP3 İndirici"
IDENTITY="Developer ID Application: Mehmet Yerli (VTVG4G3NFH)"

# Eski DMG'yi sil
if [ -f "$DMG_NAME" ]; then
    echo "🗑️  Eski DMG siliniyor..."
    rm "$DMG_NAME"
fi

# Geçici DMG oluştur
echo "🔨 DMG oluşturuluyor..."
create-dmg \
    --volname "$VOLUME_NAME" \
    --volicon "assets/icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "$APP_NAME.app" 200 190 \
    --hide-extension "$APP_NAME.app" \
    --app-drop-link 600 185 \
    --no-internet-enable \
    "$DMG_NAME" \
    "dist/"

# DMG'yi imzala
echo "🔐 DMG imzalanıyor..."
codesign --force --deep --sign "$IDENTITY" "$DMG_NAME"

# İmzayı doğrula
echo "✅ İmza doğrulanıyor..."
codesign --verify --verbose=2 "$DMG_NAME"

echo -e "\n📊 DMG Bilgileri:"
echo "=================="
echo "Dosya: $DMG_NAME"
echo "Boyut: $(du -h $DMG_NAME | cut -f1)"
echo "İmza: $IDENTITY"

echo -e "\n✅ DMG hazır!"