"""Pytest configuration and shared fixtures"""
import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize database if needed before running tests
from database.migration_runner import ensure_translations_db
ensure_translations_db()


@pytest.fixture
def translation_manager():
    """Fixture that provides translation_manager instance"""
    from utils.translation_manager import translation_manager
    return translation_manager


@pytest.fixture(params=['en', 'tr'])
def language(request, translation_manager):
    """Parametrized fixture to test in both English and Turkish"""
    original_lang = translation_manager.get_current_language()
    translation_manager.set_language(request.param)
    yield request.param
    # Restore original language after test
    translation_manager.set_language(original_lang)


@pytest.fixture
def mock_download_signals(mocker):
    """Mock PyQt5 signals for downloader tests"""
    signals = mocker.MagicMock()
    signals.progress = mocker.MagicMock()
    signals.finished = mocker.MagicMock()
    signals.error = mocker.MagicMock()
    signals.status_update = mocker.MagicMock()
    return signals
