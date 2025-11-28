"""
Parent Process Watchdog
Monitors stdin for EOF to detect when parent process (Flutter) dies.
When stdin closes, the backend automatically shuts down.

This is the most reliable way to prevent zombie processes because:
- When parent dies (crash, force kill, etc.), OS closes the pipe
- Python detects EOF immediately
- No polling needed, no race conditions
- Works across all platforms (macOS, Windows, Linux)
"""
import sys
import os
import threading
import logging

logger = logging.getLogger(__name__)

_watchdog_thread = None
_shutdown_callback = None


def _watch_stdin():
    """
    Watch stdin for EOF (parent process death).
    This runs in a daemon thread and blocks on stdin.read().
    When parent dies, stdin is closed by OS and read() returns.
    """
    import time

    # Small delay to allow normal startup
    # This prevents false triggers when shell disconnects stdin immediately
    time.sleep(2)

    try:
        # Block until stdin is closed (EOF)
        # This happens when parent process dies
        sys.stdin.read()
    except Exception as e:
        logger.debug(f"stdin read exception (expected on shutdown): {e}")

    logger.warning("stdin EOF detected - parent process died!")

    # Call shutdown callback if registered
    if _shutdown_callback:
        try:
            _shutdown_callback()
        except Exception as e:
            logger.error(f"Error in shutdown callback: {e}")

    # Force exit - parent is gone, no point in graceful shutdown
    logger.info("Watchdog triggering immediate shutdown...")
    os._exit(0)


def start_watchdog(shutdown_callback=None):
    """
    Start the parent process watchdog.

    Args:
        shutdown_callback: Optional function to call before exit
                          (e.g., to cleanup resources)

    Returns:
        True if watchdog started, False if already running or stdin not a pipe
    """
    global _watchdog_thread, _shutdown_callback

    # Don't start if already running
    if _watchdog_thread is not None and _watchdog_thread.is_alive():
        logger.debug("Watchdog already running")
        return False

    # Check if stdin is a pipe (i.e., we were started by another process)
    # If running interactively (terminal), stdin is a TTY, not a pipe
    if sys.stdin is None:
        logger.info("stdin is None - watchdog disabled")
        return False

    try:
        if sys.stdin.isatty():
            logger.info("stdin is TTY (interactive mode) - watchdog disabled")
            return False
    except Exception:
        # isatty() might fail in some edge cases
        pass

    _shutdown_callback = shutdown_callback

    # Start watchdog in daemon thread
    # Daemon threads are automatically killed when main thread exits
    _watchdog_thread = threading.Thread(
        target=_watch_stdin,
        name="ParentWatchdog",
        daemon=True
    )
    _watchdog_thread.start()

    logger.info("Parent process watchdog started (monitoring stdin for EOF)")
    return True


def stop_watchdog():
    """
    Stop the watchdog (for clean shutdown).
    Note: Since we use os._exit() in watchdog, this is mainly for testing.
    """
    global _watchdog_thread, _shutdown_callback
    _shutdown_callback = None
    # Thread will die when main process exits (daemon=True)
    logger.debug("Watchdog stop requested")
