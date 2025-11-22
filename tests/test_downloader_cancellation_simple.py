"""
Simplified tests for DOWNLOAD_CANCELLED_MARKER exception handling

These tests focus on the core logic of detecting the cancellation marker
without requiring full integration with yt-dlp.
"""
import pytest
import yt_dlp
from core.downloader import DOWNLOAD_CANCELLED_MARKER
from utils.translation_manager import translation_manager


class TestCancellationMarkerLogic:
    """Test the core cancellation marker logic"""

    def test_marker_is_language_independent_constant(self):
        """
        CRITICAL: Verify DOWNLOAD_CANCELLED_MARKER is a hardcoded English string

        This is the key fix - the marker must be language-independent.
        """
        assert DOWNLOAD_CANCELLED_MARKER == "DOWNLOAD_CANCELLED_BY_USER"
        assert isinstance(DOWNLOAD_CANCELLED_MARKER, str)

    def test_marker_detection_logic(self):
        """
        Test the actual detection logic that would be used in exception handling

        This simulates what happens at line 505 in core/downloader.py:
            if DOWNLOAD_CANCELLED_MARKER in str(e):
        """
        # Create exceptions with and without the marker
        cancellation_error = yt_dlp.DownloadError(DOWNLOAD_CANCELLED_MARKER)
        regular_error = yt_dlp.DownloadError("Network timeout")
        embedded_marker_error = yt_dlp.DownloadError(f"Failed: {DOWNLOAD_CANCELLED_MARKER} at 50%")

        # Test detection logic
        assert DOWNLOAD_CANCELLED_MARKER in str(cancellation_error)
        assert DOWNLOAD_CANCELLED_MARKER not in str(regular_error)
        assert DOWNLOAD_CANCELLED_MARKER in str(embedded_marker_error)

    def test_marker_case_sensitivity(self):
        """
        Verify marker detection is case-sensitive

        This prevents false positives from case variations.
        """
        wrong_case = yt_dlp.DownloadError(DOWNLOAD_CANCELLED_MARKER.lower())
        assert DOWNLOAD_CANCELLED_MARKER not in str(wrong_case)

    @pytest.mark.parametrize('language', ['en', 'tr'])
    def test_translated_messages_exist(self, language):
        """
        Verify cancellation error messages exist in both languages

        While detection uses the constant, user-facing messages should be translated.
        """
        translation_manager.set_language(language)
        msg = translation_manager.tr('downloader.errors.download_cancelled')

        # Message should exist and not be the key itself
        assert msg != 'downloader.errors.download_cancelled'
        assert len(msg) > 0

    def test_english_and_turkish_messages_differ(self):
        """
        Verify different languages produce different user-facing messages
        """
        translation_manager.set_language('en')
        msg_en = translation_manager.tr('downloader.errors.download_cancelled')

        translation_manager.set_language('tr')
        msg_tr = translation_manager.tr('downloader.errors.download_cancelled')

        assert msg_en != msg_tr


class TestCancellationMarkerRegression:
    """
    Regression tests to prevent reintroduction of language-dependent bugs
    """

    def test_marker_not_translated(self):
        """
        CRITICAL REGRESSION TEST: Marker must be a constant, not translated

        The bug we fixed was checking for translated strings:
            cancelled_msg = translation_manager.tr('...')
            if cancelled_msg in str(e):

        This test ensures the marker is a simple constant.
        """
        # The marker should be importable without translation_manager
        from core.downloader import DOWNLOAD_CANCELLED_MARKER

        # Should be a simple string, not involving translations
        assert DOWNLOAD_CANCELLED_MARKER == "DOWNLOAD_CANCELLED_BY_USER"

        # Should not change with language
        translation_manager.set_language('en')
        from core.downloader import DOWNLOAD_CANCELLED_MARKER as marker_en

        translation_manager.set_language('tr')
        from core.downloader import DOWNLOAD_CANCELLED_MARKER as marker_tr

        # Marker should be identical regardless of language
        assert marker_en == marker_tr == "DOWNLOAD_CANCELLED_BY_USER"

    def test_exception_creation_uses_marker(self):
        """
        Verify exceptions can be created with the marker

        This simulates what happens at line 344 in core/downloader.py:
            raise yt_dlp.DownloadError(DOWNLOAD_CANCELLED_MARKER)
        """
        # Should be able to create exception with marker
        error = yt_dlp.DownloadError(DOWNLOAD_CANCELLED_MARKER)

        # Marker should be in the exception string
        assert DOWNLOAD_CANCELLED_MARKER in str(error)
        assert str(error) == DOWNLOAD_CANCELLED_MARKER


class TestCancellationWorkflow:
    """
    Test the expected workflow for cancellation detection
    """

    def test_cancellation_workflow_simulation(self):
        """
        Simulate the complete cancellation workflow:
        1. Cancel button pressed -> is_running = False
        2. Progress hook raises DownloadError(DOWNLOAD_CANCELLED_MARKER)
        3. Exception handler detects marker
        4. Displays translated cancellation message to user
        """
        # Step 1: Cancellation is triggered (simulated)
        is_running = False

        # Step 2: Exception is raised with marker (as in line 344)
        if not is_running:
            cancellation_exception = yt_dlp.DownloadError(DOWNLOAD_CANCELLED_MARKER)

        # Step 3: Exception handler detects marker (as in line 505)
        is_cancellation = DOWNLOAD_CANCELLED_MARKER in str(cancellation_exception)
        assert is_cancellation, "Cancellation should be detected"

        # Step 4: Get translated message for user (as in line 506)
        translation_manager.set_language('tr')  # User's language
        user_message = translation_manager.tr('downloader.errors.download_cancelled')

        # User sees translated message, not the marker
        assert user_message != DOWNLOAD_CANCELLED_MARKER
        assert DOWNLOAD_CANCELLED_MARKER not in user_message
