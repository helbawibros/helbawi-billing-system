import streamlit as st

# إعدادات واجهة البرنامج
st.set_page_config(page_title="نظام فواتير حلباوي", layout="centered")

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
    st.title("📄 فاتورة تجريبية")
    rate = st.number_input("سعر صرف الضريبة (L.L)", value=89500)
    customer = st.text_input("اسم الزبون")

    # قائمة الأصناف التي أرسلتها (النجمة تعني خاضع للضريبة)
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

    total_usd = 0.0
    vat_usd = 0.0

    st.subheader("الكميات")
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            sub = qty * price
            total_usd += sub
            if "*" in p: # حساب الضريبة للأصناف المحددة بنجمة
                vat_usd += (sub * 0.11)

    st.divider()
    
    # الحسابات النهائية
    final_total_usd = total_usd + vat_usd
    vat_ll = vat_usd * rate

    st.subheader("ملخص الفاتورة")
    st.write(f"المجموع الأساسي: **${total_usd:.2f}**")
    st.write(f"ضريبة VAT (11%): **${vat_usd:.2f}**")
    st.success(f"الصافي النهائي المطلوب: **${final_total_usd:.2f}**")
    
    # خانة الضريبة بالليرة اللبنانية (كما طلبت)
    st.info(f"قيمة الضريبة بالليرة (V.A.T L.L): **{vat_ll:,.0f} L.L**")

    if st.button("حفظ"):
        st.balloons()
        st.write("تم حفظ الفاتورة التجريبية بنجاح!")
