import streamlit as st
from datetime import datetime

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
    st.title("📄 إنشاء فاتورة")
    st.sidebar.write(f"👤 المندوب: {st.session_state.user}")
    
    rate = st.number_input("سعر صرف الضريبة (L.L)", value=89500)
    customer = st.text_input("اسم الزبون / المحل")

    # الأصناف (النجمة تعني خاضع للضريبة)
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
            item_vat = 0.0
            if "*" in p:
                item_vat = sub * 0.11
            
            total_usd += sub
            total_vat_usd += item_vat
            
            # إضافة البيانات للجدول بالترتيب المطلوب
            selected_items.append({
                "الصنف": p,
                "العدد": qty,
                "السعر ($)": f"{price:.2f}",
                "VAT ($)": f"{item_vat:.2f}", # الخانة الجديدة
                "الإجمالي ($)": f"{(sub + item_vat):.2f}"
            })

    st.divider()
    
    # خانة الحسم %
    discount_percent = st.number_input("نسبة الحسم % (Discount)", min_value=0.0, max_value=100.0, step=0.5, value=0.0)
    discount_amount = total_usd * (discount_percent / 100)
    
    # الحسابات النهائية
    total_after_discount = total_usd - discount_amount
    final_total_usd = total_after_discount + total_vat_usd
    vat_ll = total_vat_usd * rate

    # أزرار التحكم
    col1, col2 = st.columns(2)
    with col1:
        show_view = st.button("👁️ مشاهده الفاتورة (Preview)")
    with col2:
        save_bill = st.button("💾 حفظ وطباعة")

    if show_view:
        if not customer:
            st.warning("الرجاء إدخال اسم الزبون أولاً!")
        elif not selected_items:
            st.warning("الفاتورة فارغة!")
        else:
            st.markdown("---")
            st.subheader("🔍 مراجعة الفاتورة")
            
            now = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
            st.write(f"**الزبون:** {customer} | **التاريخ:** {now}")
            
            # عرض الجدول مع عمود VAT
            st.table(selected_items)
            
            # ملخص المبالغ
            st.write(f"المجموع (قبل الحسم والضريبة): **${total_usd:.2f}**")
            if discount_percent > 0:
                st.write(f"الحسم ({discount_percent}%): **-${discount_amount:.2f}**")
                st.write(f"المجموع بعد الحسم: **${total_after_discount:.2f}**")
            
            st.write(f"إجمالي الضريبة (VAT 11%): **${total_vat_usd:.2f}**")
            st.success(f"الصافي النهائي المطلوب: **${final_total_usd:.2f}**")
            st.info(f"قيمة الضريبة بالليرة (VAT L.L): **{vat_ll:,.0f} L.L**")
            st.markdown("---")

    if save_bill:
        if customer and selected_items:
            st.balloons()
            st.success("تم الحفظ بنجاح!")
        else:
            st.error("تأكد من البيانات!")
