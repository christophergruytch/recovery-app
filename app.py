import streamlit as st # type: ignore
import datetime
import pandas as pd # type: ignore
from streamlit_javascript import st_javascript # type: ignore

# ====================== SESSION STATE ======================
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None
if 'journal' not in st.session_state:
    st.session_state.journal = []
if 'sobriety_start' not in st.session_state:
    st.session_state.sobriety_start = None
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'nickname' not in st.session_state:
    st.session_state.nickname = None
if 'longest_streak' not in st.session_state:
    st.session_state.longest_streak = 0
if 'longest_sobriety' not in st.session_state:
    st.session_state.longest_sobriety = 0

# ====================== HELPER FUNCTIONS ======================
def get_storage_key(base_key: str) -> str:
    if st.session_state.get('nickname'):
        return f"recovery_{base_key}_{st.session_state.nickname}"
    return f"recovery_{base_key}_temp"

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Recovery",
    page_icon="🥹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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

# ====================== HOME PAGE ======================
if page == "🏠 Home":
    st.title("Welcome to Recovery")
    st.write("Our mission is to support you on your journey toward freedom.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Streak", f"{st.session_state.get('streak', 0)} days")
    with col2:
        if st.session_state.get('sobriety_start') is None:
            st.metric("Days Sober", "Not set")
        else:
            days_sober = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric("Days Sober", f"{days_sober} days")

    st.write("---")
    st.subheader("⏱️ Sobriety Timer")
    if st.session_state.get('sobriety_start') is None:
        sobriety_date = st.date_input("When did your current sobriety period begin?", 
                                      value=datetime.date.today(), 
                                      max_value=datetime.date.today())
        if st.button("Start Sobriety Timer"):
            st.session_state.sobriety_start = sobriety_date
            st.success("Sobriety timer started!")
            st.rerun()
    else:
        if st.button("I Relapsed Today", type="secondary"):
            st.session_state.sobriety_start = None
            st.warning("Timer has been reset.")
            st.rerun()

# ====================== DAILY CHECK-IN ======================
elif page == "✅ Daily Check-In":
    st.header("Daily Check-In")
    if st.button("Check In Today", key="checkin_btn", type="primary", use_container_width=True):
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
            st.rerun()

    st.metric("Current Streak", st.session_state.get('streak', 0), "days")

# ====================== JOURNAL ======================
elif page == "📓 Journal":
    st.header("Journal Your Thoughts")

    if st.button("🗑️ Clear All Journal Entries", type="secondary"):
        st.session_state.journal = []
        st.success("All entries cleared.")
        st.rerun()

    entry = st.text_area("What's on your mind today?", key="new_journal_input")
    if st.button("💾 Save Entry", key="save_entry_btn", type="primary"):
        if entry.strip():
            if 'journal' not in st.session_state:
                st.session_state.journal = []
            st.session_state.journal.append({
                "date": str(datetime.date.today()),
                "text": entry.strip()
            })
            st.success("Entry saved!")
            st.rerun()

    st.header("Your Journal Entries")
    if not st.session_state.get('journal'):
        st.info("No entries yet.")
    else:
        for idx, item in enumerate(st.session_state.journal):
            col_text, col_edit, col_delete = st.columns([7, 1, 1])
            with col_text:
                if st.session_state.get('editing_index') == idx:
                    edited_text = st.text_area("Edit", value=item["text"], key=f"edit_{idx}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Save", key=f"save_edit_{idx}"):
                            st.session_state.journal[idx]["text"] = edited_text.strip()
                            st.session_state.editing_index = None
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_{idx}"):
                            st.session_state.editing_index = None
                            st.rerun()
                else:
                    st.write(f"**{item['date']}**: {item['text']}")
            with col_edit:
                if st.button("✏️", key=f"edit_btn_{idx}"):
                    st.session_state.editing_index = idx
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"del_{idx}"):
                    del st.session_state.journal[idx]
                    st.rerun()

# ====================== LET'S ALL TALK ======================
elif page == "🎙️ Let's All Talk":
    st.write("Let's All Talk page coming soon...")

# ====================== PROGRESS ======================
elif page == "📊 Progress":
    st.header("📊 Your Progress")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Streak", f"{st.session_state.get('streak', 0)} days")
    with col2:
        if st.session_state.get('sobriety_start') is None:
            st.metric("Days Sober", "Not set")
        else:
            days = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric("Days Sober", f"{days} days")

    st.metric("Total Journal Entries", len(st.session_state.get('journal', [])))

    st.subheader("Personal Bests")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Longest Streak", f"{st.session_state.get('longest_streak', 0)} days")
    with col4:
        st.metric("Longest Sobriety", f"{st.session_state.get('longest_sobriety', 0)} days")

    st.subheader("Journaling Activity")
    journal = st.session_state.get('journal', [])
    if journal:
        df = pd.DataFrame(journal)
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby('date').size().reset_index(name='count')
        st.line_chart(daily.set_index('date'))
    else:
        st.info("No journal entries yet.")

# ====================== RESOURCES ======================
elif page == "🆘 Resources":
    st.write("Resource page coming soon...")

# ====================== SETTINGS ======================
elif page == "⚙️ Settings":
    st.header("⚙️ Settings - Make This Private To You!")

    if not st.session_state.get('nickname'):
        st.info("First time here? Let's create your private space.")
        new_nickname = st.text_input(
            "Choose a nickname (e.g. chris_burbank)",
            placeholder="chris_burbank",
            max_chars=30,
            key="nickname_input"
        )
        if st.button("✅ Save My Nickname & Start Fresh!"):
            if new_nickname.strip():
                clean_nickname = "".join(c for c in new_nickname.strip().lower() if c.isalnum() or c == "_")
                if clean_nickname:
                    st.session_state.nickname = clean_nickname
                    st_javascript(f'localStorage.setItem("recovery_nickname", "{clean_nickname}")')
                    st.success(f"Welcome, {clean_nickname}! Your data is now private to you!")
                    st.rerun()
                else:
                    st.error("Please choose a valid nickname.")
            else:
                st.warning("Please enter a nickname.")
    else:
        st.success(f"Current nickname: **{st.session_state.nickname}**")
        st.caption("All your data is stored privately under this name.")

        if st.button("Change Nickname (starts fresh data)", key="change_nickname_btn"):
            st.session_state.nickname = None
            st_javascript('localStorage.removeItem("recovery_nickname")')
            st.rerun()