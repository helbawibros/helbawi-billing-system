import streamlit as st
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيق الدقيق للمقاسات (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; overflow-x: hidden; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; }
    .invoice-header { text-align: center; font-size: 22px; font-weight: bold; margin: 5px 0; }
    
    /* تصغير حجم خانات الإدخال الصغيرة */
    div[data-testid="column"]:nth-of-type(2) input {
        padding: 5px !important;
        text-align: center !important;
    }
    /* إلغاء الفراغات الزائدة بين الأعمدة */
    [data-testid="column"] { padding: 0 5px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []

# --- تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user
            st.rerun()

# --- الصفحة الرئيسية ---
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary", on_click=lambda: setattr(st.session_state, 'page', 'order_page'))
    if st.button("🚪 خروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- صفحة الطلبية بمقاسات 4سم و 1سم ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<div class="invoice-header">رقم الفاتورة: {random.randint(1000, 9999)}</div>', unsafe_allow_html=True)
    
    # السطر الأول: زبون (نسبة 4) وحسم (نسبة 1)
    c1, c2 = st.columns([4, 1])
    with c1: cust = st.text_input("الزبون", placeholder="اسم المحل")
    with c2: disc = st.text_input("حسم%", value="0")

    st.write("---")

    # السطر الثاني: صنف (نسبة 4) وكمية (نسبة 1)
    all_p = ["حمص 12", "حمص 9", "فول عريض", "بهار اسود"]
    c3, c4 = st.columns([4, 1])
    with c3:
        search = st.text_input("🔍 بحث صنف")
        filtered = [p for p in all_p if search in p] if search else all_p
        sel_p = st.selectbox("اختر", ["--"] + filtered)
    with c4: qty = st.text_input("عدد", "1")

    if st.button("➕ إضافة", use_container_width=True):
        if sel_p != "--" and cust:
            st.session_state.temp_items.append({"الصنف": sel_p, "الكمية": convert_ar_nav(qty)})
            st.success("تم")

    if st.session_state.temp_items:
        st.table(pd.DataFrame(st.session_state.temp_items))

    st.button("🔙 عودة", on_click=lambda: setattr(st.session_state, 'page', 'home'))

