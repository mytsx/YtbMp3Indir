"""
Backend Integration Tests
Tests backend startup, port allocation, and basic API functionality
"""
import subprocess
import time
import requests
import re
import sys


def test_backend_startup():
    """Test that backend starts and prints port to stdout"""
    print("🧪 Test 1: Backend startup and port discovery...")

    # Start backend process
    process = subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Read first line (should contain BACKEND_READY)
        line = process.stdout.readline()
        print(f"   First line: {line.strip()}")

        # Check format
        if not line.startswith("BACKEND_READY PORT="):
            print("   ❌ FAIL: Backend did not print BACKEND_READY message")
            return False, None

        # Extract port
        match = re.search(r'PORT=(\d+)', line)
        if not match:
            print("   ❌ FAIL: Could not extract port number")
            return False, None

        port = int(match.group(1))
        print(f"   ✅ PASS: Backend started on port {port}")

        # Wait for server to be ready
        time.sleep(2)

        return True, port

    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        return False, None

    finally:
        # Don't kill yet, we'll use it for other tests
        pass


def test_health_endpoint(port):
    """Test /api/health endpoint"""
    print("\n🧪 Test 2: Health endpoint...")

    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/health", timeout=5)

        if response.status_code != 200:
            print(f"   ❌ FAIL: Status code {response.status_code}")
            return False

        data = response.json()
        if data.get('status') != 'ok':
            print(f"   ❌ FAIL: Status not ok: {data}")
            return False

        print(f"   ✅ PASS: Health check successful: {data}")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        return False


def test_config_endpoint(port):
    """Test /api/config endpoint"""
    print("\n🧪 Test 3: Config endpoint...")

    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/config", timeout=5)

        if response.status_code != 200:
            print(f"   ❌ FAIL: Status code {response.status_code}")
            return False

        data = response.json()

        # Check ApiResponse envelope
        if 'success' not in data:
            print(f"   ❌ FAIL: Missing 'success' field")
            return False

        if data['success'] != True:
            print(f"   ❌ FAIL: success is not True")
            return False

        if 'data' not in data:
            print(f"   ❌ FAIL: Missing 'data' field")
            return False

        config = data['data']
        required_fields = ['output_dir', 'quality', 'auto_open', 'language']
        for field in required_fields:
            if field not in config:
                print(f"   ❌ FAIL: Missing required field: {field}")
                return False

        print(f"   ✅ PASS: Config endpoint successful")
        print(f"      Config: {config}")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        return False


def test_downloads_endpoint(port):
    """Test /api/downloads POST endpoint"""
    print("\n🧪 Test 4: Downloads endpoint (POST)...")

    try:
        payload = {
            "url": "https://youtube.com/watch?v=test",
            "quality": "192"
        }

        response = requests.post(
            f"http://127.0.0.1:{port}/api/downloads",
            json=payload,
            timeout=5
        )

        if response.status_code != 200:
            print(f"   ❌ FAIL: Status code {response.status_code}")
            return False

        data = response.json()

        # Check ApiResponse envelope
        if not data.get('success'):
            print(f"   ❌ FAIL: success is not True")
            return False

        download = data['data']
        required_fields = ['id', 'url', 'status', 'progress']
        for field in required_fields:
            if field not in download:
                print(f"   ❌ FAIL: Missing required field: {field}")
                return False

        print(f"   ✅ PASS: Download created successfully")
        print(f"      Download ID: {download['id']}")
        print(f"      Status: {download['status']}")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        return False


def test_downloads_list(port):
    """Test /api/downloads GET endpoint"""
    print("\n🧪 Test 5: Downloads endpoint (GET)...")

    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/downloads", timeout=5)

        if response.status_code != 200:
            print(f"   ❌ FAIL: Status code {response.status_code}")
            return False

        data = response.json()

        if not data.get('success'):
            print(f"   ❌ FAIL: success is not True")
            return False

        downloads = data['data']
        if not isinstance(downloads, list):
            print(f"   ❌ FAIL: data is not a list")
            return False

        print(f"   ✅ PASS: Downloads list retrieved")
        print(f"      Total downloads: {len(downloads)}")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        return False


def test_response_envelope(port):
    """Test that all endpoints return correct ApiResponse format"""
    print("\n🧪 Test 6: ApiResponse envelope format...")

    endpoints = [
        ('GET', f"http://127.0.0.1:{port}/api/config"),
        ('GET', f"http://127.0.0.1:{port}/api/downloads"),
        ('GET', f"http://127.0.0.1:{port}/api/history"),
    ]

    all_pass = True
    for method, url in endpoints:
        try:
            if method == 'GET':
                response = requests.get(url, timeout=5)

            data = response.json()

            # Check envelope structure
            if 'success' not in data:
                print(f"   ❌ FAIL: {url} missing 'success'")
                all_pass = False
                continue

            if 'data' not in data:
                print(f"   ❌ FAIL: {url} missing 'data'")
                all_pass = False
                continue

            if 'error' not in data:
                print(f"   ❌ FAIL: {url} missing 'error'")
                all_pass = False
                continue

            # On success, error should be None
            if data['success'] and data['error'] is not None:
                print(f"   ❌ FAIL: {url} success=True but error is not None")
                all_pass = False
                continue

        except Exception as e:
            print(f"   ❌ FAIL: {url} exception: {e}")
            all_pass = False

    if all_pass:
        print(f"   ✅ PASS: All endpoints return correct ApiResponse format")

    return all_pass


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Backend Integration Tests")
    print("=" * 60)

    # Test 1: Startup
    success, port = test_backend_startup()
    if not success:
        print("\n❌ CRITICAL: Backend startup failed, aborting tests")
        return False

    # Give backend time to fully start
    time.sleep(2)

    # Run remaining tests
    results = []
    results.append(("Health endpoint", test_health_endpoint(port)))
    results.append(("Config endpoint", test_config_endpoint(port)))
    results.append(("Downloads POST", test_downloads_endpoint(port)))
    results.append(("Downloads GET", test_downloads_list(port)))
    results.append(("Response envelope", test_response_envelope(port)))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results) + 1  # +1 for startup test

    print(f"Passed: {passed + 1}/{total}")
    print(f"Failed: {total - passed - 1}/{total}")

    if passed + 1 == total:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False


if __name__ == '__main__':
    import os

    # Change to backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(backend_dir)
    print(f"Working directory: {os.getcwd()}\n")

    success = run_all_tests()

    # Cleanup: kill backend process
    print("\n🧹 Cleaning up...")
    import signal
    import psutil

    # Kill any Python processes running main.py
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python3' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and 'main.py' in ' '.join(cmdline):
                    print(f"   Killing process {proc.info['pid']}")
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    sys.exit(0 if success else 1)
