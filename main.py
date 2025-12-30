import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# إعدادات الصفحة
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

# الاتصال بقاعدة البيانات
conn = st.connection("gsheets", type=GSheetsConnection)

# نظام تسجيل الدخول
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
    
    # مدخلات الزبون
    customer_id = st.text_input("رقم الحساب (ID)")
    customer_name = st.text_input("اسم الزبون")
    
    # الأصناف والأسعار
    products = {
        "حمص رقم 12 907غ": 2.25, "حمص رقم 9 907غ": 2.00, "حمص كسر 1000غ": 1.60,
        "فول حب 1000غ": 1.30, "فول مجروش 1000غ": 1.75, "فول عريض 1000غ": 2.30
    }

    selected_items = []
    for p, price in products.items():
        qty = st.number_input(f"{p} (${price})", min_value=0, step=1, key=p)
        if qty > 0:
            selected_items.append({
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "المندوب": st.session_state.user,
                "رقم الفاتورة": st.session_state.bill_counters[st.session_state.user],
                "رقم الحساب": customer_id,
                "اسم الزبون": customer_name,
                "الصنف": p,
                "العدد": qty,
                "السعر": price,
                "الإجمالي": qty * price
            })

    if st.button("💾 حفظ الفاتورة"):
        if customer_name and selected_items:
            try:
                # محاولة قراءة البيانات أو إنشاء جدول جديد
                try:
                    existing_data = conn.read()
                except:
                    existing_data = pd.DataFrame()
                
                new_data = pd.DataFrame(selected_items)
                updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                
                # تحديث الملف
                conn.update(data=updated_df)
                
                st.session_state.bill_counters[st.session_state.user] += 1
                st.balloons()
                st.success("✅ تم الحفظ بنجاح!")
            except Exception as e:
                st.error(f"خطأ في الحفظ: {e}")
                st.info("ملاحظة: إذا ظهر خطأ 'Public Spreadsheet', سنحتاج لإضافة مفتاح خاص بك.")
        else:
            st.warning("الرجاء إدخال اسم الزبون والأصناف")
