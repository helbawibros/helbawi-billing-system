import streamlit as st
import requests

# هذا هو الرابط السحري الذي استخرجته أنت من صورك
URL_LINK = "https://script.google.com/macros/s/AKfycyb8jgJRAQwW2oc4pOE4Med1pwb3NQ79m2p5f1q3-Wg9RfK4l6YkODMgWe6KGeRAY3HmA/exec"

st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="centered")

# تصميم بسيط وواضح
st.title("🚀 نظام تسجيل الطلبيات - حلباوي")
st.markdown("---")

# نموذج إدخال البيانات داخل إطار (Form) لضمان الترتيب
with st.form("order_form", clear_on_submit=True):
    st.subheader("إدخال بيانات الزبون")
    mandoub = st.selectbox("اسم المندوب", ["حسين", "علي", "مدير"])
    customer = st.text_input("اسم الزبون (أو رقم الحساب)")
    
    st.divider()
    
    st.subheader("تفاصيل الطلبية")
    product = st.selectbox("الصنف", [
        "حمص رقم 12 907غ", 
        "حمص رقم 9 907غ", 
        "حمص كسر 1000غ", 
        "فول حب 1000غ", 
        "فول مجروش 1000غ", 
        "فول عريض 1000غ"
    ])
    quantity = st.number_input("العدد (كمية)", min_value=1, step=1)
    
    # زر الحفظ
    submit_button = st.form_submit_button("💾 حفظ وإرسال للشركة")

# معالجة الضغط على الزر
if submit_button:
    if customer:
        # تجهيز البيانات للإرسال إلى جوجل شيت
        payload = {
            "user": mandoub,
            "customer": customer,
            "item": product,
            "qty": quantity
        }
        
        try:
            # إرسال البيانات للرابط الذي أنشأته
            with st.spinner("جاري الحفظ..."):
                response = requests.post(URL_LINK, json=payload)
            
            if response.status_code == 200:
                st.balloons() # طيران البالونات احتفالاً بالنجاح!
                st.success(f"✅ مبروك! تم تسجيل طلبية ({customer}) في ملف الإكسل بنجاح.")
            else:
                st.error("فشل في الاتصال، تأكد من أنك قمت بعمل Deploy بشكل صحيح.")
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {e}")
    else:
        st.warning("⚠️ يرجى كتابة اسم الزبون قبل الحفظ.")

st.markdown("---")
st.caption("نظام حلباوي الخاص - يعمل مباشرة مع Google Sheets")
