import streamlit as st
import pandas as pd
import os

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
    
    /* هيدر الصفحة */
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

    /* بطاقات العرض */
    .salary-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-right: 5px solid #2a5298;
    }
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

    /* تحسين العرض للجداول والتنبيهات */
    .stMetric { background-color: #ffffff; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "Salary_Current.xlsx"
ADMIN_PASSWORD = "Admin@Salary2026"  # يمكنك تغيير كلمة سر الإدارة من هنا

# ---------------------------------------------------------
# 2. وظائف تحميل ومعالجة البيانات
# ---------------------------------------------------------
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
    """تنسيق القيم المادية كأرقام صحيحة أو عشرية ممثلة بصورة واضحة"""
    try:
        if pd.isna(val):
            return 0
        return float(val)
    except:
        return 0

# ---------------------------------------------------------
# 3. الهيكل الرئيسي للتطبيق (قوائم تنقل)
# ---------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h1>💳 بوابة استعلام مفردات الراتب الشهري</h1>
        <p>نظام إلكتروني آمن للاستعلام الفردي عن الرواتب والبدلات والاستقطاعات</p>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🔒 استعلام الموظف", "⚙️ لوحة تحكم الإدارة"])

# =========================================================
# الواجهة الأولى: بوابة الموظف (استعلام الراتب)
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
                # التحقق من وجود أعمدة التحقق
                if 'الرقم الوظيفي' not in df.columns or 'كود الموظف' not in df.columns:
                    st.error("خطأ في بنية ملف البيانات: يجب أن يحتوي الملف على عمودي 'الرقم الوظيفي' و 'كود الموظف'. يرجى مراجعة لوحة الإدارة.")
                else:
                    # تحويل القيم لنصوص لمطابقة دقيقة
                    df['الرقم الوظيفي_str'] = df['الرقم الوظيفي'].astype(str).str.strip()
                    df['كود الموظف_str'] = df['كود الموظف'].astype(str).str.strip()

                    match = df[(df['الرقم الوظيفي_str'] == str(emp_id).strip()) & 
                               (df['كود الموظف_str'] == str(secret_code).strip())]

                    if not match.empty:
                        emp = match.iloc[0]
                        
                        st.success(f"✅ تم العثور على سجل الموظف: **{emp.get('اسم الموظف', 'غير محدد')}**")
                        
                        # --- بطاقة المعلومات الوظيفية ---
                        st.markdown("### 👤 البيانات الوظيفية")
                        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                        info_col1.metric("اسم الموظف", str(emp.get('اسم الموظف', '-')))
                        info_col2.metric("العنوان الوظيفي", str(emp.get('عنوان وظيفي', '-')))
                        info_col3.metric("الدرجة الوظيفية", str(emp.get('الدرجة الوظيفية', '-')))
                        info_col4.metric("المرحلة", str(emp.get('المرحلة', '-')))

                        st.markdown("---")

                        # --- قسم البدلات والأرباح والاستقطاعات ---
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

                        # --- بطاقة الصافي النهائي ---
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
# الواجهة الثانية: لوحة تحكم الإدارة (رفع الملف والتحكم)
# =========================================================
with tabs[1]:
    st.subheader("⚙️ لوحة إدارة كشوفات الرواتب")
    
    admin_pass = st.text_input("أدخل كلمة مرور الإدارة:", type="password")

    if admin_pass == ADMIN_PASSWORD:
        st.success("تم تسجيل الدخول بصلاحيات مدير النظام.")
        
        st.markdown("---")
        st.markdown("### 📤 رفع ملف إكسل الشهري الجديد")
        st.info("تأكد أن الملف يحتوي على كافة أعمدة الراتب بـالإضافة إلى عمودي: **`الرقم الوظيفي`** و **`كود الموظف`**.")

        uploaded_excel = st.file_uploader("اختر ملف الإكسل (XLSX أو XLS)", type=["xlsx", "xls"])

        if uploaded_excel is not None:
            try:
                new_df = pd.read_excel(uploaded_excel)
                new_df.columns = new_df.columns.astype(str).str.strip()

                # التحقق من وجود الأعمدة المطلوبة
                required_cols = ['الرقم الوظيفي', 'كود الموظف', 'اسم الموظف', 'الصافي']
                missing_cols = [c for c in required_cols if c not in new_df.columns]

                if missing_cols:
                    st.error(f"❌ الملف المرفوع تنقصه الأعمدة التالية: {', '.join(missing_cols)}")
                    st.write("يرجى تعديل الملف وإضافة هذه الأعمدة ثم إعادة الرفع.")
                else:
                    # حفظ الملف كملف رئيسي جديد
                    new_df.to_excel(DATA_FILE, index=False)
                    st.success("✅ تم تحديث كشف الرواتب وحفظه بنجاح! أصبح بإمكان الموظفين الآن الاستعلام.")

                    st.markdown("#### 📊 ملخص الملف المرفوع:")
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    stat_col1.metric("إجمالي الموظفين", len(new_df))
                    stat_col2.metric("إجمالي الرواتب الصافية", f"{new_df['الصافي'].sum():,.0f} د.ع")
                    stat_col3.metric("متوسط صافي الراتب", f"{new_df['الصافي'].mean():,.0f} د.ع")

                    st.markdown("#### 👁️ معاينة من البيانات المرفوعة (أول 5 سجلات):")
                    st.dataframe(new_df.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

        st.markdown("---")
        st.markdown("### 📥 تحميل قالب إكسل جاهز للتعبئة")
        st.write("يمكنك تحميل القالب الجاهز المبني على هيكلية ملفك مع إضافة عمودي الأمان (`الرقم الوظيفي` و `كود الموظف`):")

        # إنشاء نموذج للتحميل
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
        
        # تحويل القالب إلى خيار تحميل مباشر
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

    elif admin_pass != "":
        st.error("كلمة المرور غير صحيحة.")