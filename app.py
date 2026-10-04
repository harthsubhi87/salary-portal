import io
import json
import os
import time
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="تطبيق استعلام الرواتب",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
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
        max-width: 950px !important;
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
        padding: 16px 20px;
        margin-bottom: 15px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);
    }
    
    .info-card-bottom {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-top: 4px solid #16a34a;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.08);
    }

    .card-label {
        font-size: 14px;
        color: #475569;
        font-weight: 700;
        margin-bottom: 4px;
        text-align: center !important;
    }
    .card-value {
        font-size: 18px;
        color: #0f172a;
        font-weight: 800;
        text-align: center !important;
    }

    .net-salary-box {
        background: linear-gradient(135deg, #d8b4fe 0%, #818cf8 50%, #34d399 100%);
        color: white;
        border-radius: 18px;
        padding: 24px;
        text-align: center !important;
        box-shadow: 0 8px 25px rgba(129, 140, 248, 0.3);
        margin: 25px auto 15px auto;
        max-width: 600px;
    }
    .net-salary-box h2 {
        color: #ffffff !important;
        margin: 0;
        font-size: 19px;
        font-weight: 700;
        text-align: center !important;
    }
    .net-salary-box h1 {
        color: #ffffff !important;
        margin: 10px 0 0 0;
        font-size: 36px;
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
    .custom-alert-success h3 { color: #065f46 !important; margin: 0 0 5px 0; font-size: 20px; font-weight: 800; }
    .custom-alert-success p { margin: 0; font-size: 15px; font-weight: 600; }

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
    .custom-alert-danger h3 { color: #9f1239 !important; margin: 0 0 5px 0; font-size: 20px; font-weight: 800; }
    .custom-alert-danger p { margin: 0; font-size: 15px; font-weight: 600; }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

COMPANIES_FILE = "companies.json"

# ---------------------------------------------------------
# 2. إدارة قاعدة البيانات
# ---------------------------------------------------------
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

def load_company_data(data_file_path):
    if os.path.exists(data_file_path):
        try:
            if data_file_path.endswith('.csv'):
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

# ---------------------------------------------------------
# 3. الهيكل الرئيسي للتطبيق
# ---------------------------------------------------------

st.markdown(
    """
    <div class="main-blue-header">
        <h1>💳 تطبيق استعلام مفردات الراتب الشهري</h1>
        <p>النظام الموحد لاستعلام الرواتب لكافة المؤسسات والشركات</p>
    </div>
""",
    unsafe_allow_html=True,
)

companies = load_companies()

tabs = st.tabs(
    ["🔒 استعلام الموظف", "⚙️ إدارة المؤسسات", "➕ إضافة مؤسسة", "🗑️ حذف مؤسسة"]
)

# =========================================================
# الواجهة الأولى: استعلام الموظف
# =========================================================
with tabs[0]:
    st.subheader("🔑 إدخال بيانات الاستعلام")

    if not companies:
        st.info(
            "ℹ️️ لا توجد مؤسسات مضافة في النظام حالياً. يرجى إضافة مؤسسة من تبويب (➕ إضافة مؤسسة)."
        )
    else:
        comp_options = {v["name"]: k for k, v in companies.items()}
        selected_comp_name = st.selectbox(
            "اختر المؤسسة / الشركة التابع لها:", list(comp_options.keys())
        )
        selected_comp_key = comp_options[selected_comp_name]
        comp_info = companies[selected_comp_key]

        col_input1, col_input2 = st.columns(2)
        with col_input1:
            emp_id = st.text_input(
                "الرقم الوظيفي:", placeholder="مثال: 1001", key="emp_id"
            )
        with col_input2:
            secret_code = st.text_input(
                "الكود الخاص / الرمز السري:",
                type="password",
                placeholder="••••••••",
                key="code",
            )

        btn_search = st.button(
            "🔍 عرض مفردات الراتب", use_container_width=True, type="primary"
        )

        if btn_search:
            df = load_company_data(comp_info["data_file"])
            if df is None:
                st.warning(
                    f"⚠️️ لم يتم رفع كشف الرواتب لهذا الشهر لمؤسسة ({selected_comp_name}) بعد."
                )
            elif not emp_id or not secret_code:
                st.error(
                    "يرجى إدخال الرقم الوظيفي والكود الخاص بك لاستكمال الاستعلام."
                )
            else:
                if "الرقم الوظيفي" not in df.columns or "كود الموظف" not in df.columns:
                    st.error(
                        "خطأ في بنية ملف البيانات لهذه المؤسسة: يجب أن يحتوي الملف على عمودي 'الرقم الوظيفي' و 'كود الموظف'."
                    )
                else:
                    df["الرقم الوظيفي_str"] = (
                        df["الرقم الوظيفي"].astype(str).str.strip()
                    )
                    df["كود الموظف_str"] = df["كود الموظف"].astype(str).str.strip()

                    match = df[
                        (df["الرقم الوظيفي_str"] == str(emp_id).strip())
                        & (df["كود الموظف_str"] == str(secret_code).strip())
                    ]

                    if not match.empty:
                        emp = match.iloc[0]
                        st.success(
                            f"✅ تم العثور على سجل الموظف بنجاح في ({selected_comp_name})!"
                        )

                        st.markdown(
                            "<h3 style='text-align:center;'>👤 البيانات الوظيفية</h3>",
                            unsafe_allow_html=True,
                        )
                        st.write("")

                        col_top1, col_top2 = st.columns(2)
                        with col_top1:
                            st.markdown(
                                f"""
                                <div class="info-card-top">
                                    <div class="card-label">اسم الموظف</div>
                                    <div class="card-value">{emp.get('اسم الموظف', '-')}</div>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )
                        with col_top2:
                            st.markdown(
                                f"""
                                <div class="info-card-top">
                                    <div class="card-label">العنوان الوظيفي</div>
                                    <div class="card-value">{emp.get('عنوان وظيفي', '-')}</div>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        col_bot1, col_bot2 = st.columns(2)
                        with col_bot1:
                            st.markdown(
                                f"""
                                <div class="info-card-bottom">
                                    <div class="card-label">الدرجة الوظيفية</div>
                                    <div class="card-value">{emp.get('الدرجة الوظيفية', '-')}</div>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )
                        with col_bot2:
                            st.markdown(
                                f"""
                                <div class="info-card-bottom">
                                    <div class="card-label">المرحلة</div>
                                    <div class="card-value">{emp.get('المرحلة', '-')}</div>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("---")

                        st.markdown(
                            "<h3 style='text-align:center;'>📋 كشف تفاصيل ومفردات الراتب</h3>",
                            unsafe_allow_html=True,
                        )
                        st.write("")

                        col_earn, col_ded = st.columns(2)

                        with col_earn:
                            st.markdown(
                                "<h4 style='text-align:center; color:#1e3c72;'>📈 الاستحقاقات والبدلات</h4>",
                                unsafe_allow_html=True,
                            )
                            earn_data = {
                                "مفردات الاستحقاق": [
                                    "الراتب الاسمي",
                                    "مخصصات الزوجية",
                                    "مخصصات الأطفال",
                                    "مخصصات المنصب",
                                    "مخصصات الشهادة",
                                    "موقع جغرافي",
                                    "مخصصات مهنية",
                                    "مخصصات هندسية",
                                    "مخصصات الخطورة",
                                    "الإضافات الأخرى",
                                ],
                                "المبلغ": [
                                    fmt(emp.get("الراتب الاسمي", 0)),
                                    fmt(emp.get("الزوجية", 0)),
                                    fmt(emp.get("الاطفال", 0)),
                                    fmt(emp.get("المنصب", 0)),
                                    fmt(emp.get("الشهادة", 0)),
                                    fmt(emp.get("موقع جغرافي", 0)),
                                    fmt(emp.get("مهنية", 0)),
                                    fmt(emp.get("الهندسية", 0)),
                                    fmt(emp.get("الخطورة", 0)),
                                    fmt(emp.get("الاضافات", 0)),
                                ],
                            }
                            df_earn = pd.DataFrame(earn_data)
                            st.dataframe(df_earn, use_container_width=True, hide_index=True)

                            st.info(
                                f"**إجمالي الاستحقاقات: {fmt(emp.get('المجموع', 0))}**"
                            )

                        with col_ded:
                            st.markdown(
                                "<h4 style='text-align:center; color:#780206;'>📉 الخصومات والاستقطاعات</h4>",
                                unsafe_allow_html=True,
                            )
                            ded_data = {
                                "مفردات الاستقطاع": [
                                    "استقطاع التقاعد",
                                    "ضريبة الدخل",
                                    "الضمان الاجتماعي",
                                    "استقطاعات أخرى",
                                ],
                                "المبلغ": [
                                    fmt(emp.get("التقاعد", 0)),
                                    fmt(emp.get("الضريبة", 0)),
                                    fmt(emp.get("الضمان الاجتماعي", 0)),
                                    fmt(emp.get("الاستقطاعات", 0)),
                                ],
                            }
                            df_ded = pd.DataFrame(ded_data)
                            st.dataframe(df_ded, use_container_width=True, hide_index=True)

                            st.warning(
                                f"**إجمالي الاستقطاعات: {fmt(emp.get('المجموع.1', 0))}**"
                            )

                        st.markdown(
                            f"""
                            <div class="net-salary-box">
                                <h2>💰 صافي الراتب المستحق للقبض</h2>
                                <h1>{fmt(emp.get('الصافي', 0))}</h1>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    else:
                        st.error(
                            "❌ البيانات المدخلة غير صحيحة. يرجى التأكد من الرقم الوظيفي والكود الخاص والمؤسسة المختارة."
                        )

# =========================================================
# الواجهة الثانية: لوحة تحكم إدارة مؤسسة
# =========================================================
with tabs[1]:
    st.subheader("⚙️ لوحة إدارة كشف رواتب المؤسسة")

    if not companies:
        st.warning("⚠️ لا توجد مؤسسات مسجلة في النظام بعد.")
    else:
        admin_comp_options = {v["name"]: k for k, v in companies.items()}
        admin_selected_comp_name = st.selectbox(
            "اختر المؤسسة التي تديرها:",
            list(admin_comp_options.keys()),
            key="admin_comp_select",
        )
        admin_comp_key = admin_comp_options[admin_selected_comp_name]
        target_comp = companies[admin_comp_key]

        admin_pass_input = st.text_input(
            f"أدخل كلمة مرور إدارة ({admin_selected_comp_name}):",
            type="password",
            key="admin_login_pass_multi",
        )

        if admin_pass_input == target_comp["password"]:
            st.success(
                f"تم تسجيل الدخول بصلاحيات إدارة ({admin_selected_comp_name}) بنجاح."
            )

            admin_subtabs = st.tabs(
                ["📤 رفع كشف الراتب الشهري", "🔐 تغيير كلمة مرور المؤسسة"]
            )

            # 1. رفع الملف وتحميل النماذج
            with admin_subtabs[0]:
                st.markdown(f"### 📥 تحميل قالب كشف الرواتب المعتمد (Template)")
                st.info("💡 يمكنك تحميل ملف النموذج الفارغ بصيغة Excel المجهز بكافة الأعمدة، ثم تعبئته ورفعه:")

                template_data = pd.DataFrame([{
                    "الرقم الوظيفي": 1001,
                    "كود الموظف": "1234",
                    "اسم الموظف": "أحمد محمد علي",
                    "عنوان وظيفي": "مهندس قدم",
                    "الدرجة الوظيفية": "الثالثة",
                    "المرحلة": "2",
                    "الراتب الاسمي": 600000,
                    "الزوجية": 50000,
                    "الاطفال": 30000,
                    "المنصب": 100000,
                    "الشهادة": 150000,
                    "موقع جغرافي": 20000,
                    "مهنية": 0,
                    "الهندسية": 100000,
                    "الخطورة": 50000,
                    "الاضافات": 0,
                    "المجموع": 1100000,
                    "التقاعد": 60000,
                    "الضريبة": 15000,
                    "الضمان الاجتماعي": 0,
                    "الاستقطاعات": 25000,
                    "المجموع.1": 100000,
                    "الصافي": 1000000
                }])

                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    template_data.to_excel(writer, index=False, sheet_name="Salary_Template")

                st.download_button(
                    label="📥 تحميل قالب الإكسل النموذجي (Salary_Template.xlsx)",
                    data=excel_buffer.getvalue(),
                    file_name="Salary_Template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="secondary"
                )

                st.markdown("---")
                st.markdown(f"### 📤 رفع ملف الإكسل الشهري لـ ({admin_selected_comp_name})")
                uploaded_excel = st.file_uploader(
                    "اختر ملف الإكسل أو CSV المعبأ",
                    type=["xlsx", "xls", "csv"],
                    key="multi_uploader",
                )

                if uploaded_excel is not None:
                    try:
                        if uploaded_excel.name.endswith('.csv'):
                            new_df = pd.read_csv(uploaded_excel)
                        else:
                            new_df = pd.read_excel(uploaded_excel)
                        
                        new_df.columns = new_df.columns.astype(str).str.strip()

                        required_cols = [
                            "الرقم الوظيفي",
                            "كود الموظف",
                            "اسم الموظف",
                            "الصافي",
                        ]
                        missing_cols = [
                            c for c in required_cols if c not in new_df.columns
                        ]

                        if missing_cols:
                            st.error(
                                "❌ الملف المرفوع تنقصه الأعمدة التالية:"
                                f" {', '.join(missing_cols)}"
                            )
                        else:
                            new_df.to_excel(target_comp["data_file"], index=False)
                            st.success(
                                "✅ تم تحديث كشف الرواتب الخاص بـ"
                                f" ({admin_selected_comp_name}) بنجاح!"
                            )

                            st.markdown("#### 📊 ملخص الكشف المرفوع:")
                            stat_col1, stat_col2, stat_col3 = st.columns(3)
                            stat_col1.metric("إجمالي الموظفين", len(new_df))
                            stat_col2.metric(
                                "إجمالي الرواتب الصافية", fmt(new_df["الصافي"].sum())
                            )
                            stat_col3.metric(
                                "متوسط صافي الراتب", fmt(new_df["الصافي"].mean())
                            )

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

            # 2. تغيير كلمة المرور
            with admin_subtabs[1]:
                st.markdown(
                    f"### 🔐 تغيير كلمة مرور إدارة ({admin_selected_comp_name})"
                )

                with st.form("change_comp_pass_form"):
                    new_pass = st.text_input("كلمة المرور الجديدة:", type="password")
                    confirm_pass = st.text_input(
                        "تأكيد كلمة المرور الجديدة:", type="password"
                    )
                    submit_pass = st.form_submit_button("💾 حفظ كلمة المرور")

                    if submit_pass:
                        if not new_pass:
                            st.error("يرجى إدخال كلمة مرور جديدة.")
                        elif new_pass != confirm_pass:
                            st.error("كلمتا المرور غير متطابقتين.")
                        else:
                            companies[admin_comp_key]["password"] = new_pass
                            save_companies(companies)
                            st.success("✅ تم تحديث كلمة المرور الخاصة بالمؤسسة بنجاح!")

        elif admin_pass_input != "":
            st.error("كلمة المرور غير صحيحة.")

# =========================================================
# الواجهة الثالثة: إضافة مؤسسة جديدة
# =========================================================
with tabs[2]:
    st.subheader("➕ تسجيل وإضافة مؤسسة جديدة للنظام")
    st.info(
        "يتطلب إضافة مؤسسة جديدة إدخال كلمة مرور مدير النظام العام (Super Admin Master Password)."
    )

    master_pass_input = st.text_input(
        "أدخل كلمة مرور مدير النظام العام:", type="password", key="master_pass"
    )
    MASTER_PASSWORD = "hsj1987hsj"

    if master_pass_input == MASTER_PASSWORD:
        st.success(
            "مرحباً بك يا مدير النظام الرئيسي. يمكنك الآن إضافة مؤسسة جديدة وتخصيص كلمة مرور لها."
        )

        with st.form("add_company_form"):
            new_comp_name = st.text_input(
                "اسم المؤسسة / الشركة الجديدة:", placeholder="مثال: شركة النور للمقاولات"
            )
            new_comp_pass = st.text_input(
                "كلمة مرور الإدارة الخاصة بهذه المؤسسة:",
                type="password",
                placeholder="••••••••",
            )
            submit_add = st.form_submit_button("✨ إنشاء وإضافة المؤسسة")

            if submit_add:
                if not new_comp_name or not new_comp_pass:
                    st.error("يرجى تعبئة جميع الحقول المطلوبة.")
                else:
                    new_key = f"comp_{int(time.time())}"
                    new_data_file = f"Salary_{new_key}.xlsx"

                    companies[new_key] = {
                        "name": new_comp_name,
                        "password": new_comp_pass,
                        "data_file": new_data_file,
                    }
                    save_companies(companies)

                    st.markdown(
                        f"""
                        <div class="custom-alert-success">
                            <h3>🎉 تم إضافة المؤسسة بنجاح!</h3>
                            <p>تم اعتماد مؤسسة <b>({new_comp_name})</b> وإضافتها لدليل النظام الموحد.</p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

    elif master_pass_input != "":
        st.error("كلمة مرور مدير النظام العام غير صحيحة.")

# =========================================================
# الواجهة الرابعة: حذف مؤسسة
# =========================================================
with tabs[3]:
    st.subheader("🗑️ حذف مؤسسة من النظام")

    master_pass_del = st.text_input(
        "أدخل كلمة مرور مدير النظام العام للتحقق:",
        type="password",
        key="master_pass_del",
    )

    if master_pass_del == "SuperAdmin@Salary2026":
        if not companies:
            st.info("لا توجد مؤسسات مضافة حالياً لحذفها.")
        else:
            del_comp_options = {v["name"]: k for k, v in companies.items()}
            del_selected_name = st.selectbox(
                "اختر المؤسسة المراد حذفها نهائياً:", list(del_comp_options.keys())
            )
            del_key = del_comp_options[del_selected_name]

            if st.button("🚨 حذف المؤسسة وكشف رواتبها نهائياً", type="primary"):
                file_to_del = companies[del_key].get("data_file")
                if file_to_del and os.path.exists(file_to_del):
                    try:
                        os.remove(file_to_del)
                    except:
                        pass

                del companies[del_key]
                save_companies(companies)

                st.markdown(
                    f"""
                    <div class="custom-alert-danger">
                        <h3>🗑️ تم حذف المؤسسة بنجاح</h3>
                        <p>تم إزالة <b>({del_selected_name})</b> وكافة بياناتها نهائياً.</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
