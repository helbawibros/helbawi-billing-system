import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام حلباوي للمبيعات", layout="centered")

# دالة تحويل الأرقام العربية
def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# تنسيقات الواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .invoice-card { background-color: white; border: 2px solid #000; padding: 20px; color: black; border-radius: 10px; }
    .stTable { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# إدارة البيانات المخزنة مؤقتاً
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'show_invoice' not in st.session_state: st.session_state.show_invoice = False

# --- واجهة إدخال البيانات ---
st.subheader("📝 إدخال بيانات الطلبية")

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    cust_name = st.text_input("👤 اسم الزبون")
with col_head2:
    discount_pct = st.number_input("الحسم %", min_value=0, max_value=6, step=1)

# بيانات ثابتة (سيتم ربطها بالإكسل لاحقاً)
all_products = ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول عريض 1000غ", "فلفل اسود 50غ", "عدس"]

st.write("---")

# سطر إدخال الصنف والعدد (على نفس السطر كما طلبت)
col_search, col_q = st.columns([4, 1])
with col_search:
    search_input = st.text_input("🔍 ابحث عن الصنف (اكتب أول حرفين مثل: حم)")
    # فلترة الأصناف بناءً على البحث
    filtered_list = [p for p in all_products if search_input in p] if search_input else []
    selected_p = st.selectbox("اختر من النتائج:", ["-- اختر الصنف --"] + filtered_list)
with col_q:
    qty_input = st.text_input("العدد", value="1")

if st.button("➕ إضافة للجدول", use_container_width=True):
    if selected_p != "-- اختر الصنف --":
        real_qty = int(convert_ar_nav(qty_input))
        unit_price = 2.5 # افتراضي حالياً
        st.session_state.temp_items.append({
            "الصنف": selected_p,
            "الكمية": real_qty,
            "السعر": unit_price,
            "الإجمالي": real_qty * unit_price
        })
        st.success(f"تمت إضافة {selected_p}")

# --- عرض الجدول المباشر للمندوب (التابلو) ---
if st.session_state.temp_items:
    st.write("### 📋 الأصناف المضافة حالياً:")
    df = pd.DataFrame(st.session_state.temp_items)
    st.table(df[["الصنف", "الكمية", "الإجمالي"]])
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("👁️ مشاهدة الفاتورة النهائية", use_container_width=True):
            st.session_state.show_invoice = True
    with col_btn2:
        if st.button("🗑️ مسح الجدول", use_container_width=True):
            st.session_state.temp_items = []
            st.session_state.show_invoice = False
            st.rerun()

# --- شكل الفاتورة النهائية (المعاينة) ---
if st.session_state.show_invoice and st.session_state.temp_items:
    st.divider()
    st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
    st.markdown(f"### فاتورة: {cust_name}")
    st.write(f"المندوب: {st.session_state.user_name if 'user_name' in st.session_state else 'غير معروف'}")
    st.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.table(df)
    
    total_base = df["الإجمالي"].sum()
    disc_val = total_base * (discount_pct / 100)
    after_disc = total_base - disc_val
    vat_val = after_disc * 0.11
    final_net = after_disc + vat_val
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write(f"المجموع الأساسي: ${total_base:,.2f}")
        st.write(f"الحسم ({discount_pct}%): -${disc_val:,.2f}")
        st.write(f"قيمة الـ VAT (11%): ${vat_val:,.2f}")
    with col_res2:
        st.markdown(f"## الصافي: ${final_net:,.2f}")
        st.caption(f"الضريبة بالليرة: {int(vat_val * 89000):,} ل.ل") # سعر صرف افتراضي
    
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 حفظ وإرسال للشركة", use_container_width=True, type="primary"):
        st.balloons()
        st.success("تم تسجيل الطلبية بنجاح في ملف الإكسل!")
        st.session_state.temp_items = []
        st.session_state.show_invoice = False
