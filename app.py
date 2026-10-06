import base64
import io
import json
import os
import time
import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="تطبيق استعلام الرواتب والعلاوات",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background: linear-gradient(180deg, #f0f4f8 0%, #e2e8f0 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 980px !important;
        margin: 0 auto;
    }

    .main-blue-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 22px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(30, 60, 114, 0.2);
    }
    .main-blue-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 26px;
        margin: 0;
        text-align: center;
    }
    .main-blue-header p {
        color: #e2e8f0;
        margin-top: 6px;
        font-size: 15px;
        font-weight: 400;
        text-align: center;
    }

    .info-card-top {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-top: 4px solid #0284c7;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);
    }
    
    .info-card-bottom {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-top: 4px solid #16a34a;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.08);
    }

    .info-card-date {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-top: 4px solid #d97706;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.08);
    }

    .card-label {
        font-size: 13px;
        color: #475569;
        font-weight: 700;
        margin-bottom: 4px;
        text-align: center !important;
    }
    .card-value {
        font-size: 17px;
        color: #0f172a;
        font-weight: 800;
        text-align: center !important;
    }

    .net-salary-box {
        background: linear-gradient(135deg, #d8b4fe 0%, #818cf8 50%, #34d399 100%);
        color: white;
        border-radius: 18px;
        padding: 22px;
        text-align: center !important;
        box-shadow: 0 8px 25px rgba(129, 140, 248, 0.3);
        margin: 25px auto 15px auto;
        max-width: 600px;
    }
    .net-salary-box h2 {
        color: #ffffff !important;
        margin: 0;
        font-size: 18px;
        font-weight: 700;
        text-align: center !important;
    }
    .net-salary-box h1 {
        color: #ffffff !important;
        margin: 8px 0 0 0;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 0.5px;
        text-align: center !important;
    }

    .custom-alert-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-right: 6px solid #059669;
        color: #065f46;
        padding: 18px 22px;
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
        text-align: center;
    }

    .custom-alert-danger {
        background: linear-gradient(135deg, #ffe4e6 0%, #fecdd3 100%);
        border-right: 6px solid #e11d48;
        color: #9f1239;
        padding: 18px 22px;
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.15);
        text-align: center;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

COMPANIES_FILE = "companies.json"
MASTER_PASSWORD = "SuperAdmin@Salary2026"

# ---------------------------------------------------------
# 2. إدارة الجلسة والدوال المساعدة
# ---------------------------------------------------------
if "is_super_admin" not in st.session_state:
    st.session_state["is_super_admin"] = False

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)
REPO_NAME = st.secrets.get("REPO_NAME", None)


def sync_file_to_github(file_path, commit_message="تحديث البيانات تلقائياً"):
    if not GITHUB_TOKEN or not REPO_NAME:
        return False
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        res_get = requests.get(url, headers=headers)
        sha = res_get.json().get("sha", None) if res_get.status_code == 200 else None

        with open(file_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "message": commit_message,
            "content": content_b64,
        }
        if sha:
            payload["sha"] = sha

        res_put = requests.put(url, json=payload, headers=headers)
        return res_put.status_code in [200, 201]
    except Exception as e:
        print(f"خطأ في المزامنة السحابية: {e}")
        return False


def load_companies():
    if os.path.exists(COMPANIES_FILE):
        try:
            with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
                companies = json.load(f)
                if "comp_default" in companies:
                    del companies["comp_default"]
                    save_companies(companies)
                return companies
        except:
            pass
    return {}


def save_companies(companies_dict):
    with open(COMPANIES_FILE, "w", encoding="utf-8") as f:
        json.dump(companies_dict, f, ensure_ascii=False, indent=4)
    sync_file_to_github(COMPANIES_FILE, "تحديث قائمة المؤسسات")


def load_company_data(data_file_path):
    if os.path.exists(data_file_path):
        try:
            if data_file_path.endswith(".csv"):
                df = pd.read_csv(data_file_path)
            else:
                df = pd.read_excel(data_file_path)
            df.columns = df.columns.astype(str).str.strip()
            return df
        except Exception as e:
            st.error(f"خطأ في قراءة ملف البيانات: {e}")
            return None
    return None


def fmt(val):
    try:
        if pd.isna(val):
            return "0 د.ع"
        return f"{float(val):,.0f} د.ع"
    except:
        return "0 د.ع"


def clean_date(val):
    if pd.isna(val) or str(val).strip() in ["", "nan", "None", "-"]:
        return "-"
    val_str = str(val).split("T")[0].split(" ")[0].strip()
    return val_str


def find_emp_field(emp_row, keywords):
    """دالة مرنة لاستخراج القيمة من السطر بغض النظر عن المسافات أو مسمى العمود الدقيق"""
    for col_name in emp_row.index:
        col_clean = " ".join(str(col_name).split())
        for kw in keywords:
            if kw in col_clean:
                val = emp_row[col_name]
                if pd.notna(val) and str(val).strip() not in ["", "nan", "None"]:
                    return val
    return "-"


# ---------------------------------------------------------
# 3. القائمة الجانبية: تسجيل دخول مدير النظام العام
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.markdown("### 👑 مدير النظام العام")

    if not st.session_state["is_super_admin"]:
        admin_pass_input = st.text_input(
            "كلمة مرور مدير النظام:",
            type="password",
            key="sidebar_master_pass",
            placeholder="••••••••",
        )
        if st.button("🔑 تسجيل الدخول", use_container_width=True, type="primary"):
            if admin_pass_input == MASTER_PASSWORD:
                st.session_state["is_super_admin"] = True
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
    else:
        st.success("🟢 أنت الآن مسجّل كـ مدير النظام العام")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state["is_super_admin"] = False
            st.rerun()

# ---------------------------------------------------------
# 4. الهيكل الرئيسي للتطبيق
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-blue-header">
        <h1>💳 تطبيق استعلام مفردات الراتب والتنشيط الوظيفي</h1>
        <p>النظام الموحد لاستعلام الرواتب وتواريخ العلاوات والترقيات</p>
    </div>
""",
    unsafe_allow_html=True,
)

companies = load_companies()

if st.session_state["is_super_admin"]:
    tab_titles = ["🔒 استعلام الموظف", "⚙️ إدارة المؤسسات", "➕ إضافة مؤسسة", "🗑️ حذف مؤسسة"]
else:
    tab_titles = ["🔒 استعلام الموظف", "⚙️ إدارة المؤسسات"]

tabs = st.tabs(tab_titles)

# =========================================================
# الواجهة الأولى: استعلام الموظف
# =========================================================
with tabs[0]:
    st.subheader("🔑 إدخال بيانات الاستعلام")

    if not companies:
        st.info("ℹ️ لا توجد مؤسسات مضافة في النظام حالياً. يرجى مراجعة مدير النظام لإضافة مؤسستك.")
    else:
        comp_options = {v["name"]: k for k, v in companies.items()}
        selected_comp_name = st.selectbox("اختر المؤسسة / الشركة التابع لها:", list(comp_options.keys()))
        selected_comp_key = comp_options[selected_comp_name]
        comp_info = companies[selected_comp_key]

        col_input1, col_input2 = st.columns(2)
        with col_input1:
            emp_id = st.text_input("الرقم الوظيفي:", placeholder="مثال: 101", key="emp_id")
        with col_input2:
            secret_code = st.text_input("الكود الخاص / الرمز السري:", type="password", placeholder="••••••••", key="code")

        btn_search = st.button("🔍 عرض مفردات الراتب والعلاوة", use_container_width=True, type="primary")

        if btn_search:
            df = load_company_data(comp
