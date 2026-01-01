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
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    @media print {
        .no-print { display: none !important; }
        .stButton, .stTextInput, .stSelectbox { display: none !important; }
    }

    .invoice-preview { background-color: white; padding: 25px; border: 2px solid #1E3A8A; border-radius: 10px; color: black; }
    
    /* تنسيق الهيدر الجديد: اسم الشركة بالنص */
    .company-header-center { text-align: center; border-bottom: 2px double #1E3A8A; padding-bottom: 10px; margin-bottom: 10px; }
    .company-name { font-size: 28px; font-weight: 800; color: black; }
    .company-details { font-size: 16px; color: black; }
    
    /* عنوان الفاتورة ورقمها تحته */
    .invoice-title-section { text-align: center; margin: 15px 0; }
    .invoice-main-title { font-size: 24px; font-weight: bold; color: #1E3A8A; text-decoration: underline; }
    .invoice-no-small { font-size: 14px; color: #333; margin-top: 5px; }
    
    .invoice-info-row { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }
    .cust-right { text-align: right; font-size: 22px; font-weight: 800; }
    .meta-left { text-align: left; font-size: 12px; color: #333; line-height: 1.3; }
    
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 15px; text-align: center; color: black; }
    .styled-table th { background-color: #f0f2f6; border: 1px solid #000; padding: 8px; }
    .styled-table td { border: 1px solid #000; padding: 8px; }
    
    .summary-section { margin-top: 15px; width: 100%; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 10px; font-size: 16px; border-bottom: 1px solid #ddd; }
    .total-final { background-color: #d4edda; font-size: 22px; font-weight: 800; color: #155724; border: 2px solid #c3e6cb; margin-top: 10px; padding: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الربط ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"
GID_DATA = "0"
GID_CUSTOMERS = "155973706" 

@st.cache_data(ttl=60)
def load_products():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df = pd.read_csv(url)
        return pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    except: return {}

PRODUCTS = load_products()

# --- إدارة الجلسة ---
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'search_val' not in st.session_state: st.session_state.search_val = ""

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- واجهة الدخول (مختصرة للسرعة) ---
if not st.session_state.logged_in:
    # (كود الدخول نفسه الذي تستخدمه)
    st.session_state.logged_in = True # للتجربة فقط
    st.session_state.user_name = "عبد الكريم حوراني"

# --- واجهة الطلب ---
st.markdown('<div class="no-print header-box"><h2>تسجيل فاتورة</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    cust = st.text_input("اسم الزبون")
with col2:
    disc_input = st.text_input("الحسم %", value="0")

st.divider()

# ميزة تصفير البحث: نستخدم key من session_state
search_p = st.text_input("🔍 ابحث عن صنف...", value=st.session_state.search_val, key="prod_search")
filtered_p = [p for p in PRODUCTS.keys() if search_p in p] if search_p else list(PRODUCTS.keys())
sel_p = st.selectbox("اختر الصنف", ["-- اختر --"] + filtered_p)
qty_str = st.text_input("العدد")

if st.button("➕ إضافة صنف"):
    if sel_p != "-- اختر --" and qty_str:
        st.session_state.temp_items.append({
            "الصنف": sel_p, 
            "العدد": int(convert_ar_nav(qty_str)), 
            "السعر": PRODUCTS[sel_p]
        })
        # تصفير قيمة البحث في الجلسة
        st.session_state.search_val = "" 
        st.rerun()

if st.session_state.temp_items:
    h_val = float(convert_ar_nav(disc_input))
    raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
    discount_amt = raw_total * (h_val / 100)
    total_after_disc = raw_total - discount_amt
    total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
    final_net = total_after_disc + total_vat

    # --- تصميم الفاتورة المطلوب ---
    st.markdown(f"""
        <div class="invoice-preview">
            <div class="company-header-center">
                <div class="company-name">شركة حلباوي إخوان ش.م.م</div>
                <div class="company-details">بيروت - الرويس | 03/220893 - 01/556058</div>
            </div>
            
            <div class="invoice-title-section">
                <div class="invoice-main-title">فاتورة مبيعات</div>
                <div class="invoice-no-small">الرقم: #99764</div>
            </div>

            <div class="invoice-info-row">
                <div class="cust-right">الزبون: {cust}</div>
                <div class="meta-left">
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
                <div class="summary-row"><span>الحسم ({h_val}%):</span><span>-${discount_amt:,.2f}</span></div>
                <div class="summary-row" style="font-weight:bold; color:#1E3A8A;"><span>المجموع بعد الحسم:</span><span>${total_after_disc:,.2f}</span></div>
                <div class="summary-row"><span>الضريبة (VAT 11%):</span><span>+${total_vat:,.2f}</span></div>
                <div class="total-final">الإجمالي الصافي: ${final_net:,.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
