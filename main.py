import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات الصفحة والتنسيق (نفس الشكل الذي تفضله) ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    div[data-testid="InputInstructions"], div[data-baseweb="helper-text"] { display: none !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    @media print { .no-print { display: none !important; } .stButton, .stTextInput, .stSelectbox { display: none !important; } body { background-color: white !important; } }
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 18px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 10px; border: 1px solid #ddd; }
    .styled-table td { padding: 10px; border: 1px solid #ddd; }
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 18px; border-bottom: 1px solid #eee; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة الإرسال المعدلة (لضمان وصول البيانات للـ Sheets) ---
def send_to_google_sheets(vat, total_pre, inv_no, customer, representative, date_time):
    # الرابط الخاص بك
    url = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"
    
    # هذه الأسماء يجب أن تتطابق مع ما تم برمجته في Script جوجل
    data = {
        "vat_value": vat,           # العمود A
        "total_before": total_pre,  # العمود B
        "invoice_no": inv_no,       # العمود C
        "cust_name": customer,      # العمود D
        "rep_name": representative, # العمود E
        "date_full": date_time      # العمود F
    }
    
    try:
        # نستخدم timeout لضمان عدم تعليق البرنامج
        response = requests.post(url, data=data, timeout=10)
        return True
    except:
        return False

# --- 3. البيانات الأساسية وإدارة الدخول ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}
PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ازر مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 4. واجهة البرنامج ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.page = True, user_sel, 'home'
            st.rerun()

elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold; font-size:20px;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed = 'order', [], False
        st.session_state.inv_no = str(random.randint(10000, 99999))
        st.rerun()

elif st.session_state.page == 'order':
    st.markdown(f'<h3 class="no-print" style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: cust = st.text_input("اسم الزبون")
    with col2: disc_input = st.text_input("الحسم %", value="0")
    
    st.divider()
    search = st.text_input("🔍 ابحث عن صنف...")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
    qty_str = st.text_input("العدد")

    if st.button("➕ إضافة صنف", use_container_width=True):
        if sel_p != "-- اختر الصنف --" and qty_str:
            q = float(convert_ar_nav(qty_str))
            st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": PRODUCTS[sel_p]})
            st.rerun()

    if st.button("✅ ثبت الفاتورة", use_container_width=True, type="primary"):
        st.session_state.confirmed = True

    if st.session_state.confirmed and st.session_state.temp_items:
        h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        discount_amt = raw_total * (h_val / 100)
        total_after_disc = raw_total - discount_amt
        
        total_vat = 0
        table_html = '<table class="styled-table"><tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>'
        for item in st.session_state.temp_items:
            line_total = item["العدد"] * item["السعر"]
            if "*" in item["الصنف"]: total_vat += (line_total * (1 - h_val/100)) * 0.11
            table_html += f'<tr><td>{item["الصنف"]}</td><td>{item["العدد"]}</td><td>{item["السعر"]:.2f}</td><td>{line_total:.2f}</td></tr>'
        table_html += '</table>'
        st.markdown(table_html, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="summary-container">
                <div class="summary-row"><span>المجموع قبل الحسم:</span><span>${raw_total:,.2f}</span></div>
                <div class="summary-row"><span>ضريبة VAT:</span><span>+${total_vat:,.2f}</span></div>
                <div class="final-total">الصافي النهائي: ${(total_after_disc + total_vat):,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            # إرسال البيانات
            success = send_to_google_sheets(
                f"{total_vat:.2f}", 
                f"{raw_total:.2f}", 
                st.session_state.inv_no, 
                cust, 
                st.session_state.user_name, 
                now
            )
            if success:
                st.success("✅ تم الإرسال بنجاح! تأكد من ملف Sheets الآن.")
            else:
                st.error("❌ فشل الإرسال. تأكد من اتصال الإنترنت أو إعدادات الرابط.")

    if st.button("🔙 عودة", key="back"):
        st.session_state.page = 'home'
        st.rerun()
