import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات التنسيق والجمالية ---
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

    /* تنسيق الفاتورة للمعاينة والطباعة */
    .invoice-preview { 
        background-color: white; 
        padding: 20px; 
        border: 1px solid #eee; 
        border-radius: 10px; 
        color: black;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
    }
    .invoice-header { text-align: center; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px; }
    .invoice-info { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 14px; }
    
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; text-align: center; color: black; }
    .styled-table th { background-color: #f8f9fa; color: #1E3A8A; padding: 8px; border: 1px solid #ddd; }
    .styled-table td { padding: 8px; border: 1px solid #ddd; }
    
    .summary-section { margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; }
    .summary-line { display: flex; justify-content: space-between; padding: 3px 0; font-size: 15px; }
    .total-line { font-weight: bold; font-size: 18px; color: #1E3A8A; margin-top: 5px; border-top: 2px solid #1E3A8A; padding-top: 5px; }

    .thermal-receipt { width: 100%; max-width: 300px; margin: 0 auto; padding: 10px; border: 1px solid #eee; text-align: center; background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الربط بالإكسل ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"
GID_DATA = "0"

def get_next_invoice_number():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_DATA}"
        df = pd.read_csv(url)
        col_name = 'رقم الفاتوره'
        if col_name in df.columns:
            valid_nums = pd.to_numeric(df[col_name], errors='coerce').dropna()
            if not valid_nums.empty: return str(int(valid_nums.max()) + 1)
        return "1001"
    except: return str(random.randint(10000, 99999))

@st.cache_data(ttl=60)
def load_products_from_excel():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df_p = pd.read_csv(url)
        df_p.columns = [c.strip() for c in df_p.columns]
        name_col = [c for c in df_p.columns if 'الاسم' in c or 'الإسم' in c][0]
        price_col = [c for c in df_p.columns if 'السعر' in c][0]
        return pd.Series(df_p[price_col].values, index=df_p[name_col]).to_dict()
    except: return {"⚠️ خطأ في تحميل الأصناف": 0.0}

PRODUCTS = load_products_from_excel()

def send_to_google_sheets(vat, total_pre, inv_no, customer, representative, date_time):
    url = "https://script.google.com/macros/s/AKfycbzi3kmbVyg_MV1Nyb7FwsQpCeneGVGSJKLMpv2YXBJR05v8Y77-Ub2SpvViZWCCp1nyqA/exec"
    data = {"vat_value": vat, "total_before": total_pre, "invoice_no": inv_no, "cust_name": customer, "rep_name": representative, "date_full": date_time}
    try:
        requests.post(url, data=data, timeout=10)
        return True
    except: return False

USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'confirmed' not in st.session_state: st.session_state.confirmed = False
if 'receipt_view' not in st.session_state: st.session_state.receipt_view = False
if 'is_sent' not in st.session_state: st.session_state.is_sent = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 4. منطق واجهة المستخدم ---

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
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold; font-size:20px;">ببركة الصلاة على محمد وال محمد</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed, st.session_state.receipt_view, st.session_state.is_sent = 'order', [], False, False, False
        st.session_state.inv_no = get_next_invoice_number()
        st.rerun()

elif st.session_state.page == 'order':
    if st.session_state.receipt_view:
        # واجهة إشعار الاستلام (كما هي)
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(st.session_state.get('last_disc', '0')))
        total_after_disc = raw_total * (1 - h_val/100)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat
        cust_name = st.session_state.get('last_cust', '..........')
        st.markdown(f'<div class="thermal-receipt"><div class="receipt-header">شركة حلباوي إخوان ش.م.م</div><div class="receipt-sub">بيروت - الرويس<br>01/556058</div><div class="receipt-title">إشعار بالاستلام</div><div class="receipt-body">وصلنا من السيد: <b>{cust_name}</b><br>مبلغ وقدره: <b style="font-size: 20px;">${final_net:,.2f}</b><br>وذلك عن فاتورة رقم: #{st.session_state.inv_no}</div><div class="receipt-footer">التاريخ: {datetime.now().strftime("%Y-%m-%d | %H:%M")}<br>المندوب: {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
        if st.button("🖨️ طباعة الإيصال", use_container_width=True): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        if st.button("🔙 العودة للفاتورة", use_container_width=True): st.session_state.receipt_view = False; st.rerun()

    else:
        # واجهة إدخال الفاتورة
        st.markdown(f'<h2 class="no-print" style="text-align:center; color:#1E3A8A;">رقم الفاتورة: {st.session_state.inv_no}</h2>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1: cust = st.text_input("اسم الزبون (المحل)", key="cust_input")
        with col_c2: disc_input = st.text_input("الحسم %", value="0", key="disc_input")
        st.session_state.last_cust, st.session_state.last_disc = cust, disc_input

        st.divider()
        if 'clear_counter' not in st.session_state: st.session_state.clear_counter = 0
        search = st.text_input("🔍 ابحث عن صنف...", key=f"s_{st.session_state.clear_counter}")
        filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
        sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered, key=f"p_{st.session_state.clear_counter}")
        qty_str = st.text_input("العدد", key=f"q_{st.session_state.clear_counter}")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ إضافة صنف", use_container_width=True):
                if sel_p != "-- اختر الصنف --" and qty_str:
                    q = float(convert_ar_nav(qty_str))
                    st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": PRODUCTS[sel_p]})
                    st.session_state.confirmed, st.session_state.clear_counter = False, st.session_state.clear_counter + 1
                    st.rerun()
        with col_btn2:
            if st.button("👁️ معاينة وتثبيت", use_container_width=True, type="primary"): st.session_state.confirmed = True

        if st.session_state.confirmed and st.session_state.temp_items:
            # --- معاينة الفاتورة بشكل احترافي ---
            h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
            raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
            discount_amt = raw_total * (h_val / 100)
            total_after_disc = raw_total - discount_amt
            total_vat = 0
            
            items_rows = ""
            for item in st.session_state.temp_items:
                line_total = item["العدد"] * item["السعر"]
                line_vat = (line_total * (1 - h_val/100)) * 0.11 if "*" in item["الصنف"] else 0
                total_vat += line_vat
                items_rows += f'<tr><td>{item["الصنف"]}</td><td>{item["العدد"]}</td><td>{item["السعر"]:.2f}</td><td>{line_vat:.2f}</td><td>{line_total:.2f}</td></tr>'
            
            final_net = total_after_disc + total_vat

            st.markdown(f"""
                <div class="invoice-preview">
                    <div class="invoice-header">
                        <h2 style="margin:0; color:#1E3A8A;">فاتورة مبيعات</h2>
                        <div style="font-size:18px;">شركة حلباوي إخوان</div>
                    </div>
                    <div class="invoice-info">
                        <div><b>الزبون:</b> {cust}</div>
                        <div><b>الرقم:</b> #{st.session_state.inv_no}<br><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</div>
                    </div>
                    <table class="styled-table">
                        <tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>VAT</th><th>الإجمالي</th></tr>
                        {items_rows}
                    </table>
                    <div class="summary-section">
                        <div class="summary-line"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                        <div class="summary-line"><span>الحسم ({h_val}%):</span><span>-${discount_amt:,.2f}</span></div>
                        <div class="summary-line"><span>الضريبة (11%):</span><span>+${total_vat:,.2f}</span></div>
                        <div class="total-line"><span>الإجمالي الصافي:</span><span>${final_net:,.2f}</span></div>
                    </div>
                    <div style="margin-top:10px; font-size:12px; color:#777; text-align:left;">المندوب: {st.session_state.user_name}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col_s, col_p = st.columns(2)
            with col_s:
                if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
                    if send_to_google_sheets(f"{total_vat:.2f}", f"{raw_total:.2f}", st.session_state.inv_no, cust, st.session_state.user_name, datetime.now().strftime("%Y-%m-%d %H:%M")):
                        st.session_state.is_sent = True
                        st.success("✅ تم الحفظ بنجاح!")
                        st.rerun()
            with col_p:
                if st.button("🖨️ طباعة الفاتورة الآن", use_container_width=True, disabled=not st.session_state.is_sent):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

        st.divider()
        col_back, col_rec = st.columns(2)
        with col_back:
            if st.button("🔙 عودة للرئيسية", use_container_width=True): st.session_state.page = 'home'; st.rerun()
        with col_rec:
            if st.button("🧾 إشعار استلام مبلغ", use_container_width=True): st.session_state.receipt_view = True; st.rerun()
