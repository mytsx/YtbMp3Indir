#!/usr/bin/env python3
"""Generate translation files for MP3Yap"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Common translations for all languages
COMMON_TRANSLATIONS = {
    # Main window
    "İndir": {"en": "Download", "de": "Herunterladen", "es": "Descargar", "fr": "Télécharger"},
    "Geçmiş": {"en": "History", "de": "Verlauf", "es": "Historial", "fr": "Historique"},
    "Sıra": {"en": "Queue", "de": "Warteschlange", "es": "Cola", "fr": "File d'attente"},
    "Dönüştür": {"en": "Convert", "de": "Konvertieren", "es": "Convertir", "fr": "Convertir"},
    
    # Buttons
    "▶ İndir": {"en": "▶ Download", "de": "▶ Herunterladen", "es": "▶ Descargar", "fr": "▶ Télécharger"},
    "⏹ İptal": {"en": "⏹ Cancel", "de": "⏹ Abbrechen", "es": "⏹ Cancelar", "fr": "⏹ Annuler"},
    "➕ Kuyruğa Ekle": {"en": "➕ Add to Queue", "de": "➕ Zur Warteschlange", "es": "➕ Añadir a Cola", "fr": "➕ Ajouter à la file"},
    "🗑 Temizle": {"en": "🗑 Clear", "de": "🗑 Löschen", "es": "🗑 Limpiar", "fr": "🗑 Effacer"},
    
    # Menu items  
    "Dosya": {"en": "File", "de": "Datei", "es": "Archivo", "fr": "Fichier"},
    "Düzen": {"en": "Edit", "de": "Bearbeiten", "es": "Editar", "fr": "Édition"},
    "Ayarlar": {"en": "Settings", "de": "Einstellungen", "es": "Configuración", "fr": "Paramètres"},
    "Yardım": {"en": "Help", "de": "Hilfe", "es": "Ayuda", "fr": "Aide"},
    "Hakkında": {"en": "About", "de": "Über", "es": "Acerca de", "fr": "À propos"},
    "Çıkış": {"en": "Exit", "de": "Beenden", "es": "Salir", "fr": "Quitter"},
    "Tercihler": {"en": "Preferences", "de": "Einstellungen", "es": "Preferencias", "fr": "Préférences"},
    
    # Status messages
    "Hazır": {"en": "Ready", "de": "Bereit", "es": "Listo", "fr": "Prêt"},
    "İndiriliyor...": {"en": "Downloading...", "de": "Herunterladen...", "es": "Descargando...", "fr": "Téléchargement..."},
    "İndirme tamamlandı": {"en": "Download completed", "de": "Download abgeschlossen", "es": "Descarga completada", "fr": "Téléchargement terminé"},
    "Dönüştürülüyor...": {"en": "Converting...", "de": "Konvertierung...", "es": "Convirtiendo...", "fr": "Conversion..."},
    "Tamamlandı": {"en": "Completed", "de": "Abgeschlossen", "es": "Completado", "fr": "Terminé"},
    "Hata oluştu": {"en": "Error occurred", "de": "Fehler aufgetreten", "es": "Error ocurrido", "fr": "Erreur survenue"},
    
    # Settings dialog
    "Dil / Language:": {"en": "Language:", "de": "Sprache:", "es": "Idioma:", "fr": "Langue:"},
    "Tema:": {"en": "Theme:", "de": "Thema:", "es": "Tema:", "fr": "Thème:"},
    "Açık": {"en": "Light", "de": "Hell", "es": "Claro", "fr": "Clair"},
    "Koyu": {"en": "Dark", "de": "Dunkel", "es": "Oscuro", "fr": "Sombre"},
    "Görünüm": {"en": "Appearance", "de": "Aussehen", "es": "Apariencia", "fr": "Apparence"},
    "Bildirimler": {"en": "Notifications", "de": "Benachrichtigungen", "es": "Notificaciones", "fr": "Notifications"},
    "İndirme": {"en": "Download", "de": "Download", "es": "Descarga", "fr": "Téléchargement"},
    "Uygulama": {"en": "Application", "de": "Anwendung", "es": "Aplicación", "fr": "Application"},
    "Ses Kalitesi:": {"en": "Audio Quality:", "de": "Audioqualität:", "es": "Calidad de Audio:", "fr": "Qualité Audio:"},
    "İndirme Konumu:": {"en": "Download Location:", "de": "Download-Ort:", "es": "Ubicación de Descarga:", "fr": "Emplacement:"},
    "Eş Zamanlı İndirme:": {"en": "Simultaneous Downloads:", "de": "Gleichzeitige Downloads:", "es": "Descargas Simultáneas:", "fr": "Téléchargements Simultanés:"},
    "Kaydet": {"en": "Save", "de": "Speichern", "es": "Guardar", "fr": "Enregistrer"},
    "İptal": {"en": "Cancel", "de": "Abbrechen", "es": "Cancelar", "fr": "Annuler"},
    
    # Language change message
    "Dil Değiştirildi": {"en": "Language Changed", "de": "Sprache Geändert", "es": "Idioma Cambiado", "fr": "Langue Modifiée"},
    "Dil değişikliğinin tam olarak uygulanması için uygulamayı yeniden başlatmanız önerilir.": {
        "en": "Please restart the application for the language change to take full effect.",
        "de": "Bitte starten Sie die Anwendung neu, damit die Sprachänderung vollständig wirksam wird.",
        "es": "Por favor, reinicie la aplicación para que el cambio de idioma surta efecto completo.",
        "fr": "Veuillez redémarrer l'application pour que le changement de langue prenne pleinement effet."
    },
    
    # Download tab
    "YouTube URL'lerini buraya yapıştırın (her satıra bir URL)": {
        "en": "Paste YouTube URLs here (one URL per line)",
        "de": "YouTube-URLs hier einfügen (eine URL pro Zeile)",
        "es": "Pegue las URL de YouTube aquí (una URL por línea)",
        "fr": "Collez les URL YouTube ici (une URL par ligne)"
    },
    "Klasör Aç": {"en": "Open Folder", "de": "Ordner Öffnen", "es": "Abrir Carpeta", "fr": "Ouvrir le Dossier"},
    
    # History tab
    "Ara...": {"en": "Search...", "de": "Suchen...", "es": "Buscar...", "fr": "Rechercher..."},
    "Başlık": {"en": "Title", "de": "Titel", "es": "Título", "fr": "Titre"},
    "Dosya Adı": {"en": "File Name", "de": "Dateiname", "es": "Nombre de Archivo", "fr": "Nom du Fichier"},
    "Boyut": {"en": "Size", "de": "Größe", "es": "Tamaño", "fr": "Taille"},
    "Süre": {"en": "Duration", "de": "Dauer", "es": "Duración", "fr": "Durée"},
    "Tarih": {"en": "Date", "de": "Datum", "es": "Fecha", "fr": "Date"},
    "İşlem": {"en": "Action", "de": "Aktion", "es": "Acción", "fr": "Action"},
    
    # Queue tab
    "Öncelik": {"en": "Priority", "de": "Priorität", "es": "Prioridad", "fr": "Priorité"},
    "Durum": {"en": "Status", "de": "Status", "es": "Estado", "fr": "Statut"},
    "Bekliyor": {"en": "Waiting", "de": "Wartend", "es": "Esperando", "fr": "En attente"},
    "İndiriliyor": {"en": "Downloading", "de": "Herunterladen", "es": "Descargando", "fr": "Téléchargement"},
    "Başarılı": {"en": "Success", "de": "Erfolgreich", "es": "Éxito", "fr": "Succès"},
    "Başarısız": {"en": "Failed", "de": "Fehlgeschlagen", "es": "Fallido", "fr": "Échec"},
    
    # Converter tab
    "Dönüştürülecek dosyaları sürükleyip bırakın\nveya tıklayarak seçin": {
        "en": "Drop files here to convert\nor click to select",
        "de": "Dateien hier ablegen zum Konvertieren\noder klicken zum Auswählen",
        "es": "Suelte archivos aquí para convertir\no haga clic para seleccionar",
        "fr": "Déposez les fichiers ici pour convertir\nou cliquez pour sélectionner"
    },
    "Dosya Seç": {"en": "Select Files", "de": "Dateien Wählen", "es": "Seleccionar Archivos", "fr": "Sélectionner Fichiers"},
    "Dönüştür": {"en": "Convert", "de": "Konvertieren", "es": "Convertir", "fr": "Convertir"},
    "Temizle": {"en": "Clear", "de": "Löschen", "es": "Limpiar", "fr": "Effacer"},
    
    # Common actions
    "Yenile": {"en": "Refresh", "de": "Aktualisieren", "es": "Actualizar", "fr": "Actualiser"},
    "Sil": {"en": "Delete", "de": "Löschen", "es": "Eliminar", "fr": "Supprimer"},
    "Kopyala": {"en": "Copy", "de": "Kopieren", "es": "Copiar", "fr": "Copier"},
    "Yapıştır": {"en": "Paste", "de": "Einfügen", "es": "Pegar", "fr": "Coller"},
    "Kes": {"en": "Cut", "de": "Ausschneiden", "es": "Cortar", "fr": "Couper"},
    "Geri Al": {"en": "Undo", "de": "Rückgängig", "es": "Deshacer", "fr": "Annuler"},
    "Yinele": {"en": "Redo", "de": "Wiederholen", "es": "Rehacer", "fr": "Rétablir"},
    "Tümünü Seç": {"en": "Select All", "de": "Alles Auswählen", "es": "Seleccionar Todo", "fr": "Tout Sélectionner"},
    
    # Dialogs
    "Uyarı": {"en": "Warning", "de": "Warnung", "es": "Advertencia", "fr": "Avertissement"},
    "Hata": {"en": "Error", "de": "Fehler", "es": "Error", "fr": "Erreur"},
    "Bilgi": {"en": "Information", "de": "Information", "es": "Información", "fr": "Information"},
    "Onay": {"en": "Confirmation", "de": "Bestätigung", "es": "Confirmación", "fr": "Confirmation"},
    "Evet": {"en": "Yes", "de": "Ja", "es": "Sí", "fr": "Oui"},
    "Hayır": {"en": "No", "de": "Nein", "es": "No", "fr": "Non"},
    "Tamam": {"en": "OK", "de": "OK", "es": "OK", "fr": "OK"},
}


def create_ts_file(language_code, translations):
    """Create a Qt translation file (.ts) for a language"""
    
    # Create root element
    root = ET.Element("TS", version="2.1", language=language_code)
    
    # Group translations by context (class name)
    contexts = {
        "MainWindow": [],
        "SettingsDialog": [],
        "HistoryWidget": [],
        "QueueWidget": [],
        "ConverterWidget": [],
        "General": []
    }
    
    # Categorize translations
    for source, trans_dict in translations.items():
        if language_code not in trans_dict:
            continue
            
        translation = trans_dict[language_code]
        
        # Determine context based on content
        if source in ["İndir", "Geçmiş", "Sıra", "Dönüştür", "Dosya", "Düzen", "Ayarlar", "Yardım"]:
            context = "MainWindow"
        elif source in ["Dil / Language:", "Tema:", "Açık", "Koyu", "Görünüm", "Bildirimler"]:
            context = "SettingsDialog"
        elif source in ["Başlık", "Dosya Adı", "Boyut", "Süre", "Tarih"]:
            context = "HistoryWidget"
        elif source in ["Öncelik", "Durum", "Bekliyor", "İndiriliyor"]:
            context = "QueueWidget"
        elif "Dönüştür" in source or "dosya" in source.lower():
            context = "ConverterWidget"
        else:
            context = "General"
        
        contexts[context].append((source, translation))
    
    # Create context elements
    for context_name, messages in contexts.items():
        if not messages:
            continue
            
        context = ET.SubElement(root, "context")
        name = ET.SubElement(context, "name")
        name.text = context_name
        
        for source_text, translation_text in messages:
            message = ET.SubElement(context, "message")
            source = ET.SubElement(message, "source")
            source.text = source_text
            translation = ET.SubElement(message, "translation")
            translation.text = translation_text
    
    # Pretty print XML
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="    ")
    
    # Remove extra blank lines
    lines = pretty_xml.split('\n')
    lines = [line for line in lines if line.strip()]
    
    return '\n'.join(lines)


def main():
    """Generate translation files for supported languages"""
    
    languages = ["en", "de", "es", "fr"]
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")
    
    os.makedirs(translations_dir, exist_ok=True)
    
    for lang in languages:
        ts_content = create_ts_file(lang, COMMON_TRANSLATIONS)
        ts_file = os.path.join(translations_dir, f"mp3yap_{lang}.ts")
        
        with open(ts_file, 'w', encoding='utf-8') as f:
            f.write(ts_content)
        
        print(f"Created {ts_file}")
        
        # Try to compile to .qm file using lrelease if available
        try:
            import subprocess
            qm_file = os.path.join(translations_dir, f"mp3yap_{lang}.qm")
            subprocess.run(["lrelease", ts_file, "-qm", qm_file], check=True)
            print(f"Compiled {qm_file}")
        except:
            print(f"Could not compile {lang}.qm - lrelease not found")
    
    print("\nTranslation files generated successfully!")
    print("Note: You may need to install Qt tools to compile .qm files:")
    print("  brew install qt (macOS)")
    print("  apt-get install qttools5-dev-tools (Ubuntu/Debian)")
    print("  pip install PyQt5-tools (Python)")


if __name__ == "__main__":
    main()