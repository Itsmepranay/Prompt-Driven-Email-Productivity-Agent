# Prompt-Driven Email Productivity Agent

## Overview
This is a Streamlit-based Email Productivity Agent that uses LLMs (Large Language Models) to process emails. It features:
- **Inbox Ingestion**: Loads emails from a mock source.
- **Prompt-Driven Processing**: Uses user-defined prompts to categorize emails and extract action items.
- **Email Agent**: A chat interface to ask questions about your emails.
- **Draft Generation**: Auto-drafts replies based on context.

## Setup Instructions

1. **Clone the repository** (or download the files).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Configuration
- **API Key**: The app defaults to a "Mock Mode" which simulates LLM responses. To use real AI, enter your Google Gemini API Key in the sidebar.
- **Prompts**: You can edit the behavior of the agent by modifying the prompts in the "Prompt Brain" tab.

## Usage
1. **Load Inbox**: Go to the "Inbox" tab and click "Load Mock Inbox".
2. **Process**: Click "Process Inbox" to categorize emails and extract tasks.
3. **Chat**: Go to the "Email Agent" tab to summarize or ask questions about specific emails.
4. **Draft**: Use the "Drafts" tab to generate email replies.
