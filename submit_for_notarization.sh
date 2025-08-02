#!/bin/bash

echo "🔔 macOS Notarization Script"
echo "============================"

DMG_FILE="MP3Yap-2.1.1-signed.dmg"

# Check if DMG exists
if [ ! -f "$DMG_FILE" ]; then
    echo "❌ DMG file not found: $DMG_FILE"
    exit 1
fi

echo "📦 DMG File: $DMG_FILE"
echo "📏 Size: $(du -h $DMG_FILE | cut -f1)"

echo -e "\n⚠️  UYARI: Bu console versiyonudur. Terminal penceresi açılacaktır."
echo "Notarization 5-30 dakika sürebilir."
echo -e "\nDevam etmek istiyor musunuz? (y/n): "
read -r response

if [ "$response" != "y" ]; then
    echo "❌ İptal edildi"
    exit 0
fi

echo -e "\n📤 Notarization başlatılıyor..."
xcrun notarytool submit "$DMG_FILE" \
    --keychain-profile "MP3YAP_NOTARIZE" \
    --wait

if [ $? -eq 0 ]; then
    echo "✅ Notarization başarılı!"
    
    # Staple the notarization
    echo "🔖 Stapling notarization..."
    xcrun stapler staple "$DMG_FILE"
    
    echo "✅ DMG hazır: $DMG_FILE"
else
    echo "❌ Notarization başarısız!"
    exit 1
fi