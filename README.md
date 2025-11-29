# 📧 Prompt-Driven Email Productivity Agent

Live demo: **https://prompt-driven-email-agent.streamlit.app/**

---

## 🔧 Project Overview

This project is a simple but powerful email-productivity assistant that lets you:

- Load a mock (or real) Gmail inbox  
- Automatically categorize incoming emails using an LLM  
- Extract action items from emails  
- Generate reply drafts (quick or full) using configurable prompts  
- Interactively browse emails via a table UI  
- Chat with your inbox or individual emails using AI  
- Configure prompt behaviour (categorization, action-item extraction, auto-reply templates) via UI  

The aim is to help you manage emails, keep track of tasks, and respond efficiently — all using AI and minimal effort.

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Itsmepranay/Prompt-Driven-Email-Productivity-Agent.git
cd Prompt-Driven-Email-Productivity-Agent
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. (Optional) Setup real Gmail / Google OAuth (or use mock)
- If you have credentials (OAuth client ID / secret), create `credentials.json` or `token.json` locally (do **not** commit them).
- **By default** the app uses a *mock inbox* from `data/mock_inbox.json` so you can try everything without real credentials.

---

## 🚀 Running the App Locally

```bash
streamlit run main.py
```

Then open the local URL (usually `http://localhost:8501`) in your browser.

---

## 🧪 Using the App — Mock Inbox & UI Flow

1. Open **Inbox** from the sidebar.
2. Click **“🔄 Fetch Emails”** to load the mock inbox.
3. Click **“⚡ Process Inbox”** to run AI-based categorization & action extraction.
4. Click any email row to view full details.
5. View **Actions** (if any).
6. Use **Quick Draft Generator** to create and save replies.
7. Use the **Drafts** tab to review all saved drafts.
8. Use **Email Agent (Chat)** to talk to your inbox.

---

## ⚙️ Configuring Prompts

Use the **Prompt Brain** page to modify:
- Categorization prompt
- Action extraction prompt
- Auto-reply prompt

Click **Save Prompts** to update AI behavior instantly.

---

## ✅ Security Notes

- Never commit `credentials.json`, `token.json`, or `.env`
- Use mock inbox for demos
- Regenerate keys immediately if exposed

---

## 📦 Deployment

This project is deployed using Streamlit Cloud:

👉 https://prompt-driven-email-agent.streamlit.app/

---

## 📄 License & Disclaimer

Use for educational and productivity purposes.  
Never expose private credentials in public repositories.

---

Happy coding! 🚀
