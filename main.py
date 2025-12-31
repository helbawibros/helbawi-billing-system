import streamlit as st
import pandas as pd
import random

# --- إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stTable { direction: rtl; }
    th { background-color: #1E3A8A !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    .total-box { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة البيانات (Session State) ---
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))

# --- واجهة تسجيل الطلبية ---
st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)

# 1. معلومات الزبون
cust_name = st.text_input("الزبون", placeholder="اسم المحل")
discount_val = st.text_input("حسم %", value="0")

st.divider()

# 2. إدخال الأصناف
all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "سبع بهارات 50غ"]
search_prod = st.text_input("🔍 ابحث عن صنف...")
filtered_prod = [p for p in all_products if search_prod in p] if search_prod else all_products
selected_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered_prod)
qty_input = st.number_input("العدد", min_value=1, value=1)

# كبسة الإضافة
if st.button("➕ إضافة للصنف", use_container_width=True, type="secondary"):
    if selected_p != "-- اختر الصنف --" and cust_name != "":
        # حسبة تجريبية للسعر
        price = 2.25 if "حمص" in selected_p else 10.00
        tax = 1.10 if "بهارات" in selected_p else 0.00
        total = (price * qty_input) + tax
        
        # إضافة الصنف للقائمة
        st.session_state.temp_items.append({
            "الرقم": len(st.session_state.temp_items),
            "الصنف": selected_p,
            "العدد": qty_input,
            "السعر": f"{price:.2f}",
            "VAT": f"{tax:.2f}",
            "الإجمالي": f"{total:.2f}"
        })
        st.success(f"تمت إضافة {selected_p}")
    else:
        st.warning("يرجى إدخال اسم الزبون واختيار الصنف")

st.divider()

# --- 3. الجدول (الذي يظهر تحت الكبسات) ---
if st.session_state.temp_items:
    st.markdown(f"### الزبون: {cust_name}")
    st.write(f"رقم الفاتورة: {st.session_state.inv_no}")
    
    # تحويل القائمة لجدول بيانات
    df = pd.DataFrame(st.session_state.temp_items)
    
    # عرض الجدول بتنسيق مشابه للصورة
    st.table(df[["الرقم", "الصنف", "العدد", "السعر", "VAT", "الإجمالي"]])
    
    # حساب الصافي النهائي
    net_total = sum(float(item["الإجمالي"]) for item in st.session_state.temp_items)
    st.markdown(f'<div class="total-box">الصافي النهائي: ${net_total:.2f}</div>', unsafe_allow_html=True)

    st.write("") # فراغ

    # أزرار الإجراءات النهائية (كما في صورتك)
    col_view, col_save = st.columns(2)
    with col_view:
        if st.button("👁️ مشاهدة الفاتورة", use_container_width=True):
            st.info("جاري تجهيز عرض الفاتورة...")
    with col_save:
        if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
            st.success("✅ تم حفظ الفاتورة وإرسالها بنجاح!")

if st.button("🔙 عودة للرئيسية"):
    st.session_state.page = 'home'
    st.rerun()

