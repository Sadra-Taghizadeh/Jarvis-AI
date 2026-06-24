import os
import re
import subprocess
import platform
import time
import tempfile
import pyautogui
import psutil

ALLOWED_COMMANDS = {"dir", "echo", "python", "pip", "where", "systeminfo", "ipconfig", "ipconfig /all", "hostname", "whoami", "date", "time"}
BLOCKED_PATTERNS = re.compile(r"(rm |format |del |shutdown|taskkill|[|]|&&|\|\||;)", re.IGNORECASE)

class ComputerController:
    def __init__(self):
        self.system = platform.system()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

    def _validate_path(self, path: str) -> bool:
        try:
            resolved = os.path.realpath(os.path.expanduser(path))
            home = os.path.expanduser("~")
            allowed_dirs = [
                os.path.join(home, "Desktop"),
                os.path.join(home, "Documents"),
                os.path.join(home, "Downloads"),
                os.path.join(home, "Pictures"),
                os.path.join(home, "Music"),
                os.path.join(home, "Videos"),
                tempfile.gettempdir(),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory"),
            ]
            return any(resolved.startswith(allowed) for allowed in allowed_dirs)
        except Exception:
            return False

    def _find_browser(self) -> str:
        if self.system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
        elif self.system == "Darwin":
            path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(path):
                return path
        else:
            for name in ["google-chrome", "chromium-browser", "chromium"]:
                try:
                    result = subprocess.run(["which", name], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except Exception:
                    pass
        return ""

    def execute(self, action: dict) -> dict:
        action_type = action.get("action")

        if action_type == "chain":
            return self._chain_actions(action.get("steps", []))

        handlers = {
            "open_app": self._open_app,
            "close_app": self._close_app,
            "type_text": self._type_text,
            "press_key": self._press_key,
            "screenshot": self._screenshot,
            "save_screenshot_to_desktop": self._save_screenshot_to_desktop,
            "save_to_desktop": self._save_to_desktop,
            "search_web": self._search_web,
            "file_operation": self._file_operation,
            "system_info": self._system_info,
            "mouse_click": self._mouse_click,
            "mouse_move": self._mouse_move,
            "wait": self._wait,
            "focus_window": self._focus_window,
            "open_url": self._open_url,
            "run_command": self._run_command,
            "write_and_open": self._write_and_open,
            "google_search": self._google_search,
            "open_new_tab": self._open_new_tab,
            "type_in_chrome": self._type_in_chrome,
        }

        handler = handlers.get(action_type)
        if handler:
            return handler(action)
        return {"success": False, "error": f"Unknown action: {action_type}"}

    def _chain_actions(self, steps: list) -> dict:
        results = []
        for i, step in enumerate(steps):
            action_name = step.get("action", "unknown")
            print(f"[CHAIN] Step {i+1}/{len(steps)}: {action_name}")

            result = self.execute(step)
            results.append({"step": i + 1, "action": action_name, "result": result})

            if not result.get("success", False):
                return {"success": False, "error": f"Step {i+1} ({action_name}) failed: {result.get('error')}", "results": results}

            time.sleep(step.get("delay", 0.5))

        return {"success": True, "message": f"Completed {len(steps)} steps", "results": results}

    def _open_app(self, action: dict) -> dict:
        app = action.get("app", "")
        app_lower = app.lower()

        windows_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "powershell": "powershell.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "brave": "brave.exe",
        }

        exe = windows_apps.get(app_lower, app)

        if app_lower in ["chrome", "google chrome", "firefox", "edge", "brave"]:
            try:
                subprocess.Popen([exe, "--new-window"])
                time.sleep(2)
                return {"success": True, "message": f"Opened {app}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        try:
            if self.system == "Darwin":
                subprocess.Popen(["open", "-a", app])
            elif self.system == "Linux":
                subprocess.Popen([exe])
            else:
                subprocess.Popen([exe])
            time.sleep(1.5)
            self._focus_window_by_title(app_lower)
            return {"success": True, "message": f"Opened {app}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _focus_window_by_title(self, app_name: str):
        try:
            import pygetwindow as gw
            time.sleep(0.5)
            windows = gw.getWindowsWithTitle("")
            for w in windows:
                title = w.title.lower()
                if app_name in title or app_name.replace(".exe", "") in title:
                    try:
                        w.restore()
                        time.sleep(0.2)
                        w.activate()
                        time.sleep(0.3)
                        print(f"[FOCUS] Focused: '{w.title}'")
                        return
                    except Exception:
                        pass
            print(f"[FOCUS] Window not found for '{app_name}'")
        except Exception as e:
            print(f"[FOCUS] Error: {e}")

    def _type_text(self, action: dict) -> dict:
        text = action.get("text", "")
        try:
            screen_w, screen_h = pyautogui.size()
            pyautogui.click(screen_w // 2, screen_h // 2)
            time.sleep(0.3)

            try:
                import pyperclip
                pyperclip.copy(text)
                time.sleep(0.1)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.1)
            except Exception as e:
                print(f"[TYPE] Clipboard failed: {e}, using typewrite")
                pyautogui.typewrite(text, interval=0.03)

            return {"success": True, "message": f"Typed: {text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _write_and_open(self, action: dict) -> dict:
        text = action.get("text", "")
        app = action.get("app", "notepad")
        file_path = action.get("path", os.path.join(tempfile.gettempdir(), "jarvis_output.txt"))

        if not self._validate_path(file_path):
            return {"success": False, "error": "Path not allowed"}

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            if app.lower() == "notepad":
                subprocess.Popen(["notepad.exe", file_path])
            elif self.system == "Darwin":
                subprocess.Popen(["open", file_path])
            else:
                os.startfile(file_path)

            time.sleep(1.5)
            return {"success": True, "message": f"Written to {file_path} and opened in {app}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _google_search(self, action: dict) -> dict:
        query = action.get("query", "")
        try:
            import urllib.parse
            url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
            chrome_path = self._find_browser()
            if chrome_path:
                subprocess.Popen([chrome_path, url])
            else:
                if self.system == "Windows":
                    os.startfile(url)
                elif self.system == "Darwin":
                    subprocess.Popen(["open", url])
                else:
                    subprocess.Popen(["xdg-open", url])
            return {"success": True, "message": f"Searching Google for: {query}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _open_new_tab(self, action: dict) -> dict:
        try:
            pyautogui.hotkey("ctrl", "t")
            time.sleep(1)
            return {"success": True, "message": "Opened new tab"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _type_in_chrome(self, action: dict) -> dict:
        text = action.get("text", "")
        url = action.get("url", "")
        search_url = action.get("search_url", "")

        try:
            pyautogui.hotkey("ctrl", "t")
            time.sleep(0.8)

            content = search_url or url or text
            if content:
                import pyperclip
                pyperclip.copy(content)
                pyautogui.hotkey("ctrl", "v")

            time.sleep(0.2)
            pyautogui.press("enter")
            return {"success": True, "message": f"Navigated to: {content}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _close_app(self, action: dict) -> dict:
        app = action.get("app", "")
        try:
            if self.system == "Windows":
                subprocess.run(["taskkill", "/IM", f"{app}.exe", "/F"], capture_output=True)
            elif self.system == "Darwin":
                subprocess.run(["pkill", "-f", app], capture_output=True)
            else:
                subprocess.run(["killall", app], capture_output=True)
            return {"success": True, "message": f"Closed {app}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _press_key(self, action: dict) -> dict:
        key = action.get("key", "")
        try:
            pyautogui.hotkey(*key.split("+"))
            return {"success": True, "message": f"Pressed: {key}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _screenshot(self, action: dict) -> dict:
        try:
            screenshot = pyautogui.screenshot()
            path = action.get("path", "")
            if not path:
                path = os.path.join(tempfile.gettempdir(), "jarvis_screenshot.png")
            screenshot.save(path)
            return {"success": True, "message": f"Screenshot saved to {path}", "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_to_desktop(self, action: dict) -> dict:
        content = action.get("content", "")
        filename = action.get("filename", "jarvis_output.txt")
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filepath = os.path.join(desktop, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "message": f"Saved to {filepath}", "path": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_screenshot_to_desktop(self, action: dict) -> dict:
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = action.get("filename", "screenshot.png")
            filepath = os.path.join(desktop, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return {"success": True, "message": f"Screenshot saved to {filepath}", "path": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_web(self, action: dict) -> dict:
        query = action.get("query", "")
        return self._google_search({"query": query})

    def _file_operation(self, action: dict) -> dict:
        operation = action.get("operation", "read")
        path = action.get("path", "")
        content = action.get("content", "")

        if not self._validate_path(path):
            return {"success": False, "error": "Path not allowed"}

        try:
            if operation == "read":
                with open(path, "r", encoding="utf-8") as f:
                    return {"success": True, "content": f.read()}
            elif operation == "write":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"success": True, "message": f"Written to {path}"}
            elif operation == "append":
                with open(path, "a", encoding="utf-8") as f:
                    f.write(content + "\n")
                return {"success": True, "message": f"Appended to {path}"}
            elif operation == "list":
                return {"success": True, "files": os.listdir(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": f"Unknown operation: {operation}"}

    def _system_info(self, action: dict) -> dict:
        try:
            disk_path = "C:\\" if self.system == "Windows" else "/"
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage(disk_path).percent,
            }
            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _mouse_click(self, action: dict) -> dict:
        x = action.get("x", 0)
        y = action.get("y", 0)
        try:
            pyautogui.click(x, y)
            return {"success": True, "message": f"Clicked at ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _mouse_move(self, action: dict) -> dict:
        x = action.get("x", 0)
        y = action.get("y", 0)
        try:
            pyautogui.moveTo(x, y)
            return {"success": True, "message": f"Moved to ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _wait(self, action: dict) -> dict:
        seconds = min(action.get("seconds", 1), 30)
        time.sleep(seconds)
        return {"success": True, "message": f"Waited {seconds} seconds"}

    def _focus_window(self, action: dict) -> dict:
        try:
            if self.system == "Windows":
                pyautogui.hotkey("alt", "tab")
            elif self.system == "Darwin":
                subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke tab using {command down}'], capture_output=True)
            time.sleep(0.5)
            return {"success": True, "message": "Switched window"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _open_url(self, action: dict) -> dict:
        url = action.get("url", "")
        try:
            chrome_path = self._find_browser()
            if chrome_path:
                subprocess.Popen([chrome_path, url])
            elif self.system == "Windows":
                os.startfile(url)
            elif self.system == "Darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            return {"success": True, "message": f"Opened URL: {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_command(self, action: dict) -> dict:
        command = action.get("command", "")
        cmd_lower = command.lower().strip()

        if BLOCKED_PATTERNS.search(command):
            return {"success": False, "error": "Command contains blocked patterns"}

        base_cmd = cmd_lower.split()[0] if cmd_lower.split() else ""
        if base_cmd not in ALLOWED_COMMANDS:
            return {"success": False, "error": f"Command '{base_cmd}' is not in the allowlist"}

        try:
            result = subprocess.run(command, shell=False, capture_output=True, text=True, timeout=30)
            return {"success": True, "output": result.stdout, "error_output": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
