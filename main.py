import streamlit as st
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

# 3. التنسيق الإجباري للسطر الواحد (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* منع كسر السطر في الأعمدة نهائياً */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-end !important;
        width: fit-content !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important; /* يمنع نزول العناصر لسطر جديد */
        gap: 5px !important;
    }
    
    .invoice-header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #000; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []

# --- نظام الدخول والترحيب (مختصر للحفاظ على التركيز) ---
if not st.session_state.logged_in:
    st.title("🔐 دخول المندوبين")
    user = st.selectbox("المندوب", list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user
            st.rerun()
elif st.session_state.page == 'home':
    st.header(f"أهلاً سيد {st.session_state.user_name}")
    if st.button("📝 تسجيل الفاتورة"):
        st.session_state.page = 'order_page'
        st.rerun()

# --- صفحة الطلبية (الحل النهائي للسطر الواحد) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<div class="invoice-header">رقم الفاتورة: {random.randint(1000, 9999)}</div>', unsafe_allow_html=True)

    # السطر الأول: زبون وحسم (إجبارياً في سطر واحد)
    col_cust, col_disc = st.columns([4, 1]) 
    with col_cust:
        cust = st.text_input("الزبون", placeholder="اسم المحل")
    with col_disc:
        disc = st.text_input("حسم%", value="0")

    st.write("---")

    # السطر الثاني: صنف وكمية (إجبارياً في سطر واحد)
    col_prod, col_qty = st.columns([4, 1])
    with col_prod:
        search = st.text_input("🔍 البحث عن صنف")
        # مثال للأصناف
        sel_p = st.selectbox("اختر الصنف", ["حمص 12", "حمص 9", "فول", "بهار"])
    with col_qty:
        qty = st.text_input("عدد", value="1")

    if st.button("➕ إضافة", use_container_width=True):
        if cust:
            st.session_state.temp_items.append({"الصنف": sel_p, "الكمية": qty})
            st.success("تمت الإضافة")

    if st.session_state.temp_items:
        st.table(pd.DataFrame(st.session_state.temp_items))

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.rerun()
