import streamlit as st
import pandas as pd
import os
import json

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم (RTL & Professional Styling)
# ---------------------------------------------------------
st.set_page_config(
    page_title="بوابة استعلام الرواتب الشهرية",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الواجهة بلغة عربية واتجاه من اليمين إلى اليسار مع تنسيق الألوان
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: #ffffff !important; font-weight: 800; font-size: 26px; margin: 0; }
    .main-header p { color: #e0e0e0; margin-top: 5px; font-size: 15px; }

    .net-salary-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(56, 239, 125, 0.3);
        margin-top: 20px;
    }
    .net-salary-card h2 { color: #ffffff !important; margin: 0; font-size: 20px; }
    .net-salary-card h1 { color: #ffffff !important; margin: 10px 0 0 0; font-size: 36px; font-weight: 800; }

    .stMetric { background-color: #ffffff; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "Salary_Current.xlsx"
CONFIG_FILE = "config.json"
DEFAULT_ADMIN_PASS = "Admin@Salary2026"

# ---------------------------------------------------------
# 2. إدارة كلمة المرور والبيانات
# ---------------------------------------------------------
def get_admin_password():
    """قراءة كلمة المرور المحفوظة أو إرجاع الافتراضية"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("admin_password", DEFAULT_ADMIN_PASS)
        except:
            return DEFAULT_ADMIN_PASS
    return DEFAULT_ADMIN_PASS

def save_admin_password(new_password):
    """حفظ كلمة المرور الجديدة في ملف الإعدادات"""
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

def clean_value(val):
    try:
        if pd.isna(val):
            return 0
        return float(val)
    except:
        return 0

# ---------------------------------------------------------
# 3. الهيكل الرئيسي للتطبيق
# ---------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h1>💳 بوابة استعلام مفردات الراتب الشهري</h1>
        <p>نظام إلكتروني آمن للاستعلام الفردي عن الرواتب والبدلات والاستقطاعات</p>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🔒 استعلام الموظف", "⚙️ لوحة تحكم الإدارة"])

# =========================================================
# الواجهة الأولى: بوابة الموظف
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
                        
                        st.success(f"✅ تم العثور على سجل الموظف: **{emp.get('اسم الموظف', 'غير محدد')}**")
                        
                        st.markdown("### 👤 البيانات الوظيفية")
                        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                        info_col1.metric("اسم الموظف", str(emp.get('اسم الموظف', '-')))
                        info_col2.metric("العنوان الوظيفي", str(emp.get('عنوان وظيفي', '-')))
                        info_col3.metric("الدرجة الوظيفية", str(emp.get('الدرجة الوظيفية', '-')))
                        info_col4.metric("المرحلة", str(emp.get('المرحلة', '-')))

                        st.markdown("---")

                        col_earnings, col_deductions = st.columns(2)

                        with col_earnings:
                            st.markdown("### 📈 الراتب الأساسي والبدلات (الاستحقاقات)")
                            st.write(f"• **الراتب الاسمي:** {clean_value(emp.get('الراتب الاسمي', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات الزوجية:** {clean_value(emp.get('الزوجية', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات الأطفال:** {clean_value(emp.get('الاطفال', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات المنصب:** {clean_value(emp.get('المنصب', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات الشهادة:** {clean_value(emp.get('الشهادة', 0)):,.0f} د.ع")
                            st.write(f"• **موقع جغرافي:** {clean_value(emp.get('موقع جغرافي', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات مهنية:** {clean_value(emp.get('مهنية', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات هندسية:** {clean_value(emp.get('الهندسية', 0)):,.0f} د.ع")
                            st.write(f"• **مخصصات الخطورة:** {clean_value(emp.get('الخطورة', 0)):,.0f} د.ع")
                            st.write(f"• **الإضافات:** {clean_value(emp.get('الاضافات', 0)):,.0f} د.ع")
                            
                            gross_total = clean_value(emp.get('المجموع', 0))
                            st.info(f"**إجمالي الاستحقاقات (المجموع): {gross_total:,.0f} د.ع**")

                        with col_deductions:
                            st.markdown("### 📉 الاستقطاعات والخصومات")
                            st.write(f"• **استقطاع التقاعد:** {clean_value(emp.get('التقاعد', 0)):,.0f} د.ع")
                            st.write(f"• **ضريبة الدخل:** {clean_value(emp.get('الضريبة', 0)):,.0f} د.ع")
                            st.write(f"• **الضمان الاجتماعي:** {clean_value(emp.get('الضمان الاجتماعي', 0)):,.0f} د.ع")
                            st.write(f"• **استقطاعات أخرى:** {clean_value(emp.get('الاستقطاعات', 0)):,.0f} د.ع")
                            
                            deductions_total = clean_value(emp.get('المجموع.1', 0))
                            st.warning(f"**إجمالي الاستقطاعات: {deductions_total:,.0f} د.ع**")

                        net_salary = clean_value(emp.get('الصافي', 0))
                        st.markdown(f"""
                            <div class="net-salary-card">
                                <h2>💰 صافي الراتب المستحق للقبض</h2>
                                <h1>{net_salary:,.0f} د.ع</h1>
                            </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error("❌ البيانات المدخلة غير صحيحة. يرجى التأكد من الرقم الوظيفي والكود الخاص.")

# =========================================================
# الواجهة الثانية: لوحة تحكم الإدارة (رفع الملف وتغيير كلمة السر)
# =========================================================
with tabs[1]:
    st.subheader("⚙️ لوحة إدارة كشوفات الرواتب")
    
    current_admin_pass = get_admin_password()
    admin_pass_input = st.text_input("أدخل كلمة مرور الإدارة:", type="password", key="admin_login_pass")

    if admin_pass_input == current_admin_pass:
        st.success("تم تسجيل الدخول بصلاحيات مدير النظام بنجاح.")
        
        # أقسام الإدارة المتاحة
        admin_subtabs = st.tabs(["📤 رفع كشف الراتب الشهري", "🔐 تغيير كلمة مرور الإدارة", "📥 تحميل قالب تجريبي"])

        # --- قسم رفع الملف ---
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
                        stat_col2.metric("إجمالي الرواتب الصافية", f"{new_df['الصافي'].sum():,.0f} د.ع")
                        stat_col3.metric("متوسط صافي الراتب", f"{new_df['الصافي'].mean():,.0f} د.ع")

                        st.markdown("#### 👁️ معاينة البيانات المرفوعة (أول 5 سجلات):")
                        st.dataframe(new_df.head(5), use_container_width=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

        # --- قسم تغيير كلمة المرور ---
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
                    elif len(new_pass) < 6:
                        st.warning("يُفضل أن لا تقل كلمة المرور عن 6 أرقام أو حروف لزيادة الأمان.")
                    else:
                        save_admin_password(new_pass)
                        st.success("✅ تم تغيير كلمة المرور بنجاح! استخدم كلمة المرور الجديدة في المرة القادمة.")

        # --- قسم تحميل القالب ---
        with admin_subtabs[2]:
            st.markdown("### 📥 تحميل قالب إكسل جاهز للتعبئة")
            st.write("يمكنك تحميل القالب التجريبي الجاهز المبني على هيكلية ملفك:")

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
