import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# الرابط الخاص بجوجل شيت (سيتم تفعيله عند الربط النهائي)
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

# 2. قاعدة بيانات المناديب الثابتة
USERS = {
    "محمد الحسيني": "8822",
    "علي دوغان": "5500",
    "عزات حلاوي": "6611",
    "علي حسين حلباوي": "4455",
    "محمد حسين حلباوي": "3366",
    "احمد حسين حلباوي": "7722",
    "علي محمد حلباوي": "6600"
}

# دالة تحويل الأرقام العربية
def convert_ar_nav(text):
    if not isinstance(text, str): return text
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيقات الجمالية (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 15px; margin-bottom: 20px; }
    .welcome-container { text-align: center; margin: 20px 0; }
    .welcome-text { font-size: 22px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    .invoice-header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة حالة التطبيق (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []

# --- 🔐 الصفحة الأولى: شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("إختر اسمك", ["-- اختر اسمك --"] + list(USERS.keys()))
    password_input = st.text_input("كلمة السر", type="password")
    
    if st.button("دخول", use_container_width=True):
        if user_choice != "-- اختر اسمك --" and USERS[user_choice] == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# --- الصفحة الثانية: الترحيب ---
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="welcome-container">
                <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
                <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</div>
            </div>
        """, unsafe_allow_html=True)
        
        # الزر المطلوب في الصفحة الثانية
        if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
            st.session_state.page = 'order_page'
            st.rerun()
            
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- صفحة الطلبية ---
    elif st.session_state.page == 'order_page':
        # أ- رقم الفاتورة في الأعلى الوسط
        inv_no = str(random.randint(10000, 99999))
        st.markdown(f'<div class="invoice-header">رقم الفاتورة: {inv_no}</div>', unsafe_allow_html=True)
        
        st.divider()

        # ب- اسم الزبون والحسم على نفس السطر
        col_cust, col_disc = st.columns([3, 1])
        with col_cust:
            cust_name = st.text_input("👤 اسم الزبون")
        with col_disc:
            discount_pct = st.number_input("الحسم %", min_value=0, max_value=6, step=1)

        st.divider()

        # ج- مكان استكمال نظام التابلو والبحث
        st.write("🔧 بانتظار شرحك لتكملة نظام البحث والتابلو هنا...")
        
        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()

