#!/usr/bin/env python3
"""Database migration runner - initializes translations.db from SQL migrations"""

import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MigrationRunner:
    """Runs SQL migration files to initialize/update the translations database"""

    def __init__(self, db_path='data/translations.db', migrations_dir='scripts/migrations'):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.db_exists = os.path.exists(db_path)

    def needs_initialization(self):
        """Check if database needs to be initialized"""
        return not self.db_exists

    def run_migrations(self):
        """Run all migration files in order"""
        if not self.migrations_dir.exists():
            logger.error(f"Migrations directory not found: {self.migrations_dir}")
            return False

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Get all .sql files sorted by name
        migration_files = sorted(self.migrations_dir.glob('*.sql'))

        if not migration_files:
            logger.error(f"No migration files found in {self.migrations_dir}")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                for migration_file in migration_files:
                    logger.info(f"Running migration: {migration_file.name}")

                    with open(migration_file, 'r', encoding='utf-8') as f:
                        sql = f.read()

                    # Execute the migration
                    conn.executescript(sql)
                    logger.info(f"✅ Migration completed: {migration_file.name}")

            logger.info(f"✅ All migrations completed successfully. Database created at: {self.db_path}")
            return True

        except sqlite3.Error as e:
            logger.error(f"❌ Migration failed: {e}")
            # Clean up partial database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            return False

    def initialize_if_needed(self):
        """Initialize database if it doesn't exist"""
        if self.needs_initialization():
            logger.info("Translations database not found. Initializing from migrations...")
            return self.run_migrations()
        else:
            logger.debug("Translations database already exists")
            return True


def ensure_translations_db():
    """Convenience function to ensure translations database exists"""
    runner = MigrationRunner()
    return runner.initialize_if_needed()


if __name__ == '__main__':
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    runner = MigrationRunner()

    if runner.needs_initialization():
        print("🔄 Initializing translations database...")
        success = runner.run_migrations()
        if success:
            print("✅ Database initialization complete!")
        else:
            print("❌ Database initialization failed!")
            exit(1)
    else:
        print("✅ Translations database already exists")
