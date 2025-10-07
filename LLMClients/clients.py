import os
from openai import OpenAI
from google import genai
from dotenv import load_dotenv

load_dotenv()
class Model:
    def __init__(self, LLM_name, prompt):
        self.LLM_name = LLM_name
        self.prompt = prompt

    def get_response_from_client(self):
        if self.LLM_name == "OPENAI":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-5-mini",   # you can adjust model
                messages=[{"role": "user", "content": self.prompt}],
            )
            return response.choices[0].message.content.strip()
        
        elif self.LLM_name == "GEMINI":
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model="gemini-2.5-pro", contents=self.prompt
            )
            return response.candidates[0].content.parts[0].text.strip()   
        