import streamlit as st # type: ignore
import datetime
from streamlit_javascript import st_javascript # type: ignore
import json

st.set_page_config(
    page_title="Recovery",
    page_icon="🥹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# initialization
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None
if 'journal' not in st.session_state:
    st.session_state.journal = []
if 'motivation' not in st.session_state:
    st.session_state.motivation = 5

# Load streak and last_checkin from localStorage (this already works)
saved_streak = st_javascript("localStorage.getItem('recovery_streak') || '0'")
try:
    st.session_state.streak = int(saved_streak)
except (ValueError, TypeError):
    st.session_state.streak = 0

saved_last = st_javascript("localStorage.getItem('recovery_last_checkin')")
if saved_last and saved_last != "null":
    try:
        st.session_state.last_checkin = datetime.date.fromisoformat(saved_last)
    except ValueError:
        st.session_state.last_checkin = None
else:
    st.session_state.last_checkin = None


page = st.sidebar.radio(
    label="Menu",
    options=["🏠 Home", "✅ Daily Check-In", "📓 Journal", "🎙️ Let's All Talk", "📊 Progress", "🆘 Resources", "⚙️ Settings"],
    index=0,
    key="nav_menu"
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="manifest.json">
""", unsafe_allow_html=True)


def save_journal():
    """Save journal list to localStorage"""
    if 'journal' not in st.session_state:
        return
    journal_json = json.dumps(st.session_state.journal, ensure_ascii=False)
    js_code = f'''
        try {{
            localStorage.setItem("recovery_journal", JSON.stringify({json.dumps(journal_json)}));
            console.log("✅ Journal saved! Entries:", {len(st.session_state.journal)});
        }} catch (e) {{
            console.error("Save failed:", e);
        }}
    '''
    st_javascript(js_code)


if page == "🏠 Home":
    st.title("Welcome to Recovery")
    st.write("Our mission is to...")
    st.metric("Current Streak", st.session_state.get('streak', 0), "days")
    st.session_state.motivation = st.slider("How motivated are you today?", 1, 10)
    st.write(f"Your motivation: {st.session_state.motivation}")

elif page == "✅ Daily Check-In":
    st.header("Daily Check-In")
    if st.button("Check In Today"):
        today = datetime.date.today()
        if st.session_state.last_checkin == today:
            st.warning("You have already checked in today")
        else:
            if st.session_state.last_checkin is None:
                st.success("You have started a new streak!")
                st.session_state.streak += 1
                st.session_state.last_checkin = today
            else:
                delta = today - st.session_state.last_checkin
                if delta.days == 1:
                    st.success("You've added another day!")
                    st.session_state.streak += 1
                    st.session_state.last_checkin = today
                else:
                    st.warning(f"You have missed {delta.days - 1} day(s). Streak is reset to 1.")
                    st.session_state.streak = 1
                    st.session_state.last_checkin = today
            
            # Save streak (already working)
            st_javascript(f"localStorage.setItem('recovery_streak', '{st.session_state.streak}')")
            if st.session_state.last_checkin is not None:
                st_javascript(f"localStorage.setItem('recovery_last_checkin', '{st.session_state.last_checkin.isoformat()}')")
            else:
                st_javascript("localStorage.removeItem('recovery_last_checkin')")
        
        st.metric("Current Streak", st.session_state.streak, "days")

elif page == "📓 Journal":
    st.header("Journal Your Thoughts")

    # Temporary clear button (in-memory only for now)
    if st.button("🔴 Clear ALL Journal Data (temporary)"):
        st.session_state.journal = []
        st.success("Journal cleared in memory!")
        st.rerun()

    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None

    entry = st.text_area("What's on your mind today?", key="new_journal_entry")

    if st.button("Save Entry", key="save_entry_btn"):
        if entry.strip():
            if 'journal' not in st.session_state:
                st.session_state.journal = []
            st.session_state.journal.append({
                "date": str(datetime.date.today()),
                "text": entry.strip()
            })
            save_journal()
            st.success("Entry Saved! (in memory only)")
            st.rerun()
        else:
            st.warning("Please write something.")

    st.header("Your Journal Entries")

    if not st.session_state.journal:
        st.info("No entries yet. Add one above.")
    else:
        for idx, item in enumerate(st.session_state.journal):
            col_text, col_edit, col_delete = st.columns([7, 1, 1])

            with col_text:
                if st.session_state.editing_index == idx:
                    # === EDIT MODE ===
                    edited_text = st.text_area(
                        "Edit your entry",
                        value=item["text"],
                        key=f"edit_area_{idx}"
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("💾 Save Changes", key=f"save_edit_{idx}", use_container_width=True):
                            st.session_state.journal[idx]["text"] = edited_text.strip()
                            st.session_state.editing_index = None
                            st.success("✅ Entry updated!")
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_edit_{idx}", use_container_width=True):
                            st.session_state.editing_index = None
                            st.rerun()
                else:
                    # Normal display mode
                    st.write(f"**{item['date']}**: {item['text']}")

            with col_edit:
                if st.session_state.editing_index is None:  # Only allow one edit at a time
                    if st.button("✏️", key=f"edit_btn_{idx}", help="Edit this entry"):
                        st.session_state.editing_index = idx
                        st.rerun()

            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
                    del st.session_state.journal[idx]
                    st.success("Entry deleted.")
                    st.rerun()

elif page == "🎙️ Let's All Talk":
    st.write("Where you can talk with others will go here.")

elif page == "📊 Progress":
    st.write("Your progress will go here.")

elif page == "🆘 Resources":
    st.write("Resources to help will go here.")

elif page == "⚙️ Settings":
    st.write("Settings will go here.")