import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات التنسيق والهوية البصرية الجديدة ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
        body { background-color: white !important; }
    }

    /* تنسيق الفاتورة الجديد */
    .invoice-preview { background-color: white; padding: 20px; border: 1.5px solid #000; border-radius: 5px; color: black; }
    .company-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px; }
    .company-name { font-size: 26px; font-weight: 800; margin-bottom: 2px; }
    .company-details { font-size: 14px; color: #333; }
    
    .invoice-title-section { text-align: center; margin-bottom: 20px; }
    .invoice-main-title { font-size: 22px; font-weight: bold; text-decoration: underline; margin-bottom: 5px; }
    .invoice-no-small { font-size: 16px; font-weight: normal; color: #444; }

    .customer-section { margin-bottom: 15px; border-right: 4px solid #1E3A8A; padding-right: 10px; }
    .customer-label { font-size: 14px; color: #555; }
    .customer-name-big { font-size: 20px; font-weight: 800; color: black; line-height: 1.2; }

    .meta-info { display: flex; justify-content: space-between; font-size: 13px; color: #333; margin-bottom: 10px; border-top: 1px dotted #ccc; padding-top: 5px; }
    
    .styled-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 14px; }
    .styled-table th { background-color: #f2f2f2; border: 1px solid #000; padding: 8px; }
    .styled-table td { border: 1px solid #000; padding: 8px; text-align: center; }
    
    .summary-box { width: 100%; margin-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 14px; }
    .total-final-bold { background-color: #eee; border: 2px solid #000; padding: 8px; font-size: 20px; font-weight: 800; text-align: center; margin-top: 10px; }

    .thermal-receipt { width: 100%; max-width: 300px; margin: 0 auto; padding: 10px; border: 1px solid #eee; text-align: center; background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الربط بالإكسل (القيم مأخوذة من صورك) ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"
GID_DATA = "0"
GID_CUSTOMERS = "155973706" 

@st.cache_data(ttl=60)
def load_rep_customers(rep_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_CUSTOMERS}"
        df = pd.read_csv(url)
        rep_df = df[df.iloc[:, 0].astype(str).str.strip() == rep_name.strip()]
        return {f"{row.iloc[1]} ({row.iloc[2]})": row.iloc[1] for _, row in rep_df.iterrows()}
    except: return {}

def get_next_invoice_number():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_DATA}"
        df = pd.read_csv(url)
        if 'رقم الفاتوره' in df.columns:
            valid_nums = pd.to_numeric(df['رقم الفاتوره'], errors='coerce').dropna()
            if not valid_nums.empty: return str(int(valid_nums.max()) + 1)
        return "1001"
    except: return str(random.randint(10000, 99999))

@st.cache_data(ttl=60)
def load_products_from_excel():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df_p = pd.read_csv(url)
        df_p.columns = [c.strip() for c in df_p.columns]
        return pd.Series(df_p.iloc[:, 1].values, index=df_p.iloc[:, 0]).to_dict()
    except: return {"⚠️ خطأ": 0.0}

PRODUCTS = load_products_from_excel()

def send_to_google_sheets(vat, total_pre, inv_no, customer, representative, date_time):
    url = "https://script.google.com/macros/s/AKfycbzi3kmbVyg_MV1Nyb7FwsQpCeneGVGSJKLMpv2YXBJR05v8Y77-Ub2SpvViZWCCp1nyqA/exec"
    data = {"vat_value": vat, "total_before": total_pre, "invoice_no": inv_no, "cust_name": customer, "rep_name": representative, "date_full": date_time}
    try:
        requests.post(url, data=data, timeout=10)
        return True
    except: return False

USERS = {
    "عبد الكريم حوراني": "9900", "محمد الحسيني": "8822", "علي دوغان": "5500", 
    "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", 
    "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'confirmed' not in st.session_state: st.session_state.confirmed = False
if 'receipt_view' not in st.session_state: st.session_state.receipt_view = False
if 'is_sent' not in st.session_state: st.session_state.is_sent = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- منطق الواجهة ---
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
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold; font-size:22px;">ببركة الصلاة على محمد وال محمد</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed, st.session_state.receipt_view, st.session_state.is_sent = 'order', [], False, False, False
        st.session_state.inv_no = get_next_invoice_number()
        st.rerun()

elif st.session_state.page == 'order':
    if st.session_state.receipt_view:
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(st.session_state.get('last_disc', '0')))
        total_after_disc = raw_total * (1 - h_val/100)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat
        cust_name = st.session_state.get('last_cust', '..........')
        st.markdown(f'<div class="thermal-receipt"><div class="receipt-header">شركة حلباوي إخوان ش.م.م</div><div class="receipt-sub">لبنان - بيروت - الرويس<br>03/220893 - 01/556058</div><div class="receipt-title">إشعار بالاستلام</div><div class="receipt-body">وصلنا من السيد: <b>{cust_name}</b><br>مبلغ وقدره: <b style="font-size: 20px;">${final_net:,.2f}</b><br>وذلك عن فاتورة رقم: #{st.session_state.inv_no}</div><div class="receipt-footer">التاريخ: {datetime.now().strftime("%Y-%m-%d | %H:%M")}<br>المندوب: {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
        if st.button("🖨️ طباعة الإيصال", use_container_width=True): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        if st.button("🔙 العودة للفاتورة", use_container_width=True): st.session_state.receipt_view = False; st.rerun()

    else:
        st.markdown(f'<h2 class="no-print" style="text-align:center; color:#1E3A8A;">فاتورة جديدة #{st.session_state.inv_no}</h2>', unsafe_allow_html=True)
        
        cust_dict = load_rep_customers(st.session_state.user_name)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            search_c = st.text_input("🔍 ابحث عن زبون...")
            filtered_c = [k for k in cust_dict.keys() if search_c in k] if search_c else list(cust_dict.keys())
            sel_display = st.selectbox("اختر الزبون", ["-- اختر --"] + filtered_c)
            cust = cust_dict.get(sel_display, sel_display if sel_display != "-- اختر --" else "")
        with col_c2:
            disc_input = st.text_input("الحسم %", value="0")
        
        st.session_state.last_cust, st.session_state.last_disc = cust, disc_input

        st.divider()
        search_p = st.text_input("🔍 ابحث عن صنف...")
        filtered_p = [p for p in PRODUCTS.keys() if search_p in p] if search_p else list(PRODUCTS.keys())
        sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered_p)
        qty_str = st.text_input("العدد")

        if st.button("➕ إضافة صنف", use_container_width=True):
            if sel_p != "-- اختر الصنف --" and qty_str:
                q = float(convert_ar_nav(qty_str))
                st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": PRODUCTS[sel_p]})
                st.rerun()

        if st.button("👁️ معاينة الفاتورة", use_container_width=True, type="primary"): st.session_state.confirmed = True

        if st.session_state.confirmed and st.session_state.temp_items:
            h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
            raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
            discount_amt = raw_total * (h_val / 100)
            total_after_disc = raw_total - discount_amt
            total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
            final_net = total_after_disc + total_vat

            # تصميم المعاينة الجديد
            st.markdown(f"""
                <div class="invoice-preview">
                    <div class="company-header">
                        <div class="company-name">شركة حلباوي إخوان ش.م.م</div>
                        <div class="company-details">بيروت - الرويس | 03/220893 - 01/556058</div>
                    </div>
                    
                    <div class="invoice-title-section">
                        <div class="invoice-main-title">فاتورة مبيعات</div>
                        <div class="invoice-no-small">رقم الفاتورة: {st.session_state.inv_no}</div>
                    </div>

                    <div class="customer-section">
                        <div class="customer-label">الزبون المحترم:</div>
                        <div class="customer-name-big">{cust}</div>
                    </div>

                    <div class="meta-info">
                        <div>التاريخ: {datetime.now().strftime("%Y-%m-%d")}</div>
                        <div>المندوب: {st.session_state.user_name}</div>
                    </div>

                    <table class="styled-table">
                        <tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>
                        {"".join([f'<tr><td>{x["الصنف"]}</td><td>{x["العدد"]}</td><td>${x["السعر"]:.2f}</td><td>${x["العدد"]*x["السعر"]:.2f}</td></tr>' for x in st.session_state.temp_items])}
                    </table>

                    <div class="summary-box">
                        <div class="summary-row"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                        <div class="summary-row"><span>الحسم ({h_val}%):</span><span>-${discount_amt:,.2f}</span></div>
                        <div class="summary-row" style="border-top: 1px solid #eee;"><span>بعد الحسم:</span><span>${total_after_disc:,.2f}</span></div>
                        <div class="summary-row"><span>الضريبة (VAT 11%):</span><span>+${total_vat:,.2f}</span></div>
                        <div class="total-final-bold">الإجمالي الصافي: ${final_net:,.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_save, col_print = st.columns(2)
            with col_save:
                if st.button("💾 حفظ وإرسال", use_container_width=True):
                    if send_to_google_sheets(f"{total_vat:.2f}", f"{raw_total:.2f}", st.session_state.inv_no, cust, st.session_state.user_name, datetime.now().strftime("%Y-%m-%d %H:%M")):
                        st.session_state.is_sent = True
                        st.success("✅ تم الحفظ بنجاح")
            with col_print:
                if st.button("🖨️ طباعة الفاتورة", use_container_width=True, disabled=not st.session_state.is_sent):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

        st.divider()
        col_b, col_r = st.columns(2)
        with col_b:
            if st.button("🔙 الرئيسية"): st.session_state.page = 'home'; st.rerun()
        with col_r:
            if st.button("🧾 إشعار استلام"): st.session_state.receipt_view = True; st.rerun()
