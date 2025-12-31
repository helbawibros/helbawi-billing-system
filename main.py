import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    div[data-testid="InputInstructions"] { display: none !important; }
    div[data-baseweb="helper-text"] { display: none !important; }
    
    @media print {
        .no-print { display: none !important; }
        body { background-color: white !important; }
    }

    .styled-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 16px; text-align: center; }
    .styled-table th { background-color: #1E3A8A; color: #ffffff; padding: 8px; border: 1px solid #ddd; }
    .styled-table td { padding: 8px; border: 1px solid #ddd; }
    
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 15px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 16px; border-bottom: 1px solid #eee; }
    .highlight-row { background-color: #f8f9fa; font-weight: bold; color: #1E3A8A; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 20px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات ---
PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ارز مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(10000, 99999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 3. الواجهة ---
st.markdown(f'<h3 class="no-print" style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
cust = st.text_input("اسم الزبون (المحل)")
cust_id = st.text_input("رقم الزبون")
disc_perc = st.text_input("الحسم %", value="0")

st.divider()
search = st.text_input("🔍 ابحث عن صنف...")
filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
qty_str = st.text_input("العدد")

if st.button("➕ إضافة للصنف", use_container_width=True):
    if sel_p != "-- اختر الصنف --" and qty_str != "":
        q = float(convert_ar_nav(qty_str))
        st.session_state.temp_items.append({"الصنف": sel_p, "العدد": int(q), "السعر": PRODUCTS[sel_p]})
        st.session_state.confirmed = False
        st.rerun()

if st.button("✅ ثبت الفاتورة", use_container_width=True, type="primary"):
    st.session_state.confirmed = True

if st.session_state.confirmed and st.session_state.temp_items:
    st.markdown("<hr class='no-print'>", unsafe_allow_html=True)
    
    # رأس الفاتورة
    now_date = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div style="text-align: right;">
                <p><b>الزبون:</b> {cust}<br><b>رقم الزبون:</b> {cust_id}<br><b>التاريخ:</b> {now_date}</p>
            </div>
            <div style="text-align: left;"><p><b>المندوب:</b> {st.session_state.get('user_name', 'محمد')}</p></div>
        </div>
    """, unsafe_allow_html=True)

    # حسابات الجدول والضرائب
    h_val = float(convert_ar_nav(disc_perc)) if disc_perc else 0
    raw_total = sum(i["العدد"] * i["السعر"] for i in st.session_state.temp_items)
    discount_amt = raw_total * (h_val / 100)
    total_after_disc = raw_total - discount_amt
    
    # حساب الضريبة بعد الحسم للأصناف المحددة بنجمة
    total_vat = 0
    table_html = '<table class="styled-table"><tr><th>الصنف</th><th>العدد</th><th>السعر</th><th>الإجمالي</th></tr>'
    for item in st.session_state.temp_items:
        line_total = item["العدد"] * item["السعر"]
        # حساب حصة هذا الصنف من الحسم لخصمها قبل حساب الضريبة
        line_after_disc = line_total * (1 - (h_val / 100))
        if "*" in item["الصنف"]:
            total_vat += line_after_disc * 0.11
        table_html += f'<tr><td>{item["الصنف"]}</td><td>{item["العدد"]}</td><td>{item["السعر"]:.2f}</td><td>{line_total:.2f}</td></tr>'
    table_html += '</table>'
    st.markdown(table_html, unsafe_allow_html=True)

    final_net = total_after_disc + total_vat

    st.markdown(f"""
        <div class="summary-container">
            <div class="summary-row"><span>المجموع (قبل الحسم):</span><span>${raw_total:,.2f}</span></div>
            <div class="summary-row"><span>قيمة الحسم ({h_val}%):</span><span>-${discount_amt:,.2f}</span></div>
            <div class="summary-row highlight-row"><span>المجموع بعد الحسم:</span><span>${total_after_disc:,.2f}</span></div>
            <div class="summary-row"><span>VAT (11% بعد الحسم):</span><span>+${total_vat:,.2f}</span></div>
            <div class="final-total">الصافي النهائي: ${final_net:,.2f}</div>
            <div class="lbp-box">VAT بالليرة (89,500): {int(total_vat * 89500):,} ل.ل.</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_save, col_print = st.columns(2)
    with col_save: st.button("💾 حفظ وإرسال", use_container_width=True)
    with col_print:
        if st.button("🖨️ طباعة", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

