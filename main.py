import streamlit as st
import requests
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# الرابط الخاص بك (Web App URL)
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

# --- التنسيقات (CSS) لتحسين الخط والموقع ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 15px; margin-bottom: 30px; }
    
    .welcome-container {
        text-align: center;
        margin-top: 30px;
        margin-bottom: 30px;
    }
    .welcome-text { 
        font-size: 35px; 
        color: #1E3A8A; 
        font-weight: bold;
        margin-bottom: 10px;
    }
    .blessing-text { 
        font-size: 24px; 
        color: #2e7d32; 
        font-weight: bold;
    }
    .preview-box { background-color: #f8f9fa; border: 2px solid #1E3A8A; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 🔐 شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المناديب</h1></div>', unsafe_allow_html=True)
    user_choice = st.selectbox("إختر اسمك من القائمة", ["-- اختر اسمك --"] + list(USERS.keys()))
    password_input = st.text_input("أدخل كلمة السر الخاصة بك", type="password")
    
    if st.button("دخول للنظام", use_container_width=True):
        if user_choice != "-- اختر اسمك --" and USERS[user_choice] == password_input:
            st.session_state.logged_in = True
            st.session_state.user_name = user_choice
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# --- 🚀 الصفحة الرئيسية بعد الدخول ---
else:
    st.sidebar.write(f"👤 المندوب المتصل: **{st.session_state.user_name}**")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h1>شركة حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # الترحيب في منتصف الصفحة بخط جميل وكبير
        st.markdown(f"""
            <div class="welcome-container">
                <div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>
                <div class="blessing-text">ببركة الصلاة على محمد وال محمد<br>ابدأ تسجيل الطلبيه</div>
            </div>
        """, unsafe_allow_html=True)
        
        # زر واحد فقط لكل الأصناف
        if st.button("📝 تسجيل الطلبية", use_container_width=True, type="primary"):
            st.session_state.page = 'order_page'
            st.rerun()

    # --- صفحة الطلبية الموحدة (حبوب + بهارات) ---
    elif st.session_state.page == 'order_page':
        st.markdown('<div class="header-box"><h2>📝 تسجيل طلبية جديدة</h2></div>', unsafe_allow_html=True)
        
        customer = st.text_input("👤 اسم الزبون الكامل:")
        inv_no = st.text_input("📄 رقم الفاتورة المرجعي", value=str(random.randint(10000, 99999)))

        st.divider()
        
        # قائمة موحدة للأصناف (يمكنك إضافة كل ما تريد هنا)
        items = [
            "حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول حب 1000غ", "عدس مجروش",
            "بهارات شاورما", "بهارات فلافل", "فلفل أسود", "كمون ناعم"
        ]
        
        order_list = []
        
        st.write("🔧 أدخل الأسعار والكميات للأصناف المطلوبة:")
        
        for item in items:
            col_item, col_p, col_q = st.columns([2, 1, 1])
            with col_item:
                st.write(f"**{item}**")
            with col_p:
                price = st.number_input("السعر", min_value=0.0, key=f"p_{item}", label_visibility="collapsed")
            with col_q:
                qty = st.number_input("الكمية", min_value=0, step=1, key=f"q_{item}", label_visibility="collapsed")
            
            if qty > 0 and price > 0:
                order_list.append({"الصنف": item, "السعر": price, "الكمية": qty, "الإجمالي": price * qty})

        if order_list and customer:
            st.divider()
            
            # زر المعاينة
            if st.button("👁️ معاينة الفاتورة قبل الإرسال", use_container_width=True):
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.subheader("🔍 مراجعة الطلبية")
                st.table(order_list)
                total_all = sum(d['الإجمالي'] for d in order_list)
                st.markdown(f"### 💰 الصافي النهائي: {total_all:,.0f} ل.ل")
                st.markdown('</div>', unsafe_allow_html=True)

            # زر الحفظ النهائي
            if st.button("💾 تأكيد وحفظ في الإكسل", use_container_width=True):
                with st.spinner("جاري الحفظ في الإكسل..."):
                    for entry in order_list:
                        payload = {
                            "total": entry['الإجمالي'], "price": entry['السعر'], "qty": entry['الكمية'],
                            "item": entry['الصنف'], "customer": customer, "inv_no": inv_no, 
                            "user": st.session_state.user_name
                        }
                        requests.post(URL_LINK, json=payload)
                st.balloons()
                st.success("✅ تم الحفظ بنجاح! يمكن العودة للرئيسية.")
                if st.button("العودة للرئيسية"):
                    st.session_state.page = 'home'
                    st.rerun()

        if st.button("🔙 إلغاء والعودة"):
            st.session_state.page = 'home'
            st.rerun()
