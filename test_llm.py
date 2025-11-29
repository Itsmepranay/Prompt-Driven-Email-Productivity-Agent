from backend.llm_service import GeminiLLMService
import os

api_key = "AIzaSyCT3JVnuY-zWlLAtZY266eg3y559sgXcf4"

print("Initializing Gemini Service...")
try:
    service = GeminiLLMService(api_key)
    print(f"Model: {service.model.model_name}")
    
    print("Testing generation...")
    response = service.categorize_email("Subject: Hello\nBody: Just testing", "Categorize this.")
    print(f"Response: {response}")
except Exception as e:
    print(f"ERROR: {e}")
