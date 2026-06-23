import os
import subprocess
import platform
import time
import tempfile
import pyautogui
import psutil

class ComputerController:
    def __init__(self):
        self.system = platform.system()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

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
                subprocess.Popen([exe, "--new-window"], shell=True)
                time.sleep(2)
                return {"success": True, "message": f"Opened {app}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        try:
            subprocess.Popen([exe], shell=True)
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
                    except:
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

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            if app.lower() == "notepad":
                subprocess.Popen(["notepad.exe", file_path], shell=True)
            else:
                os.startfile(file_path)

            time.sleep(1.5)
            return {"success": True, "message": f"Written to {file_path} and opened in {app}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _google_search(self, action: dict) -> dict:
        query = action.get("query", "")
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, url], shell=True)
            else:
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, url], shell=True)
                else:
                    os.startfile(url)
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
            import pyautogui
            from PIL import Image
            screenshot = pyautogui.screenshot()
            path = action.get("path", "")
            if not path:
                import tempfile
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
            import pyautogui
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

    def _system_info(self, action: dict) -> dict:
        try:
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('C:\\').percent if platform.system() == "Windows" else psutil.disk_usage('/').percent,
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
        seconds = action.get("seconds", 1)
        time.sleep(seconds)
        return {"success": True, "message": f"Waited {seconds} seconds"}

    def _focus_window(self, action: dict) -> dict:
        try:
            if self.system == "Windows":
                pyautogui.hotkey("alt", "tab")
                time.sleep(0.5)
            return {"success": True, "message": "Switched window"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _open_url(self, action: dict) -> dict:
        url = action.get("url", "")
        try:
            if self.system == "Windows":
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, url], shell=True)
                else:
                    os.startfile(url)
            return {"success": True, "message": f"Opened URL: {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_command(self, action: dict) -> dict:
        command = action.get("command", "")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {"success": True, "output": result.stdout, "error_output": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
