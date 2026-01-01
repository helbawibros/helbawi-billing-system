import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات التنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    @media print { .no-print { display: none !important; } .stButton { display: none !important; } }
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 16px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 8px; border: 1px solid #ddd; }
    .styled-table td { padding: 8px; border: 1px solid #ddd; }
    .final-total-box { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 20px; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #c3e6cb; }
    .thermal-receipt { width: 100%; max-width: 300px; margin: 0 auto; padding: 10px; border: 1px solid #eee; text-align: center; background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الروابط الحقيقية من ملفك ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"  # صفحة أسعار
GID_DATA = "0"            # صفحة بيانات المندوبين

# دالة جلب الرقم التسلسلي التالي من الإكسل
def get_next_invoice_number():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_DATA}"
        df = pd.read_csv(url)
        # نبحث عن عمود رقم الفاتورة (تأكد أن اسمه مطابق في Sheet1)
        col_name = 'رقم الفاتوره'
        if col_name in df.columns:
            last_no = pd.to_numeric(df[col_name], errors='coerce').max()
            if pd.isna(last_no): return "1001"
            return str(int(last_no) + 1)
        return "1001"
    except:
        return str(random.randint(10000, 99999))

# دالة جلب الأصناف (معدلة لتقبل أي كتابة للاسم والسعر)
@st.cache_data(ttl=60)
def load_products():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df_p = pd.read_csv(url)
        # تنظيف أسماء الأعمدة من المسافات
        df_p.columns = [c.strip() for c in df_p.columns]
        
        # محاولة إيجاد عمود الاسم والسعر مهما كانت طريقة كتابتهما
        name_col = [c for c in df_p.columns if 'الاسم' in c or 'الإسم' in c][0]
        price_col = [c for c in df_p.columns if 'السعر' in c][0]
        
        return pd.Series(df_p[price_col].values, index=df_p[name_col]).to_dict()
    except Exception as e:
        return {"⚠️ عطل في الإكسل: تأكد من A1 الاسم و B1 السعر": 0.0}

PRODUCTS = load_products()

# --- 3. إدارة الجلسة والمستخدمين ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'is_sent' not in st.session_state: st.session_state.is_sent = False

USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 4. واجهات التطبيق ---

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
    st.info(f"مرحباً بك: {st.session_state.user_name}")
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.is_sent = 'order', [], False
        # توليد الرقم التسلسلي الجديد
        st.session_state.inv_no = get_next_invoice_number()
        st.rerun()

elif st.session_state.page == 'order':
    if st.session_state.get('receipt_view', False):
        # واجهة الإيصال الحراري
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(st.session_state.get('last_disc', '0')))
        total_after_disc = raw_total * (1 - h_val/100)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat
        
        st.markdown(f"""
            <div class="thermal-receipt">
                <div style="font-size:22px; font-weight:bold;">شركة حلباوي إخوان ش.م.م</div>
                <div style="font-size:14px;">بيروت - الرويس | 01/556058</div>
                <div style="margin:10px 0; border-top:1px dashed #000; border-bottom:1px dashed #000; padding:5px; font-weight:bold;">إشعار استلام مبلغ</div>
                <div style="text-align:right;">
                    وصلنا من السيد: {st.session_state.get('last_cust', '.......')}<br>
                    مبلغ وقدره: <b>${final_net:,.2f}</b><br>
                    عن فاتورة رقم: {st.session_state.inv_no}
                </div>
                <div style="margin-top:15px; font-size:12px; text-align:right; border-top:1px solid #eee;">
                    التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
                    المندوب: {st.session_state.user_name}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🖨️ طباعة الإيصال", use_container_width=True): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        if st.button("🔙 عودة", use_container_width=True): st.session_state.receipt_view = False; st.rerun()

    else:
        st.markdown(f"<h3 style='text-align:center;'>فاتورة رقم: {st.session_state.inv_no}</h3>", unsafe_allow_html=True)
        cust = st.text_input("اسم الزبون", key="c_in")
        disc = st.text_input("الحسم %", value="0", key="d_in")
        st.session_state.last_cust, st.session_state.last_disc = cust, disc

        st.divider()
        search = st.text_input("🔍 ابحث عن صنف...")
        filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
        sel_p = st.selectbox("اختر الصنف", ["-- اختر --"] + filtered)
        qty = st.text_input("العدد")

        if st.button("➕ إضافة"):
            if sel_p != "-- اختر --" and qty:
                st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(convert_ar_nav(qty)), "السعر": PRODUCTS[sel_p]})
                st.rerun()

        if st.session_state.temp_items:
            raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
            h_val = float(convert_ar_nav(disc))
            
            table_html = '<table class="styled-table"><tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>'
            for item in st.session_state.temp_items:
                table_html += f"<tr><td>{item['الصنف']}</td><td>{item['العدد']}</td><td>{item['السعر']:.2f}</td><td>{item['العدد']*item['السعر']:.2f}</td></tr>"
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)
            
            total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
            final_net = (raw_total * (1 - h_val/100)) + total_vat
            st.markdown(f"<div class='final-total-box'>المجموع الصافي: ${final_net:,.2f}</div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 حفظ وإرسال", use_container_width=True):
                    # دالة الإرسال إلى Google Apps Script
                    url_script = "https://script.google.com/macros/s/AKfycbzi3kmbVyg_MV1Nyb7FwsQpCeneGVGSJKLMpv2YXBJR05v8Y77-Ub2SpvViZWCCp1nyqA/exec"
                    payload = {"vat_value": f"{total_vat:.2f}", "total_before": f"{raw_total:.2f}", "invoice_no": st.session_state.inv_no, "cust_name": cust, "rep_name": st.session_state.user_name, "date_full": datetime.now().strftime("%Y-%m-%d %H:%M")}
                    requests.post(url_script, data=payload)
                    st.session_state.is_sent = True
                    st.success("تم الحفظ!")
                    st.rerun()
            with col2:
                if st.button("🖨️ طباعة الفاتورة", use_container_width=True, disabled=not st.session_state.is_sent):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            
            if st.button("🧾 إشعار استلام", use_container_width=True):
                st.session_state.receipt_view = True
                st.rerun()

    if st.button("🔙 خروج"):
        st.session_state.page = 'home'
        st.rerun()
