import streamlit as st
import pandas as pd
import random

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px; }
    .welcome-container { text-align: center; margin: 20px 0; }
    .welcome-text { font-size: 22px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    .total-box { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; }
    th { background-color: #1E3A8A !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات وإدارة الحالة ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 3. نظام الصفحات ---

# أ- صفحة تسجيل الدخول
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
        else:
            st.error("❌ كلمة السر خاطئة")

# ب- الصفحة الرئيسية (بركة الصلاة)
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
            <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page = 'order'
        st.rerun()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ج- صفحة الطلبية (الجدول والكبسات)
elif st.session_state.page == 'order':
    st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    
    cust_name = st.text_input("الزبون", placeholder="اسم المحل")
    discount = st.text_input("حسم %", value="0")
    
    st.divider()
    
    # اختيار الصنف والعدد
    all_p = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "سبع بهارات 50غ"]
    search = st.text_input("🔍 ابحث عن صنف...")
    filtered = [p for p in all_p if search in p] if search else all_p
    sel_p = st.selectbox("اختر الصنف", ["-- اختر --"] + filtered)
    qty = st.text_input("العدد", value="1")

    # كبسات الإضافة والتثبيت بجانب بعضها
    col_add, col_fix = st.columns(2)
    with col_add:
        add_btn = st.button("➕ إضافة للصنف", use_container_width=True)
    with col_fix:
        fix_btn = st.button("✅ ثبت", use_container_width=True, type="primary")

    if add_btn:
        if sel_p != "-- اختر --" and cust_name != "":
            q = float(convert_ar_nav(qty))
            price = 2.25 # افتراضي
            st.session_state.temp_items.append({
                "الرقم": len(st.session_state.temp_items) + 1,
                "الصنف": sel_p,
                "العدد": q,
                "السعر": price,
                "الإجمالي": q * price
            })
            st.success(f"تمت إضافة {sel_p}")

    if fix_btn:
        st.info("تم تثبيت البيانات الحالية")

    st.divider()

    # الجدول تحت الكبسات
    if st.session_state.temp_items:
        st.markdown(f"**الزبون:** {cust_name}")
        df = pd.DataFrame(st.session_state.temp_items)
        st.table(df)
        
        total_sum = sum(item["الإجمالي"] for item in st.session_state.temp_items)
        st.markdown(f'<div class="total-box">الصافي النهائي: ${total_sum:.2f}</div>', unsafe_allow_html=True)

        if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
            st.success("تم الإرسال بنجاح")

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.rerun()
