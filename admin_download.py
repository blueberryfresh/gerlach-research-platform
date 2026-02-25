"""
Admin Download Page for Gerlach Research Platform
Password-protected data export
"""

import streamlit as st
import json
import zipfile
import io
from pathlib import Path
from datetime import datetime

ADMIN_PASSWORD = "Big5llmstudy"

def check_password():
    """Password protection for admin page"""
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if st.session_state.admin_authenticated:
        return True
    
    st.title("🔒 Admin Access")
    st.write("Enter password to access data download page")
    
    password = st.text_input("Password", type="password", key="admin_password_input")
    
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    
    return False

def get_all_participants():
    """Get list of all participants from session files"""
    data_dir = Path("research_data")
    sessions_dir = data_dir / "sessions"
    
    if not sessions_dir.exists():
        return []
    
    participants = []
    for session_file in sessions_dir.glob("*.json"):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
                participants.append({
                    'user_id': session.get('user_id', 'Unknown'),
                    'session_id': session.get('session_id', 'Unknown'),
                    'created_at': session.get('created_at', 'Unknown'),
                    'current_stage': session.get('current_stage', 'Unknown'),
                    'file': session_file.name
                })
        except Exception as e:
            st.warning(f"Error reading {session_file.name}: {e}")
    
    return participants

def create_zip_all_data():
    """Create ZIP file containing all research data"""
    data_dir = Path("research_data")
    
    if not data_dir.exists():
        return None
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['sessions', 'assessments', 'dialogues', 'task_responses', 'surveys', 'reports']:
            folder_path = data_dir / folder
            if folder_path.exists():
                for file_path in folder_path.rglob('*.json'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
                
                for file_path in folder_path.rglob('*.md'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
                
                for file_path in folder_path.rglob('*.html'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer

def create_zip_participant_data(user_id):
    """Create ZIP file for a specific participant"""
    data_dir = Path("research_data")
    
    if not data_dir.exists():
        return None
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['sessions', 'assessments', 'dialogues', 'task_responses', 'surveys', 'reports']:
            folder_path = data_dir / folder
            if folder_path.exists():
                for file_path in folder_path.rglob(f'*{user_id}*.json'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
                
                for file_path in folder_path.rglob(f'*{user_id}*.md'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
                
                for file_path in folder_path.rglob(f'*{user_id}*.html'):
                    arcname = file_path.relative_to(data_dir)
                    zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer

def export_to_csv():
    """Export all data to CSV format for analysis"""
    import csv
    
    data_dir = Path("research_data")
    csv_buffer = io.StringIO()
    
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow([
        'User ID', 'Session ID', 'Created At', 'Current Stage',
        'Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism',
        'Gerlach Type', 'Gerlach Confidence',
        'Task Name', 'LLM Personality',
        'Message Count', 'Dialogue Duration',
        'Survey Completed'
    ])
    
    sessions_dir = data_dir / "sessions"
    if sessions_dir.exists():
        for session_file in sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                
                user_id = session.get('user_id', '')
                session_id = session.get('session_id', '')
                created_at = session.get('created_at', '')
                current_stage = session.get('current_stage', '')
                task_name = session.get('task_name', '')
                llm_personality = session.get('llm_personality', '')
                
                assessment_id = session.get('assessment_id', '')
                o, c, e, a, n, gerlach_type, gerlach_conf = '', '', '', '', '', '', ''
                
                if assessment_id:
                    assessment_file = data_dir / "assessments" / f"{assessment_id}.json"
                    if assessment_file.exists():
                        with open(assessment_file, 'r', encoding='utf-8') as af:
                            assessment = json.load(af)
                            o = assessment.get('openness', '')
                            c = assessment.get('conscientiousness', '')
                            e = assessment.get('extraversion', '')
                            a = assessment.get('agreeableness', '')
                            n = assessment.get('neuroticism', '')
                            gerlach_type = assessment.get('gerlach_type', '')
                            gerlach_conf = assessment.get('gerlach_confidence', '')
                
                dialogue_id = session.get('dialogue_id', '')
                message_count, duration = '', ''
                
                if dialogue_id:
                    dialogue_file = data_dir / "dialogues" / f"{dialogue_id}.json"
                    if dialogue_file.exists():
                        with open(dialogue_file, 'r', encoding='utf-8') as df:
                            dialogue = json.load(df)
                            message_count = len(dialogue.get('messages', []))
                            duration = dialogue.get('duration_seconds', '')
                
                survey_id = session.get('survey_id', '')
                survey_completed = 'Yes' if survey_id else 'No'
                
                csv_writer.writerow([
                    user_id, session_id, created_at, current_stage,
                    o, c, e, a, n, gerlach_type, gerlach_conf,
                    task_name, llm_personality,
                    message_count, duration,
                    survey_completed
                ])
            
            except Exception as e:
                st.warning(f"Error processing {session_file.name}: {e}")
    
    csv_buffer.seek(0)
    return csv_buffer.getvalue()

def admin_page():
    """Main admin download page"""
    
    if not check_password():
        return
    
    st.title("📊 Admin Data Download Center")
    st.write("Download participant data and manage research data exports")
    
    if st.button("🔓 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📥 Download All Data", "👤 Download by Participant", "📊 Export to CSV"])
    
    with tab1:
        st.header("Download All Research Data")
        st.write("Download a ZIP file containing all participant data from all folders.")
        
        participants = get_all_participants()
        st.metric("Total Participants", len(participants))
        
        if st.button("📦 Create ZIP File", key="zip_all"):
            with st.spinner("Creating ZIP file..."):
                zip_data = create_zip_all_data()
                
                if zip_data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    st.download_button(
                        label="⬇️ Download All Data (ZIP)",
                        data=zip_data,
                        file_name=f"gerlach_research_data_{timestamp}.zip",
                        mime="application/zip"
                    )
                    st.success("✅ ZIP file created successfully!")
                else:
                    st.error("❌ No data found to export")
    
    with tab2:
        st.header("Download Individual Participant Data")
        
        participants = get_all_participants()
        
        if participants:
            st.write(f"Found {len(participants)} participant(s)")
            
            for p in participants:
                with st.expander(f"👤 {p['user_id']} - {p['current_stage']}"):
                    st.write(f"**Session ID:** {p['session_id']}")
                    st.write(f"**Created:** {p['created_at']}")
                    st.write(f"**Current Stage:** {p['current_stage']}")
                    
                    if st.button(f"📦 Download {p['user_id']} Data", key=f"download_{p['session_id']}"):
                        with st.spinner(f"Creating ZIP for {p['user_id']}..."):
                            zip_data = create_zip_participant_data(p['user_id'])
                            
                            if zip_data:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                st.download_button(
                                    label=f"⬇️ Download {p['user_id']} Data (ZIP)",
                                    data=zip_data,
                                    file_name=f"participant_{p['user_id']}_{timestamp}.zip",
                                    mime="application/zip",
                                    key=f"dl_btn_{p['session_id']}"
                                )
                                st.success(f"✅ ZIP created for {p['user_id']}")
                            else:
                                st.error(f"❌ No data found for {p['user_id']}")
        else:
            st.info("No participants found yet")
    
    with tab3:
        st.header("Export to CSV for Analysis")
        st.write("Export all participant data to CSV format for analysis in Excel, SPSS, R, etc.")
        
        if st.button("📊 Generate CSV", key="csv_export"):
            with st.spinner("Generating CSV..."):
                csv_data = export_to_csv()
                
                if csv_data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"gerlach_research_data_{timestamp}.csv",
                        mime="text/csv"
                    )
                    st.success("✅ CSV file generated successfully!")
                    
                    st.write("**CSV includes:**")
                    st.write("- User ID, Session ID, Timestamps")
                    st.write("- Big5 scores (O, C, E, A, N)")
                    st.write("- Gerlach type and confidence")
                    st.write("- Task and LLM personality selections")
                    st.write("- Dialogue statistics")
                    st.write("- Survey completion status")
                else:
                    st.error("❌ No data found to export")

if __name__ == "__main__":
    admin_page()
