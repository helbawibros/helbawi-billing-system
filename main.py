import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات الصفحة والتنسيق ---
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

    /* تنسيق جدول الفاتورة */
    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 16px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 8px; border: 1px solid #ddd; }
    .styled-table td { padding: 8px; border: 1px solid #ddd; }
    
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 10px; font-size: 16px; border-bottom: 1px solid #eee; }
    .highlight-blue { color: #1E3A8A; font-weight: bold; font-size: 18px; }
    .final-total-box { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 20px; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center; border: 1px solid #c3e6cb; }
    
    /* تنسيق الإيصال الجديد للطابعة الحرارية */
    .thermal-receipt { 
        width: 100%; 
        max-width: 300px; 
        margin: 0 auto; 
        padding: 10px; 
        border: 1px solid #eee; 
        text-align: center;
    }
    .receipt-header { font-size: 22px; font-weight: 800; margin-bottom: 2px; }
    .receipt-sub { font-size: 14px; margin-bottom: 10px; line-height: 1.2; }
    .receipt-title { font-size: 20px; font-weight: bold; margin: 15px 0; border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding: 5px 0; }
    .receipt-body { text-align: right; font-size: 17px; line-height: 1.6; margin-bottom: 20px; }
    .receipt-footer { font-size: 14px; border-top: 1px solid #eee; padding-top: 10px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة الإرسال ---
def send_to_google_sheets(vat, total_pre, inv_no, customer, representative, date_time):
    url = "https://script.google.com/macros/s/AKfycbzi3kmbVyg_MV1Nyb7FwsQpCeneGVGSJKLMpv2YXBJR05v8Y77-Ub2SpvViZWCCp1nyqA/exec"
    data = {"vat_value": vat, "total_before": total_pre, "invoice_no": inv_no, "cust_name": customer, "rep_name": representative, "date_full": date_time}
    try:
        requests.post(url, data=data, timeout=10)
        return True
    except: return False

# --- 3. قاعدة البيانات ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}
PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ارز مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False
if 'receipt_view' not in st.session_state: st.session_state.receipt_view = False
if 'is_sent' not in st.session_state: st.session_state.is_sent = False

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
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed, st.session_state.receipt_view, st.session_state.is_sent = 'order', [], False, False, False
        st.session_state.inv_no = str(random.randint(10000, 99999))
        st.rerun()

elif st.session_state.page == 'order':
    
    if st.session_state.receipt_view:
        # حساب المجموع الصافي للإيصال
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(st.session_state.get('last_disc', '0')))
        total_after_disc = raw_total * (1 - h_val/100)
        total_vat = sum(((i["العدد"] * i["السعر"]) * (1 - h_val/100)) * 0.11 for i in st.session_state.temp_items if "*" in i["الصنف"])
        final_net = total_after_disc + total_vat
        cust_name = st.session_state.get('last_cust', '..........')
        
        st.markdown(f"""
            <div class="thermal-receipt">
                <div class="receipt-header">شركة حلباوي إخوان ش.م.م</div>
                <div class="receipt-sub">بيروت - الرويس<br>01/556058 - 03/220893</div>
                <div class="receipt-title">إشعار بالاستلام</div>
                <div class="receipt-body">
                    وصلنا من السيد: <b>{cust_name}</b><br>
                    مبلغ وقدره: <b style="font-size: 20px;">${final_net:,.2f}</b><br>
                    وذلك عن فاتورة رقم: #{st.session_state.inv_no}
                </div>
                <div class="receipt-footer">
                    التاريخ: {datetime.now().strftime("%Y-%m-%d | %H:%M")}<br>
                    المندوب: {st.session_state.user_name}
                </div>
            </div>
            <br>
        """, unsafe_allow_html=True)
        
        if st.button("🖨️ طباعة الإيصال", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        if st.button("🔙 العودة للفاتورة", use_container_width=True):
            st.session_state.receipt_view = False
            st.rerun()

    else:
        st.markdown(f'<h2 class="no-print" style="text-align:center; color:#1E3A8A;">رقم الفاتورة: {st.session_state.inv_no}</h2>', unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1: cust = st.text_input("اسم الزبون (المحل)", key="cust_input")
        with col_c2: disc_input = st.text_input("الحسم %", value="0", key="disc_input")
        
        st.session_state.last_cust = cust
        st.session_state.last_disc = disc_input

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
                    st.session_state.confirmed = False
                    st.session_state.clear_counter += 1
                    st.rerun()
        with col_btn2:
            if st.button("✅ تثبيت الفاتورة", use_container_width=True, type="primary"):
                st.session_state.confirmed = True

        if st.session_state.confirmed and st.session_state.temp_items:
            st.markdown("<hr class='no-print'>", unsafe_allow_html=True)
            now_date = datetime.now().strftime("%Y-%m-%d")
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px;"><h2 style="color:#1E3A8A;">رقم الفاتورة: {st.session_state.inv_no}</h2></div>
                <div style="text-align: right; margin-bottom: 20px;">
                    <div style="font-size: 26px; font-weight: bold; color: #1E3A8A;">الزبون: {cust}</div>
                    <div style="font-size: 16px; margin-top: 5px; color: #333;">التاريخ: {now_date}</div>
                    <div style="font-size: 16px; margin-top: 5px; color: #555;">المندوب: {st.session_state.user_name}</div>
                </div>
            """, unsafe_allow_html=True)

            h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
            raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
            discount_amt = raw_total * (h_val / 100)
            total_after_disc = raw_total - discount_amt
            
            total_vat = 0
            table_html = '<table class="styled-table"><tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>VAT</th><th>الإجمالي</th></tr>'
            for item in st.session_state.temp_items:
                line_total = item["العدد"] * item["السعر"]
                line_vat = (line_total * (1 - h_val/100)) * 0.11 if "*" in item["الصنف"] else 0
                total_vat += line_vat
                table_html += f'<tr><td>{item["الصنف"]}</td><td>{item["العدد"]}</td><td>{item["السعر"]:.2f}</td><td>{line_vat:.2f}</td><td>{line_total:.2f}</td></tr>'
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)

            final_net = total_after_disc + total_vat

            st.markdown(f"""
                <div class="summary-container">
                    <div class="summary-row"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                    <div class="summary-row"><span>الحسم ({h_val}%):</span><span>-${discount_amt:,.2f}</span></div>
                    <div class="summary-row highlight-blue"><span>المجموع بعد الحسم:</span><span>${total_after_disc:,.2f}</span></div>
                    <div class="summary-row"><span>الضريبة 11%:</span><span>+${total_vat:,.2f}</span></div>
                    <div class="final-total-box">المجموع الصافي: ${final_net:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col_s, col_p = st.columns(2)
            with col_s:
                if st.button("💾 حفظ وإرسال", use_container_width=True):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    if send_to_google_sheets(f"{total_vat:.2f}", f"{raw_total:.2f}", st.session_state.inv_no, cust, st.session_state.user_name, now_str):
                        st.session_state.is_sent = True
                        st.success("✅ تم الحفظ والإرسال بنجاح!")
                        st.rerun()
            with col_p:
                if st.button("🖨️ طباعة الفاتورة", use_container_width=True, disabled=not st.session_state.is_sent):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

        st.divider()
        col_back, col_rec = st.columns(2)
        with col_back:
            if st.button("🔙 عودة للرئيسية", use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
        with col_rec:
            if st.button("🧾 طباعة إشعار استلام", use_container_width=True):
                st.session_state.receipt_view = True
                st.rerun()
