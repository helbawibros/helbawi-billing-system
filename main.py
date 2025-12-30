import streamlit as st
import pandas as pd
from gspread_pandas import Spread
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

# رابط ملفك الذي جعلته "Anyone with the link can edit"
# تأكد من وضع الرابط الخاص بك هنا
file_url = "https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/edit"

st.title("📄 نظام تسجيل الطلبيات")

# مدخلات بسيطة
customer_name = st.text_input("اسم الزبون")
product = st.selectbox("الصنف", ["حمص رقم 12", "حمص رقم 9", "فول حب"])
qty = st.number_input("العدد", min_value=1)

if st.button("💾 حفظ وإرسال"):
    if customer_name:
        try:
            # استخدام المكتبة للحفظ المباشر عبر الرابط العام
            spread = Spread(file_url)
            
            # تجهيز البيانات
            new_data = pd.DataFrame([{
                "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                "الزبون": customer_name,
                "الصنف": product,
                "العدد": qty
            }])
            
            # إضافة البيانات لآخر الملف
            spread.df_to_sheet(new_data, index=False, sheet=0, start='A1', replace=False)
            
            st.balloons()
            st.success("✅ تم الحفظ بنجاح في الإكسل!")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
            st.info("تأكد أن الملف في جوجل شيت مضبوط على: Anyone with the link can EDIT")
    else:
        st.warning("الرجاء إدخال اسم الزبون")
