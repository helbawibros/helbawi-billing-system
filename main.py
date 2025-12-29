import streamlit as st

st.set_page_config(page_title="نظام فوترة حلباوي", layout="centered")

# قائمة المندوبين
users = {"حسين": "1111", "علي": "2222", "عمر": "3333"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 دخول المندوبين")
    user_choice = st.selectbox("اسم المندوب", list(users.keys()))
    password = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if users[user_choice] == password:
            st.session_state.logged_in = True
            st.session_state.user = user_choice
            st.rerun()
else:
    st.sidebar.write(f"المندوب: {st.session_state.user}")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📄 فاتورة جديدة")
    st.write("أهلاً بك. بانتظار إدخال قائمة الأسعار لتفعيل الحسابات.")
