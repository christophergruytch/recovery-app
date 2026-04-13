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
if 'nickname' not in st.session_state:
    st.session_state.nickname = None
if 'confirm_change_nickname' not in st.session_state:
    st.session_state.confirm_change_nickname = False
if 'pending_journal_save' not in st.session_state:
    st.session_state.pending_journal_save = False
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'journal_buffer' not in st.session_state:
    st.session_state.journal_buffer = None



# ----- DEFINITOINS ------

def save_journal():
    """Simple save - we'll call this manually at first"""
    if 'journal' not in st.session_state:
        return
    journal_key = get_storage_key("journal")
    journal_json = json.dumps(st.session_state.journal, ensure_ascii=False)
    
    js_code = f'''
        try {{
            localStorage.setItem("{journal_key}", JSON.stringify({journal_json}));
            console.log("Journal saved for", "{journal_key}");
            return "success";
        }} catch (e) {{
            console.error("Save failed", e);
            return "failed";
        }}
    '''
    result = st_javascript(js_code)
    print(f"DEBUG: JS save result = {result}")


def get_storage_key(base_key: str) -> str:
    """Creates a private key for each user, e.g. 'recovery_journal_chrisIsCool
    
    Why? So different people using the same app link don't see each others data"""
    
    if st.session_state.nickname:
        return f"recovery_{base_key}_{st.session_state.nickname}"
    return f"recovery_{base_key}_temporary" #for if there's no nickname yet


# ----- END OF DEFINITOINS ------


# Load streak, last_checkin, and nickname from localStorage
streak_key = get_storage_key("streak")
saved_streak = st_javascript(f"localStorage.getItem('{streak_key}') || '0'")
try:
    st.session_state.streak = int(saved_streak)
except (ValueError, TypeError):
    st.session_state.streak = 0


last_key = get_storage_key("last_checkin")
saved_last = st_javascript(f"localStorage.getItem('{last_key}')")
if saved_last and saved_last != "null":
    try:
        st.session_state.last_checkin = datetime.date.fromisoformat(saved_last)
    except ValueError:
        st.session_state.last_checkin = None
else:
    st.session_state.last_checkin = None





saved_nickname = st_javascript("localStorage.getItem('recovery_nickname')")
if saved_nickname and saved_nickname != "null" and saved_nickname.strip():
    st.session_state.nickname = saved_nickname.strip()


# to fix consistency
# if streak is 0 but we have a last_checkin for today, it means the data got out of sync
# clear last_checkin so the user can check in again
# this was an edge case I ran into, where the streak and last_checkin don't save together, only one did
today = datetime.date.today()
if st.session_state.streak == 0 and st.session_state.last_checkin == today:
    st.session_state.last_checkin = None
    st_javascript(f"localStorage.removeItem('{last_key}')")
    print("Fixed inconsistent state: cleared last checkin because streak was 0")



# ----- MOBILE + PAGE SETUP ------


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


# ----- END OF MOBILE + PAGE SETUP ------




# ----- MAIN PAGES AND LOGIC ------


if page == "🏠 Home":
    st.title("Welcome to Recovery")
    st.write("Our mission is to...")
    
    col1, col2 = st.columns(2)

    with col1:
        # streak count
        st.metric(
            label="Current Streak",
            value=f"{st.session_state.get('streak', 0)} days",
            delta="Keep it going!" if st.session_state.get('streak', 0) > 0 else None
        )

    with col2:
        # sobriety timer
        if st.session_state.get('sobriety_start') is None:
            st.metric(
                label="Days Sober",
                value="Not set",
                delta="Set your start date"
            )
        else:
            days_sober = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric(
                label="Days Sober",
                value=f"{days_sober} days",
                delta="Good work!" if days_sober > 0 else None
            )

    st.write("-----")

    # sobriety timer setup and reset, below the metrics
    st.subheader("Sobriety Timer")

    if st.session_state.get('sobriety_start') is None:
        sobriety_date = st.date_input(
            "When did your current sobriety period being?",
            value=datetime.date.today(),
            max_value=datetime.date.today(),
            key="sobriety_start_input"
        )
        if st.button("Start Sobriety Timer"):
            st.session_state.sobriety_start = sobriety_date
            st.success("Sobriety timer started!")
            st.rerun()
    else:
        if st.button("I relapsed today", type="secondary"):
            st.session_state.sobriety_start = None
            st.warning("Timer has been reset")
            st.rerun()


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
            

            # Save streak and last check-in using username
            streak_key = get_storage_key("streak")
            last_key = get_storage_key("last_checkin")

            st_javascript(f"localStorage.setItem('{streak_key}', '{st.session_state.streak}')")
            if st.session_state.last_checkin is not None:
                st_javascript(f"localStorage.setItem('{last_key}', '{st.session_state.last_checkin.isoformat()}')")
            else:
                st_javascript(f"localStorage.removeItem('{last_key}')")
            # st.rerun()
        
        st.metric("Current Streak", st.session_state.streak, "days")

elif page == "📓 Journal":
    st.header("Journal Your Thoughts")

    # Clear All button - useful for testing and giving users a fresh start
    if st.button("🗑️ Clear All Journal Entries", type="secondary"):
        st.session_state.journal = []
        st.success("All journal entries have been cleared.")
        st.rerun()

    entry = st.text_area("What's on your mind today?", key="new_journal_input")

    if st.button("💾 Save Entry", key="save_new_entry_btn", type="primary", use_container_width=True):
        if entry.strip():
            if 'journal' not in st.session_state:
                st.session_state.journal = []
            st.session_state.journal.append({
                "date": str(datetime.date.today()),
                "text": entry.strip()
            })
            st.success("✅ Entry saved (in memory)")
            st.rerun()
    

    st.header("Your Journal Entries")

    if not st.session_state.journal:
        st.info("No entries yet. Add one above.")
    else:
        for idx, item in enumerate(st.session_state.journal):
            col_text, col_edit, col_delete = st.columns([7, 1, 1])

            with col_text:
                if st.session_state.get('editing_index') == idx:
                    # Edit mode
                    edited_text = st.text_area("Edit your entry", value=item["text"], key=f"edit_area_{idx}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("💾 Save Changes", key=f"save_edit_{idx}"):
                            st.session_state.journal[idx]["text"] = edited_text.strip()
                            st.session_state.editing_index = None
                            st.success("✅ Entry updated!")
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_edit_{idx}"):
                            st.session_state.editing_index = None
                            st.rerun()
                else:
                    st.write(f"**{item['date']}**: {item['text']}")

            with col_edit:
                if st.session_state.get('editing_index') is None:
                    if st.button("✏️", key=f"edit_btn_{idx}"):
                        st.session_state.editing_index = idx
                        st.rerun()

            with col_delete:
                if st.button("🗑️", key=f"delete_btn_{idx}"):
                    del st.session_state.journal[idx]
                    st.success("Entry deleted.")
                    st.rerun()
    

elif page == "🎙️ Let's All Talk":
    st.write("Where you can talk with others will go here.")

elif page == "📊 Progress":
    st.header("📊 Your Progress")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Current Streak",
            value=f"{st.session_state.get('streak', 0)} days"
        )

    with col2:
        if st.session_state.get('sobriety_start') is None:
            st.metric(
                label="Days Sober",
                value="Not set"
            )
        else:
            days_sober = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric(
                label="Days Sober",
                value=f"{days_sober} days"
            )

    total_journal = len(st.session_state.get('journal', []))
    st.metric("Total Journal Entries", total_journal)

    st.write("-----")

    st.subheader("Journaling Activity")
    st.write("Coming Soon: A chart showing how often you journal.")


elif page == "🆘 Resources":
    st.write("Resources to help will go here.")
    # st.write(f"Here is: {get_storage_key("resources")}")

elif page == "⚙️ Settings":
    st.header("⚙️ Settings - Make This Private To You!")

    # This page for now lets the user set (or change) thier nickname
    # Once set, all their data (streak, journal, etc.) will be saved under their own private key

    if not st.session_state.nickname:
        # Case 1: User has never set a nickname yet
        st.info("First time here? Let's create your private space.")
        new_nickname = st.text_input(
            "Choose a nickname (e.g john_123)",
            placeholder="john_123",
            max_chars=30,
            key="nickname_input"
        )
        if st.button("✅ Save My Nickname & Start Fresh!"):
            if new_nickname.strip():
                # clean up the nickname (remove spaces, make lowercase, keep only letters/numbers/underscores)
                clean_nickname = "".join(c for c in new_nickname.strip().lower() if c.isalnum or c == "_")
                if clean_nickname:
                    st.session_state.nickname = clean_nickname
                    # saving the nickname to localStorage so it survives refreshes
                    st_javascript(f'localStorage.setItem("recovery_nickname", "{clean_nickname}")')
                    st.success(f"Welcome {clean_nickname}! Your data is now private to you!")
                    st.rerun()
                else:
                    st.error("Nickname must contain at least one letter or number.")
            else:
                st.warning("Please enter a nickname.")
    else:
        # Case 2: User already has a nickname
        st.success(f"Current nickname: {st.session_state.nickname}")
        st.caption("All your streak, journal, and future date is stored privatly in your browser under this nickname.")

        if st.button("Change Nickname (this will start with fresh data)",
                    key = "change_nickname_btn",
                    type = "secondary"):
            # first clear the current nickname so the user can set a new one
            st.session_state.confirm_change_nickname = True
            st.rerun()
        
        if st.session_state.get('confirm_change_nickname'):
            st.warning("Are you sure? This will clear your current nickname and date.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Change Nickname", key = "confirm_yes_btn", type = "primary"):
                    st.session_state.nickname = None
                    st_javascript('localStorage.removeItem("recovery_nickname")')
                    st.session_state.confirm_change_nickname = False
                    st.success("Nickname cleared. Please set a new nickname.")
                    st.rerun()
            with col2:
                if st.button("Cancel", key = "confirm_no_btn"):
                    st.session_state.confirm_change_nickname = False
                    st.rerun()


# ----- END OF MAIN PAGES AND LOGIC ------