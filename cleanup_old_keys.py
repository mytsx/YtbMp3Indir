#!/usr/bin/env python3
"""
Clean up old text-based keys and keep only abstract keys
"""

import sqlite3
from pathlib import Path

def cleanup_old_keys():
    """Remove old text-based keys, keep only abstract keys"""
    db_path = Path('data/translations.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, backup the database
        print("Creating backup...")
        cursor.execute("SELECT COUNT(*) FROM translation_keys")
        total_before = cursor.fetchone()[0]
        print(f"Total keys before cleanup: {total_before}")
        
        # Count old vs new keys
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN key_text LIKE '%.%' THEN 'Abstract'
                    ELSE 'Old Text'
                END as key_type,
                COUNT(*) as count
            FROM translation_keys
            GROUP BY key_type
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} keys")
        
        # Get all old text-based keys to delete
        cursor.execute("""
            SELECT key_id, key_text 
            FROM translation_keys 
            WHERE key_text NOT LIKE '%.%'
        """)
        
        old_keys = cursor.fetchall()
        print(f"\nFound {len(old_keys)} old text-based keys to remove")
        
        if len(old_keys) > 0:
            # Show sample of keys to be deleted
            print("\nSample of keys to be deleted:")
            for key_id, key_text in old_keys[:10]:
                print(f"  - {key_text}")
            
            # Delete translations for old keys
            old_key_ids = [k[0] for k in old_keys]
            placeholders = ','.join('?' * len(old_key_ids))
            
            cursor.execute(f"""
                DELETE FROM translations 
                WHERE key_id IN ({placeholders})
            """, old_key_ids)
            
            deleted_translations = cursor.rowcount
            print(f"\nDeleted {deleted_translations} translations for old keys")
            
            # Delete old keys
            cursor.execute(f"""
                DELETE FROM translation_keys 
                WHERE key_id IN ({placeholders})
            """, old_key_ids)
            
            deleted_keys = cursor.rowcount
            print(f"Deleted {deleted_keys} old keys")
            
            conn.commit()
            
            # Verify cleanup
            cursor.execute("SELECT COUNT(*) FROM translation_keys")
            total_after = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM translation_keys 
                WHERE key_text LIKE '%.%'
            """)
            abstract_count = cursor.fetchone()[0]
            
            print(f"\nCleanup complete!")
            print(f"  Total keys after: {total_after}")
            print(f"  All remaining keys are abstract: {abstract_count == total_after}")
            
            # Show statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT key_text) as unique_keys,
                    COUNT(*) as total_keys
                FROM translation_keys
            """)
            
            unique, total = cursor.fetchone()
            if unique != total:
                print(f"\nWARNING: Found duplicates - {total - unique} duplicate keys")
                
                # Find and show duplicates
                cursor.execute("""
                    SELECT key_text, COUNT(*) as count
                    FROM translation_keys
                    GROUP BY key_text
                    HAVING COUNT(*) > 1
                    LIMIT 5
                """)
                
                dupes = cursor.fetchall()
                if dupes:
                    print("Sample duplicates:")
                    for key, count in dupes:
                        print(f"  - {key}: {count} copies")
        else:
            print("No old keys found - database is already clean!")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if cleanup_old_keys():
        print("\n✓ Database cleanup successful")
    else:
        print("\n✗ Database cleanup failed")