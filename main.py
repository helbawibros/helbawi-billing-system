import streamlit as st
import requests
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

# الرابط الخاص بك
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

# 2. قاعدة بيانات المناديب
USERS = {
    "محمد الحسيني": "8822",
    "علي دوغان": "5500",
    "عزات حلاوي": "6611",
    "علي حسين حلباوي": "4455",
    "محمد حسين حلباوي": "3366",
    "احمد حسين حلباوي": "7722",
    "علي محمد حلباوي": "6600"
}

# --- التنسيقات (CSS) ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .welcome-text { font-size: 24px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .blessing-text { font-size: 20px; color: #2e7d32; font-style: italic; margin-bottom: 20px; }
    .preview-box { background-color: #f0f2f6; border-right: 5px solid #1E3A8A; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 🔐 شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المناديب</h1></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        user_choice = st.selectbox("إختر اسمك", ["-- اختر مندوباً --"] + list(USERS.keys()))
        password_input = st.text_input("كلمة السر", type="password")
        if st.button("دخول", use_container_width=True):
            if user_choice != "-- اختر مندوباً --" and USERS[user_choice] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_name = user_choice
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")

# --- 🚀 الصفحة الرئيسية بعد الدخول ---
else:
    st.sidebar.write(f"👤 المندوب: **{st.session_state.user_name}**")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h1>شركة حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # العبارات الترحيبية المطلوبة
        st.markdown(f'<div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</div>', unsafe_allow_html=True)
        
        if st.button("🌾 تسجيل طلبية حبوب", use_container_width=True):
            st.session_state.page = 'grains'
            st.rerun()
        if st.button("🌶️ تسجيل طلبية بهارات", use_container_width=True):
            st.session_state.page = 'spices'
            st.rerun()

    # --- نموذج الحبوب ---
    elif st.session_state.page == 'grains':
        st.markdown('<div class="header-box"><h2>📦 طلبية حبوب</h2></div>', unsafe_allow_html=True)
        customer = st.text_input("👤 اسم الزبون:")
        inv_no = st.text_input("📄 رقم الفاتورة", value=str(random.randint(10000, 99999)))

        st.divider()
        # هنا يمكنك إضافة أصنافك الحقيقية
        items = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول حب 1000غ", "فاصوليا"]
        order_list = []

        for item in items:
            col_p, col_q = st.columns([2, 1])
            with col_p:
                price = st.number_input(f"سعر {item}", min_value=0.0, key=f"p_{item}")
            with col_q:
                qty = st.number_input(f"كمية {item}", min_value=0, step=1, key=f"q_{item}")
            if qty > 0 and price > 0:
                order_list.append({"الصنف": item, "السعر": price, "الكمية": qty, "الإجمالي": price * qty})

        if order_list and customer:
            st.divider()
            if st.button("👁️ معاينة الفاتورة للتأكد", use_container_width=True):
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.subheader("🔍 مراجعة البيانات")
                st.table(order_list)
                total_all = sum(d['الإجمالي'] for d in order_list)
                st.markdown(f"### 💰 الصافي النهائي: {total_all:,.0f} ل.ل")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 تأكيد وحفظ في الإكسل", use_container_width=True):
                with st.spinner("جاري الحفظ..."):
                    for entry in order_list:
                        payload = {
                            "total": entry['الإجمالي'], "price": entry['السعر'], "qty": entry['الكمية'],
                            "item": entry['الصنف'], "customer": customer, "inv_no": inv_no, 
                            "user": st.session_state.user_name
                        }
                        requests.post(URL_LINK, json=payload)
                st.balloons()
                st.success("✅ تم الحفظ بنجاح")

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
