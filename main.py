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

# 3. التنسيق "الحديدي" (CSS) لضمان السطر الواحد وإعادة البركة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; }
    .welcome-container { text-align: center; margin: 15px 0; }
    .welcome-text { font-size: 20px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    
    /* تنسيق الجداول لتكون سطراً واحداً إجبارياً */
    .custom-table { width: 100%; border-collapse: collapse; }
    .custom-table td { padding: 5px; vertical-align: bottom; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

# --- الصفحة الأولى: دخول المندوبين ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name = True, user
            st.rerun()

# --- الصفحة الثانية: الترحيب (إعادة بركة الصلاة) ---
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
            <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
        st.session_state.page = 'order_page'
        st.rerun()
    if st.button("🚪 خروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- الصفحة الثالثة: صفحة الطلبية (التابلو الذي طلبته) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)

    # السطر الأول: زبون (عريض) وحسم (صغير) في سطر واحد حقيقي
    c1, c2 = st.columns([4, 1.2])
    with c1:
        cust = st.text_input("الزبون", placeholder="اسم المحل", label_visibility="visible")
    with c2:
        disc = st.text_input("حسم %", value="0")

    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

    # السطر الثاني: صنف (عريض) وعدد (صغير)
    all_p = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "فلفل اسود"]
    
    # بحث الصنف
    search_val = st.text_input("🔍 ابحث عن صنف...")
    filtered = [p for p in all_p if search_val in p] if search_val else all_p
    
    c3, c4 = st.columns([4, 1.2])
    with c3:
        sel_p = st.selectbox("اختر الصنف", ["-- اختر --"] + filtered)
    with c4:
        qty = st.text_input("العدد", value="1")

    if st.button("➕ إضافة للصنف", use_container_width=True):
        if sel_p != "-- اختر --" and cust:
            st.session_state.temp_items.append({"الصنف": sel_p, "الكمية": convert_ar_nav(qty)})
            st.success("تمت الإضافة")

    if st.session_state.temp_items:
        st.table(pd.DataFrame(st.session_state.temp_items))

    if st.button("🔙 عودة للرئيسية"):
        st.session_state.page = 'home'
        st.rerun()
