import streamlit as st
import requests
import random

# الرابط الخاص بك (لا تغيره)
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

st.set_page_config(page_title="نظام حلباوي المحاسبي", layout="centered")

st.title("📊 تسجيل فاتورة مبيعات")

with st.form("billing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        mandoub = st.selectbox("المندوب", ["حسين", "علي", "مدير"])
        customer = st.text_input("اسم الزبون")
    with col2:
        inv_number = st.text_input("رقم الفاتورة", value=str(random.randint(1000, 9999)))
        cust_number = st.text_input("رقم الزبون (إن وجد)", value="-")

    st.divider()
    
    product = st.selectbox("الصنف", ["حمص رقم 12 907غ", "حمص رقم 9 907غ", "فول حب 1000غ"])
    
    c3, c4 = st.columns(2)
    with c3:
        price = st.number_input("السعر الإفرادي", min_value=0.0, format="%.2f")
    with c4:
        quantity = st.number_input("العدد", min_value=1, step=1)

    total_amount = price * quantity
    st.info(### الإجمالي: {total_amount} ل.ل)

    submit = st.form_submit_button("🚀 حفظ الفاتورة بالترتيب الجديد")

if submit:
    if customer and price > 0:
        payload = {
            "total": total_amount,
            "price": price,
            "qty": quantity,
            "item": product,
            "customer": customer,
            "cust_no": cust_number,
            "inv_no": inv_number,
            "user": mandoub
        }
        try:
            response = requests.post(URL_LINK, json=payload)
            if response.status_code == 200:
                st.balloons()
                st.success(f"✅ تم الحفظ! الإجمالي {total_amount} سجل في العمود A")
        except Exception as e:
            st.error(f"خطأ: {e}")
    else:
        st.warning("يرجى التأكد من اسم الزبون والسعر")
