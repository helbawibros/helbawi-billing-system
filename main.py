import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container { direction: rtl; }
    table { width: 100% !important; direction: rtl; border-collapse: collapse; margin-top: 10px; }
    th { background-color: #1a1c23 !important; color: white !important; text-align: center !important; padding: 10px !important; border: 1px solid #ffffff !important; }
    td { text-align: center !important; padding: 8px !important; border: 1px solid #444444 !important; color: white; }
    .right-text { text-align: right; direction: rtl; }
    .total-box { border-top: 2px solid #ffffff; padding-top: 10px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. الاتصال بقاعدة البيانات
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
    
    col1, col2 = st.columns(2)
    with col1:
        customer_id = st.text_input("رقم الحساب (ID)")
    with col2:
        customer_name = st.text_input("اسم الزبون")
    
    products = {
        "حمص رقم 12 907غ": 2.25, "حمص رقم 9 907غ": 2.00, 
        "حمص كسر 1000غ": 1.60, "فول حب 1000غ": 1.30, 
        "فول مجروش 1000غ": 1.75, "فول عريض 1000غ": 2.30
    }

    selected_items = []
    total_usd = 0.0

    st.subheader("إدخال الطلبية")
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            sub = qty * price
            total_usd += sub
            selected_items.append({
                "الصنف": p, "العدد": qty, "السعر": price, "الإجمالي": sub
            })

    st.divider()
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        show_view = st.button("👁️ مشاهدة الفاتورة")
    with col_btn2:
        save_bill = st.button("💾 حفظ الفاتورة")

    # --- عرض المعاينة عند الضغط على زر المشاهدة ---
    if show_view:
        if customer_name and selected_items:
            st.markdown("---")
            st.markdown(f"<div class='right-text'><h3>الزبون: {customer_name}</h3></div>", unsafe_allow_html=True)
            st.table(pd.DataFrame(selected_items))
            st.markdown(f"<div class='right-text total-box'><h2>المجموع: ${total_usd:.2f}</h2></div>", unsafe_allow_html=True)
        else:
            st.warning("يرجى إدخال البيانات أولاً")

    # --- عملية الحفظ ---
    if save_bill:
        if customer_name and selected_items:
            # تجهيز الصفوف للحفظ في الإكسل
            rows_to_add = []
            for item in selected_items:
                rows_to_add.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المندوب": st.session_state.user,
                    "رقم الفاتورة": st.session_state.bill_counters[st.session_state.user],
                    "رقم الحساب": customer_id,
                    "اسم الزبون": customer_name,
                    "الصنف": item["الصنف"],
                    "العدد": item["العدد"],
                    "السعر": item["السعر"],
                    "الإجمالي": item["الإجمالي"]
                })
            
            try:
                try:
                    existing_df = conn.read()
                except:
                    existing_df = pd.DataFrame()
                
                updated_df = pd.concat([existing_df, pd.DataFrame(rows_to_add)], ignore_index=True)
                conn.update(data=updated_df)
                
                st.session_state.bill_counters[st.session_state.user] += 1
                st.balloons()
                st.success("✅ تم الحفظ بنجاح في ملف الإكسل!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")
