import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests # لإرسال البيانات عبر الرابط

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    div[data-testid="InputInstructions"] { display: none !important; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 18px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 10px; border: 1px solid #ddd; }
    .styled-table td { padding: 10px; border: 1px solid #ddd; }
    
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 18px; border-bottom: 1px solid #eee; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة الإرسال عبر الرابط الذي أرسلته ---
def send_data_via_link(vat, rep, cust, inv, pre_disc, date):
    url = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"
    
    # تجهيز البيانات حسب ترتيب الأعمدة في ملفك
    payload = {
        "vat": vat,        # سيذهب للعمود A
        "rep": rep,        # B
        "cust": cust,      # C
        "inv": inv,        # D
        "pre_disc": pre_disc, # E
        "date": date       # F
    }
    
    try:
        response = requests.post(url, data=payload)
        return True
    except:
        return False

# --- 3. البيانات ونظام الدخول ---
USERS = {
    "محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", 
    "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", 
    "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"
}

PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ارز مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False

# --- 4. واجهة البرنامج ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user_sel
            st.rerun()
else:
    # واجهة الفاتورة
    st.markdown(f'<h3 class="no-print" style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    cust = st.text_input("اسم الزبون")
    disc_input = st.text_input("الحسم %", value="0")

    st.divider()
    search = st.text_input("🔍 ابحث عن صنف...")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
    qty = st.text_input("العدد")

    if st.button("➕ إضافة"):
        if sel_p != "-- اختر الصنف --" and qty:
            st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(qty), "السعر": PRODUCTS[sel_p]})
            st.rerun()

    if st.button("✅ تثبيت", type="primary"): st.session_state.confirmed = True

    if st.session_state.confirmed and st.session_state.temp_items:
        # حسابات
        h_val = float(disc_input) if disc_input else 0
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100) * 0.11) for i in st.session_state.temp_items if "*" in i["الصنف"])

        # عرض الفاتورة والملخص
        st.write(f"المجموع قبل الحسم: ${raw_total:.2f}")
        st.write(f"ضريبة VAT: ${total_vat:.2f}")

        col_s, col_p = st.columns(2)
        with col_s:
            if st.button("💾 حفظ وإرسال"):
                date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                if send_data_via_link(f"{total_vat:.2f}", st.session_state.user_name, cust, st.session_state.inv_no, f"{raw_total:.2f}", date_now):
                    st.success("✅ تم الإرسال!")
        with col_p:
            if st.button("🖨️ طباعة"): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

