import streamlit as st
from datetime import datetime

# إعدادات واجهة البرنامج
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

# تنسيق الديزاين والجدول
st.markdown("""
    <style>
    .reportview-container .main .block-container { direction: rtl; }
    table { width: 100% !important; direction: rtl; border-collapse: collapse; margin-top: 10px; }
    th { background-color: #1a1c23 !important; color: white !important; text-align: center !important; 
         padding: 10px !important; border: 1px solid #ffffff !important; font-size: 14px; }
    td { text-align: center !important; padding: 8px !important; border: 1px solid #444444 !important; color: white; }
    .right-text { text-align: right; direction: rtl; }
    .customer-header { font-size: 30px; font-weight: bold; color: #ffffff; margin-bottom: 0px; }
    .bill-info { font-size: 18px; color: #bbbbbb; margin-bottom: 5px; }
    .total-box { border-top: 2px solid #ffffff; padding-top: 10px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 1. نظام تسجيل الدخول وإدارة أرقام الفواتير
users = {"حسين": "1111", "علي": "2222", "مدير": "9999"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# إنشاء عداد فواتير مستقل لكل مندوب (مؤقت حالياً)
if 'bill_counters' not in st.session_state:
    st.session_state.bill_counters = {user: 1 for user in users}

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
        customer_id = st.text_input("رقم الحساب (ID)")
    with col_cust2:
        customer_name = st.text_input("اسم الزبون")
    
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
    items_count = 0 # عداد الأصناف المطلوبة

    st.subheader("إدخال الطلبية")
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            sub = qty * price
            item_vat = (sub * 0.11) if "*" in p else 0.0
            total_usd += sub
            total_vat_usd += item_vat
            items_count += 1 # زيادة عداد الأصناف
            selected_items.append({
                "الصنف": p,
                "العدد": qty,
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

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        show_view = st.button("👁️ مشاهدة الفاتورة (Preview)")
    with col_btn2:
        save_bill = st.button("💾 حفظ الفاتورة")

    if show_view:
        if not customer_name:
            st.warning("الرجاء إدخال اسم الزبون!")
        elif not selected_items:
            st.warning("الفاتورة فارغة!")
        else:
            st.markdown("---")
            
            # الحصول على رقم الفاتورة الحالي للمندوب
            current_bill_no = st.session_state.bill_counters[st.session_state.user]
            
            # رأس الفاتورة المعدل
            st.markdown(f"""
                <div class="right-text">
                    <div class="customer-header">الزبون: {customer_name}</div>
                    <div class="bill-info">رقم الحساب: {customer_id} | <b>رقم الفاتورة: {current_bill_no}</b></div>
                    <div class="bill-info">المندوب: {st.session_state.user} | التاريخ: {datetime.now().strftime("%Y-%m-%d | %H:%M:%S")}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.table(selected_items)
            
            # عرض عدد الأصناف تحت الجدول مباشرة
            st.markdown(f"<div class='right-text'><b>عدد الأصناف: {items_count}</b></div>", unsafe_allow_html=True)
            
            # المبالغ النهائية
            st.markdown(f"""
                <div class="right-text total-box">
                    <p>المجموع الأساسي: ${total_usd:.2f}</p>
                    <p>الحسم ({discount_percent}%): -${discount_amount:.2f}</p>
                    <p>إجمالي الضريبة: ${total_vat_usd:.2f}</p>
                    <h1 style='color: #4CAF50; font-size: 40px; margin-top:5px;'>الصافي: ${final_total_usd:.2f}</h1>
                    <h2 style='color: #1E90FF; margin-top:0px;'>VAT L.L: {vat_ll:,.0f} ل.ل</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")

    if save_bill:
        if customer_name and selected_items:
            # زيادة رقم الفاتورة للمندوب الحالي بعد الحفظ
            st.session_state.bill_counters[st.session_state.user] += 1
            st.balloons()
            st.success(f"تم حفظ فاتورة {customer_name} بنجاح!")
        else:
            st.error("تأكد من البيانات!")
