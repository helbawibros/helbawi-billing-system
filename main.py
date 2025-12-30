import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات واجهة البرنامج
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

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

# 2. اتصال قاعدة البيانات (باستخدام الرابط العام من Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. نظام تسجيل الدخول
users = {"حسين": "1111", "علي": "2222", "مدير": "9999"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
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
    st.title(f"📄 فاتورة: {st.session_state.user}")
    
    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        customer_id = st.text_input("رقم الحساب (ID)")
    with col_cust2:
        customer_name = st.text_input("اسم الزبون")
    
    rate = st.number_input("سعر صرف الضريبة (L.L)", value=89500)

    products = {
        "حمص رقم 12 907غ": 2.25, "حمص رقم 9 907غ": 2.00, "حمص كسر 1000غ": 1.60,
        "فول حب 1000غ": 1.30, "فول مجروش 1000غ": 1.75, "فول عريض 1000غ": 2.30,
        "سبع بهارات 50غ * 12 *": 10.00, "فلفل اسود 50غ * 12 *": 13.00, "بهار حلو 500غ *": 13.50
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
                "الصنف": p, "العدد": qty, "السعر": price,
                "VAT": item_vat, "الإجمالي": (sub + item_vat)
            })

    st.divider()
    discount_percent = st.number_input("نسبة الحسم %", min_value=0.0, value=0.0)
    
    discount_amount = total_usd * (discount_percent / 100)
    total_after_discount = total_usd - discount_amount
    final_total_usd = total_after_discount + total_vat_usd
    vat_ll = total_vat_usd * rate

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        show_view = st.button("👁️ مشاهدة الفاتورة")
    with col_btn2:
        save_bill = st.button("💾 حفظ وإرسال للشركة")

    if show_view:
        if customer_name and selected_items:
            st.markdown("---")
            current_bill_no = st.session_state.bill_counters[st.session_state.user]
            st.markdown(f"""
                <div class="right-text">
                    <div class="customer-header">الزبون: {customer_name}</div>
                    <div class="bill-info">رقم الحساب: {customer_id} | رقم الفاتورة: {current_bill_no}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.table(selected_items)
            
            st.markdown(f"""
                <div class="right-text total-box">
                    <p>المجموع الأساسي: ${total_usd:.2f}</p>
                    <p>الحسم ({discount_percent}%): -${discount_amount:.2f}</p>
                    <p>إجمالي الضريبة: ${total_vat_usd:.2f}</p>
                    <h1 style='color: #4CAF50; font-size: 35px; margin-top:5px;'>الصافي: ${final_total_usd:.2f}</h1>
                    <h2 style='color: #1E90FF; margin-top:0px;'>VAT L.L: {vat_ll:,.0f} ل.ل</h2>
                </div>
            """, unsafe_allow_html=True)

    if save_bill:
        if not customer_name or not selected_items:
            st.warning("يرجى ملء البيانات أولاً")
        else:
            new_rows = []
            for item in selected_items:
                new_rows.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المندوب": st.session_state.user,
                    "رقم الفاتورة": st.session_state.bill_counters[st.session_state.user],
                    "رقم الزبون": customer_id,
                    "اسم الزبون": customer_name,
                    "الصنف": item["الصنف"],
                    "العدد": item["العدد"],
                    "السعر": item["السعر"],
                    "الإجمالي": item["الإجمالي"]
                })
            
            try:
                # 1. قراءة البيانات الحالية من الجدول
                existing_df = conn.read()
                
                # 2. تجهيز البيانات الجديدة
                new_data_df = pd.DataFrame(new_rows)
                
                # 3. دمج القديم والجديد
                updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                
                # 4. تحديث الجدول بالكامل (يعمل مع صلاحية Anyone with link can edit)
                conn.update(data=updated_df)
                
                st.session_state.bill_counters[st.session_state.user] += 1
                st.balloons()
                st.success("✅ تم الحفظ بنجاح في الإكسل!")
            except Exception as e:
                st.error(f"❌ خطأ في الحفظ: {e}")
