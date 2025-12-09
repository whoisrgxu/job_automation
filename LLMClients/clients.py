# LLMClients/clients.py

import os
from openai import OpenAI
from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv

load_dotenv()


class Model:
    def __init__(self, LLM_name: str, prompt: str):
        self.LLM_name = LLM_name
        self.prompt = prompt

        # Order: 8 -> 7 -> 6 → 5 → 4 → 3 → 2 → 1 → base
        key_names = [
            "GEMINI_API_KEY_8",
            "GEMINI_API_KEY_7",
            "GEMINI_API_KEY_6",
            "GEMINI_API_KEY_5",
            "GEMINI_API_KEY_4",
            "GEMINI_API_KEY_3",
            "GEMINI_API_KEY_2",
            "GEMINI_API_KEY_1",
            "GEMINI_API_KEY",
        ]
        self.gemini_keys = [os.getenv(name) for name in key_names if os.getenv(name)]

    def _call_gemini_once(self, api_key: str) -> str:
        """Single Gemini call with a specific key."""
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.prompt,
        )
        # You can adjust this if your responses can be more complex
        return response.candidates[0].content.parts[0].text.strip()

    def get_response_from_client(self) -> str:
        if self.LLM_name == "OPENAI":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": self.prompt}],
            )
            return response.choices[0].message.content.strip()

        elif self.LLM_name == "GEMINI":
            if not self.gemini_keys:
                raise RuntimeError(
                    "No Gemini API keys found. Please set GEMINI_API_KEY or "
                    "GEMINI_API_KEY_1..8 in your .env"
                )

            last_exc: Exception | None = None

            for idx, key in enumerate(self.gemini_keys, start=1):
                try:
                    print(f"🔑 [GEMINI] Trying key {idx}/{len(self.gemini_keys)}...")
                    return self._call_gemini_once(key)
                except ClientError as e:
                    msg = str(e)
                    # Detect quota / 429 style errors
                    if (
                        "RESOURCE_EXHAUSTED" in msg
                        or "quota" in msg.lower()
                        or "429" in msg
                    ):
                        print(
                            f"⚠️ [GEMINI] Quota/429 on key {idx}, trying next key..."
                        )
                        last_exc = e
                        continue  # try next key
                    # Other Gemini errors: re-raise immediately
                    raise
                except Exception as e:
                    # Other unexpected errors (network, etc.) – keep and try the next key
                    print(
                        f"⚠️ [GEMINI] Unexpected error with key {idx}, trying next key: {e}"
                    )
                    last_exc = e
                    continue

            # If we exit the loop, all keys failed
            raise RuntimeError(
                f"All Gemini keys failed or quota exhausted. Last error: {last_exc}"
            )

        else:
            raise ValueError(f"Unknown LLM_name: {self.LLM_name}")
