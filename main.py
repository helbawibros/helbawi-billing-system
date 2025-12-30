import streamlit as st
import requests
import urllib.parse

# 1. إعدادات الصفحة والسرعة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

# الرابط السحري الخاص بك للحفظ في الإكسل
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

# كلمات سر المناديب
USERS = {
    "حسين": "1234",
    "علي": "5566",
    "مدير": "admin77"
}

# --- التنسيقات (CSS) ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
    .stButton>button { border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# إدارة الصفحات والدخول
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 🔐 شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المناديب</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("اختر اسمك", list(USERS.keys()))
    password_input = st.text_input("أدخل كلمة المرور", type="password")
    
    if st.button("دخول", use_container_width=True):
        if USERS[user_choice] == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# --- 🚀 بعد تسجيل الدخول ---
else:
    st.sidebar.markdown(f"### 👤 المندوب: {st.session_state.user_name}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h1>شركة حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌾 قسم الحبوب", use_container_width=True):
                st.session_state.page = 'grains'
                st.rerun()
        with col2:
            if st.button("🌶️ قسم البهارات", use_container_width=True):
                st.session_state.page = 'spices'
                st.rerun()

    # --- نموذج الحبوب (مثال مطور) ---
    elif st.session_state.page == 'grains':
        st.markdown('<div class="header-box"><h2>📦 طلبية حبوب جديدة</h2></div>', unsafe_allow_html=True)
        customer = st.text_input("👤 إسم الزبون:")
        
        items = ["حمص رقم 12", "حمص رقم 9", "فول حب", "عدس", "فاصوليا"]
        order_data = []

        for item in items:
            c1, c2 = st.columns([2, 1])
            with c1:
                price = st.number_input(f"سعر {item}", min_value=0.0, key=f"p_{item}")
            with c2:
                qty = st.number_input(f"كمية {item}", min_value=0, step=1, key=f"q_{item}")
            
            if qty > 0 and price > 0:
                order_data.append({"item": item, "price": price, "qty": qty, "total": price * qty})

        st.divider()
        
        if st.button("✅ حفظ في الإكسل وإرسال", use_container_width=True):
            if customer and order_data:
                success_count = 0
                for entry in order_data:
                    payload = {
                        "total": entry['total'],
                        "price": entry['price'],
                        "qty": entry['qty'],
                        "item": entry['item'],
                        "customer": customer,
                        "user": st.session_state.user_name,
                        "inv_no": str(random.randint(1000, 9999))
                    }
                    response = requests.post(URL_LINK, json=payload)
                    if response.status_code == 200:
                        success_count += 1
                
                if success_count > 0:
                    st.balloons()
                    st.success(f"✅ تم حفظ {success_count} أصناف في ملف الإكسل!")
            else:
                st.warning("يرجى إدخال اسم الزبون والكميات والأسعار")

        if st.button("🔙 عودة للقائمة"):
            st.session_state.page = 'home'
            st.rerun()
