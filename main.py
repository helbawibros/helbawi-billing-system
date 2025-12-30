import streamlit as st
import requests

# الرابط الجديد الذي أرسلته (Web App URL)
URL_LINK = "https://script.google.com/macros/s/AKfycbyaxdN2TPOOXsNSx8yy4eKBhLPccNe41wKR9MMw9QCM2HbEmJ-Oc6pqGfN5REY0OEratQ/exec"

st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="centered")

st.title("🚀 نظام تسجيل الطلبيات - حلباوي")
st.markdown("---")

# نموذج إدخال البيانات
with st.form("order_form", clear_on_submit=True):
    st.subheader("إدخال بيانات الطلبية")
    
    mandoub = st.selectbox("اسم المندوب", ["حسين", "علي", "مدير"])
    customer = st.text_input("اسم الزبون (أو رقم الحساب)")
    
    st.divider()
    
    product = st.selectbox("الصنف", [
        "حمص رقم 12 907غ", 
        "حمص رقم 9 907غ", 
        "حمص كسر 1000غ", 
        "فول حب 1000غ", 
        "فول مجروش 1000غ", 
        "فول عريض 1000غ"
    ])
    quantity = st.number_input("العدد (كمية)", min_value=1, step=1)
    
    # زر الحفظ والإرسال
    submit_button = st.form_submit_button("💾 حفظ وإرسال للشركة")

# معالجة الضغط على الزر
if submit_button:
    if customer:
        # تجهيز البيانات للإرسال بتنسيق JSON
        payload = {
            "user": mandoub,
            "customer": customer,
            "item": product,
            "qty": quantity
        }
        
        try:
            with st.spinner("جاري الحفظ في ملف الإكسل..."):
                # إرسال البيانات للرابط الجديد
                response = requests.post(URL_LINK, json=payload, timeout=10)
            
            # التحقق من نجاح العملية (حالة 200 تعني موافقة جوجل)
            if response.status_code == 200:
                st.balloons() # احتفال بنجاح العملية! 🎈
                st.success(f"✅ ممتاز! تم تسجيل طلبية ({customer}) بنجاح في ملف الإكسل.")
            else:
                st.error(f"حدث خطأ في الصلاحيات (كود: {response.status_code}). تأكد من إعداد Anyone في جوجل.")
        except Exception as e:
            st.error(f"فشل الاتصال: {e}")
    else:
        st.warning("⚠️ يرجى كتابة اسم الزبون أولاً.")

st.markdown("---")
st.caption("نظام حلباوي المستقل - الربط المباشر عبر Apps Script")
