import streamlit as st
from datetime import datetime

# إعدادات الواجهة
st.set_page_config(page_title="نظام حلباوي", layout="wide")

# تنسيق بسيط جداً لضمان ظهور الجداول بشكل طبيعي
st.markdown("""
    <style>
    .reportview-container .main .block-container { direction: rtl; }
    table { width: 100% !important; direction: rtl; }
    th, td { text-align: center !important; font-size: 14px !important; }
    /* جعل خانة الصنف مريحة للعين */
    td:nth-child(2) { text-align: right !important; white-space: nowrap !important; }
    </style>
    """, unsafe_allow_html=True)

# نظام الدخول
users = {"حسين": "1111", "علي": "2222", "مدير": "9999"}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'bill_counters' not in st.session_state: st.session_state.bill_counters = {user: 1 for user in users}

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
    st.title(f"📄 فاتورة: {st.session_state.user}")
    
    # مدخلات الزبون
    c1, c2 = st.columns(2)
    with c1: customer_id = st.text_input("رقم الحساب")
    with c2: customer_name = st.text_input("اسم الزبون")
    
    rate = st.number_input("سعر الصرف", value=89500)

    # الأصناف
    products = {
        "حمص رقم 12 907غ": 2.25,
        "حمص رقم 9 907غ": 2.00,
        "فول عريض 1000غ": 2.30,
        "سبع بهارات 50غ * 12 *": 10.00,
        "فلفل اسود 50غ * 12 *": 13.00,
        "بهار حلو 500غ *": 13.50
    }

    selected_items = []
    total_usd = 0.0
    total_vat_usd = 0.0

    st.subheader("الطلبية")
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            sub = qty * price
            item_vat = (sub * 0.11) if "*" in p else 0.0
            total_usd += sub
            total_vat_usd += item_vat
            selected_items.append({
                "م": len(selected_items) + 1,
                "الصنف": p,
                "العدد": qty,
                "السعر": f"{price:.2f}",
                "VAT": f"{item_vat:.2f}",
                "الإجمالي": f"{(sub + item_vat):.2f}"
            })

    st.divider()
    discount_p = st.number_input("الحسم %", min_value=0.0)

    if st.button("👁️ مشاهدة الفاتورة"):
        if not customer_name:
            st.warning("أدخل اسم الزبون")
        else:
            now = datetime.now().strftime("%Y-%m-%d | %H:%M")
            bill_no = st.session_state.bill_counters[st.session_state.user]
            
            st.markdown(f"### الزبون: {customer_name}")
            st.write(f"رقم الحساب: {customer_id} | رقم الفاتورة: {bill_no}")
            st.write(f"المندوب: {st.session_state.user} | التاريخ: {now}")
            
            st.table(selected_items)
            
            st.write(f"**عدد الأصناف: {len(selected_items)}**")
            
            disc_amt = total_usd * (discount_p / 100)
            final_usd = (total_usd - disc_amt) + total_vat_usd
            
            st.write(f"المجموع الأساسي: ${total_usd:.2f}")
            st.write(f"الحسم: -${disc_amt:.2f}")
            st.write(f"الضريبة: ${total_vat_usd:.2f}")
            st.success(f"الصافي النهائي: ${final_usd:.2f}")
            st.info(f"VAT L.L: {total_vat_usd * rate:,.0f}")

    if st.button("💾 حفظ"):
        st.session_state.bill_counters[st.session_state.user] += 1
        st.success("تم الحفظ بنجاح")

