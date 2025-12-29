import streamlit as st
from datetime import datetime

# إعدادات واجهة البرنامج
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

# تصحيح الديزاين بالكامل - CSS
st.markdown("""
    <style>
    .reportview-container .main .block-container { direction: rtl; }
    /* تنسيق الجدول ليظهر بوضوح */
    table { width: 100% !important; direction: rtl; border-collapse: collapse; }
    th { background-color: #262730 !important; color: white !important; text-align: right !important; padding: 10px !important; }
    td { text-align: right !important; padding: 8px !important; border-bottom: 1px solid #444; }
    /* تنسيق نصوص اليمين */
    .right-text { text-align: right; direction: rtl; }
    .customer-header { font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
    .customer-sub { font-size: 20px; color: #cccccc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 1. قائمة المندوبين
users = {"حسين": "1111", "علي": "2222", "مدير": "9999"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 دخول المندوبين")
    user_choice = st.selectbox("اختر الاسم", list(users.keys()))
    password = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if users.get(user_choice) == password:
            st.session_state.logged_in = True
            st.session_state.user = user_choice
            st.rerun()
        else: st.error("خطأ!")
else:
    st.title("📄 فاتورة بيع جديدة")
    
    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        customer_id = st.text_input("رقم الزبون (ID)")
    with col_cust2:
        customer_name = st.text_input("اسم الزبون / المحل")
    
    rate = st.number_input("سعر صرف الضريبة (L.L)", value=89500)

    # الأصناف
    products = {
        "حمص رقم 12 907غ": 2.25,
        "حمص رقم 9 907غ": 2.00,
        "حمص كسر 1000غ": 1.60,
        "فول حب 1000غ": 1.30,
        "فول مجروش 1000غ": 1.75,
        "فول عريض 1000غ": 2.30,
        "سبع بهارات 50غ * 12 *": 10.00,
        "فلفل اسود 50غ * 12 *": 13.00,
        "بهار حلو 500غ *": 13.50
    }

    selected_items = []
    total_usd = 0.0
    total_vat_usd = 0.0

    st.subheader("إدخال الطلبية")
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            sub = qty * price
            item_vat = (sub * 0.11) if "*" in p else 0.0
            total_usd += sub
            total_vat_usd += item_vat
            selected_items.append({
                "الصنف": p,
                "الكمية": qty,
                "السعر $": f"{price:.2f}",
                "VAT $": f"{item_vat:.2f}",
                "الإجمالي $": f"{(sub + item_vat):.2f}"
            })

    st.divider()
    discount_percent = st.number_input("نسبة الحسم %", min_value=0.0, value=0.0)
    
    discount_amount = total_usd * (discount_percent / 100)
    total_after_discount = total_usd - discount_amount
    final_total_usd = total_after_discount + total_vat_usd
    vat_ll = total_vat_usd * rate

    if st.button("👁️ مشاهدة الفاتورة (Preview)"):
        if not customer_name or not customer_id:
            st.warning("الرجاء إدخال اسم ورقم الزبون!")
        elif not selected_items:
            st.warning("الفاتورة فارغة!")
        else:
            st.markdown("---")
            
            # رأس الفاتورة - أقصى اليمين
            st.markdown(f"""
                <div class="right-text">
                    <div class="customer-header">الزبون: {customer_name}</div>
                    <div class="customer-sub">رقم الحساب: {customer_id}</div>
                </div>
            """, unsafe_allow_html=True)
            
            now = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
            st.markdown(f"<p class='right-text'><b>التاريخ:</b> {now} | <b>المندوب:</b> {st.session_state.user}</p>", unsafe_allow_html=True)
            
            # عرض الجدول المعدل
            st.table(selected_items)
            
            # ملخص المبالغ - جهة اليمين
            st.markdown(f"""
                <div class="right-text">
                    <p>المجموع الأساسي: ${total_usd:.2f}</p>
                    <p>الحسم ({discount_percent}%): -${discount_amount:.2f}</p>
                    <p>إجمالي الضريبة: ${total_vat_usd:.2f}</p>
                    <h1 style='color: #4CAF50;'>الصافي النهائي: ${final_total_usd:.2f}</h1>
                    <h2 style='color: #1E90FF;'>VAT L.L: {vat_ll:,.0f} ل.ل</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
