from typing import List
from backend.models import Email, PromptConfig
from backend.llm_service import LLMService

class EmailAgent:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def process_emails(self, emails: List[Email], prompts: PromptConfig) -> List[Email]:
        """
        Iterates through emails and applies categorization and action extraction
        if they haven't been processed yet (or if we want to re-process).
        """
        processed_emails = []
        for email in emails:
            # Construct a string representation for the LLM
            email_text = f"Subject: {email.subject}\nBody: {email.body}"
            
            # Categorize
            category = self.llm.categorize_email(
                email_text, 
                prompts.categorization.replace("{subject}", email.subject).replace("{body}", email.body)
            )
            email.category = category

            # Extract Actions
            actions = self.llm.extract_action_items(
                email_text, 
                prompts.action_extraction.replace("{subject}", email.subject).replace("{body}", email.body)
            )
            email.action_items = actions
            
            processed_emails.append(email)
        
        return processed_emails

    def generate_draft(self, email: Email, prompts: PromptConfig, instructions: str = "") -> str:
        email_text = f"Sender: {email.sender}\nSubject: {email.subject}\nBody: {email.body}"
        prompt = prompts.auto_reply.replace("{sender}", email.sender).replace("{subject}", email.subject).replace("{body}", email.body)
        if instructions:
            prompt += f"\n\nAdditional Instructions: {instructions}"
        
        return self.llm.generate_reply(email_text, prompt)

    def chat_with_email(self, email: Email, user_query: str) -> str:
        context = f"Sender: {email.sender}\nSubject: {email.subject}\nBody: {email.body}\nCategory: {email.category}\nAction Items: {email.action_items}"
        return self.llm.chat(context, user_query)
