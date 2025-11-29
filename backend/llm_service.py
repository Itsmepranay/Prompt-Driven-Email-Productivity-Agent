import os
import json
import random
import google.generativeai as genai
from abc import ABC, abstractmethod
from typing import List, Dict

class LLMService(ABC):
    @abstractmethod
    def categorize_email(self, email_content: str, prompt_template: str) -> str:
        pass

    @abstractmethod
    def extract_action_items(self, email_content: str, prompt_template: str) -> List[str]:
        pass

    @abstractmethod
    def generate_reply(self, email_content: str, prompt_template: str) -> str:
        pass
    
    @abstractmethod
    def chat(self, context: str, user_query: str) -> str:
        pass


class GeminiLLMService(LLMService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def categorize_email(self, email_content: str, prompt_template: str) -> str:
        prompt = prompt_template + "\n\n" + email_content
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_action_items(self, email_content: str, prompt_template: str) -> List[str]:
        prompt = prompt_template + "\n\n" + email_content
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Attempt to parse JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                 text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text)
            return data.get("tasks", [])
        except Exception:
            return []

    def generate_reply(self, email_content: str, prompt_template: str) -> str:
        prompt = prompt_template + "\n\n" + email_content
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating draft: {str(e)}"

    def chat(self, context: str, user_query: str) -> str:
        prompt = f"Context: {context}\n\nUser Question: {user_query}\n\nAnswer:"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
