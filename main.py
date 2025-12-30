import streamlit as st
import requests
import random

# 1. إعدادات الصفحة - وضعنا الـ layout="centered" لمنع تداخل القوائم الجانبية
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

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

# --- التنسيقات (CSS) المحدثة ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    /* تصحيح مشكلة النصوص الجانبية */
    .stApp { overflow: hidden; }
    
    .header-box { 
        background-color: #1E3A8A; 
        color: white; 
        text-align: center; 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
    }
    .welcome-container { text-align: center; margin: 20px 0; }
    
    /* تصغير الخط ليكون على سطر واحد */
    .welcome-text { 
        font-size: 22px; 
        color: #1E3A8A; 
        font-weight: 800; 
        white-space: nowrap; 
    }
    .blessing-text { 
        font-size: 18px; 
        color: #2e7d32; 
        font-weight: 600;
        margin-top: 5px;
    }
    .preview-box { background-color: #f8f9fa; border: 2px solid #1E3A8A; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 🔐 شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المناديب</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("إختر اسمك", ["-- اختر اسمك --"] + list(USERS.keys()))
    password_input = st.text_input("كلمة السر", type="password")
    
    if st.button("دخول", use_container_width=True):
        if user_choice != "-- اختر اسمك --" and USERS[user_choice] == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# --- 🚀 الصفحة الرئيسية بعد الدخول ---
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
        
        # الترحيب المصغر على سطر واحد
        st.markdown(f"""
            <div class="welcome-container">
                <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
                <div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 تسجيل الطلبية", use_container_width=True, type="primary"):
            st.session_state.page = 'order_page'
            st.rerun()
            
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- صفحة الطلبية ---
    elif st.session_state.page == 'order_page':
        st.markdown('<div class="header-box"><h3>📝 تسجيل طلبية جديدة</h3></div>', unsafe_allow_html=True)
        customer = st.text_input("👤 اسم الزبون:")
        inv_no = st.text_input("📄 رقم الفاتورة", value=str(random.randint(10000, 99999)))

        st.divider()
        items = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول حب 1000غ", "عدس مجروش", "فلفل أسود", "كمون"]
        order_list = []

        for item in items:
            col_item, col_p, col_q = st.columns([2, 1, 1])
            with col_item: st.write(f"**{item}**")
            with col_p: p = st.number_input("السعر", min_value=0.0, key=f"p_{item}", label_visibility="collapsed")
            with col_q: q = st.number_input("الكمية", min_value=0, step=1, key=f"q_{item}", label_visibility="collapsed")
            if q > 0 and p > 0:
                order_list.append({"الصنف": item, "السعر": p, "الكمية": q, "الإجمالي": p * q})

        if order_list and customer:
            st.divider()
            if st.button("👁️ معاينة الفاتورة", use_container_width=True):
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.table(order_list)
                total = sum(d['الإجمالي'] for d in order_list)
                st.markdown(f"#### 💰 الصافي النهائي: {total:,.0f} ل.ل")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 تأكيد وحفظ نهائي", use_container_width=True):
                with st.spinner("جاري الحفظ..."):
                    for entry in order_list:
                        payload = {"total": entry['الإجمالي'], "price": entry['السعر'], "qty": entry['الكمية'], "item": entry['الصنف'], "customer": customer, "inv_no": inv_no, "user": st.session_state.user_name}
                        requests.post(URL_LINK, json=payload)
                st.balloons()
                st.success("✅ تم الحفظ بنجاح")
                st.session_state.page = 'home'

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
