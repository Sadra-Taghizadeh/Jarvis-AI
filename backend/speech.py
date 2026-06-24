import os
import tempfile
import base64
from openai import OpenAI

class SpeechRecognizer:
    def __init__(self):
        self.engine = os.getenv("STT_ENGINE", "openai")
        self.client = None

        if self.engine == "openai":
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://opencode.ai/zen/v1")
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = os.getenv("STT_MODEL", "whisper-1")
            print(f"[STT] Using OpenAI Whisper via {base_url}")
        else:
            print(f"[STT] Using local engine: {self.engine}")

    def transcribe(self, audio_base64: str, format: str = "webm") -> dict:
        try:
            audio_bytes = base64.b64decode(audio_base64)

            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                if self.engine == "openai" and self.client:
                    return self._transcribe_openai(tmp_path)
                else:
                    return {"success": False, "error": f"Unknown STT engine: {self.engine}"}
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        except Exception as e:
            print(f"[STT] Error: {e}")
            return {"success": False, "error": str(e)}

    def _transcribe_openai(self, audio_path: str) -> dict:
        try:
            with open(audio_path, "rb") as audio_file:
                result = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language="en"
                )

            text = result.text if hasattr(result, 'text') else str(result)
            print(f"[STT] Transcribed: {text[:100]}")
            return {"success": True, "text": text}

        except Exception as e:
            print(f"[STT] OpenAI error: {e}")
            return {"success": False, "error": str(e)}
