import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="شركة حلباوي إخوان", layout="centered")

# --- 2. الربط بملف الإكسل (بياناتك من الرابط) ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID = "339292430"
# رابط محدث لضمان القراءة الصحيحة
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

@st.cache_data(ttl=60)
def load_products():
    try:
        # قراءة البيانات والتأكد من حذف أي مسافات زائدة في أسماء الأعمدة
        df_p = pd.read_csv(sheet_url)
        df_p.columns = df_p.columns.str.strip() 
        # جلب البيانات من عمود "الاسم" وعمود "السعر"
        return pd.Series(df_p['السعر'].values, index=df_p['الاسم']).to_dict()
    except Exception as e:
        # رسالة تنبيه توضح نوع الخطأ إذا استمر
        return {f"⚠️ خطأ: تأكد من أسماء الأعمدة (الاسم، السعر) في الإكسل": 0.0}

PRODUCTS = load_products()

# --- بقية الكود كما هو (دالة الإرسال، المستخدمين، منطق التطبيق) ---
# انسخ بقية الكود الذي أرسلته لك سابقاً من قسم USERS فما دون ليعمل النظام بالكامل.
