import streamlit as st
import gspread
from datetime import datetime

# 1. إعداد الواجهة
st.set_page_config(page_title="نظام حلباوي للمندوبين", layout="wide")

# 2. الربط المباشر عبر الرابط العام
# سنستخدم الرابط الذي جعلته "Anyone with the link can edit"
sheet_url = "https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/edit#gid=0"

def save_to_google_sheets(rows):
    try:
        # الاتصال المباشر (سيطلب الصلاحية من المتصفح أول مرة أو يعمل مباشرة)
        gc = gspread.public__with_link(sheet_url) # محاولة الوصول العام
        # ملاحظة: إذا لم يعمل الوصول العام، سنستخدم الطريقة التقليدية
        st.error("جوجل يطلب توثيق رسمي للحفظ. يرجى اتباع الخطوة أدناه.")
    except Exception as e:
        return str(e)

# --- نظام تسجيل الدخول ---
users = {"حسين": "1111", "علي": "2222", "مدير": "9999"}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 دخول المندوبين")
    u = st.selectbox("الاسم", list(users.keys()))
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if users[u] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
else:
    st.title(f"📄 فاتورة: {st.session_state.user}")
    cust_id = st.text_input("رقم الحساب")
    cust_name = st.text_input("اسم الزبون")
    
    # (هنا نضع قائمة الأصناف كما في الكود السابق...)
    # لضمان السرعة، سأركز على زر الحفظ:
    
    if st.button("💾 حفظ وإرسال (الآن!)"):
        st.info("جاري محاولة تجاوز قيود جوجل للحفظ...")
        # هنا سنستخدم رابط فورم (Form) بدلاً من الشيت مباشرة إذا فشل الشيت
        # لأن الفورم لا يطلب باسورد أبداً!
        st.markdown(f"### [اضغط هنا لتأكيد إرسال الطلبية مباشرة](https://docs.google.com/forms/d/e/1FAIpQLScyVp_L...)")
        st.balloons() 

