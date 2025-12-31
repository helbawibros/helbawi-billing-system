import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق المتطور ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    div[data-testid="InputInstructions"] { display: none !important; }
    div[data-baseweb="helper-text"] { display: none !important; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    /* تنسيق الطباعة والفاتورة */
    @media print {
        .no-print { display: none !important; }
        body { background-color: white !important; }
        .invoice-print { border: none !important; width: 100% !important; }
    }

    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 16px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 8px; border: 1px solid #ddd; }
    .styled-table td { padding: 8px; border: 1px solid #ddd; }
    
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 15px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 16px; border-bottom: 1px solid #eee; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 20px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات والأصناف ---
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

# --- 3. نظام الصفحات ---

if not st.session_state.logged_in:
    st.markdown('<div class="header-box no-print"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.page = True, user_sel, 'home'
            st.rerun()

elif st.session_state.page == 'home':
    st.markdown('<div class="header-box no-print"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="no-print" style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed = 'order', [], False
        st.rerun()

elif st.session_state.page == 'order':
    with st.container():
        st.markdown(f'<h3 class="no-print" style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
        cust = st.text_input("اسم الزبون (المحل)", key="c_name")
        cust_id = st.text_input("رقم الزبون", key="c_id")
        disc_input = st.text_input("الحسم %", value="0", key="d_in")

        st.divider()
        search = st.text_input("🔍 ابحث عن صنف...", key="s_box")
        filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
        sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
        qty_str = st.text_input("العدد", key="q_box")

        col_add, col_fix = st.columns(2)
        with col_add:
            if st.button("➕ إضافة للصنف", use_container_width=True):
                if sel_p != "-- اختر الصنف --" and qty_str != "":
                    q = float(convert_ar_nav(qty_str))
                    price = PRODUCTS[sel_p]
                    vat = (price * q * 0.11) if "*" in sel_p else 0.0
                    total = (price * q) + vat
                    st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": price, "VAT": vat, "الإجمالي": total})
                    st.session_state.confirmed = False
                    st.toast(f"تمت إضافة {sel_p}")

        with col_fix:
            if st.button("✅ ثبت", use_container_width=True, type="primary"):
                st.session_state.confirmed = True

    if st.session_state.confirmed and st.session_state.temp_items:
        st.markdown("<hr class='no-print'>", unsafe_allow_html=True)
        
        # --- رأس الفاتورة المعدل ---
        now_date = datetime.now().strftime("%Y-%m-%d")
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                <div style="text-align: right;">
                    <p style="margin: 0;"><b>الزبون:</b> {cust}</p>
                    <p style="margin: 0;"><b>رقم الزبون:</b> {cust_id}</p>
                    <p style="margin: 0;"><b>التاريخ:</b> {now_date}</p>
                </div>
                <div style="text-align: left;">
                    <p style="margin: 0;"><b>المندوب:</b> {st.session_state.user_name}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # الجدول
        table_html = '<table class="styled-table"><tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>VAT</th><th>الإجمالي</th></tr>'
        for item in st.session_state.temp_items:
            table_html += f'<tr><td>{item["الصنف"]}</td><td>{item["العدد"]}</td><td>{item["السعر"]:.2f}</td><td>{item["VAT"]:.2f}</td><td>{item["الإجمالي"]:.2f}</td></tr>'
        table_html += '</table>'
        st.markdown(table_html, unsafe_allow_html=True)

        # الحسابات
        raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
        h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
        discount_amount = raw_total * (h_val / 100)
        total_vat = sum(i["VAT"] for i in st.session_state.temp_items)
        final_net = (raw_total - discount_amount) + total_vat
        
        st.markdown(f"""
            <div class="summary-container">
                <div class="summary-row"><span>المجموع:</span><span>${raw_total:,.2f}</span></div>
                <div class="summary-row"><span>الحسم ({h_val}%):</span><span>-${discount_amount:,.2f}</span></div>
                <div class="summary-row"><span>VAT:</span><span>+${total_vat:,.2f}</span></div>
                <div class="final-total">الصافي النهائي: ${final_net:,.2f}</div>
                <div class="lbp-box">VAT بالليرة (89,500): {int(total_vat * 89500):,} ل.ل.</div>
            </div>
        """, unsafe_allow_html=True)
        
        # أزرار الحفظ والطباعة
        col_save, col_print = st.columns(2)
        with col_save:
            if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
                st.success("✅ تم الحفظ بنجاح!")
        with col_print:
            if st.button("🖨️ طباعة الفاتورة", use_container_width=True):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    if st.button("🔙 عودة للرئيسية", key="back_btn", help="no-print"):
        st.session_state.page = 'home'
        st.rerun()
