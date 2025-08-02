#!/bin/bash

echo "🔐 FFmpeg İmzalama Script"
echo "========================"

FFMPEG_DIR="assets/ffmpeg/darwin"
IDENTITY="Developer ID Application: Mehmet Yerli (VTVG4G3NFH)"

# FFmpeg ve ffprobe'u imzala
for binary in ffmpeg ffprobe; do
    if [ -f "$FFMPEG_DIR/$binary" ]; then
        echo "📝 İmzalanıyor: $binary"
        codesign --force --deep --sign "$IDENTITY" \
                 --options runtime \
                 --timestamp \
                 --entitlements entitlements.plist \
                 "$FFMPEG_DIR/$binary"
        
        if [ $? -eq 0 ]; then
            echo "✅ $binary başarıyla imzalandı"
            codesign --verify --verbose=2 "$FFMPEG_DIR/$binary"
        else
            echo "❌ $binary imzalama başarısız!"
            exit 1
        fi
    else
        echo "❌ $binary bulunamadı: $FFMPEG_DIR/$binary"
        exit 1
    fi
done

echo -e "\n✅ Tüm FFmpeg binary'leri imzalandı!"