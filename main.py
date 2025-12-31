import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# الرابط الخاص بجوجل شيت (Web App URL)
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

# 2. قاعدة بيانات المناديب (التي اتفقنا عليها ولا نغيرها)
USERS = {
    "محمد الحسيني": "8822",
    "علي دوغان": "5500",
    "عزات حلاوي": "6611",
    "علي حسين حلباوي": "4455",
    "محمد حسين حلباوي": "3366",
    "احمد حسين حلباوي": "7722",
    "علي محمد حلباوي": "6600"
}

# دالة تحويل الأرقام العربية (لضمان صحة الحسابات)
def convert_ar_nav(text):
    if not isinstance(text, str): return text
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# 3. التنسيقات (CSS) - الحفاظ على الترحيب والخطوط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 15px; margin-bottom: 20px; }
    .welcome-container { text-align: center; margin: 20px 0; }
    .welcome-text { font-size: 22px; color: #1E3A8A; font-weight: 800; }
    .blessing-text { font-size: 18px; color: #2e7d32; font-weight: 600; margin-top: 5px; }
    .invoice-card { background-color: white; border: 2px solid #000; padding: 20px; color: black; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة حالة الجلسة (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'show_invoice' not in st.session_state: st.session_state.show_invoice = False

# --- 🔐 المرحلة الأولى: شاشة تسجيل الدخول ---
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

# --- المرحلة الثانية: الصفحة الرئيسية بعد الدخول ---
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
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

    # --- المرحلة الثالثة: صفحة تسجيل الطلبية (التابلو الذكي) ---
    elif st.session_state.page == 'order_page':
        st.markdown('<div class="header-box"><h3>📝 تسجيل طلبية جديدة</h3></div>', unsafe_allow_html=True)
        
        # رأس الفاتورة
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            cust_name = st.text_input("👤 اسم الزبون")
        with col_h2:
            discount_pct = st.number_input("الحسم %", min_value=0, max_value=6, step=1)
        
        # بيانات افتراضية (غداً نربطها بالإكسل)
        all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "فلفل اسود 50غ", "كمون"]
        
        st.divider()

        # سطر الإدخال الموحد (صنف + عدد)
        col_search, col_q = st.columns([4, 1])
        with col_search:
            search_input = st.text_input("🔍 ابحث عن الصنف (مثال: حم)")
            filtered = [p for p in all_products if search_input in p] if search_input else []
            selected_p = st.selectbox("النتائج:", ["-- اختر الصنف --"] + filtered)
        with col_q:
            qty_input = st.text_input("العدد", value="1")

        if st.button("➕ إضافة للجدول", use_container_width=True):
            if selected_p != "-- اختر الصنف --":
                qty_val = int(convert_ar_nav(qty_input))
                price_val = 2.5 # افتراضي
                st.session_state.temp_items.append({
                    "الصنف": selected_p, "الكمية": qty_val, "السعر": price_val, "الإجمالي": qty_val * price_val
                })
                st.success(f"تمت إضافة {selected_p}")

        # التابلو المباشر (يبقى ظاهراً للمندوب)
        if st.session_state.temp_items:
            st.write("### 📋 الأصناف في الفاتورة:")
            df = pd.DataFrame(st.session_state.temp_items)
            st.table(df[["الصنف", "الكمية", "الإجمالي"]])
            
            if st.button("👁️ مشاهدة الفاتورة النهائية", use_container_width=True):
                st.session_state.show_invoice = True

        # معاينة الفاتورة (للطباعة الحرارية)
        if st.session_state.show_invoice and st.session_state.temp_items:
            st.divider()
            st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
            st.write(f"**الزبون:** {cust_name}")
            st.caption(f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')} | 👤 المندوب: {st.session_state.user_name}")
            st.table(df)
            
            total_b = df["الإجمالي"].sum()
            disc_v = total_b * (discount_pct / 100)
            net_v = total_b - disc_v
            vat_v = net_v * 0.11
            final_v = net_v + vat_v
            
            st.write(f"المجموع: ${total_b:,.2f} | الحسم: ${disc_v:,.2f}")
            st.write(f"VAT (11%): ${vat_v:,.2f}")
            st.markdown(f"### الصافي النهائي: ${final_v:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 حفظ وإرسال للشركة", use_container_width=True, type="primary"):
                # كود الإرسال للجوجل شيت...
                st.balloons()
                st.success("تم الحفظ!")
                st.session_state.temp_items = []
                st.session_state.page = 'home'
                st.rerun()

        if st.button("🔙 عودة للرئيسية"):
            st.session_state.page = 'home'
            st.rerun()
