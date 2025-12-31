import streamlit as st
import pandas as pd
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    div[data-testid="InputInstructions"] { display: none !important; }
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
        body { background-color: white !important; }
    }

    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 18px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 10px; border: 1px solid #ddd; }
    .styled-table td { padding: 10px; border: 1px solid #ddd; }
    
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 18px; border-bottom: 1px solid #eee; }
    .highlight-row { background-color: #f8f9fa; font-weight: bold; color: #1E3A8A; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة الاتصال بجوجل شيت ---
def send_to_google_sheets(data_row):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # تأكد من وضع المفاتيح في st.secrets أو استخدام ملف JSON محلي
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Helbawi_Database").sheet1
        sheet.append_row(data_row)
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء الإرسال: {e}")
        return False

# --- 3. البيانات الأساسية ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}
PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ارز مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 4. واجهة التطبيق ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">🔐 دخول المندوبين</h1>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user_sel
            st.rerun()

else:
    st.markdown(f'<h3 class="no-print" style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    cust = st.text_input("اسم الزبون (المحل)")
    cust_id = st.text_input("رقم الزبون")
    disc_input = st.text_input("الحسم %", value="0")

    st.divider()
    search = st.text_input("🔍 ابحث عن صنف...")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
    qty_str = st.text_input("العدد")

    if st.button("➕ إضافة صنف", use_container_width=True):
        if sel_p != "-- اختر الصنف --" and qty_str != "":
            q = float(convert_ar_nav(qty_str))
            st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": PRODUCTS[sel_p]})
            st.session_state.confirmed = False
            st.rerun()

    if st.button("✅ ثبت الفاتورة", use_container_width=True, type="primary"):
        st.session_state.confirmed = True

    if st.session_state.confirmed and st.session_state.temp_items:
        st.markdown("<hr class='no-print'>", unsafe_allow_html=True)
        
        # حساب المبالغ
        h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        discount_amt = raw_total * (h_val / 100)
        total_after_disc = raw_total - discount_amt
        
        total_vat = 0
        for item in st.session_state.temp_items:
            if "*" in item["الصنف"]:
                line_after_disc = (item["العدد"] * item["السعر"]) * (1 - (h_val / 100))
                total_vat += line_after_disc * 0.11

        # عرض الفاتورة (رأس الصفحة)
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="text-align: right;">
                    <p><b>الزبون:</b> {cust}<br><b>رقم الزبون:</b> {cust_id}<br><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
                </div>
                <div style="text-align: left;"><p><b>المندوب:</b> {st.session_state.user_name}</p></div>
            </div>
        """, unsafe_allow_html=True)

        # زر الحفظ والطباعة
        col_s, col_p = st.columns(2)
        with col_s:
            if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
                # الترتيب الجديد المطلوب: التاريخ - المندوب - الزبون - رقم الفاتورة - قبل الحسم - VAT
                row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    st.session_state.user_name,
                    cust,
                    st.session_state.inv_no,
                    f"{raw_total:.2f}",
                    f"{total_vat:.2f}"
                ]
                if send_to_google_sheets(row):
                    st.success("✅ تم الإرسال بنجاح!")
        
        with col_p:
            if st.button("🖨️ طباعة الفاتورة", use_container_width=True):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
