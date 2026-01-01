import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات الهوية والترويسة ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
    }

    .invoice-preview { background-color: white; padding: 25px; border: 2px solid #1E3A8A; border-radius: 10px; color: black; }
    .company-header { text-align: center; margin-bottom: 20px; border-bottom: 2px double #1E3A8A; padding-bottom: 10px; }
    .company-name { font-size: 28px; font-weight: 800; color: black; }
    .company-details { font-size: 16px; color: black; line-height: 1.4; }
    .invoice-title { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 15px 0; text-decoration: underline; }
    
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; text-align: center; color: black; }
    .styled-table th { background-color: #f0f2f6; padding: 10px; border: 1px solid #000; }
    .styled-table td { padding: 10px; border: 1px solid #000; }
    
    .summary-row { display: flex; justify-content: space-between; padding: 5px 10px; font-size: 16px; border-bottom: 1px solid #ddd; color: black;}
    .total-final { background-color: #d4edda; font-size: 22px; font-weight: 800; color: #155724; border: 2px solid #c3e6cb; margin-top: 10px; padding: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الربط بالإكسل ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"
GID_CUSTOMERS = "0" # ضَع هنا رقم GID صفحة الزبائن الجديدة من الإكسل
GID_DATA = "0"

# قائمة المندوبين مع المندوب الجديد عبد الكريم حوراني
USERS = {
    "عبد الكريم حوراني": "9900", # كلمة سر افتراضية، يمكنك تغييرها
    "محمد الحسيني": "8822", 
    "علي دوغان": "5500", 
    "عزات حلاوي": "6611", 
    "علي حسين حلباوي": "4455", 
    "محمد حسين حلباوي": "3366", 
    "احمد حسين حلباوي": "7722", 
    "علي محمد حلباوي": "6600"
}

@st.cache_data(ttl=60)
def load_products():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df = pd.read_csv(url)
        return pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    except: return {"خطأ في التحميل": 0}

@st.cache_data(ttl=60)
def load_rep_customers(rep_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_CUSTOMERS}"
        df = pd.read_csv(url)
        # جلب الزبائن التابعين لهذا المندوب فقط
        return df[df['المندوب'] == rep_name]['الزبون'].tolist()
    except: return []

# --- 3. منطق الصفحات ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user_sel
            st.rerun()

elif 'page' not in st.session_state or st.session_state.page == 'home':
    st.markdown(f'<div class="header-box"><h2>أهلاً بك: {st.session_state.user_name}</h2></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة مبيعات جديدة", use_container_width=True):
        st.session_state.page = 'order'
        st.session_state.temp_items = []
        st.rerun()

elif st.session_state.page == 'order':
    st.markdown('<h3 style="text-align:center;">إعداد فاتورة مبيعات</h3>', unsafe_allow_html=True)
    
    # --- قسم اختيار الزبون (بحث ذكي مخصص للمندوب) ---
    my_customers = load_rep_customers(st.session_state.user_name)
    search_cust = st.text_input("🔍 ابحث عن اسم الزبون...")
    filtered_cust = [c for c in my_customers if search_cust in c] if search_cust else my_customers
    cust_name = st.selectbox("اختر الزبون من القائمة", ["-- اختر --"] + filtered_cust)
    
    disc_val = st.number_input("الحسم %", min_value=0.0, max_value=100.0, value=0.0)
    
    st.divider()
    
    # --- قسم إضافة الأصناف ---
    prods = load_products()
    search_p = st.text_input("🔍 ابحث عن صنف...")
    filtered_p = [p for p in prods.keys() if search_p in p] if search_p else list(prods.keys())
    sel_p = st.selectbox("الصنف", ["-- اختر --"] + filtered_p)
    qty = st.number_input("الكمية", min_value=1, value=1)
    
    if st.button("➕ إضافة للفاتورة"):
        if sel_p != "-- اختر --":
            st.session_state.temp_items.append({"الصنف": sel_p, "العدد": qty, "السعر": prods[sel_p]})
            st.success(f"تم إضافة {sel_p}")

    # --- عرض المعاينة المحاسبية ---
    if st.session_state.temp_items:
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        discount_amt = raw_total * (disc_val / 100)
        total_after_disc = raw_total - discount_amt
        
        # حساب VAT 11% على الأصناف التي تحتوي على * بعد الحسم
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - disc_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat

        st.markdown(f"""
            <div class="invoice-preview">
                <div class="company-header">
                    <div class="company-name">شركة حلباوي إخوان ش.م.م</div>
                    <div class="company-details">لبنان - بيروت - الرويس | هاتف: 01556058</div>
                    <div class="invoice-title">فاتورة مبيعات</div>
                </div>
                <div style="margin-bottom:10px;"><b>الزبون:</b> {cust_name}</div>
                <table class="styled-table">
                    <tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>
                    {"".join([f'<tr><td>{x["الصنف"]}</td><td>{x["العدد"]}</td><td>{x["السعر"]:.2f}</td><td>{x["العدد"]*x["السعر"]:.2f}</td></tr>' for x in st.session_state.temp_items])}
                </table>
                <div class="summary-row"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                <div class="summary-row"><span>الحسم ({disc_val}%):</span><span>-${discount_amt:,.2f}</span></div>
                <div class="summary-row" style="font-weight:bold;"><span>المجموع بعد الحسم:</span><span>${total_after_disc:,.2f}</span></div>
                <div class="summary-row"><span>الضريبة VAT (11%):</span><span>+${total_vat:,.2f}</span></div>
                <div class="total-final">الإجمالي الصافي: ${final_net:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🖨️ طباعة وحفظ"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    if st.button("🔙 العودة للرئيسية"):
        st.session_state.page = 'home'
        st.rerun()
