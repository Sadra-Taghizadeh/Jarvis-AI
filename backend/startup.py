import os
import sys
import socket

def check_python_version():
    if sys.version_info < (3, 10):
        print(f"[STARTUP] ERROR: Python {sys.version_info.major}.{sys.version_info.minor} found, 3.10+ required")
        return False
    print(f"[STARTUP] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")
    return True

def check_env_vars():
    required = ["OPENROUTER_API_KEY"]
    optional = ["GOOGLE_AI_KEY", "AI_MODEL", "WS_PORT", "OPENROUTER_BASE_URL", "GOOGLE_VISION_MODEL"]
    ok = True

    for var in required:
        if not os.getenv(var):
            print(f"[STARTUP] ERROR: Required env var {var} is not set")
            ok = False
        else:
            print(f"[STARTUP] {var} OK")

    for var in optional:
        val = os.getenv(var)
        if val:
            print(f"[STARTUP] {var} = {val[:20]}..." if len(val) > 20 else f"[STARTUP] {var} = {val}")

    return ok

def check_port():
    port = int(os.getenv("WS_PORT", 8765))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
            print(f"[STARTUP] Port {port} available")
            return True
    except OSError:
        print(f"[STARTUP] ERROR: Port {port} is already in use")
        return False

def check_packages():
    packages = ["websockets", "openai", "pyautogui", "psutil", "dotenv"]
    ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[STARTUP] {pkg} OK")
        except ImportError:
            print(f"[STARTUP] ERROR: Package {pkg} is not installed")
            ok = False
    return ok

def run_checks():
    print("[STARTUP] Running pre-flight checks...")
    print("=" * 50)

    results = [
        check_python_version(),
        check_env_vars(),
        check_port(),
        check_packages()
    ]

    print("=" * 50)
    if all(results):
        print("[STARTUP] All checks passed!")
        return True
    else:
        print("[STARTUP] Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
