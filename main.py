import streamlit as st
import requests
import random
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="نظام حلباوي للمبيعات", layout="centered")

# رابط الربط مع جوجل شيت (تأكد من تحديثه إذا تغير)
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

# 2. تحويل الأرقام العربية إلى إنجليزية لضمان صحة الحسابات
def convert_ar_nav(text):
    if not isinstance(text, str): return text
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيقات (CSS) لضبط الواجهة وخط الفاتورة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .welcome-text { font-size: 20px; color: #1E3A8A; font-weight: bold; text-align: center; }
    .blessing-text { font-size: 16px; color: #2e7d32; text-align: center; margin-bottom: 20px; }
    .invoice-card { background-color: white; border: 1px solid #000; padding: 15px; color: black; }
    .stNumberInput input { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة حالة الجلسة (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []

# --- نظام تسجيل الدخول (اختصاراً سأستخدم الأسماء التي حددتها سابقاً) ---
USERS = {"محمد الحسيني":"8822", "علي دوغان":"5500", "عزات حلاوي":"6611", "علي حسين حلباوي":"4455", "محمد حسين حلباوي":"3366", "احمد حسين حلباوي":"7722", "علي محمد حلباوي":"6600"}

if not st.session_state.logged_in:
    st.title("🔐 دخول المناديب")
    user = st.selectbox("المندوب", ["--"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if USERS.get(user) == pwd:
            st.session_state.logged_in = True
            st.session_state.user_name = user
            st.rerun()
else:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown(f'<div class="welcome-text">أهلاً بك سيد {st.session_state.user_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="blessing-text">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الطلبيه</div>', unsafe_allow_html=True)
        if st.button("📝 تسجيل الطلبية", use_container_width=True, type="primary"):
            st.session_state.page = 'order'
            st.rerun()

    # --- صفحة الطلبية الذكية ---
    elif st.session_state.page == 'order':
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            cust_name = st.text_input("👤 اسم الزبون")
        with col_r2:
            discount_pct = st.number_input("الحسم %", min_value=0, max_value=6, step=1)
        
        now = datetime.now()
        st.caption(f"📅 {now.strftime('%d-%m-%Y | %H:%M')} | 👤 المندوب: {st.session_state.user_name}")
        
        st.divider()

        # نظام البحث في 300 صنف (سأضع أمثلة، وغداً نربطها بالإكسل)
        all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "فلفل اسود 50غ", "كمون ناعم"]
        
        with st.container():
            c_item, c_qty = st.columns([4, 1])
            with c_item:
                selected_product = st.selectbox("ابحث عن الصنف...", ["-- اكتب للبحث --"] + all_products)
            with c_qty:
                # حقل نصي للعدد للسماح بالأرقام العربية
                qty_input = st.text_input("العدد", value="1")
            
            if st.button("➕ إضافة للصنف"):
                if selected_product != "-- اكتب للبحث --":
                    qty_final = int(convert_ar_nav(qty_input))
                    # هنا السعر سيوضع تلقائياً غداً من الإكسل، حالياً نضعه يدوياً للتجربة
                    price_test = 2.5 # افتراضي
                    st.session_state.temp_items.append({
                        "item": selected_product,
                        "qty": qty_final,
                        "price": price_test,
                        "total": qty_final * price_test
                    })
        
        if st.session_state.temp_items:
            st.write("---")
            if st.button("👁️ مشاهدة الفاتورة"):
                st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
                st.write(f"**الزبون:** {cust_name}")
                
                # جدول الفاتورة (أسود وأبيض للطباعة الحرارية)
                total_base = sum(i['total'] for i in st.session_state.temp_items)
                st.table(st.session_state.temp_items)
                
                # الحسابات المالية
                disc_val = total_base * (discount_pct / 100)
                after_disc = total_base - disc_val
                vat_val = after_disc * 0.11
                final_net = after_disc + vat_val
                
                st.write(f"المجموع الأساسي: {total_base:,.0f}")
                st.write(f"الحسم ({discount_pct}%): {disc_val:,.0f}-")
                st.write(f"الصافي بعد الحسم: {after_disc:,.0f}")
                st.write(f"ضريبة VAT (11%): {vat_val:,.0f}")
                st.markdown(f"### الصافي النهائي: {final_net:,.0f} ل.ل")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 تأكيد وحفظ في الإكسل", use_container_width=True):
                # كود الإرسال للجوجل شيت...
                st.success("تم الحفظ بنجاح")
                st.session_state.temp_items = []
                st.session_state.page = 'home'
                st.rerun()

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
