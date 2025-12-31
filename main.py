import streamlit as st
import pandas as pd
import random

# --- 1. إعدادات الصفحة والتنسيق المتطور ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* إخفاء نص "Press Enter to apply" ونصوص المساعدة المزعجة */
    div[data-testid="InputInstructions"] { display: none !important; }
    div[data-baseweb="helper-text"] { display: none !important; }
    
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}
    
    /* تنسيق جدول البيانات ليظهر الزيح بوضوح */
    th { background-color: #1E3A8A !important; color: white !important; text-align: center !important; border: 1px solid #ffffff !important; }
    td { text-align: center !important; border: 1px solid #dee2e6 !important; padding: 8px !important; }
    
    /* تنسيق منطقة الحسابات تحت الجدول */
    .summary-container { border-top: 2px solid #1E3A8A; margin-top: 20px; padding-top: 10px; }
    .summary-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 18px; border-bottom: 1px solid #eee; }
    .final-total { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; padding: 10px; border-radius: 5px; margin-top: 10px; }
    .lbp-box { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات والأصناف ---
USERS = {"محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

PRODUCTS = {
    "حمص١٢ ٩٠٧غ": 2.20, "حمص٩ ٩٠٧ غ": 2.00, "عدس مجروش ٩٠٧غ": 1.75, "عدس عريض٩٠٧غ": 1.90,
    "عدس احمر ٩٠٧غ": 1.75, "ازر مصري ٩٠٧غ": 1.15, "ارز ايطالي ٩٠٧ غ": 2.25, "ارز عنبري ١٠٠٠غ": 1.90,
    "*سبع بهارات ٥٠غ*١٢": 10.00, "*بهار كبسه٥٠غ*١٢": 10.00, "*بهار سمك٥٠غ*١٢": 8.00
}

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
            st.session_state.logged_in = True
            st.session_state.user_name = user
            st.session_state.page = 'home'
            st.rerun()

elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً {st.session_state.user_name}</h3><p style="color:green; font-weight:bold;">ببركة الصلاة على محمد وال محمد ابدأ تسجيل الفاتورة</p></div>', unsafe_allow_html=True)
    if st.button("📝 تسجيل فاتورة جديدة", use_container_width=True, type="primary"):
        st.session_state.page = 'order'
        st.session_state.temp_items = []
        st.session_state.confirmed = False
        st.rerun()

elif st.session_state.page == 'order':
    st.markdown(f'<h3 style="text-align:center;">رقم الفاتورة: {st.session_state.inv_no}</h3>', unsafe_allow_html=True)
    cust = st.text_input("اسم الزبون (المحل)", value="")
    disc_input = st.text_input("الحسم %", value="0")
    
    st.divider()
    
    search = st.text_input("🔍 ابحث عن صنف...", value="")
    filtered = [p for p in PRODUCTS.keys() if search in p] if search else list(PRODUCTS.keys())
    sel_p = st.selectbox("اختر الصنف", ["-- اختر الصنف --"] + filtered)
    
    # خانة العدد فارغة افتراضياً (باستخدام نص ليتمكن المستخدم من المسح)
    qty_str = st.text_input("العدد", value="")

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
        # رأس الجدول: المندوب يسار والزبون يمين
        col_header_r, col_header_l = st.columns(2)
        with col_header_r: st.markdown(f"**الزبون:** {cust}")
        with col_header_l: st.markdown(f"<div style='text-align:left;'>**المندوب:** {st.session_state.user_name}</div>", unsafe_allow_html=True)
        
        df = pd.DataFrame(st.session_state.temp_items)
        # تنسيق الأرقام في الجدول
        df_display = df.copy()
        for col in ["السعر", "VAT", "الإجمالي"]:
            df_display[col] = df_display[col].map("{:,.2f}".format)
        st.table(df_display)
        
        # --- منطقة الحسابات النهائية ---
        raw_total = sum(df["العدد"] * df["السعر"].astype(float))
        h_val = float(convert_ar_nav(disc_input)) if disc_input else 0
        discount_amount = raw_total * (h_val / 100)
        total_vat = sum(df["VAT"].astype(float))
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
        
        st.write("")
        if st.button("💾 حفظ وإرسال للشركة", use_container_width=True):
            st.success("✅ تم حفظ الطلبية بنجاح!")

    if st.button("🔙 عودة للرئيسية"):
        st.session_state.page = 'home'
        st.rerun()

