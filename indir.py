import yt_dlp
import os
import sys
import argparse
import json
import logging
from datetime import datetime

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mp3_indirici.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mp3_indirici')

def download_progress_hook(d):
    """İndirme ilerlemesini takip eden fonksiyon"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] > 0:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            sys.stdout.write(f"\rİndiriliyor: {d['filename']} - %{percent:.1f} tamamlandı")
            sys.stdout.flush()
            logger.debug(f"İndiriliyor: {d['filename']} - %{percent:.1f} tamamlandı")
        else:
            sys.stdout.write(f"\rİndiriliyor: {d['filename']} - {d['downloaded_bytes']/1024/1024:.1f} MB")
            sys.stdout.flush()
            logger.debug(f"İndiriliyor: {d['filename']} - {d['downloaded_bytes']/1024/1024:.1f} MB")
    elif d['status'] == 'finished':
        sys.stdout.write(f"\nİndirme tamamlandı: {d['filename']}\n")
        sys.stdout.flush()
        logger.info(f"İndirme tamamlandı: {d['filename']}")
    elif d['status'] == 'error':
        sys.stdout.write(f"\nHata: {d['filename']}\n")
        sys.stdout.flush()
        logger.error(f"Hata: {d['filename']}")

def process_url(url, output_path='.', limit=None, download_archive=None):
    logger.info(f"URL işleniyor: {url}")
    """
    URL'yi işler ve MP3 olarak indirir. Playlist veya tekli video olabilir.
    yt-dlp'nin doğrudan playlist işleme özelliğini kullanır.
    
    Args:
        url: İndirilecek video veya playlist URL'si
        output_path: İndirilen dosyaların kaydedileceği dizin
        limit: Playlist'ten indirilecek maksimum video sayısı
        download_archive: İndirilen videoları takip etmek için arşiv dosyası
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '44100',
            '-ac', '2',
        ],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'prefer_ffmpeg': True,
        'ignoreerrors': True,
        'noplaylist': False,  # Playlist'leri işlemeye izin ver
        'progress_hooks': [download_progress_hook],
    }
    
    # Arşiv dosyası belirtilmişse, indirilen videoları takip et
    if download_archive:
        ydl_opts['download_archive'] = download_archive
    
    # Playlist limiti belirtilmişse ekle
    if limit and limit > 0:
        ydl_opts['playlistend'] = limit
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"yt-dlp ile indirme başlatılıyor: {url}")
            ydl.download([url])
        logger.info(f"İndirme tamamlandı: {url}")
        print(f"[✓] İndirme tamamlandı: {url}")
        return True
    except KeyboardInterrupt:
        logger.warning("İndirme kullanıcı tarafından durduruldu.")
        print("\n[!] İndirme kullanıcı tarafından durduruldu.")
        return False
    except Exception as e:
        logger.error(f"İndirme hatası: {e} ({url})")
        print(f"[!] İndirme hatası: {e} ({url})")
        return False

def save_progress(processed_urls, progress_file):
    """İşlenen URL'leri kaydet"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'processed_urls': processed_urls
        }, f, ensure_ascii=False, indent=2)

def load_progress(progress_file):
    """Önceki ilerlemeyi yükle"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_urls', []))
        except Exception as e:
            print(f"[!] İlerleme dosyası yüklenirken hata: {e}")
    return set()

def main():
    logger.info("Program başlatıldı")
    parser = argparse.ArgumentParser(description='YouTube videolarını MP3 olarak indir')
    parser.add_argument('--url', help='İndirilecek YouTube URL\'si')
    parser.add_argument('--limit', type=int, help='Playlist\'ten indirilecek maksimum video sayısı')
    parser.add_argument('--output', default='indirilen_mp3ler', help='İndirilen dosyaların kaydedileceği dizin')
    parser.add_argument('--no-resume', action='store_true', help='İlerlemeyi kaydetme ve devam etme')
    parser.add_argument('--reset', action='store_true', help='İlerlemeyi sıfırla ve baştan başla')
    args = parser.parse_args()
    
    try:
        # Çıktı dizinini oluştur
        output_dir = args.output
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Çıktı dizini: {output_dir}")
        
        # İlerleme ve arşiv dosyaları
        progress_file = os.path.join(output_dir, '.progress.json')
        download_archive = os.path.join(output_dir, '.download_archive.txt')
        
        # İlerlemeyi sıfırla
        if args.reset:
            if os.path.exists(progress_file):
                os.remove(progress_file)
                logger.info(f"İlerleme dosyası silindi: {progress_file}")
            if os.path.exists(download_archive):
                os.remove(download_archive)
                logger.info(f"Arşiv dosyası silindi: {download_archive}")
            print("[+] İlerleme sıfırlandı.")
        
        # İşlenmiş URL'leri yükle
        processed_urls = set()
        if not args.no_resume and not args.reset:
            processed_urls = load_progress(progress_file)
            if processed_urls:
                print(f"[+] {len(processed_urls)} URL daha önce işlenmiş.")
        
        # URL'leri topla
        urls = []
        if args.url:
            urls.append(args.url)
            logger.info(f"Komut satırından URL alındı: {args.url}")
        else:
            try:
                with open("url_list.txt", "r", encoding="utf-8") as file:
                    urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
                logger.info(f"url_list.txt dosyasından {len(urls)} URL okundu")
            except Exception as e:
                logger.error(f"url_list.txt dosyası okunamadı: {e}")
                print(f"[!] url_list.txt dosyası okunamadı: {e}")
                if not urls:
                    logger.error("İndirilecek URL bulunamadı")
                    print("[!] İndirilecek URL bulunamadı. url_list.txt dosyasını kontrol edin veya --url parametresi kullanın.")
                    return
        
        # Daha önce işlenmemiş URL'leri filtrele
        if not args.reset and not args.no_resume:
            remaining_urls = [url for url in urls if url not in processed_urls]
            skipped = len(urls) - len(remaining_urls)
            if skipped > 0:
                print(f"[+] {skipped} URL daha önce işlenmiş, atlanıyor.")
            urls = remaining_urls
        
        if not urls:
            logger.warning("İndirilecek URL kalmadı")
            print("[!] İndirilecek URL kalmadı.")
            return
            
        logger.info(f"{len(urls)} URL işlenecek")
        print(f"[+] {len(urls)} URL işlenecek")
        
        # URL'leri işle
        for i, url in enumerate(urls, 1):
            logger.info(f"URL {i}/{len(urls)} işleniyor: {url}")
            print(f"\n[+] URL {i}/{len(urls)} işleniyor: {url}")
            success = process_url(
                url, 
                output_path=output_dir, 
                limit=args.limit,
                download_archive=None if args.no_resume else download_archive
            )
            
            if success:
                processed_urls.add(url)
                if not args.no_resume:
                    save_progress(list(processed_urls), progress_file)
                    logger.info(f"İlerleme kaydedildi: {len(processed_urls)} URL işlendi")
            
            if not success and not args.no_resume:
                logger.warning("İşlem başarısız oldu, ilerleme kaydedildi")
                print("[!] İşlem başarısız oldu, ilerleme kaydedildi.")
                break
            
        logger.info("Tüm indirmeler tamamlandı")
        print("\n[✓] Tüm indirmeler tamamlandı!")
        
    except KeyboardInterrupt:
        logger.warning("İşlem kullanıcı tarafından durduruldu")
        print("\n[!] İşlem kullanıcı tarafından durduruldu.")
        if not args.no_resume and 'processed_urls' in locals():
            save_progress(list(processed_urls), progress_file)
            logger.info("İlerleme kaydedildi")
            print("[+] İlerleme kaydedildi. Daha sonra aynı komutla devam edebilirsiniz.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
        print(f"\n[!] Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()
