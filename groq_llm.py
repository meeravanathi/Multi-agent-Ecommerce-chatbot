from groq import Groq
from langchain.llms.base import LLM
from typing import Optional, List
from langchain.pydantic_v1 import PrivateAttr
import os
from dotenv import load_dotenv

load_dotenv()

class GroqLLM(LLM):
    _client: Groq = PrivateAttr()
    _model_name: str = PrivateAttr()

    def __init__(self, model_name: str = "llama3-8b-8192"):
        super().__init__()
        self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self._model_name = model_name

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            response = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self._model_name,
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    @property
    def _llm_type(self) -> str:
        return "groq"
