import streamlit as st
import pandas as pd
import random

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# 2. قاعدة بيانات المناديب الثابتة
USERS = {
    "محمد الحسيني": "8822", 
    "علي دوغان": "5500", 
    "عزات حلاوي": "6611", 
    "علي حسين حلباوي": "4455", 
    "محمد حسين حلباوي": "3366", 
    "احمد حسين حلباوي": "7722", 
    "علي محمد حلباوي": "6600"
}

# دالة تحويل الأرقام لضمان الحسابات
def convert_ar_nav(text):
    if not isinstance(text, str): return text
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيقات (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px; }
    .welcome-container { text-align: center; margin: 20px 0; }
    .welcome-text { font-size: 22px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة حالة التطبيق
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

# --- الصفحة الأولى: دخول المندوبين ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("إختر اسمك", ["-- اختر اسمك --"] + list(USERS.keys()))
    password_input = st.text_input("كلمة السر", type="password")
    
    if st.button("دخول", use_container_width=True):
        if user_choice != "-- اختر اسمك --" and USERS.get(user_choice) == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# --- الصفحة الثانية: الترحيب ---
elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
            <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبية</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 تسجيل الفاتورة", use_container_width=True, type="primary"):
        st.session_state.page = 'order_page'
        st.rerun()
            
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- الصفحة الثالثة: صفحة الطلبية (بالصيغة المعتمدة) ---
elif st.session_state.page == 'order_page':
    st.markdown(f'<h2 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h2>', unsafe_allow_html=True)
    st.divider()

    # قسم الزبون والحسم
    cust_name = st.text_input("الزبون", placeholder="اسم المحل")
    discount_val = st.text_input("حسم %", value="0")

    st.divider()

    # قسم الصنف والبحث
    all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "عدس", "بهار"]
    search_prod = st.text_input("🔍 ابحث عن صنف...")
    filtered_prod = [p for p in all_products if search_prod in p] if search_prod else all_products
    selected_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered_prod)
    
    qty_input = st.text_input("العدد", value="1")

    if st.button("➕ إضافة للصنف", use_container_width=True):
        if selected_p != "-- اختر الصنف --" and cust_name != "":
            qty_clean = convert_ar_nav(qty_input)
            st.session_state.temp_items.append({
                "الصنف": selected_p, 
                "الكمية": qty_clean,
                "الإجمالي": float(qty_clean) * 2.5 # السعر الافتراضي حتى ربط الملف
            })
            st.success(f"تمت إضافة {selected_p}")
        else:
            st.warning("يرجى التأكد من اسم الزبون واختيار الصنف")

    # عرض جدول الأصناف المضافة
    if st.session_state.temp_items:
        st.write("### الأصناف المضافة:")
        st.table(pd.DataFrame(st.session_state.temp_items))

    if st.button("🔙 عودة للرئيسية", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

