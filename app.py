import streamlit as st
import pandas as pd
import os
import json

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="بوابة استعلام الرواتب الشهرية",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تطبيق اتجاه النص العربي فقط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    /* جعل العرض يرتكز بالمنتصف */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "Salary_Current.xlsx"
CONFIG_FILE = "config.json"
DEFAULT_ADMIN_PASS = "Admin@Salary2026"

# ---------------------------------------------------------
# 2. إدارة البيانات وكلمة المرور
# ---------------------------------------------------------
def get_admin_password():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("admin_password", DEFAULT_ADMIN_PASS)
        except:
            return DEFAULT_ADMIN_PASS
    return DEFAULT_ADMIN_PASS

def save_admin_password(new_password):
    config = {"admin_password": new_password}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
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
st.title("💳 بوابة استعلام مفردات الراتب الشهري")
st.caption("نظام إلكتروني آمن لاستعلام مفردات الراتب والبدلات والاستقطاعات")
st.markdown("---")

tabs = st.tabs(["🔒 استعلام الموظف", "⚙️ لوحة تحكم الإدارة"])

# =========================================================
# الواجهة الأولى: استعلام الموظف
# =========================================================
with tabs[0]:
    df = load_data()

    if df is None:
        st.warning("⚠️ لم يتم رفع كشف الرواتب لهذا الشهر بعد. يرجى التواصل مع قسم الموارد البشرية / الحسابات.")
    else:
        st.subheader("🔑 إدخال بيانات الاستعلام")
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            emp_id = st.text_input("الرقم الوظيفي:", placeholder="مثال: 1001", key="emp_id")
        with col_input2:
            secret_code = st.text_input("الكود الخاص / الرمز السري:", type="password", placeholder="••••••••", key="code")

        btn_search = st.button("🔍 عرض مفردات الراتب", use_container_width=True, type="primary")

        if btn_search:
            if not emp_id or not secret_code:
                st.error("يرجى إدخال الرقم الوظيفي والكود الخاص بك لاستكمال الاستعلام.")
            else:
                if 'الرقم الوظيفي' not in df.columns or 'كود الموظف' not in df.columns:
                    st.error("خطأ في بنية ملف البيانات: يجب أن يحتوي الملف على عمودي 'الرقم الوظيفي' و 'كود الموظف'. يرجى مراجعة لوحة الإدارة.")
                else:
                    df['الرقم الوظيفي_str'] = df['الرقم الوظيفي'].astype(str).str.strip()
                    df['كود الموظف_str'] = df['كود الموظف'].astype(str).str.strip()

                    match = df[(df['الرقم الوظيفي_str'] == str(emp_id).strip()) & 
                               (df['كود الموظف_str'] == str(secret_code).strip())]

                    if not match.empty:
                        emp = match.iloc[0]
                        st.success(f"✅ تم العثور على سجل الموظف بنجاح!")

                        # --- 1. معلومات الموظف في منتصف الصفحة ---
                        with st.container():
                            st.markdown("### 👤 البيانات الوظيفية للموظف")
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("اسم الموظف", str(emp.get('اسم الموظف', '-')))
                            m2.metric("العنوان الوظيفي", str(emp.get('عنوان وظيفي', '-')))
                            m3.metric("الدرجة الوظيفية", str(emp.get('الدرجة الوظيفية', '-')))
                            m4.metric("المرحلة", str(emp.get('المرحلة', '-')))

                        st.markdown("---")

                        # --- 2. بناء الجداول في منتصف الورقة ---
                        st.markdown("### 📋 كشف تفاصيل ومفردات الراتب")
                        
                        col_earn, col_ded = st.columns(2)

                        # جدول الاستحقاقات والبدلات
                        with col_earn:
                            st.markdown("#### 📈 الاستحقاقات والبدلات")
                            
                            earn_data = {
                                "مفردات الاستحقاق": [
                                    "الراتب الاسمي", "مخصصات الزوجية", "مخصصات الأطفال",
                                    "مخصصات المنصب", "مخصصات الشهادة", "موقع جغرافي",
                                    "مخصصات مهنية", "مخصصات هندسية", "مخصصات الخطورة",
                                    "الإضافات الأخرى"
                                ],
                                "المبلغ": [
                                    fmt(emp.get('الراتب الاسمي', 0)), fmt(emp.get('الزوجية', 0)),
                                    fmt(emp.get('الاطفال', 0)), fmt(emp.get('المنصب', 0)),
                                    fmt(emp.get('الشهادة', 0)), fmt(emp.get('موقع جغرافي', 0)),
                                    fmt(emp.get('مهنية', 0)), fmt(emp.get('الهندسية', 0)),
                                    fmt(emp.get('الخطورة', 0)), fmt(emp.get('الاضافات', 0))
                                ]
                            }
                            df_earn = pd.DataFrame(earn_data)
                            st.dataframe(df_earn, use_container_width=True, hide_index=True)
                            
                            st.info(f"**إجمالي الاستحقاقات (المجموع): {fmt(emp.get('المجموع', 0))}**")

                        # جدول الاستقطاعات والخصومات
                        with col_ded:
                            st.markdown("#### 📉 الخصومات والاستقطاعات")
                            
                            ded_data = {
                                "مفردات الاستقطاع": [
                                    "استقطاع التقاعد", "ضريبة الدخل",
                                    "الضمان الاجتماعي", "استقطاعات أخرى"
                                ],
                                "المبلغ": [
                                    fmt(emp.get('التقاعد', 0)), fmt(emp.get('الضريبة', 0)),
                                    fmt(emp.get('الضمان الاجتماعي', 0)), fmt(emp.get('الاستقطاعات', 0))
                                ]
                            }
                            df_ded = pd.DataFrame(ded_data)
                            st.dataframe(df_ded, use_container_width=True, hide_index=True)
                            
                            st.warning(f"**إجمالي الاستقطاعات: {fmt(emp.get('المجموع.1', 0))}**")

                        st.markdown("---")

                        # --- 3. بطاقة الصافي الكبيرة في المنتصف ---
                        st.markdown("### 💰 صافي الراتب المستحق للقبض")
                        st.metric(
                            label="الصافي النهائي للموظف",
                            value=fmt(emp.get('الصافي', 0)),
                            delta="مبلغ قابل للصرف"
                        )

                    else:
                        st.error("❌ البيانات المدخلة غير صحيحة. يرجى التأكد من الرقم الوظيفي والكود الخاص.")

# =========================================================
# الواجهة الثانية: لوحة تحكم الإدارة
# =========================================================
with tabs[1]:
    st.subheader("⚙️ لوحة إدارة كشوفات الرواتب")
    
    current_admin_pass = get_admin_password()
    admin_pass_input = st.text_input("أدخل كلمة مرور الإدارة:", type="password", key="admin_login_pass")

    if admin_pass_input == current_admin_pass:
        st.success("تم تسجيل الدخول بصلاحيات مدير النظام بنجاح.")
        
        admin_subtabs = st.tabs(["📤 رفع كشف الراتب الشهري", "🔐 تغيير كلمة مرور الإدارة", "📥 تحميل قالب تجريبي"])

        # 1. رفع الملف
        with admin_subtabs[0]:
            st.markdown("### 📤 رفع ملف إكسل الشهري الجديد")
            st.info("تأكد أن الملف يحتوي على كافة أعمدة الراتب بالإضافة إلى عمودي: **`الرقم الوظيفي`** و **`كود الموظف`**.")

            uploaded_excel = st.file_uploader("اختر ملف الإكسل (XLSX أو XLS)", type=["xlsx", "xls"])

            if uploaded_excel is not None:
                try:
                    new_df = pd.read_excel(uploaded_excel)
                    new_df.columns = new_df.columns.astype(str).str.strip()

                    required_cols = ['الرقم الوظيفي', 'كود الموظف', 'اسم الموظف', 'الصافي']
                    missing_cols = [c for c in required_cols if c not in new_df.columns]

                    if missing_cols:
                        st.error(f"❌ الملف المرفوع تنقصه الأعمدة التالية: {', '.join(missing_cols)}")
                    else:
                        new_df.to_excel(DATA_FILE, index=False)
                        st.success("✅ تم تحديث كشف الرواتب وحفظه بنجاح!")

                        st.markdown("#### 📊 ملخص الملف المرفوع:")
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        stat_col1.metric("إجمالي الموظفين", len(new_df))
                        stat_col2.metric("إجمالي الرواتب الصافية", fmt(new_df['الصافي'].sum()))
                        stat_col3.metric("متوسط صافي الراتب", fmt(new_df['الصافي'].mean()))

                        st.markdown("#### 👁️ معاينة البيانات المرفوعة (أول 5 سجلات):")
                        st.dataframe(new_df.head(5), use_container_width=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

        # 2. تغيير كلمة المرور
        with admin_subtabs[1]:
            st.markdown("### 🔐 تغيير كلمة مرور الإدارة")
            st.write("يمكنك تعيين كلمة مرور جديدة لدخول لوحة تحكم الإدارة من هنا مباشرة.")

            with st.form("change_password_form"):
                new_pass = st.text_input("كلمة المرور الجديدة:", type="password")
                confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة:", type="password")
                submit_pass = st.form_submit_button("💾 حفظ كلمة المرور الجديدة")

                if submit_pass:
                    if not new_pass:
                        st.error("يرجى إدخال كلمة مرور جديدة.")
                    elif new_pass != confirm_pass:
                        st.error("كلمتا المرور غير متطابقتين. يرجى التأكد مرة أخرى.")
                    else:
                        save_admin_password(new_pass)
                        st.success("✅ تم تغيير كلمة المرور بنجاح! استخدم كلمة المرور الجديدة في المرة القادمة.")

        # 3. تحميل القالب
        with admin_subtabs[2]:
            st.markdown("### 📥 تحميل قالب إكسل جاهز للتعبئة")
            
            sample_data = {
                'الرقم الوظيفي': ['1001', '1002'],
                'كود الموظف': ['A123', 'B456'],
                'اسم الموظف': ['حارث صبحي جميل حمد', 'أحمد محمد علي'],
                'عنوان وظيفي': ['ر0 مبرمجين', 'محاسب قدم'],
                'الدرجة الوظيفية': ['الثالثة', 'الرابعة'],
                'المرحلة': ['ثالثة', 'أولى'],
                'الراتب الاسمي': [620000, 500000],
                'الزوجية': [0, 50000],
                'الاطفال': [0, 20000],
                'المنصب': [93000, 0],
                'الشهادة': [775000, 250000],
                'موقع جغرافي': [40000, 30000],
                'مهنية': [186000, 100000],
                'الهندسية': [0, 0],
                'الخطورة': [0, 0],
                'الاضافات': [0, 0],
                'المجموع': [1714000, 950000],
                'التقاعد': [62000, 50000],
                'الضريبة': [45783, 20000],
                'الاستقطاعات': [0, 0],
                'الضمان الاجتماعي': [1550, 1000],
                'المجموع.1': [109333, 71000],
                'الصافي': [1604667, 879000]
            }
            sample_df = pd.DataFrame(sample_data)
            
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                sample_df.to_excel(writer, index=False)
            
            st.download_button(
                label="⬇️ تحميل قالب إكسل تجريبي (Template)",
                data=buffer.getvalue(),
                file_name="Salary_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif admin_pass_input != "":
        st.error("كلمة المرور غير صحيحة.")
