import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
import io
import hmac
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ১. পেজ কনফিগারেশন সেটআপ
st.set_page_config(
    page_title="Exam Duty Portal | Narsingdi GPI", 
    page_icon="📝", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# লোগো ফাইল অটো-চেক করার ফাংশন
def get_logo_base64():
    possible_names = ["NPI Logo.jpg", "NPI Logo.JPG", "NPI Logo.jpeg", "NPI Logo.png", "npi logo.jpg"]
    for name in possible_names:
        if os.path.exists(name):
            try:
                with open(name, "rb") as img_file:
                    encoded_string = base64.b64encode(img_file.read()).decode()
                    ext = name.split('.')[-1].lower()
                    mime_type = "png" if ext == "png" else "jpeg"
                    return f"data:image/{mime_type};base64,{encoded_string}"
            except Exception:
                pass
    return None

logo_b64 = get_logo_base64()

# ২. মডার্ন ইউজার ইন্টারফেস ডিজাইন (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght=400;500;600;700&family=Inter:wght=400;500;600;700&display=swap');
    
    html, body, .stSelectbox, div[data-testid="stMarkdownContainer"] {
        font-family: 'Hind Siliguri', 'Inter', sans-serif;
    }
    
    .portal-header-container {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.1);
        border-bottom: 4px solid #F59E0B;
    }
    .header-img-render {
        width: 75px;
        height: 75px;
        margin-right: 20px;
        border-radius: 8px;
        background-color: white;
        padding: 2px;
    }
    .fallback-logo-render {
        font-size: 45px;
        margin-right: 20px;
        background: white;
        padding: 10px;
        border-radius: 8px;
        line-height: 1;
    }
    .header-text h1 {
        font-size: 26px !important;
        font-weight: 700 !important;
        margin: 0 0 4px 0 !important;
        color: #FFFFFF !important;
    }
    .header-text p {
        font-size: 15px;
        color: #CBD5E1;
        margin: 0;
    }
    
    .profile-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #1E3A8A;
        padding: 18px;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 25px;
    }
    .profile-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
    }
    @media (min-width: 768px) {
        .profile-grid { grid-template-columns: 1fr 1fr; gap: 20px; }
    }
    .profile-item { font-size: 15px; color: #475569; }
    .profile-item strong { color: #0F172A; font-weight: 600; display: inline-block; width: 110px; }

    /* অফিসিয়াল ডাউনলোড বোতামের কাস্টমাইজেশন */
    div.stDownloadButton {
        text-align: center;
        margin: 30px 0;
    }
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        padding: 14px 50px !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        max-width: 340px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ৩. ডেটা প্রসেসিং ইঞ্জিন
@st.cache_data
def load_and_process_roster():
    file_path = "Duty Roaster for Mid Term.xlsx"
    sheets_config = {
        "Chief Invigilator": "All Chief Invigilators",
        "Hall Super": "All Hallsupers",
        "Teacher / Invigilator": "All Teachers",
        "MLSS / Staff": "MLSS Roaster"
    }
    
    parsed_records = []
    
    for user_role, sheet_name in sheets_config.items():
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            dates_row = df.iloc[1].ffill() 
            times_row = df.iloc[2]
            
            for idx in range(3, len(df)):
                row = df.iloc[idx]
                if pd.isna(row[1]) or str(row[1]).strip() == "" or "Total" in str(row[1]):
                    continue
                    
                name = str(row[1]).strip()
                designation = str(row[2]).strip() if pd.notna(row[2]) else "N/A"
                tech_dept = str(row[3]).strip() if pd.notna(row[3]) else "N/A"
                
                for col_idx in range(4, len(row) - 1):
                    cell_value = row[col_idx]
                    if pd.notna(cell_value) and str(cell_value).strip() != "" and cell_value != 0:
                        date_str = str(dates_row[col_idx]).split(" ")[0]
                        time_slot = str(times_row[col_idx]).strip()
                        
                        if time_slot in ["9.3", "9.30"]: time_slot = "09:30 AM"
                        elif time_slot in ["11.0", "11"]: time_slot = "11:00 AM"
                        elif time_slot in ["12.3", "12.30"]: time_slot = "12:30 PM"
                        elif time_slot in ["2.3", "2.30"]: time_slot = "02:30 PM"
                        
                        clean_val = str(cell_value).strip().replace('.0','')
                        
                        if clean_val in ["1", "1.0", "Assigned"]:
                            duty_desc = "Assigned"
                        elif user_role == "MLSS / Staff":
                            duty_desc = f"Shift: {clean_val}" if clean_val.isdigit() else clean_val
                        else:
                            duty_desc = f"Room: {clean_val}"
                            
                        parsed_records.append({
                            "Role": user_role,
                            "Name": name,
                            "Designation": designation,
                            "Technology/Dept": tech_dept,
                            "Date": date_str,
                            "Time Slot": time_slot,
                            "Duty Status": duty_desc
                        })
        except Exception as e:
            st.warning(f"Error handling sheet {sheet_name}: {e}")
            
    return pd.DataFrame(parsed_records)

# ৩.৫ আসল পিডিএফ জেনারেটর (ReportLab) — বৈধ application/pdf বাইট তৈরি করে
def generate_pdf(user_info, schedule_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm,
        title=f"Duty Roster - {user_info['Name']}",
    )

    navy = colors.HexColor("#1E3A8A")
    slate = colors.HexColor("#475569")
    border = colors.HexColor("#CBD5E1")
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DocTitle", parent=styles["Title"],
                                 textColor=navy, fontSize=18, spaceAfter=4, alignment=TA_CENTER)
    sub_style = ParagraphStyle("DocSub", parent=styles["Normal"],
                               textColor=slate, fontSize=11, alignment=TA_CENTER, spaceAfter=16)
    cell_style = ParagraphStyle("ProfileCell", parent=styles["Normal"],
                                fontSize=10.5, textColor=colors.HexColor("#0F172A"))

    def profile_cell(label, value):
        return Paragraph(f"<b>{escape(str(label))}:</b> {escape(str(value))}", cell_style)

    elements = [
        Paragraph("Narsingdi Government Polytechnic Institute", title_style),
        Paragraph("Mid-Term Examination - 2026  |  Personalized Duty Roster", sub_style),
    ]

    # Profile box (2 x 2 grid)
    profile = Table(
        [[profile_cell("Name", user_info["Name"]), profile_cell("Dept/Tech", user_info["Technology/Dept"])],
         [profile_cell("Designation", user_info["Designation"]), profile_cell("Category", user_info["Role"])]],
        colWidths=[doc.width / 2.0] * 2,
    )
    profile.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, border),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements += [profile, Spacer(1, 16)]

    # Schedule table
    data = [["SL", "Date", "Time Slot", "Duty Status"]]
    for i, (_, row) in enumerate(schedule_df.iterrows(), start=1):
        data.append([str(i), str(row["Date"]), str(row["Time Slot"]), str(row["Duty Status"])])
    table = Table(data, colWidths=[doc.width * w for w in (0.12, 0.30, 0.28, 0.30)], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ৩.৬ কন্ট্রোল রুম ড্যাশবোর্ড — পাসওয়ার্ড সুরক্ষিত (এক অ্যাডমিন ইউজার)
# ক্রেডেনশিয়াল এনভায়রনমেন্ট ভেরিয়েবল থেকে আসে; ডিফল্ট থাকলে অ্যাপে সতর্কবার্তা দেখায়।
_DEFAULT_PASSWORD = "admin123"
ADMIN_USER = os.environ.get("CONTROL_ROOM_USER", "admin")
ADMIN_PASSWORD = os.environ.get("CONTROL_ROOM_PASSWORD", _DEFAULT_PASSWORD)


def _check_admin_login():
    """Render a login form; return True once the single admin user is authenticated."""
    if st.session_state.get("cr_authenticated"):
        return True

    st.markdown("#### 🔒 Control Room Login")
    st.caption("Restricted area — authorised personnel only.")
    with st.form("control_room_login", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        # constant-time comparison to avoid leaking credential length/content via timing
        ok_user = hmac.compare_digest(username.strip(), ADMIN_USER)
        ok_pass = hmac.compare_digest(password, ADMIN_PASSWORD)
        if ok_user and ok_pass:
            st.session_state["cr_authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    return False


def render_control_room(df):
    """Password-protected dashboard: filter the roster and list personnel on duty."""
    st.markdown("## 🛡️ Control Room Dashboard")

    if not _check_admin_login():
        return

    head = st.columns([3, 1])
    head[0].success(f"Logged in as **{ADMIN_USER}**")
    if head[1].button("🔓 Log out", use_container_width=True):
        st.session_state["cr_authenticated"] = False
        st.rerun()

    if ADMIN_PASSWORD == _DEFAULT_PASSWORD:
        st.warning(
            "Using the default password. Set the `CONTROL_ROOM_PASSWORD` "
            "environment variable to secure this dashboard.",
            icon="⚠️",
        )

    st.markdown("Filter the duty roster below. **Leave a filter empty to include all values.**")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_dates = st.multiselect("📅 Date", sorted(df["Date"].unique()))
    with f2:
        sel_slots = st.multiselect("⏰ Time Slot", sorted(df["Time Slot"].unique()))
    with f3:
        sel_desigs = st.multiselect("🎓 Designation", sorted(df["Designation"].unique()))
    with f4:
        sel_cats = st.multiselect("🏷️ Category", sorted(df["Role"].unique()))

    filtered = df
    if sel_dates:
        filtered = filtered[filtered["Date"].isin(sel_dates)]
    if sel_slots:
        filtered = filtered[filtered["Time Slot"].isin(sel_slots)]
    if sel_desigs:
        filtered = filtered[filtered["Designation"].isin(sel_desigs)]
    if sel_cats:
        filtered = filtered[filtered["Role"].isin(sel_cats)]

    personnel = (
        filtered[["Name", "Designation", "Role", "Technology/Dept", "Date", "Time Slot", "Duty Status"]]
        .rename(columns={"Role": "Category", "Technology/Dept": "Dept/Tech"})
        .sort_values(["Date", "Time Slot", "Name"])
        .reset_index(drop=True)
    )
    personnel.index = personnel.index + 1

    m1, m2, m3 = st.columns(3)
    m1.metric("Duty Assignments", len(personnel))
    m2.metric("Unique Personnel", personnel["Name"].nunique())
    m3.metric("Dates Covered", personnel["Date"].nunique())

    st.markdown("#### 👥 Personnel on Duty")
    if personnel.empty:
        st.info("No personnel match the selected filters.")
    else:
        st.dataframe(personnel, use_container_width=True)
        csv = personnel.to_csv(index_label="SL").encode("utf-8")
        st.download_button(
            "📥 Download Filtered List (CSV)",
            data=csv,
            file_name="control_room_personnel.csv",
            mime="text/csv",
        )

# ৪. রস্টার ডেটা লোড
try:
    df_portal = load_and_process_roster()
except Exception as e:
    st.error(f"এক্সেল ফাইলটি লোড করা যাচ্ছে না। ত্রুটি: {e}")
    st.stop()

# ৫. পোর্টাল টপ ব্যানার রেন্ডারিং
logo_element = f"<img src='{logo_b64}' class='header-img-render'>" if logo_b64 else "<div class='fallback-logo-render'>📝</div>"
st.markdown(f"""
<div class='portal-header-container'>
    {logo_element}
    <div class='header-text'>
        <h1>নরসিংদী সরকারি পলিটেকনিক ইনস্টিটিউট</h1>
        <p>পর্বমধ্য পরীক্ষা - ২০২৬ | ডিজিটাল ডিউটি রোস্টার পোর্টাল</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ৫.৫ নেভিগেশন — মূল পেজে ভিউ সুইচার (পাবলিক পোর্টাল বনাম কন্ট্রোল রুম)
app_view = st.segmented_control(
    "Navigation",
    ["🏠 Personal Roster", "🛡️ Control Room"],
    default="🏠 Personal Roster",
    label_visibility="collapsed",
)

if app_view == "🛡️ Control Room":
    render_control_room(df_portal)
    st.stop()

# ৬. ইন-পেজ ফিল্টার প্যানেল
st.markdown("<div class='filter-section-title'>🎛️ নিচের অপশনগুলো থেকে আপনার নাম সিলেক্ট করুন:</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    selected_role = st.selectbox("১. পদবি/ক্যাটাগরি নির্ধারণ করুন:", sorted(df_portal['Role'].unique()), index=None, placeholder="— নির্বাচন করুন —", key="main_role")

df_filtered_role = df_portal[df_portal['Role'] == selected_role] if selected_role else df_portal.iloc[0:0]

with col2:
    selected_tech = st.selectbox("২. টেকনোলজি/ডিপার্টমেন্ট নির্বাচন করুন:", sorted(df_filtered_role['Technology/Dept'].unique()), index=None, placeholder="— নির্বাচন করুন —", key="main_tech")

df_filtered_tech = df_filtered_role[df_filtered_role['Technology/Dept'] == selected_tech] if selected_tech else df_portal.iloc[0:0]

with col3:
    selected_name = st.selectbox("৩. তালিকায় আপনার নাম নির্বাচন করুন:", sorted(df_filtered_tech['Name'].unique()), index=None, placeholder="— নির্বাচন করুন —", key="main_name")

# ৭. ডেটা ফিল্টার ও ভিউ জেনারেশন
if not (selected_role and selected_tech and selected_name):
    st.info("👆 আপনার ডিউটি রোস্টার দেখতে উপরের তিনটি অপশন (পদবি, টেকনোলজি/ডিপার্টমেন্ট ও নাম) নির্বাচন করুন।")
    st.stop()

user_schedule = df_filtered_tech[df_filtered_tech['Name'] == selected_name][['Date', 'Time Slot', 'Duty Status']]
user_info = df_filtered_tech[df_filtered_tech['Name'] == selected_name].iloc[0]

# প্রোফাইল কার্ড প্রদর্শন
st.markdown(f"""
<div class='profile-card'>
    <div class='profile-grid'>
        <div class='profile-item'><strong>Name:</strong> {user_info['Name']}</div>
        <div class='profile-item'><strong>Dept/Tech:</strong> {user_info['Technology/Dept']}</div>
        <div class='profile-item'><strong>Designation:</strong> {user_info['Designation']}</div>
        <div class='profile-item'><strong>Category:</strong> {user_info['Role']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h4 style='color: #1E3A8A; margin-bottom: 15px;'>🗓 Your Personalized Duty Roster:</h4>", unsafe_allow_html=True)

if not user_schedule.empty:
    user_schedule.columns = ['Date', 'Time Slot', 'Duty Status']
    user_schedule.reset_index(drop=True, inplace=True)
    user_schedule.index = user_schedule.index + 1
    
    # স্ক্রিনে মেইন ইন্টারেক্টিভ টেবিল প্রদর্শন
    st.dataframe(user_schedule, use_container_width=True)
    
    # ৮. বৈধ পিডিএফ জেনারেশন (ReportLab) ও ডাউনলোড বাটন
    pdf_bytes = generate_pdf(user_info, user_schedule)
    pdf_filename = f"Duty_Roster_{str(user_info['Name']).replace(' ', '_')}.pdf"

    st.download_button(
        label="📥 Download PDF Document",
        data=pdf_bytes,
        file_name=pdf_filename,
        mime="application/pdf",
    )
else:
    st.success("🎉 No exam duty assigned to your profile in this roster.")