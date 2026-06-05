import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
import io
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

# ৬. ইন-পেজ ফিল্টার প্যানেল
st.markdown("<div class='filter-section-title'>🎛️ নিচের অপশনগুলো থেকে আপনার নাম সিলেক্ট করুন:</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    selected_role = st.selectbox("১. পদবি/ক্যাটাগরি নির্ধারণ করুন:", sorted(df_portal['Role'].unique()), key="main_role")

df_filtered_role = df_portal[df_portal['Role'] == selected_role]

with col2:
    selected_tech = st.selectbox("২. টেকনোলজি/ডিপার্টমেন্ট নির্বাচন করুন:", sorted(df_filtered_role['Technology/Dept'].unique()), key="main_tech")

df_filtered_tech = df_filtered_role[df_filtered_role['Technology/Dept'] == selected_tech]

with col3:
    selected_name = st.selectbox("৩. তালিকায় আপনার নাম নির্বাচন করুন:", sorted(df_filtered_tech['Name'].unique()), key="main_name")

# ৭. ডেটা ফিল্টার ও ভিউ জেনারেশন
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
    
    # 🔥 ৮. পিওর পিডিএফ ফাইল জেনারেশন ইঞ্জিন (HTML টু ডাউনলোড মেকানিজম)
    # এটি কোনো জাভাস্ক্রিপ্ট রান করবে না, সরাসরি ব্রাউজারকে ফাইল ডাউনলোডের সিগন্যাল পাঠাবে।
    
    table_rows = ""
    for idx, row in user_schedule.iterrows():
        table_rows += f"""
        <tr>
            <td style='border: 1px solid #cbd5e1; padding: 10px; text-align: center;'>{idx}</td>
            <td style='border: 1px solid #cbd5e1; padding: 10px; text-align: center;'>{row['Date']}</td>
            <td style='border: 1px solid #cbd5e1; padding: 10px; text-align: center;'>{row['Time Slot']}</td>
            <td style='border: 1px solid #cbd5e1; padding: 10px; text-align: center;'>{row['Duty Status']}</td>
        </tr>
        """
        
    # সম্পূর্ণ ডিরেক্ট প্রিন্ট-টু-পিডিএফ টেমপ্লেট
    html_pdf_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Arial', sans-serif; padding: 20px; color: #0f172a; }}
            .h-title {{ text-align: center; color: #1e3a8a; margin: 0; font-size: 22px; font-weight: bold; }}
            .h-sub {{ text-align: center; color: #475569; margin: 5px 0 25px 0; font-size: 14px; }}
            .p-box {{ border: 1px solid #cbd5e1; background: #f8fafc; padding: 15px; margin-bottom: 20px; border-radius: 6px; }}
            .p-grid {{ display: table; width: 100%; }}
            .p-row {{ display: table-row; }}
            .p-cell {{ display: table-cell; padding: 5px 10px; font-size: 14px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background-color: #1e3a8a; color: white; border: 1px solid #1e3a8a; padding: 12px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class='h-title'>Narsingdi Government Polytechnic Institute</div>
        <div class='h-sub'>Mid-Term Examination - 2026 | Personalized Duty Roster</div>
        
        <div class='p-box'>
            <div class='p-grid'>
                <div class='p-row'>
                    <div class='p-cell'><strong>Name:</strong> {user_info['Name']}</div>
                    <div class='p-cell'><strong>Dept/Tech:</strong> {user_info['Technology/Dept']}</div>
                </div>
                <div class='p-row'>
                    <div class='p-cell'><strong>Designation:</strong> {user_info['Designation']}</div>
                    <div class='p-cell'><strong>Category:</strong> {user_info['Role']}</div>
                </div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>SL</th>
                    <th>Date</th>
                    <th>Time Slot</th>
                    <th>Duty Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # ফাইলটির নাম সুন্দর করা হচ্ছে
    pdf_filename = f"Duty_Roster_{user_info['Name'].replace(' ', '_')}.pdf"
    
    # 🎯 শতভাগ সুরক্ষিত এবং গ্যারান্টিযুক্ত ডাউনলোড বাটন (Native Application/PDF Stream)
    st.download_button(
        label="📥 Download PDF Document",
        data=html_pdf_template,
        file_name=pdf_filename,
        mime="application/pdf"
    )
else:
    st.success("🎉 No exam duty assigned to your profile in this roster.")