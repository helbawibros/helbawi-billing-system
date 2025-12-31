import streamlit as st
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

# دالة تحويل الأرقام العربية
def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيق "الحديدي" لمنع كسر السطور
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* إجبار الأعمدة على البقاء بجانب بعضها مهما صغر العرض */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    div[data-testid="column"] {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }
    
    /* تنسيق رقم الفاتورة في الوسط */
    .invoice-header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #fff; }
    
    /* تصغير المسافات بين العناصر لتبدو مثل الجدول */
    .stTextInput, .stSelectbox, .stNumberInput { margin-bottom: -15px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

# --- الصفحة الأولى: دخول المندوبين ---
if not st.session_state.logged_in:
    st.markdown('<h2 style="text-align:center;">🔐 دخول المندوبين</h2>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user
            st.rerun()

# --- الصفحة الثانية: الترحيب ---
elif st.session_state.page == 'home':
    st.markdown(f'<h3 style="text-align:center;">أهلاً بك سيد {st.session_state.user_name}</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#2e7d32;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</p>', unsafe_allow_html=True)
    if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
        st.session_state.page = 'order_page'
        st.rerun()
    if st.button("🚪 خروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- الصفحة الثالثة: صفحة الطلبية (التابلو الحقيقي) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<div class="invoice-header">رقم الفاتورة: {st.session_state.inv_no}</div>', unsafe_allow_html=True)

    # السطر 1: الزبون (80%) والحسم (20%)
    c1, c2 = st.columns([4, 1])
    with c1:
        cust = st.text_input("", placeholder="اسم الزبون (المحل)", label_visibility="collapsed")
    with c2:
        disc = st.text_input("", placeholder="%حسم", label_visibility="collapsed")

    st.write("---")

    # السطر 2: الصنف والكمية
    all_p = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "فلفل اسود"]
    c3, c4 = st.columns([4, 1])
    with c3:
        search_val = st.text_input("", placeholder="🔍 ابحث عن صنف...", label_visibility="collapsed")
        # فلترة الأصناف بناءً على البحث
        filtered = [p for p in all_p if search_val in p] if search_val else all_p
        sel_p = st.selectbox("", ["-- اختر الصنف --"] + filtered, label_visibility="collapsed")
    with c4:
        qty = st.text_input("", value="1", placeholder="العدد", label_visibility="collapsed")

    if st.button("➕ إضافة للصنف", use_container_width=True):
        if sel_p != "-- اختر الصنف --" and cust:
            st.session_state.temp_items.append({
                "الصنف": sel_p, 
                "الكمية": convert_ar_nav(qty),
                "السعر": 2.5, # تجريبي
                "الإجمالي": float(convert_ar_nav(qty)) * 2.5
            })
            st.success("تمت الإضافة")

    # عرض الجدول (التابلو)
    if st.session_state.temp_items:
        df = pd.DataFrame(st.session_state.temp_items)
        st.table(df[["الصنف", "الكمية", "الإجمالي"]])

    if st.button("🔙 عودة"):
        st.session_state.page = 'home'
        st.rerun()
