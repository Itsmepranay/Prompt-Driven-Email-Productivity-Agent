import json
import os
from typing import List, Dict
from backend.models import Email, PromptConfig

DATA_DIR = "data"
INBOX_FILE = os.path.join(DATA_DIR, "mock_inbox.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "default_prompts.json")
PROCESSED_INBOX_FILE = os.path.join(DATA_DIR, "processed_inbox.json")

def load_inbox() -> List[Email]:
    """Loads emails from the processed file if it exists."""
    if os.path.exists(PROCESSED_INBOX_FILE):
        with open(PROCESSED_INBOX_FILE, "r") as f:
            data = json.load(f)
            return [Email(**item) for item in data]
    return []

def save_inbox(emails: List[Email]):
    """Saves the current state of emails (including categories/actions) to disk."""
    with open(PROCESSED_INBOX_FILE, "w") as f:
        json.dump([email.model_dump() for email in emails], f, indent=2)

def load_prompts() -> PromptConfig:
    """Loads prompt configurations."""
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, "r") as f:
            data = json.load(f)
            return PromptConfig(**data)
    # Fallback default
    return PromptConfig(
        categorization="Categorize this email.",
        action_extraction="Extract tasks.",
        auto_reply="Draft a reply."
    )

def save_prompts(prompts: PromptConfig):
    """Saves prompt configurations."""
    with open(PROMPTS_FILE, "w") as f:
        json.dump(prompts.model_dump(), f, indent=2)
