import streamlit as st
import pandas as pd
import random

# --- 1. إعدادات وتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; }
    .total-box { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-top: 10px; }
    th { background-color: #f0f2f6 !important; color: black !important; text-align: center !important; }
    td { text-align: center !important; border-bottom: 1px solid #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات والأصناف المحددة ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20,
    "حمص٩ ٩٠٧ غ": 2.00,
    "عدس مجروش ٩٠٧غ": 1.75,
    "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75,
    "ازر مصري ٩٠٧غ": 1.15,
    "ارز ايطالي ٩٠٧ غ": 2.25,
    "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00,
    "*بهار كبسه٥٠غ*١٢": 10.00,
    "*بهار سمك٥٠غ*١٢": 8.00
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))
if 'show_table' not in st.session_state: st.session_state.show_table = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 3. نظام الصفحات ---

# صفحة الدخول
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in = True
            st.session_state.user_name = user
            st.session_state.page = 'home'
            st.rerun()

# الصفحة الرئيسية
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page = 'order'
        st.rerun()

# صفحة الفاتورة
elif st.session_state.page == 'order':
    st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    cust = st.text_input("الزبون", placeholder="اسم المحل")
    
    st.divider()
    
    search = st.text_input("🔍 بحث عن صنف")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر --"] + filtered)
    qty = st.text_input("العدد", value="1")

    col_add, col_fix = st.columns(2)
    with col_add:
        if st.button("➕ إضافة للصنف", use_container_width=True):
            if sel_p != "-- اختر --":
                q = float(convert_ar_nav(qty))
                price = PRODUCTS[sel_p]
                # حساب الضريبة 11% للأصناف المحددة بنجمة
                vat = (price * q * 0.11) if "*" in sel_p else 0.0
                total = (price * q) + vat
                
                st.session_state.temp_items.append({
                    "الصنف": sel_p,
                    "العدد": q,
                    "السعر": f"{price:.2f}",
                    "VAT": f"{vat:.2f}",
                    "الإجمالي": f"{total:.2f}"
                })
                st.toast(f"تمت إضافة {sel_p}")

    with col_fix:
        if st.button("✅ ثبت", use_container_width=True, type="primary"):
            st.session_state.show_table = True

    # عرض الجدول عند الضغط على ثبت
    if st.session_state.show_table and st.session_state.temp_items:
        st.divider()
        st.markdown(f"**الزبون:** {cust}")
        df = pd.DataFrame(st.session_state.temp_items)
        st.table(df)
        
        total_sum = sum(float(item["الإجمالي"]) for item in st.session_state.temp_items)
        st.markdown(f'<div class="total-box">الصافي النهائي: ${total_sum:.2f}</div>', unsafe_allow_html=True)
        
        if st.button("💾 حفظ وإرسال", use_container_width=True):
            st.success("تم الحفظ بنجاح")

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.session_state.show_table = False
        st.rerun()
