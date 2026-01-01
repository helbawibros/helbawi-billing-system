import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات التنسيق والهوية ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    div[data-testid="InputInstructions"], div[data-baseweb="helper-text"] { display: none !important; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
        body { background-color: white !important; }
    }

    .invoice-preview { background-color: white; padding: 25px; border: 1px solid #000; border-radius: 5px; color: black; }
    .company-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px double #000; padding-bottom: 10px; margin-bottom: 10px; }
    .company-info { text-align: right; }
    .invoice-no-top { font-size: 16px; font-weight: bold; border: 1px solid #000; padding: 5px; }
    
    .invoice-title-box { text-align: center; margin: 10px 0; }
    .invoice-title { font-size: 22px; font-weight: bold; text-decoration: underline; }
    
    .customer-line { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15px; }
    .cust-name-big { font-size: 20px; font-weight: 800; text-align: right; }
    .meta-small { font-size: 12px; text-align: left; color: #333; line-height: 1.3; }
    
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 15px; text-align: center; color: black; }
    .styled-table th { background-color: #f0f2f6; color: black; padding: 10px; border: 1px solid #000; }
    .styled-table td { padding: 10px; border: 1px solid #000; }
    
    .summary-section { margin-top: 15px; width: 100%; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 10px; font-size: 16px; border-bottom: 1px solid #ddd; }
    .total-final { background-color: #eee; font-size: 22px; font-weight: 800; color: black; border: 2px solid #000; margin-top: 10px; padding: 10px; text-align: center; }

    .thermal-receipt { width: 100%; max-width: 300px; margin: 0 auto; padding: 10px; border: 1px solid #eee; text-align: center; background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الربط بالإكسل ---
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

# --- المنطق ---
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
        # إيصال الاستلام (يبقى كما هو)
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(st.session_state.get('last_disc', '0')))
        total_after_disc = raw_total * (1 - h_val/100)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat
        st.markdown(f'<div class="thermal-receipt"><b>شركة حلباوي إخوان</b><br>إيصال استلام<br>السيد: {st.session_state.get("last_cust", "")}<br>المبلغ: ${final_net:,.2f}<br>#{st.session_state.inv_no}</div>', unsafe_allow_html=True)
        if st.button("🔙 العودة"): st.session_state.receipt_view = False; st.rerun()
    else:
        st.markdown(f'<h3 class="no-print" style="text-align:center;">إدخال فاتورة رقم #{st.session_state.inv_no}</h3>', unsafe_allow_html=True)
        cust_dict = load_rep_customers(st.session_state.user_name)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            search_c = st.text_input("🔍 بحث عن زبون")
            sel_display = st.selectbox("الزبون", ["-- اختر --"] + [k for k in cust_dict.keys() if search_c in k])
            cust = cust_dict.get(sel_display, "")
        with col_c2:
            disc_input = st.text_input("الحسم %", value="0")
        
        st.session_state.last_cust, st.session_state.last_disc = cust if cust else sel_display, disc_input
        st.divider()
        search_p = st.text_input("🔍 بحث صنف")
        sel_p = st.selectbox("الصنف", ["-- اختر --"] + [p for p in PRODUCTS.keys() if search_p in p])
        qty_str = st.text_input("العدد")

        if st.button("➕ إضافة"):
            if sel_p != "-- اختر --" and qty_str:
                st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(convert_ar_nav(qty_str)), "السعر": PRODUCTS[sel_p]})
                st.rerun()

        if st.button("👁️ معاينة الفاتورة", use_container_width=True, type="primary"): st.session_state.confirmed = True

        if st.session_state.confirmed and st.session_state.temp_items:
            h_val = float(convert_ar_nav(disc_input))
            raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
            total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
            final_net = (raw_total * (1 - h_val/100)) + total_vat

            st.markdown(f"""
                <div class="invoice-preview">
                    <div class="company-header">
                        <div class="company-info">
                            <div class="company-name">شركة حلباوي إخوان ش.م.م</div>
                            <div class="company-details">بيروت - الرويس | 01/556058</div>
                        </div>
                        <div class="invoice-no-top">رقم: {st.session_state.inv_no}</div>
                    </div>
                    <div class="invoice-title-box"><div class="invoice-title">فاتورة مبيعات</div></div>
                    <div class="customer-line">
                        <div class="cust-name-big">{st.session_state.last_cust}</div>
                        <div class="meta-small">
                            التاريخ: {datetime.now().strftime("%Y-%m-%d | %H:%M")}<br>
                            المندوب: {st.session_state.user_name}
                        </div>
                    </div>
                    <table class="styled-table">
                        <tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>
                        {"".join([f'<tr><td>{x["الصنف"]}</td><td>{x["العدد"]}</td><td>{x["السعر"]:.2f}</td><td>{x["العدد"]*x["السعر"]:.2f}</td></tr>' for x in st.session_state.temp_items])}
                    </table>
                    <div class="summary-section">
                        <div class="summary-row"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                        <div class="summary-row"><span>الحسم:</span><span>{h_val}%</span></div>
                        <div class="summary-row"><span>الضريبة:</span><span>+${total_vat:,.2f}</span></div>
                        <div class="total-final">الإجمالي: ${final_net:,.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 حفظ وإرسال"):
                if send_to_google_sheets(f"{total_vat:.2f}", f"{raw_total:.2f}", st.session_state.inv_no, st.session_state.last_cust, st.session_state.user_name, datetime.now().strftime("%Y-%m-%d %H:%M")):
                    st.session_state.is_sent = True; st.success("✅ تم الحفظ")
            if st.button("🖨️ طباعة", disabled=not st.session_state.is_sent):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

        if st.button("🔙 الرئيسية"): st.session_state.page = 'home'; st.rerun()
