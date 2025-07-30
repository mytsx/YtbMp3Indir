import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import yt_dlp

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Yap - YouTube İndirici (Minimal)")
        self.root.geometry("600x400")
        self.setup_ui()
        self.is_running = False
        
    def setup_ui(self):
        # URL giriş alanı
        tk.Label(self.root, text="İndirilecek YouTube URL'lerini buraya yapıştırın:").pack(pady=5)
        self.url_text = scrolledtext.ScrolledText(self.root, height=10)
        self.url_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Durum etiketi
        self.status_label = tk.Label(self.root, text="Hazır")
        self.status_label.pack(pady=5)
        
        # İlerleme çubuğu
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_label = tk.Label(self.progress_frame, text="Dosya: ", width=30, anchor="w")
        self.file_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=200)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.percent_label = tk.Label(self.progress_frame, text="0%", width=10)
        self.percent_label.pack(side=tk.LEFT)
        
        # İndirme butonu
        self.download_button = tk.Button(self.root, text="İndir", command=self.start_download)
        self.download_button.pack(pady=10)
    
    def update_status(self, status):
        self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def update_progress(self, filename, percent, text):
        self.file_label.config(text=f"Dosya: {filename}")
        if percent >= 0:
            self.progress_bar["value"] = percent
        self.percent_label.config(text=text)
        self.root.update_idletasks()
    
    def download_progress_hook(self, d):
        """İndirme ilerlemesini takip eden fonksiyon"""
        if d['status'] == 'downloading':
            filename = os.path.basename(d['filename'])
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.root.after(0, lambda: self.update_progress(filename, percent, f"%{percent:.1f}"))
            else:
                mb_downloaded = d['downloaded_bytes']/1024/1024
                self.root.after(0, lambda: self.update_progress(filename, -1, f"{mb_downloaded:.1f} MB"))
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            self.root.after(0, lambda: self.update_status(f"İndirme tamamlandı: {filename}"))
        elif d['status'] == 'error':
            filename = os.path.basename(d.get('filename', 'Bilinmeyen dosya'))
            error = str(d.get('error', 'Bilinmeyen hata'))
            self.root.after(0, lambda: self.update_status(f"Hata: {filename} - {error}"))
    
    def process_url(self, url, output_path):
        """URL'yi işler ve MP3 olarak indirir"""
        self.root.after(0, lambda: self.update_status(f"İndiriliyor: {url}"))
        
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
            'progress_hooks': [self.download_progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, lambda: self.update_status(f"İndirme tamamlandı: {url}"))
            return True
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"İndirme hatası: {e}"))
            return False
    
    def download_all(self, urls, output_path):
        """Tüm URL'leri indir"""
        self.is_running = True
        
        # Çıktı dizinini oluştur
        os.makedirs(output_path, exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            if not self.is_running:
                self.root.after(0, lambda: self.update_status("İndirme durduruldu"))
                break
                
            self.root.after(0, lambda: self.update_status(f"URL {i}/{len(urls)} işleniyor"))
            success = self.process_url(url, output_path)
            
            if not success and not self.is_running:
                break
        
        self.is_running = False
        self.root.after(0, lambda: self.update_status("Tüm indirmeler tamamlandı"))
        self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))
    
    def start_download(self):
        # URL'leri al
        text = self.url_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Uyarı", "Lütfen en az bir URL girin.")
            return
        
        # URL'leri satırlara ayır ve boş satırları filtrele
        urls = [url.strip() for url in text.split('\n') if url.strip()]
        
        if not urls:
            messagebox.showwarning("Uyarı", "Geçerli URL bulunamadı.")
            return
        
        # İndirme klasörünü ayarla
        if getattr(sys, 'frozen', False):
            # PyInstaller ile paketlenmiş
            application_path = os.path.dirname(sys.executable)
        else:
            # Normal Python betiği
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        output_dir = os.path.join(application_path, "music")
        
        # Klasörün oluşturulduğundan emin ol ve kullanıcıya bildir
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.update_status(f"İndirme klasörü: {output_dir}")
            messagebox.showinfo("Bilgi", f"İndirilen dosyalar şu klasöre kaydedilecek:\n{output_dir}")
        except Exception as e:
            messagebox.showwarning("Hata", f"İndirme klasörü oluşturulamadı: {e}")
            return
        
        # Butonları güncelle
        self.download_button.config(state=tk.DISABLED)
        
        # İlerleme çubuğunu sıfırla
        self.progress_bar["value"] = 0
        self.file_label.config(text="Dosya: ")
        self.percent_label.config(text="0%")
        
        # İndirme işlemini başlat
        download_thread = threading.Thread(
            target=self.download_all,
            args=(urls, output_dir)
        )
        download_thread.daemon = True
        download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
