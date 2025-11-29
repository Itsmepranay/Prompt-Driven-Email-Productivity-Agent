from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from backend.models import Email, PromptConfig, Draft
from backend.storage import load_inbox, save_inbox, load_prompts, save_prompts
from backend.llm_service import GeminiLLMService
from backend.agent import EmailAgent

# --- Page Config ---
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide"
)

# --- Session State Initialization ---
if "emails" not in st.session_state:
    st.session_state.emails = []

if "prompts" not in st.session_state:
    st.session_state.prompts = load_prompts()

if "llm_service" not in st.session_state:
    default_key = "AIzaSyCT3JVnuY-zWlLAtZY266eg3y559sgXcf4"
    try:
        st.session_state.llm_service = GeminiLLMService(default_key)
        st.session_state.agent = EmailAgent(st.session_state.llm_service)
    except Exception as e:
        st.error(f"Failed to initialize AI Service: {e}")

if "agent" not in st.session_state and "llm_service" in st.session_state:
    st.session_state.agent = EmailAgent(st.session_state.llm_service)

if "drafts" not in st.session_state:
    st.session_state.drafts = []

if "gmail_service" not in st.session_state:
    st.session_state.gmail_service = "mock"

# --- Helper: Load Mock Inbox ---
def load_mock_inbox() -> list:
    base = Path(__file__).resolve().parent
    mock_path = base / "data" / "mock_inbox.json"

    try:
        with mock_path.open("r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        st.error(f"Failed to load mock inbox: {e}")
        return []

    emails = []
    for it in items:
        emails.append(Email(
            id=it.get("id"),
            sender=it.get("sender"),
            subject=it.get("subject"),
            body=it.get("body"),
            timestamp=it.get("timestamp"),
            category=it.get("category"),
            action_items=it.get("action_items", [])
        ))
    return emails

# --- NEW: Build inbox context for general-agent chats ---
def build_inbox_context(emails, max_items=20, max_body_chars=800):
    """
    Create a text context summarizing the inbox for the LLM.
    Limits number of emails and truncates bodies to avoid sending huge payloads.
    """
    if not emails:
        return "Inbox is empty."

    parts = []
    for i, e in enumerate(emails[:max_items], start=1):
        sender = e.sender or "<unknown sender>"
        subject = e.subject or "<no subject>"
        category = e.category or "Uncategorized"
        actions = "; ".join(e.action_items) if getattr(e, "action_items", None) else "None"
        body = (e.body or "").replace("\n", " ").strip()
        if len(body) > max_body_chars:
            body = body[:max_body_chars] + " ...[truncated]"
        parts.append(f"Email {i} | From: {sender} | Subject: {subject} | Category: {category} | Action Items: {actions} | Body: {body}")
    return "\n\n".join(parts)

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("Navigation")
    nav = st.radio("", ["📥 Inbox", "🤖 Email Agent", "📝 Drafts", "🧠 Prompt Brain"])
    st.session_state.current_page = nav

st.title("📧 Email Productivity Agent")
page = st.session_state.get("current_page", "📥 Inbox")

# ======================================================
# 📥 INBOX PAGE (✅ BOTH FIXES APPLIED HERE)
# ======================================================
if page == "📥 Inbox":
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Gmail Inbox")

    with col2:
        if st.button("🔄 Fetch Emails"):
            with st.spinner("Loading mock inbox..."):
                st.session_state.emails = load_mock_inbox()
                st.success("Loaded mock inbox!")
            st.rerun()

        # ✅✅✅ FIX #1: SAFE BULK PROCESSING
        if st.button("⚡ Process Inbox"):
            if not st.session_state.emails:
                st.warning("No emails to process.")
            else:
                with st.spinner("Processing emails with AI..."):
                    try:
                        processed_emails = st.session_state.agent.process_emails(
                            st.session_state.emails,
                            st.session_state.prompts
                        )

                        # ✅ BLOCK ERROR TEXT FROM BECOMING CATEGORY
                        for email in processed_emails:
                            if email.category and (
                                "quota" in email.category.lower() or
                                "error" in email.category.lower() or
                                "429" in email.category or
                                "rate limit" in email.category.lower() or
                                "exceeded" in email.category.lower()
                            ):
                                email.category = None  # ✅ RESET TO UNCATEGORIZED

                        st.session_state.emails = processed_emails
                        save_inbox(st.session_state.emails)
                        st.success("Processing Complete!")

                    except Exception as e:
                        st.error(f"Processing failed: {e}")

                st.rerun()

    # -------------------------
    # DISPLAY EMAIL TABLE
    # -------------------------
    if not st.session_state.emails:
        st.info("Inbox is empty. Press Fetch Emails button above to get started")
    else:
        data = []
        for email in st.session_state.emails:
            data.append({
                "ID": email.id,
                "Sender": email.sender,
                "Subject": email.subject,
                "Category": email.category or "Uncategorized",
                "Action Items": ", ".join(email.action_items) if email.action_items else "-"
            })

        df = pd.DataFrame(data)

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_column("ID", width=80)
        gb.configure_column("Subject", width=400)
        gb.configure_column("Category", width=150)

        grid_response = AgGrid(
            df,
            gridOptions=gb.build(),
            height=300,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
        )

        selected_rows = grid_response.get("selected_rows", [])
        selected_id = None

        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_id = selected_rows[0].get("ID")
        elif isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
            selected_id = selected_rows.iloc[0]["ID"]

        st.divider()

        if selected_id:
            email = next((e for e in st.session_state.emails if e.id == selected_id), None)

            if email:
                st.markdown(f"**From:** {email.sender}")
                st.markdown(f"**Subject:** {email.subject}")
                st.markdown(f"**Date:** {email.timestamp}")
                st.markdown(f"**Category:** `{email.category}`")
                st.text_area("Body", email.body, height=200, disabled=True)

                st.divider()
                st.subheader("Actions")
                
                if email.action_items:
                    st.info("\n".join([f"- {item}" for item in email.action_items]))

                # ✅✅✅ FIX #2: SAFE SINGLE EMAIL PROCESSING
                if not email.category:
                    if st.button("⚡ Process This Email", key=f"process_{email.id}"):
                        with st.spinner("Processing this email with AI..."):
                            try:
                                processed_list = st.session_state.agent.process_emails(
                                    [email],
                                    st.session_state.prompts
                                )

                                if processed_list:
                                    processed = processed_list[0]

                                    # ✅ BLOCK ERROR CATEGORY
                                    if processed.category and (
                                        "quota" in processed.category.lower() or
                                        "error" in processed.category.lower() or
                                        "429" in processed.category or
                                        "rate limit" in processed.category.lower() or
                                        "exceeded" in processed.category.lower()
                                    ):
                                        processed.category = None

                                    st.session_state.emails = [
                                        (processed if e.id == processed.id else e)
                                        for e in st.session_state.emails
                                    ]

                                    save_inbox(st.session_state.emails)
                                    st.success("Email processed individually.")

                                else:
                                    st.error("No result returned from agent.")

                            except Exception as e:
                                st.error(f"Processing failed: {e}")

                        st.rerun()

                # --- NEW: Quick Draft Generator (per-email) ---
                st.divider()
                st.subheader("Quick Draft Generator")
                draft_instr_key = f"quick_draft_instr_{email.id}"
                draft_instructions = st.text_area("Draft Instructions (optional)", value="", key=draft_instr_key, height=80)

                if st.button("Generate Quick Draft", key=f"quick_gen_{email.id}"):
                    with st.spinner("Generating quick draft..."):
                        try:
                            draft_content = st.session_state.agent.generate_draft(
                                email,
                                st.session_state.prompts,
                                draft_instructions
                            )
                            st.session_state[f"quick_draft_content_{email.id}"] = draft_content
                            st.success("Quick draft generated. Preview below.")
                        except Exception as e:
                            st.error(f"Draft generation failed: {e}")

                preview_key = f"quick_draft_content_{email.id}"
                if preview_key in st.session_state:
                    st.text_area("Quick Draft Preview", value=st.session_state[preview_key], height=200, key=f"quick_preview_{email.id}")
                    if st.button("Save Quick Draft to Drafts", key=f"save_quick_{email.id}"):
                        st.session_state.drafts.append({
                            "email_id": email.id,
                            "content": st.session_state[preview_key]
                        })
                        st.success("Draft saved to Drafts.")

elif page == "🤖 Email Agent":
    # --- Tab 2: Email Agent ---
    st.subheader("Chat with your Inbox")
    
    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Context Selection
    chat_context_mode = st.radio("Context", ["Selected Email", "General Inbox"], horizontal=True)
    
    selected_email_for_chat = None
    if chat_context_mode == "Selected Email":
        if not st.session_state.emails:
             st.warning("No emails loaded.")
        else:
            email_ids = [e.id for e in st.session_state.emails]
            selected_chat_id = st.selectbox("Choose Email", options=email_ids, key="chat_email_select")
            selected_email_for_chat = next((e for e in st.session_state.emails if e.id == selected_chat_id), None)

    # Display Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if chat_context_mode == "Selected Email" and selected_email_for_chat:
                    response = st.session_state.agent.chat_with_email(selected_email_for_chat, prompt)
                else:
                    # --- UPDATED: build and pass full inbox context to the agent/LLM ---
                    inbox_context = build_inbox_context(st.session_state.emails)
                    # Prefer an agent-level inbox chat method if available
                    if hasattr(st.session_state.agent, "chat_with_inbox"):
                        try:
                            response = st.session_state.agent.chat_with_inbox(inbox_context, prompt)
                        except Exception:
                            # fallback to llm_service
                            response = st.session_state.llm_service.chat(inbox_context, prompt)
                    else:
                        response = st.session_state.llm_service.chat(inbox_context, prompt)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "📝 Drafts":
    # --- Tab 3: Drafts ---
    st.subheader("Draft Generator")
    
    if not st.session_state.emails:
        st.warning("Fetch emails to generate drafts.")
    else:
        draft_email_id = st.selectbox("Select Email to Reply To", options=[e.id for e in st.session_state.emails], key="draft_email_select")
        draft_instructions = st.text_area("Additional Instructions (Optional)", placeholder="e.g., Be very polite, decline the offer...")
        
        if st.button("Generate Draft"):
            email_to_reply = next((e for e in st.session_state.emails if e.id == draft_email_id), None)
            if email_to_reply:
                with st.spinner("Drafting..."):
                    draft_content = st.session_state.agent.generate_draft(
                        email_to_reply, 
                        st.session_state.prompts, 
                        draft_instructions
                    )
                    st.session_state.current_draft = draft_content
        
        if "current_draft" in st.session_state:
            st.text_area("Draft Content", value=st.session_state.current_draft, height=300)
            if st.button("Save Draft"):
                st.session_state.drafts.append({
                    "email_id": draft_email_id,
                    "content": st.session_state.current_draft
                })
                st.success("Draft saved!")

    if st.session_state.drafts:
        st.divider()
        st.subheader("Saved Drafts")
        for i, draft in enumerate(st.session_state.drafts):
            with st.expander(f"Draft {i+1} (for {draft['email_id']})"):
                st.write(draft['content'])

elif page == "🧠 Prompt Brain":
    # --- Tab 4: Prompt Brain ---
    st.subheader("🧠 Configure Agent Brain")
    st.info("Edit the prompts below to change how the AI behaves.")
    
    new_cat_prompt = st.text_area("Categorization Prompt", value=st.session_state.prompts.categorization, height=150)
    new_action_prompt = st.text_area("Action Item Extraction Prompt", value=st.session_state.prompts.action_extraction, height=150)
    new_reply_prompt = st.text_area("Auto-Reply Prompt", value=st.session_state.prompts.auto_reply, height=150)
    
    if st.button("Save Prompts"):
        updated_prompts = PromptConfig(
            categorization=new_cat_prompt,
            action_extraction=new_action_prompt,
            auto_reply=new_reply_prompt
        )
        st.session_state.prompts = updated_prompts
        save_prompts(updated_prompts)
        st.success("Prompts updated successfully!")
