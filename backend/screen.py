import os
import re
import base64
import tempfile
import time
import subprocess
import pyautogui
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ScreenAnalyzer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_AI_KEY")
        self.model = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            timeout=120.0
        )
        print(f"[SCREEN] Vision model: {self.model} | Google AI Studio")

    def capture_screen(self, path=None):
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "jarvis_screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return path

    def analyze_screen(self, question="What is on the screen?"):
        screenshot_path = self.capture_screen()
        return self._analyze_image(screenshot_path, question)

    def _analyze_image(self, image_path, question):
        try:
            import pyperclip
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a detailed data extractor. Read the screenshot carefully and extract every piece of text and information visible."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Extract ALL text and information from this screenshot. Be extremely thorough.\n\n{question}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=4096
            )

            result = response.choices[0].message.content
            print(f"[SCREEN] Analysis: {result[:300]}")
            return {"success": True, "analysis": result, "screenshot": image_path}

        except Exception as e:
            print(f"[SCREEN] Error: {e}")
            return {"success": False, "error": str(e)}

    def describe_screen(self):
        return self.analyze_screen("Describe everything you see on this screen in detail. What apps are open? What content is visible?")

    def find_element(self, element):
        return self.analyze_screen(f"Where is '{element}' on this screen? Give me the approximate pixel coordinates (x, y) of its center.")

    def search_and_read(self, query, read_question=None):
        if not read_question:
            read_question = f"Extract ALL specific information about '{query}'. Include exact titles, names, companies, dates, details. List everything visible."

        try:
            import pyperclip

            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            chrome_path2 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--new-window", url], shell=True)
            elif os.path.exists(chrome_path2):
                subprocess.Popen([chrome_path2, "--new-window", url], shell=True)
            else:
                import webbrowser
                webbrowser.open(url)

            print(f"[SEARCH] Opened Google for: {query}")
            time.sleep(4)

            screenshot_path = self.capture_screen(
                os.path.join(tempfile.gettempdir(), "jarvis_search_result.png")
            )

            result = self._analyze_image(screenshot_path, read_question)

            if result.get("success") and result.get("analysis") and len(result.get("analysis", "")) > 100:
                print(f"[SEARCH] Read {len(result.get('analysis', ''))} chars from search results")
                return result

            print(f"[SEARCH] Vision result too short or failed, falling back to page scraping...")
            return self._fallback_scrape_results(query, read_question)

        except Exception as e:
            print(f"[SEARCH] Error: {e}")
            return self._fallback_scrape_results(query, read_question)

    def _fallback_scrape_results(self, query, read_question):
        try:
            import pyperclip

            print(f"[FALLBACK] Clicking on search result links...")

            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.3)
            pyperclip.copy(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(4)

            page_contents = []

            for i in range(3):
                try:
                    print(f"[FALLBACK] Clicking result {i+1}...")

                    pyautogui.press("tab")
                    time.sleep(0.1)
                    for _ in range(3 + i * 2):
                        pyautogui.press("tab")
                        time.sleep(0.05)

                    pyautogui.press("enter")
                    time.sleep(3)

                    pyautogui.hotkey("ctrl", "l")
                    time.sleep(0.2)
                    pyautogui.hotkey("ctrl", "c")
                    time.sleep(0.2)
                    current_url = pyperclip.paste()
                    print(f"[FALLBACK] Tab {i+1} URL: {current_url[:80]}")

                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.1)
                    pyautogui.hotkey("ctrl", "c")
                    time.sleep(0.5)
                    text = pyperclip.paste()

                    if text and len(text) > 100:
                        cleaned = ' '.join(text.split())[:5000]
                        page_contents.append(f"Page {i+1} ({current_url[:60]}):\n{cleaned}")
                        print(f"[FALLBACK] Got {len(cleaned)} chars from page {i+1}")

                    pyautogui.hotkey("ctrl", "w")
                    time.sleep(0.3)

                except Exception as e:
                    print(f"[FALLBACK] Page {i+1} error: {e}")
                    try:
                        pyautogui.hotkey("ctrl", "w")
                        time.sleep(0.2)
                    except:
                        pass

            if page_contents:
                all_text = "\n\n---\n\n".join(page_contents)
                print(f"[FALLBACK] Total scraped: {len(all_text)} chars, organizing with AI...")

                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a research assistant. Extract and organize key information from the provided web pages into a clear, concise summary."},
                            {"role": "user", "content": f"Search query: {query}\n\n{read_question}\n\nHere are the contents from the top search results:\n\n{all_text}"}
                        ],
                        max_tokens=4096
                    )

                    analysis = response.choices[0].message.content
                    print(f"[FALLBACK] AI organized: {len(analysis)} chars")
                    return {"success": True, "analysis": analysis, "method": "scraped"}

                except Exception as e:
                    print(f"[FALLBACK] AI organize error: {e}")
                    return {"success": True, "analysis": all_text[:5000], "method": "raw_scraped"}

            return {"success": False, "error": "Could not read any search results"}

        except Exception as e:
            print(f"[FALLBACK] Error: {e}")
            return {"success": False, "error": str(e)}
