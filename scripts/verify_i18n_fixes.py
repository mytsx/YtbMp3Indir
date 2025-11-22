#!/usr/bin/env python3
"""
Verification script for HIGH priority i18n fixes.
This script checks that all translation keys exist in the database.
"""

import sqlite3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from database.translation_db import translation_db

# Expected translation keys
EXPECTED_KEYS = [
    # ui/main_window.py keys
    'dialogs.errors.file_encoding_error',
    'main.url_validation.videos_ready',
    'main.url_validation.playlists',
    'main.url_validation.videos',
    'main.url_validation.playlist_item',
    'main.url_validation.invalid_urls',
    'main.url_validation.files_exist',
    'main.url_validation.files_missing',
    'main.url_validation.unknown_records',
    # Status detection keywords
    'keywords.converting_to_mp3',
    'keywords.conversion',
    # utils/update_checker.py keys
    'update.messages.new_version_available',
    'update.messages.up_to_date',
    'update.errors.api_response_failed',
    'update.errors.check_failed',
    'update.errors.unexpected_error'
]

def verify_translations():
    """Verify all expected translation keys exist in database."""
    print("="*60)
    print("🔍 VERIFYING HIGH PRIORITY I18N FIXES")
    print("="*60)
    print()

    conn = sqlite3.connect(translation_db.db_path)
    cursor = conn.cursor()

    all_ok = True
    missing_keys = []
    incomplete_keys = []
    verified_keys = []

    for key in EXPECTED_KEYS:
        # Check if key exists with both EN and TR translations
        cursor.execute("""
            SELECT
                k.key_text,
                k.description,
                t_en.translated_text as en,
                t_tr.translated_text as tr
            FROM translation_keys k
            LEFT JOIN translations t_en ON k.key_id = t_en.key_id AND t_en.lang_code = 'en'
            LEFT JOIN translations t_tr ON k.key_id = t_tr.key_id AND t_tr.lang_code = 'tr'
            WHERE k.key_text = ?
        """, (key,))

        result = cursor.fetchone()

        if not result:
            print(f"❌ MISSING: {key}")
            missing_keys.append(key)
            all_ok = False
        else:
            key_text, description, en_text, tr_text = result
            if not en_text or not tr_text:
                print(f"⚠️  INCOMPLETE: {key}")
                print(f"    EN: {'✓' if en_text else '✗'}")
                print(f"    TR: {'✓' if tr_text else '✗'}")
                incomplete_keys.append(key)
                all_ok = False
            else:
                print(f"✅ VERIFIED: {key}")
                print(f"    EN: {en_text}")
                print(f"    TR: {tr_text}")
                verified_keys.append(key)

    conn.close()

    print()
    print("="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    print(f"✅ Verified:   {len(verified_keys)}/{len(EXPECTED_KEYS)}")
    print(f"❌ Missing:    {len(missing_keys)}/{len(EXPECTED_KEYS)}")
    print(f"⚠️  Incomplete: {len(incomplete_keys)}/{len(EXPECTED_KEYS)}")
    print("="*60)

    if all_ok:
        print("\n🎉 SUCCESS! All translation keys are verified!")
        return True
    else:
        print("\n❌ VERIFICATION FAILED! Some keys are missing or incomplete.")
        return False

def show_code_changes():
    """Show summary of code changes made."""
    print("\n")
    print("="*60)
    print("📝 CODE CHANGES SUMMARY")
    print("="*60)
    print()
    print("File: ui/main_window.py")
    print("-" * 60)
    print("1. Line 606: file_encoding_error")
    print("   OLD: f'Dosya kodlama hatası: {str(e)}'")
    print("   NEW: translation_manager.tr('dialogs.errors.file_encoding_error').format(error=str(e))")
    print()
    print("2. Lines 839-841: CRITICAL conversion detection")
    print("   OLD: if \"MP3'e dönüştürülüyor\" in status or \"Dönüştürme\" in status:")
    print("   NEW: converting_kw = translation_manager.tr('keywords.converting_to_mp3')")
    print("        conversion_kw = translation_manager.tr('keywords.conversion')")
    print("        if converting_kw in status or conversion_kw in status:")
    print()
    print("3. Line 1028: videos_ready")
    print("   OLD: f'✓ {len(result.valid_urls)} video indirmeye hazır'")
    print("   NEW: translation_manager.tr('main.url_validation.videos_ready').format(count=len(result.valid_urls))")
    print()
    print("4. Line 1033: playlists count")
    print("   OLD: f'{len(playlists)} playlist'")
    print("   NEW: translation_manager.tr('main.url_validation.playlists').format(count=len(playlists))")
    print()
    print("5. Line 1035: videos count")
    print("   OLD: f'{len(single_videos)} video'")
    print("   NEW: translation_manager.tr('main.url_validation.videos').format(count=len(single_videos))")
    print()
    print("6. Line 1041: playlist_item")
    print("   OLD: f'  • {p['title'][:30]}'")
    print("   NEW: translation_manager.tr('main.url_validation.playlist_item').format(title=p['title'][:30])")
    print()
    print("7. Line 1049: invalid_urls")
    print("   OLD: f'✗ {len(result.invalid_urls)} geçersiz URL'")
    print("   NEW: translation_manager.tr('main.url_validation.invalid_urls').format(count=len(result.invalid_urls))")
    print()
    print("8. Line 1053: files_exist")
    print("   OLD: f'✓ {result.files_exist} dosya hem indirilmiş hem de klasörde mevcut'")
    print("   NEW: translation_manager.tr('main.url_validation.files_exist').format(count=result.files_exist)")
    print()
    print("9. Line 1056: files_missing")
    print("   OLD: f'⚠ {result.files_missing} dosya daha önce indirilmiş ama klasörde bulunamadı'")
    print("   NEW: translation_manager.tr('main.url_validation.files_missing').format(count=result.files_missing)")
    print()
    print("10. Line 1060: unknown_records")
    print("    OLD: f'? {unknown} dosya kaydı eksik bilgi içeriyor'")
    print("    NEW: translation_manager.tr('main.url_validation.unknown_records').format(count=unknown)")
    print()
    print()
    print("File: utils/update_checker.py")
    print("-" * 60)
    print("1. Added import:")
    print("   from utils.translation_manager import translation_manager")
    print()
    print("2. Line 43: new_version_available")
    print("   OLD: f'Yeni sürüm mevcut: v{latest_version}'")
    print("   NEW: translation_manager.tr('update.messages.new_version_available').format(version=latest_version)")
    print()
    print("3. Line 45: up_to_date")
    print("   OLD: 'Güncel sürümü kullanıyorsunuz'")
    print("   NEW: translation_manager.tr('update.messages.up_to_date')")
    print()
    print("4. Line 47: api_response_failed")
    print("   OLD: f'Hata: API yanıtı okunamadı: {e}'")
    print("   NEW: translation_manager.tr('update.errors.api_response_failed').format(error=str(e))")
    print()
    print("5. Line 49: check_failed")
    print("   OLD: f'Güncelleme kontrolü başarısız: {e}'")
    print("   NEW: translation_manager.tr('update.errors.check_failed').format(error=str(e))")
    print()
    print("6. Line 52: unexpected_error")
    print("   OLD: 'Hata: Beklenmedik bir hata oluştu.'")
    print("   NEW: translation_manager.tr('update.errors.unexpected_error')")
    print()
    print("="*60)

if __name__ == '__main__':
    success = verify_translations()
    show_code_changes()

    if success:
        print("\n✅ ALL HIGH PRIORITY I18N FIXES COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED!")
        sys.exit(1)
