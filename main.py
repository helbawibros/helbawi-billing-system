import streamlit as st
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

# دالة تحويل الأرقام
def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيق القسري (CSS) - الحل الوحيد لمنع كسر السطر
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* إجبار الأعمدة على البقاء في سطر واحد */
    div[data-testid="column"] {
        width: unset !important;
        flex: unset !important;
        min-width: unset !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: flex-start !important;
        justify-content: space-between !important;
        gap: 5px !important;
    }

    /* تحديد نسب العرض بدقة */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) { width: 78% !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) { width: 20% !important; }

    .invoice-header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

# --- نظام الدخول والترحيب ---
if not st.session_state.logged_in:
    st.markdown('<h2 style="text-align:center;">🔐 دخول المندوبين</h2>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user
            st.rerun()
elif st.session_state.page == 'home':
    st.markdown(f'<h3 style="text-align:center;">أهلاً بك سيد {st.session_state.user_name}</h3>', unsafe_allow_html=True)
    if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
        st.session_state.page = 'order_page'
        st.rerun()
    if st.button("🚪 خروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- صفحة الطلبية (التابلو الحديدي) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<div class="invoice-header">رقم الفاتورة: {st.session_state.inv_no}</div>', unsafe_allow_html=True)

    # السطر 1: الزبون والحسم
    row1_c1, row1_c2 = st.columns([4, 1])
    with row1_c1:
        cust = st.text_input("الزبون", placeholder="اسم المحل", label_visibility="collapsed")
    with row1_c2:
        disc = st.text_input("حسم%", value="0", label_visibility="collapsed")

    st.write("---")

    # السطر 2: الصنف والعدد
    all_p = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ"]
    row2_c1, row2_c2 = st.columns([4, 1])
    with row2_c1:
        search_val = st.text_input("بحث", placeholder="🔍 ابحث عن صنف...", label_visibility="collapsed")
        filtered = [p for p in all_p if search_val in p] if search_val else all_p
        sel_p = st.selectbox("صنف", ["-- اختر الصنف --"] + filtered, label_visibility="collapsed")
    with row2_c2:
        qty = st.text_input("عدد", value="1", label_visibility="collapsed")

    if st.button("➕ إضافة للصنف", use_container_width=True):
        if sel_p != "-- اختر الصنف --" and cust:
            st.session_state.temp_items.append({"الصنف": sel_p, "الكمية": convert_ar_nav(qty)})
            st.success("تم")

    if st.session_state.temp_items:
        st.table(pd.DataFrame(st.session_state.temp_items))

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.rerun()
