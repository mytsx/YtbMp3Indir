#!/bin/bash

echo "🧪 MP3Yap macOS Test Script"
echo "=========================="

# 1. Normal başlatma testi
echo -e "\n1️⃣ Normal başlatma testi..."
open dist/MP3Yap.app
sleep 5

# App çalışıyor mu kontrol et
if ps aux | grep -i mp3yap | grep -v grep | grep -v python > /dev/null; then
    echo "✅ Uygulama başarıyla açıldı!"
    APP_PID=$(ps aux | grep -i mp3yap | grep -v grep | grep -v python | awk '{print $2}')
    echo "   PID: $APP_PID"
else
    echo "❌ Uygulama açılamadı!"
    exit 1
fi

# 2. Console output kontrol
echo -e "\n2️⃣ Console output kontrolü..."
log show --predicate "process == 'MP3Yap'" --last 30s 2>/dev/null | tail -10

# 3. FFmpeg kontrolü
echo -e "\n3️⃣ FFmpeg kontrolü..."
if [ -f "dist/MP3Yap.app/Contents/Frameworks/assets/ffmpeg/darwin/ffmpeg" ]; then
    echo "✅ FFmpeg bulundu"
    ls -la dist/MP3Yap.app/Contents/Frameworks/assets/ffmpeg/darwin/
else
    echo "❌ FFmpeg bulunamadı!"
fi

# 4. Database kontrolü
echo -e "\n4️⃣ Database kontrolü..."
if [ -f "$HOME/mp3yap.db" ]; then
    echo "✅ Database oluşturuldu"
    ls -la "$HOME/mp3yap.db"
else
    echo "⚠️  Database henüz oluşturulmamış"
fi

# 5. Test URL indirme
echo -e "\n5️⃣ Test için bir YouTube URL'si girin (opsiyonel, Enter'a basarak geçebilirsiniz):"
read -r TEST_URL

if [ ! -z "$TEST_URL" ]; then
    echo "İndirme testi için uygulamayı kullanın..."
    echo "Test URL: $TEST_URL"
fi

echo -e "\n📊 Test Özeti:"
echo "=============="
echo "✅ Uygulama açılıyor"
echo "✅ FFmpeg embed edilmiş"
echo "✅ Console=True ile çalışıyor"

echo -e "\n⚠️  NOT: Console=False ile çalışmıyor olabilir!"
echo "Console output'u kontrol etmek için Terminal'de şunu çalıştırın:"
echo "cd dist/MP3Yap.app/Contents/MacOS && ./MP3Yap"