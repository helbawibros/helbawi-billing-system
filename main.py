import streamlit as st
import pandas as pd
import random
from datetime import datetime
from gspread_streamlit import gspread_connect

# --- 1. إعدادات الصفحة والتنسيق المتطور (إخفاء النصوص المزعجة) ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* إخفاء نصوص المساعدة المزعجة تماماً */
    div[data-testid="InputInstructions"] { display: none !important; }
    div[data-baseweb="helper-text"] { display: none !important; }
    header {visibility: hidden;}
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    /* تنسيق الجدول والحدود (الزيح) */
    th { background-color: #1E3A8A !important; color: white !important; text-align: center !important; border: 1px solid #dee2e6 !important; }
    td { text-align: center !important; border: 1px solid #dee2e6 !important; padding: 8px !important; }
    table { border-collapse: collapse !important; width: 100%; }

    /* تنسيق منطقة الحسابات */
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 18px; border-bottom: 1px solid #eee; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات والأصناف والاتصال ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ازر مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

# دالة الاتصال بـ Google Sheets لضمان وصول البيانات
def save_to_google_sheets(items, client_name, inv_no, user_name):
    try:
        conn = gspread_connect(st.secrets["gcp_service_account"]) # تأكد من وجود ملف الأسرار
        sh = conn.open("Helbawi_Database")
        worksheet = sh.get_worksheet(0)
        for item in items:
            row = [
                str(datetime.now().strftime("%Y-%m-%d %H:%M")), # الوقت
                user_name,       # المندوب
                inv_no,          # رقم الفاتورة
                client_name,     # اسم الزبون
                item["الصنف"],    # الصنف
                item["العدد"],     # العدد
                item["السعر"],     # السعر
                item["الإجمالي"]   # الإجمالي
            ]
            worksheet.append_row(row)
        return True
    except:
        return False

# إدارة الحالة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'temp_items' not in st.session_state: st.session_state.temp_items = []
if 'inv_no' not in st.session_state: st.session_state.inv_no = str(random.randint(1000, 9999))
if 'confirmed' not in st.session_state: st.session_state.confirmed = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- 3. نظام الصفحات ---

if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user) == pwd:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.page = True, user, 'home'
            st.rerun()

elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page, st.session_state.temp_items, st.session_state.confirmed = 'order', [], False
        st.rerun()

elif st.session_state.page == 'order':
    st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    cust = st.text_input("اسم الزبون (المحل)", value="", key="cust_name")
    disc_input = st.text_input("الحسم %", value="0", key="disc_input")
    
    st.divider()
    
    search = st.text_input("🔍 ابحث عن صنف...", value="", key="search_box")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
    
    # العدد فارغ تماماً
    qty_str = st.text_input("العدد", value="", key="qty_box")

    col_add, col_fix = st.columns(2)
    with col_add:
        if st.button("➕ إضافة للصنف", use_container_width=True):
            if sel_p != "-- اختر الصنف --" and qty_str != "":
                q = float(convert_ar_nav(qty_str))
                price = PRODUCTS[sel_p]
                vat = (price * q * 0.11) if "*" in sel_p else 0.0
                total = (price * q) + vat
                st.session_state.temp_items.append({
                    "الصنف": sel_p, "العدد": int(q), "السعر": price, "VAT": vat, "الإجمالي": total
                })
                st.session_state.confirmed = False
                st.toast(f"تمت إضافة {sel_p}")

    with col_fix:
        if st.button("✅ ثبت", use_container_width=True, type="primary"):
            st.session_state.confirmed = True

    if st.session_state.confirmed and st.session_state.temp_items:
        st.markdown("---")
        # الزبون يمين والمندوب يسار
        c_r, c_l = st.columns(2)
        with c_r: st.markdown(f"**الزبون:** {cust}")
        with c_l: st.markdown(f"<div style='text-align:left;'>**المندوب:** {st.session_state.user_name}</div>", unsafe_allow_html=True)
        
        df = pd.DataFrame(st.session_state.temp_items)
        df_disp = df.copy()
        for col in ["السعر", "VAT", "الإجمالي"]: df_disp[col] = df_disp[col].map("{:,.2f}".format)
        st.table(df_disp) # الجدول مع حدود واضحة
        
        # الحسابات المالية
        raw_total = sum(df["العدد"] * df["السعر"])
        h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
        discount_amount = raw_total * (h_val / 100)
        total_vat = sum(df["VAT"])
        final_net = (raw_total - discount_amount) + total_vat
        
        st.markdown(f"""
            <div class="summary-container">
                <div class="summary-row"><span>المجموع (قبل الحسم):</span><span>${raw_total:,.2f}</span></div>
                <div class="summary-row"><span>قيمة الحسم ({h_val}%):</span><span>-${discount_amount:,.2f}</span></div>
                <div class="summary-row"><span>ضريبة VAT إجمالية:</span><span>+${total_vat:,.2f}</span></div>
                <div class="final-total">الصافي النهائي: ${final_net:,.2f}</div>
                <div class="lbp-box">قيمة الـ VAT بالليرة (سعر 89,500): <br> {int(total_vat * 89500):,} ل.ل.</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
            if save_to_google_sheets(st.session_state.temp_items, cust, st.session_state.inv_no, st.session_state.user_name):
                st.success("✅ تم الإرسال لملف الإكسل بنجاح!")
            else:
                st.error("❌ فشل الإرسال، يرجى التحقق من اتصال الإنترنت")
