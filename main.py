import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب
USERS = {
    "محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611",
    "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366",
    "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"
}

# دالة تحويل الأرقام العربية
def convert_ar_nav(text):
    if not isinstance(text, str): return text
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيق السحري (CSS) لدمج العناصر في سطر واحد على الموبايل
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 15px; margin-bottom: 20px; }
    .welcome-container { text-align: center; margin: 20px 0; }
    .welcome-text { font-size: 22px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    .invoice-header { text-align: center; font-size: 26px; font-weight: bold; margin: 10px 0; color: #000; }
    
    /* هذا الجزء هو المسؤول عن دمج الحقول في سطر واحد */
    div[data-testid="column"] {
        display: inline-block !important;
        min-width: 100px !important;
        vertical-align: top !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة الحالة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))

# --- 🔐 الصفحة الأولى: دخول المندوبين ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("إختر اسمك", ["-- اختر اسمك --"] + list(USERS.keys()))
    password_input = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if user_choice != "-- اختر اسمك --" and USERS[user_choice] == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else: st.error("❌ كلمة المرور غير صحيحة")

# --- الصفحة الثانية: الترحيب ---
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="welcome-container"><div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
                <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</div></div>""", unsafe_allow_html=True)
    if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
        st.session_state.page = 'order_page'
        st.rerun()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- صفحة الطلبية (السطر الواحد) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<div class="invoice-header">رقم الفاتورة: {st.session_state.inv_no}</div>', unsafe_allow_html=True)
    st.divider()

    # السطر المدمج: اسم الزبون + الحسم
    row1_col1, row1_col2 = st.columns([2, 1])
    with row1_col1:
        cust_name = st.text_input("👤 الزبون", placeholder="اسم المحل")
    with row1_col2:
        discount = st.number_input("الحسم%", 0, 6, 0)

    st.divider()

    # السطر المدمج: الصنف + العدد
    all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ"]
    row2_col1, row2_col2 = st.columns([2, 1])
    with row2_col1:
        selected_p = st.selectbox("الصنف", ["-- اختر --"] + all_products)
    with row2_col2:
        qty = st.text_input("العدد", "1")

    if st.button("➕ إضافة", use_container_width=True):
        if selected_p != "-- اختر --" and cust_name:
            st.session_state.temp_items.append({"الصنف": selected_p, "الكمية": convert_ar_nav(qty)})
            st.success(f"تمت إضافة {selected_p}")

    if st.session_state.temp_items:
        st.table(pd.DataFrame(st.session_state.temp_items))

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.rerun()
