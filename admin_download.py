"""
Admin Download Page for Gerlach Research Platform
Password-protected data export
"""

import os
import streamlit as st
import json
import zipfile
import io
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "research_data"


def _get_admin_password():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return os.environ.get("ADMIN_PASSWORD", "")


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
        admin_pw = _get_admin_password()
        if not admin_pw:
            st.error("❌ Admin password is not configured on this server.")
        elif password == admin_pw:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")

    return False

def get_all_participants():
    """Get list of all participants from session files"""
    sessions_dir = DATA_DIR / "sessions"
    
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

def _json_to_txt(folder: str, data: dict, sub_folder: str = '') -> str:
    """Convert a JSON data dict to a human-readable plain-text string."""
    lines = []

    SEP = '=' * 60

    def add(label, value, indent=0):
        prefix = '  ' * indent
        lines.append(f"{prefix}{label:<24}{value}")

    def fmt_duration(seconds):
        if not isinstance(seconds, (int, float)):
            return '—'
        m, s = divmod(int(seconds), 60)
        return f"{m}m {s}s"

    def fmt_score(v):
        return f"{v:.1f}" if isinstance(v, (int, float)) else str(v)

    if folder == 'sessions':
        lines += ['SESSION RECORD', SEP]
        add('Participant:', data.get('user_id', ''))
        add('Session ID:', data.get('session_id', ''))
        add('Started:', data.get('started_at', ''))
        add('Ended:', data.get('ended_at') or '—')
        add('Current stage:', data.get('current_stage', ''))
        add('Completed stages:', ', '.join(data.get('completed_stages', [])) or '—')
        lines.append('')
        lines.append('Linked data:')
        add('Assessment ID:', data.get('big5_assessment_id') or '—', indent=1)
        add('Dialogue IDs:', ', '.join(data.get('dialogue_records', [])) or '—', indent=1)
        add('Task response IDs:', ', '.join(data.get('task_response_ids', [])) or '—', indent=1)
        add('Survey ID:', data.get('survey_id') or '—', indent=1)
        add('Report ID:', data.get('report_id') or '—', indent=1)

    elif folder == 'assessments':
        lines += ['BIG5 PERSONALITY ASSESSMENT', SEP]
        add('Participant:', data.get('user_id', ''))
        add('Assessment ID:', data.get('assessment_id', ''))
        add('Date:', data.get('conducted_at', ''))
        lines += ['', '--- Big5 Scores (0–100 scale) ---']
        for trait in ('openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'):
            add(f"{trait.capitalize()}:", fmt_score(data.get(trait, '')))
        lines.append('')
        gerlach_conf = data.get('gerlach_confidence')
        add('Gerlach Type:', data.get('gerlach_type') or '—')
        add('Confidence:', f"{gerlach_conf:.1f}%" if isinstance(gerlach_conf, (int, float)) else '—')
        lines += ['', '--- Individual Item Responses ---']
        responses = data.get('responses', {})
        if responses:
            for key in sorted(responses.keys()):
                lines.append(f"  {key}: {responses[key]}")
        else:
            lines.append('  (none recorded)')

    elif folder == 'dialogues':
        lines += ['DIALOGUE TRANSCRIPT', SEP]
        add('Participant:', data.get('user_id', ''))
        add('Dialogue ID:', data.get('dialogue_id', ''))
        add('Task:', data.get('task_name', ''))
        add('AI Personality:', data.get('llm_personality', ''))
        add('Started:', data.get('started_at', ''))
        add('Ended:', data.get('ended_at') or '—')
        add('Duration:', fmt_duration(data.get('duration_seconds')))
        add('Total messages:', str(data.get('total_messages', '')))
        add('Participant msgs:', str(data.get('user_message_count', '')))
        add('AI msgs:', str(data.get('assistant_message_count', '')))
        lines += ['', '--- Conversation ---']
        for msg in data.get('messages', []):
            ts = msg.get('timestamp', '')
            ts_short = ts[11:19] if len(ts) >= 19 else ts
            label = 'PARTICIPANT' if msg.get('role') == 'user' else 'AI ASSISTANT'
            lines.append(f"\n[{ts_short}] {label}:")
            for content_line in msg.get('content', '').splitlines():
                lines.append(f"  {content_line}")

    elif folder == 'task_responses':
        if sub_folder == 'noble' or 'rankings' in data:
            lines += ['TASK RESPONSE — Noble Industries', SEP]
            add('Participant:', data.get('user_id', ''))
            add('Response ID:', data.get('task_response_id', ''))
            add('Submitted:', data.get('submitted_at', ''))
            add('Time to complete:', fmt_duration(data.get('time_to_complete_seconds')))
            add('Ranking changes:', str(data.get('ranking_changes', 0)))
            lines += ['', '--- Candidate Rankings ---']
            for r in data.get('rankings', []):
                lines.append(f"\nRank {r.get('rank', '?')}: {r.get('candidate_name', '')}")
                for rl in r.get('rationale', '').splitlines():
                    lines.append(f"  {rl}")
        else:
            lines += ['TASK RESPONSE — Popcorn Brain', SEP]
            add('Participant:', data.get('user_id', ''))
            add('Response ID:', data.get('task_response_id', ''))
            add('Submitted:', data.get('submitted_at', ''))
            lines += ['', '--- Self-Assessment Ratings (1–7 scale) ---']
            for dim in ('originality', 'flexibility', 'elaboration', 'fluency'):
                add(f"{dim.capitalize()}:", str(data.get(f"{dim}_rating", '')))
            lines += ['', '--- Computed Metrics ---']
            add('Total ideas:', str(data.get('total_ideas', '')))
            add('Unique ideas:', str(data.get('unique_ideas', '')))
            add('Alternative approaches:', str(data.get('alternative_approaches', '')))
            add('Detail instances:', str(data.get('detail_instances', '')))
            ipm = data.get('ideas_per_minute', '')
            add('Ideas per minute:', f"{ipm:.2f}" if isinstance(ipm, (int, float)) else str(ipm))
            for dim in ('originality', 'flexibility', 'elaboration', 'fluency'):
                dim_data = data.get(dim)
                if dim_data and isinstance(dim_data, dict):
                    lines.append(f"\n  {dim.capitalize()} detail:")
                    lines.append(f"    Self-rating:     {dim_data.get('self_rating', '')}")
                    lines.append(f"    Computed count:  {dim_data.get('computed_count', '')}")
                    for ex in dim_data.get('examples', []):
                        lines.append(f"    - {ex}")

    elif folder == 'surveys':
        lines += ['POST-EXPERIMENT SURVEY', SEP]
        add('Participant:', data.get('user_id', ''))
        add('Survey ID:', data.get('survey_id', ''))
        add('Date:', data.get('conducted_at', ''))
        labeled = data.get('labeled_responses', {})
        if labeled:
            lines += ['', '--- Survey Responses ---']
            for key in sorted(labeled.keys()):
                item = labeled[key]
                if isinstance(item, dict):
                    q = item.get('question', key)
                    r = item.get('response', '')
                else:
                    q, r = key, str(item)
                lines.append(f"\n{q}")
                lines.append(f"  Response: {r}")
        else:
            responses = data.get('responses', {})
            if responses:
                lines += ['', '--- Survey Responses (raw) ---']
                for k, v in responses.items():
                    lines.append(f"  {k}: {v}")
        for field_key, label in [
            ('what_worked_well', 'What worked well'),
            ('what_could_improve', 'What could improve'),
            ('additional_comments', 'Additional comments'),
        ]:
            val = data.get(field_key)
            if val:
                lines.append(f"\n{label}:\n  {val}")

    elif folder == 'reports':
        lines += ['PARTICIPANT REPORT — SUMMARY', SEP]
        add('Participant:', data.get('user_id', ''))
        add('Report ID:', data.get('report_id', ''))
        add('Generated:', data.get('generated_at', ''))
        lines += ['', '--- Big5 Scores ---']
        for trait, score in data.get('big5_scores', {}).items():
            add(f"{trait.capitalize()}:", fmt_score(score))
        lines += ['', '']
        add('Gerlach Type:', data.get('gerlach_type') or '—')
        lines += ['', '--- Study Activity ---']
        add('Total messages:', str(data.get('total_messages', '')))
        add('Total time:', fmt_duration(data.get('total_time_seconds')))
        tasks = data.get('tasks_completed', [])
        if tasks:
            lines.append('\nTasks completed:')
            for t in tasks:
                lines.append(f"  - {t}")
        personalities = data.get('llm_personalities_used', [])
        if personalities:
            lines.append('\nAI personalities encountered:')
            for p in personalities:
                lines.append(f"  - {p}")
        avg_sat = data.get('average_satisfaction')
        avg_diff = data.get('average_task_difficulty')
        if avg_sat is not None:
            add('Average satisfaction:', fmt_score(avg_sat))
        if avg_diff is not None:
            add('Average difficulty:', fmt_score(avg_diff))
        lines.append('\n(For the full narrative report, see the accompanying .html file.)')

    else:
        lines += [f'DATA FILE — {folder.upper()}', SEP]
        lines.append(json.dumps(data, indent=2))

    return '\n'.join(lines)


def create_zip_all_data():
    """Create ZIP file containing all research data"""
    data_dir = DATA_DIR

    if not data_dir.exists():
        return None

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['sessions', 'assessments', 'dialogues', 'task_responses', 'surveys', 'reports']:
            folder_path = data_dir / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.rglob('*.json'):
                arcname = Path(str(file_path.relative_to(data_dir))).with_suffix('.txt')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    sub = file_path.parent.name if file_path.parent.name != folder else ''
                    zip_file.writestr(str(arcname), _json_to_txt(folder, data, sub))
                except Exception:
                    zip_file.write(file_path, file_path.relative_to(data_dir))

            for file_path in folder_path.rglob('*.md'):
                zip_file.write(file_path, file_path.relative_to(data_dir))

            for file_path in folder_path.rglob('*.html'):
                zip_file.write(file_path, file_path.relative_to(data_dir))

    zip_buffer.seek(0)
    return zip_buffer

def _descriptive_name(folder: str, file_path: Path, user_id: str) -> str:
    """Return a human-readable filename for a participant data file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return file_path.name

    suffix = file_path.suffix  # .json, .md, .html

    if folder == 'sessions':
        date = data.get('started_at', '')[:10]
        stage = data.get('current_stage', 'unknown')
        return f"SESSION_{user_id}_{date}_{stage}{suffix}"

    if folder == 'assessments':
        gerlach = data.get('gerlach_type', 'unknown').replace(' ', '_')
        return f"BIG5_ASSESSMENT_{user_id}_{gerlach}{suffix}"

    if folder == 'dialogues':
        task = data.get('task_name', 'unknown')
        task_short = (task.lower()
                      .replace('noble industries for big5.pdf', 'noble_industries')
                      .replace('popcorn brain task for big5-rev2.pdf', 'popcorn_brain')
                      .replace('.pdf', '')
                      .replace(' ', '_')[:30])
        personality = data.get('llm_personality', 'unknown').replace(' ', '_')
        return f"DIALOGUE_{user_id}_{task_short}_{personality}_llm{suffix}"

    if folder == 'surveys':
        return f"POST_TASK_SURVEY_{user_id}{suffix}"

    if folder == 'task_responses':
        return f"TASK_RESPONSE_{user_id}_{file_path.stem[-6:]}{suffix}"

    if folder == 'reports':
        return f"REPORT_{user_id}{suffix}"

    return file_path.name


def create_zip_participant_data(user_id):
    """Create ZIP file for a specific participant with descriptive filenames."""
    data_dir = DATA_DIR

    if not data_dir.exists():
        return None

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['sessions', 'assessments', 'dialogues', 'task_responses', 'surveys', 'reports']:
            folder_path = data_dir / folder
            if not folder_path.exists():
                continue
            for file_path in folder_path.rglob(f'*{user_id}*'):
                if file_path.suffix == '.json':
                    arcname = str(Path(_descriptive_name(folder, file_path, user_id)).with_suffix('.txt'))
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        sub = file_path.parent.name if file_path.parent.name != folder else ''
                        zip_file.writestr(arcname, _json_to_txt(folder, data, sub))
                    except Exception:
                        zip_file.write(file_path, _descriptive_name(folder, file_path, user_id))
                elif file_path.suffix in ('.md', '.html'):
                    arcname = _descriptive_name(folder, file_path, user_id)
                    zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer

def export_to_csv():
    """Export all data to CSV format for analysis"""
    import csv

    data_dir = DATA_DIR
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
                created_at = session.get('started_at', '')        # field is started_at, not created_at
                current_stage = session.get('current_stage', '')
                metadata = session.get('metadata', {})
                task_name = metadata.get('assigned_task', '')      # stored in metadata
                llm_personality = metadata.get('assigned_personality', '')  # stored in metadata

                assessment_id = session.get('big5_assessment_id', '')  # field is big5_assessment_id
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

                # dialogue_records is a list; use the first entry
                dialogue_records = session.get('dialogue_records', [])
                dialogue_id = dialogue_records[0] if dialogue_records else ''
                message_count, duration = '', ''

                if dialogue_id:
                    dialogue_file = data_dir / "dialogues" / f"{dialogue_id}.json"
                    if dialogue_file.exists():
                        with open(dialogue_file, 'r', encoding='utf-8') as df:
                            dialogue = json.load(df)
                            message_count = dialogue.get('user_message_count', len(dialogue.get('messages', [])))
                            duration = dialogue.get('duration_seconds', '')

                # Check surveys directory for this session (survey_id on session may not be set)
                survey_completed = 'No'
                if session.get('survey_id'):
                    survey_completed = 'Yes'
                else:
                    surveys_dir = data_dir / "surveys"
                    if surveys_dir.exists():
                        for sf in surveys_dir.glob("*.json"):
                            try:
                                with open(sf, 'r', encoding='utf-8') as svf:
                                    sv = json.load(svf)
                                if sv.get('session_id') == session_id:
                                    survey_completed = 'Yes'
                                    break
                            except Exception:
                                pass

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

def _render_activity_log():
    """Activity Log tab — who used the app, when, and their current status."""
    st.header("Participant Activity Log")
    st.caption("All sessions sorted by most recent login first. Refresh to update.")

    if st.button("🔄 Refresh", key="activity_refresh"):
        st.rerun()

    sessions_dir = DATA_DIR / "sessions"
    if not sessions_dir.exists():
        st.info("No participant sessions recorded yet.")
        return

    rows = []
    for session_file in sessions_dir.glob("*.json"):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                s = json.load(f)
            started_at = s.get('started_at', '')
            ended_at   = s.get('ended_at', '')
            stage      = s.get('current_stage', '')
            metadata   = s.get('metadata', {})
            rows.append({
                'user_id':     s.get('user_id', '—'),
                'session_id':  s.get('session_id', '—'),
                'started_at':  started_at,
                'ended_at':    ended_at,
                'stage':       stage,
                'task':        metadata.get('assigned_task', '—')
                                   .replace('NOBLE INDUSTRIES for Big5.pdf', 'Noble Industries')
                                   .replace('Popcorn Brain Task for Big5-rev2.pdf', 'Popcorn Brain'),
                'personality': metadata.get('assigned_personality', '—'),
                'completed':   stage == 'completed',
            })
        except Exception:
            continue

    if not rows:
        st.info("No sessions found.")
        return

    # Sort newest first
    rows.sort(key=lambda r: r['started_at'], reverse=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    total      = len(rows)
    completed  = sum(1 for r in rows if r['completed'])
    in_progress = total - completed
    latest     = rows[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions",   total)
    c2.metric("Completed",        completed)
    c3.metric("In Progress",      in_progress)

    st.markdown("---")

    # ── Most recent participant banner ────────────────────────────────────────
    st.subheader("Most Recent Participant")
    ts = latest['started_at']
    ts_display = ts[:19].replace('T', ' ') if len(ts) >= 19 else ts or '—'
    ended_display = latest['ended_at'][:19].replace('T', ' ') if latest['ended_at'] else '—'
    st.success(
        f"**{latest['user_id']}**  ·  "
        f"Logged in: {ts_display}  ·  "
        f"Stage: {latest['stage']}  ·  "
        f"{'✅ Completed at ' + ended_display if latest['completed'] else '🔄 In progress'}"
    )

    st.markdown("---")

    # ── Full table ────────────────────────────────────────────────────────────
    st.subheader("All Sessions")

    STAGE_LABELS = {
        'registration':    '1 — Registration',
        'big5_assessment': '2 — Big5 Assessment',
        'task_selection':  '3 — Task Selection',
        'task_dialogue':   '4 — Task Dialogue',
        'task_response':   '5 — Task Response',
        'post_survey':     '6 — Post Survey',
        'completed':       '7 — Completed ✅',
    }

    for i, r in enumerate(rows, 1):
        ts       = r['started_at'][:19].replace('T', ' ') if len(r['started_at']) >= 19 else r['started_at'] or '—'
        ended    = r['ended_at'][:19].replace('T', ' ')   if r['ended_at'] else '—'
        stage_lbl = STAGE_LABELS.get(r['stage'], r['stage'])
        icon     = '✅' if r['completed'] else '🔄'

        with st.expander(f"{icon}  #{i}  {r['user_id']}   ·   {ts}   ·   {stage_lbl}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**User ID:** {r['user_id']}")
                st.markdown(f"**Logged in:** {ts}")
                st.markdown(f"**Ended:** {ended}")
                st.markdown(f"**Stage:** {stage_lbl}")
            with col2:
                st.markdown(f"**Task:** {r['task']}")
                st.markdown(f"**AI Personality:** {r['personality']}")
                st.markdown(f"**Session ID:** `{r['session_id']}`")


def _render_personality_task_distribution():
    """Always-visible dashboard section — each participant's Gerlach type + assigned task,
    plus running totals/balance so the facilitator can see study progress at a glance."""
    st.header("🧬 Personality Type & Task Assignment")
    st.caption(
        "Each participant's Gerlach personality type (from the Big5 assessment), the task "
        "and the AI conversational personality they were assigned, with running totals so "
        "you can monitor balance across the study. This section is always shown, independent "
        "of the tabs below."
    )

    if st.button("🔄 Refresh", key="pers_task_refresh"):
        st.rerun()

    sessions_dir = DATA_DIR / "sessions"
    if not sessions_dir.exists():
        st.info("No participant sessions recorded yet.")
        return

    TASK_LABELS = {
        "NOBLE INDUSTRIES for Big5.pdf": "Noble Industries",
        "Popcorn Brain Task for Big5-rev2.pdf": "Popcorn Brain",
    }
    # gerlach_type is stored as these snake_case keys (see
    # agents/big5_assessment_agent.py classify_gerlach_type) — map to display labels.
    GERLACH_DISPLAY = {
        "average": "Average",
        "role_model": "Role Model",
        "self_centred": "Self-Centred",
        "reserved": "Reserved",
    }
    GERLACH_TYPES = list(GERLACH_DISPLAY.values())
    TASK_NAMES = list(TASK_LABELS.values())
    # assigned_personality (the AI's conversational persona) is stored using the SAME
    # snake_case keys as gerlach_type (average/role_model/self_centred/reserved) — this is
    # a coincidence of the two independent four-way taxonomies, not the same field. Reuse
    # GERLACH_DISPLAY for its display labels too.
    AI_PERSONALITY_NAMES = list(GERLACH_DISPLAY.values())

    rows = []
    for session_file in sessions_dir.glob("*.json"):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            continue

        metadata = s.get('metadata', {})
        assigned_task_raw = metadata.get('assigned_task', '')
        task_label = TASK_LABELS.get(assigned_task_raw, assigned_task_raw or '—')
        assigned_ai_raw = metadata.get('assigned_personality', '')
        ai_personality_label = GERLACH_DISPLAY.get(assigned_ai_raw, assigned_ai_raw or '—')

        gerlach_type = None
        assessment_id = s.get('big5_assessment_id')
        if assessment_id:
            assessment_file = DATA_DIR / "assessments" / f"{assessment_id}.json"
            if assessment_file.exists():
                try:
                    with open(assessment_file, 'r', encoding='utf-8') as af:
                        raw_type = json.load(af).get('gerlach_type')
                    if raw_type:
                        gerlach_type = GERLACH_DISPLAY.get(raw_type, raw_type)
                except Exception:
                    pass

        rows.append({
            'user_id': s.get('user_id', '—'),
            'gerlach_type': gerlach_type,
            'task': task_label if assigned_task_raw else None,
            'ai_personality': ai_personality_label if assigned_ai_raw else None,
            'stage': s.get('current_stage', ''),
        })

    if not rows:
        st.info("No sessions found.")
        return

    rows.sort(key=lambda r: r['user_id'])
    assessed_rows = [r for r in rows if r['gerlach_type']]
    n_assessed, n_total = len(assessed_rows), len(rows)

    st.metric("Participants with a completed Big5 assessment", f"{n_assessed} / {n_total}")

    # ── Counts per personality type ─────────────────────────────────────────
    st.subheader("Participants per Personality Type")
    st.caption(
        "Default target (30 per type) follows the common general-research rule of thumb "
        "for a reasonably reliable group comparison — adjust it if your analysis plan calls "
        "for a different number."
    )
    target_n = st.number_input(
        "Target sample size per personality type",
        min_value=1, value=30, step=1, key="pers_task_target_n",
    )

    type_counts = {t: 0 for t in GERLACH_TYPES}
    for r in assessed_rows:
        type_counts[r['gerlach_type']] = type_counts.get(r['gerlach_type'], 0) + 1

    cols = st.columns(len(type_counts))
    for col, (ptype, count) in zip(cols, type_counts.items()):
        with col:
            st.metric(ptype, count)
            if count < target_n:
                st.caption(f"⚠️ {target_n - count} more needed")
            else:
                st.caption("✅ Target reached")

    other_types = {t: c for t, c in type_counts.items() if t not in GERLACH_TYPES}
    if other_types:
        st.caption(f"Other/unrecognized type labels found: {other_types}")

    st.markdown("---")

    # ── Cross-tab: personality type x task ──────────────────────────────────
    st.subheader("Personality Type × Task Assignment")
    crosstab = {t: {task: 0 for task in TASK_NAMES} for t in GERLACH_TYPES}
    unassigned_task_count = 0
    for r in assessed_rows:
        t = r['gerlach_type']
        crosstab.setdefault(t, {task: 0 for task in TASK_NAMES})
        if r['task'] in TASK_NAMES:
            crosstab[t][r['task']] += 1
        else:
            unassigned_task_count += 1

    try:
        import pandas as pd
        df = pd.DataFrame(crosstab).T
        df = df.reindex(columns=TASK_NAMES, fill_value=0)
        df['Total'] = df.sum(axis=1)
        st.dataframe(df, use_container_width=True)
    except ImportError:
        for t, task_counts in crosstab.items():
            line = "  |  ".join(f"{task}: {task_counts.get(task, 0)}" for task in TASK_NAMES)
            st.markdown(f"**{t}** — {line}")

    if unassigned_task_count:
        st.caption(f"{unassigned_task_count} assessed participant(s) have not been assigned a task yet.")

    st.markdown("---")

    # ── Cross-tab: personality type x AI personality ────────────────────────
    st.subheader("Personality Type × AI Personality Assignment")
    ai_crosstab = {t: {p: 0 for p in AI_PERSONALITY_NAMES} for t in GERLACH_TYPES}
    unassigned_ai_count = 0
    for r in assessed_rows:
        t = r['gerlach_type']
        ai_crosstab.setdefault(t, {p: 0 for p in AI_PERSONALITY_NAMES})
        if r['ai_personality'] in AI_PERSONALITY_NAMES:
            ai_crosstab[t][r['ai_personality']] += 1
        else:
            unassigned_ai_count += 1

    try:
        import pandas as pd
        df_ai = pd.DataFrame(ai_crosstab).T
        df_ai = df_ai.reindex(columns=AI_PERSONALITY_NAMES, fill_value=0)
        df_ai['Total'] = df_ai.sum(axis=1)
        st.dataframe(df_ai, use_container_width=True)
    except ImportError:
        for t, ai_counts in ai_crosstab.items():
            line = "  |  ".join(f"{p}: {ai_counts.get(p, 0)}" for p in AI_PERSONALITY_NAMES)
            st.markdown(f"**{t}** — {line}")

    if unassigned_ai_count:
        st.caption(f"{unassigned_ai_count} assessed participant(s) have not been assigned an AI personality yet.")

    # ── Full participant list ───────────────────────────────────────────────
    with st.expander(f"All Participants ({n_total})", expanded=True):
        for r in rows:
            icon = '✅' if r['gerlach_type'] else '⏳'
            gerlach_display = r['gerlach_type'] or 'not yet assessed'
            task_display = r['task'] or 'not yet assigned'
            ai_display = r['ai_personality'] or 'not yet assigned'
            st.markdown(
                f"{icon} **{r['user_id']}** — Type: `{gerlach_display}`  ·  "
                f"Task: `{task_display}`  ·  AI: `{ai_display}`  ·  Stage: `{r['stage']}`"
            )


def _collect_progress_rows():
    """One row per session with resolved timestamps for each stage transition.

    Stage-transition timestamps aren't stored directly on the session, so they're
    approximated from the timestamp on each stage's own artifact (assessment
    conducted_at, dialogue started/ended_at, task_response submitted_at, survey
    conducted_at). last_activity is the max of everything found, used for
    stalled-session detection.
    """
    sessions_dir = DATA_DIR / "sessions"
    rows = []
    if not sessions_dir.exists():
        return rows

    for session_file in sessions_dir.glob("*.json"):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            continue

        started_at = s.get('started_at', '')
        ended_at = s.get('ended_at') or None

        assessment_at = None
        assessment_id = s.get('big5_assessment_id')
        if assessment_id:
            af = DATA_DIR / "assessments" / f"{assessment_id}.json"
            if af.exists():
                try:
                    with open(af, 'r', encoding='utf-8') as fh:
                        assessment_at = json.load(fh).get('conducted_at')
                except Exception:
                    pass

        dialogue_started_at, dialogue_ended_at, last_message_at = None, None, None
        dialogue_records = s.get('dialogue_records', [])
        if dialogue_records:
            df = DATA_DIR / "dialogues" / f"{dialogue_records[0]}.json"
            if df.exists():
                try:
                    with open(df, 'r', encoding='utf-8') as fh:
                        d = json.load(fh)
                    dialogue_started_at = d.get('started_at')
                    dialogue_ended_at = d.get('ended_at')
                    messages = d.get('messages', [])
                    if messages:
                        last_message_at = messages[-1].get('timestamp')
                except Exception:
                    pass

        task_response_at = None
        task_response_ids = s.get('task_response_ids', [])
        if task_response_ids:
            trf = DATA_DIR / "task_responses" / f"{task_response_ids[0]}.json"
            if trf.exists():
                try:
                    with open(trf, 'r', encoding='utf-8') as fh:
                        task_response_at = json.load(fh).get('submitted_at')
                except Exception:
                    pass

        survey_at = None
        survey_id = s.get('survey_id')
        if survey_id:
            svf = DATA_DIR / "surveys" / f"{survey_id}.json"
            if svf.exists():
                try:
                    with open(svf, 'r', encoding='utf-8') as fh:
                        survey_at = json.load(fh).get('conducted_at')
                except Exception:
                    pass

        all_ts = [t for t in [started_at, assessment_at, dialogue_started_at, last_message_at,
                               dialogue_ended_at, task_response_at, survey_at, ended_at] if t]
        last_activity = max(all_ts) if all_ts else started_at

        rows.append({
            'user_id': s.get('user_id', '—'),
            'session_id': s.get('session_id', '—'),
            'stage': s.get('current_stage', ''),
            'started_at': started_at,
            'ended_at': ended_at,
            'assessment_at': assessment_at,
            'dialogue_started_at': dialogue_started_at,
            'dialogue_ended_at': dialogue_ended_at,
            'task_response_at': task_response_at,
            'survey_at': survey_at,
            'last_activity': last_activity,
        })
    return rows


def _render_study_progress():
    """Study Progress tab — stage funnel vs. target, stalled sessions, enrollment
    trend, and average time per stage."""
    st.header("📈 Study Progress")
    st.caption("Funnel, pacing, stalled sessions, and stage timing across all participants.")

    if st.button("🔄 Refresh", key="progress_refresh"):
        st.rerun()

    rows = _collect_progress_rows()
    if not rows:
        st.info("No participant sessions recorded yet.")
        return

    STAGES = [
        "registration", "big5_assessment", "task_selection",
        "task_dialogue", "task_response", "post_survey", "completed",
    ]
    STAGE_LABELS = {
        "registration":    "1 — Registration",
        "big5_assessment": "2 — Big5 Assessment",
        "task_selection":  "3 — Task Selection",
        "task_dialogue":   "4 — Task Dialogue",
        "task_response":   "5 — Task Response",
        "post_survey":     "6 — Post Survey",
        "completed":       "7 — Completed",
    }

    # ── Target & overall completion ─────────────────────────────────────────
    target_n = st.number_input(
        "Target sample size (total)", min_value=1, value=100, step=1, key="progress_target_n"
    )
    total = len(rows)
    completed = sum(1 for r in rows if r['stage'] == 'completed')
    st.metric("Completed", f"{completed} / {target_n}", f"{total - completed} in progress")
    st.progress(min(completed / target_n, 1.0))

    st.markdown("---")

    # ── Stage funnel ─────────────────────────────────────────────────────────
    st.subheader("Stage Funnel — where participants are right now")
    stage_counts = {stg: 0 for stg in STAGES}
    for r in rows:
        if r['stage'] in stage_counts:
            stage_counts[r['stage']] += 1
    for stg in STAGES:
        n = stage_counts[stg]
        st.markdown(f"**{STAGE_LABELS[stg]}** — {n} participant(s)")
        st.progress(n / total if total else 0)

    st.markdown("---")

    # ── Stalled sessions ─────────────────────────────────────────────────────
    st.subheader("Stalled Sessions")
    stall_hours = st.number_input(
        "Flag as stalled if no activity for (hours)", min_value=1, value=48, step=1,
        key="progress_stall_hours",
    )
    now = datetime.now()
    stalled = []
    for r in rows:
        if r['stage'] == 'completed' or not r['last_activity']:
            continue
        try:
            la_dt = datetime.fromisoformat(r['last_activity'][:19])
        except Exception:
            continue
        hours_idle = (now - la_dt).total_seconds() / 3600
        if hours_idle >= stall_hours:
            stalled.append((r, hours_idle))

    if stalled:
        stalled.sort(key=lambda x: -x[1])
        for r, hrs in stalled:
            st.warning(
                f"⏸️ **{r['user_id']}** — stuck at *{STAGE_LABELS.get(r['stage'], r['stage'])}*, "
                f"idle for {hrs:.0f}h (last activity: {r['last_activity'][:19].replace('T', ' ')})"
            )
    else:
        st.success(f"No sessions idle for {stall_hours}+ hours.")

    st.markdown("---")

    # ── Enrollment / completion trend ────────────────────────────────────────
    st.subheader("Enrollment & Completion Trend")
    try:
        import pandas as pd
        reg_dates = [r['started_at'][:10] for r in rows if r['started_at']]
        comp_dates = [r['ended_at'][:10] for r in rows if r['ended_at']]
        all_dates = sorted(set(reg_dates) | set(comp_dates))
        if all_dates:
            trend_df = pd.DataFrame({
                'Registrations': [reg_dates.count(d) for d in all_dates],
                'Completions': [comp_dates.count(d) for d in all_dates],
            }, index=all_dates)
            st.bar_chart(trend_df)
        else:
            st.info("Not enough date data yet.")
    except ImportError:
        st.info("Install pandas to see the trend chart.")

    st.markdown("---")

    # ── Average time per stage ───────────────────────────────────────────────
    st.subheader("Average Time per Stage")
    st.caption(
        "Estimated from each stage's recorded artifact timestamp (assessment, dialogue, "
        "task response, survey). Only participants who have reached a given stage boundary "
        "are included in that segment's average."
    )

    def _delta_minutes(a, b):
        if not a or not b:
            return None
        try:
            return (datetime.fromisoformat(b[:19]) - datetime.fromisoformat(a[:19])).total_seconds() / 60
        except Exception:
            return None

    segments = [
        ("Registration → Big5 Assessment",        'started_at',          'assessment_at'),
        ("Big5 Assessment → Task Dialogue start",  'assessment_at',       'dialogue_started_at'),
        ("Task Dialogue (start → end)",            'dialogue_started_at', 'dialogue_ended_at'),
        ("Task Dialogue end → Task Response",      'dialogue_ended_at',   'task_response_at'),
        ("Task Response → Post Survey",            'task_response_at',    'survey_at'),
        ("Post Survey → Completed",                'survey_at',           'ended_at'),
        ("Total (Registration → Completed)",       'started_at',          'ended_at'),
    ]
    for label, a_key, b_key in segments:
        deltas = []
        for r in rows:
            d = _delta_minutes(r.get(a_key), r.get(b_key))
            if d is not None and d >= 0:
                deltas.append(d)
        if deltas:
            avg = sum(deltas) / len(deltas)
            st.markdown(f"**{label}:** avg {avg:.1f} min  ·  n={len(deltas)}")
        else:
            st.markdown(f"**{label}:** — (no data yet)")


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

    # Always visible, regardless of which tab is selected below, so the facilitator
    # can see personality-type/task balance at a glance without extra clicks.
    _render_personality_task_distribution()

    st.markdown("---")

    tab0, tab_progress, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["👥 Activity Log", "📈 Study Progress", "📥 Download All Data", "👤 Download by Participant", "📊 Export to CSV", "🔀 Stage Navigator", "🔌 GitHub Test", "🤖 API Monitor"])

    with tab0:
        _render_activity_log()

    with tab_progress:
        _render_study_progress()

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

    with tab4:
        st.header("Stage Navigator")
        st.markdown(
            "Jump any participant's session to a specific stage. "
            "Use this for testing, reviewing what participants see, or assisting a stuck participant."
        )
        st.warning("This directly modifies a session's current stage. Use with care.")

        participants = get_all_participants()

        STAGES = [
            "registration",
            "big5_assessment",
            "task_selection",
            "task_dialogue",
            "task_response",
            "post_survey",
            "completed",
        ]
        STAGE_LABELS = {
            "registration":    "1 — Registration",
            "big5_assessment": "2 — Big5 Assessment",
            "task_selection":  "3 — Task Selection",
            "task_dialogue":   "4 — Task Dialogue",
            "task_response":   "5 — Task Response",
            "post_survey":     "6 — Post-Experiment Survey",
            "completed":       "7 — Completed",
        }

        if not participants:
            st.info("No participant sessions found yet.")
        else:
            # Build selection list
            options = {
                f"{p['user_id']}  —  currently at: {p['current_stage']}  ({p['session_id']})": p
                for p in sorted(participants, key=lambda x: x['user_id'])
            }
            selected_label = st.selectbox("Select participant session:", list(options.keys()))
            selected = options[selected_label]

            current_idx = STAGES.index(selected['current_stage']) if selected['current_stage'] in STAGES else 0
            target_stage = st.selectbox(
                "Jump to stage:",
                STAGES,
                index=current_idx,
                format_func=lambda s: STAGE_LABELS.get(s, s)
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✈️ Jump to Stage", use_container_width=True, type="primary"):
                    session_file = DATA_DIR / "sessions" / selected['file']
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        session_data['current_stage'] = target_stage
                        if target_stage not in session_data.get('completed_stages', []):
                            session_data.setdefault('completed_stages', [])
                        with open(session_file, 'w', encoding='utf-8') as f:
                            json.dump(session_data, f, indent=2)
                        # Sync to GitHub so the change survives a server restart
                        try:
                            from github_storage import get_storage
                            get_storage().write(f"sessions/{selected['file']}", session_data)
                            github_note = "GitHub synced ✓"
                        except Exception:
                            github_note = "⚠️ GitHub sync failed — change is local only"
                        st.success(
                            f"✅ **{selected['user_id']}** moved to "
                            f"**{STAGE_LABELS.get(target_stage, target_stage)}**. "
                            f"They will see the new stage on their next page load. ({github_note})"
                        )
                    except Exception as e:
                        st.error(f"Failed to update session: {e}")
            with col2:
                st.markdown(
                    f"Current: **{STAGE_LABELS.get(selected['current_stage'], selected['current_stage'])}**"
                )

        st.markdown("---")
        st.markdown("**How to use for testing:**")
        st.markdown(
            "1. Register a test participant (e.g. ID: `test01`) on the main app\n"
            "2. Come back here and jump them to any stage\n"
            "3. Return to the main app with that ID via Resume Session to view that stage"
        )


    with tab5:
        st.header("GitHub Storage Connection Test")
        st.write("Verify that the GitHub data repository is reachable and writable.")

        if st.button("🔌 Run Connection Test", type="primary"):
            from github_storage import get_storage
            gh = get_storage()

            if not gh.enabled:
                st.error("❌ GitHub storage is **disabled**. Check that GITHUB_DATA_TOKEN, "
                         "GITHUB_DATA_OWNER, and GITHUB_DATA_REPO are all set in Streamlit secrets.")
            else:
                st.info(f"Connecting to: `{gh.owner}/{gh.repo}`")

                # Step 1: read the README to confirm read access
                with st.spinner("Testing read access…"):
                    raw = gh.read_raw("README.md")
                if raw is not None:
                    st.success("✅ Read access OK")
                else:
                    st.error("❌ Read failed — token may lack Contents permission or repo name is wrong")

                # Step 2: write a small test file to confirm write access
                with st.spinner("Testing write access…"):
                    ok = gh.write("_connection_test.json", {"status": "ok"})
                if ok:
                    st.success("✅ Write access OK — GitHub storage is fully working!")
                else:
                    st.error("❌ Write failed — token likely missing **Contents: Read and write** permission. "
                             "Regenerate the token and ensure that permission is set.")


    with tab6:
        _render_api_monitor()


def _render_api_monitor():
    """API Monitor tab — LLM call health, latency, tokens, errors."""
    import api_monitor

    st.header("🤖 Anthropic API Monitor")

    hours = st.select_slider(
        "Time window",
        options=[1, 3, 6, 12, 24, 48, 72],
        value=24,
        format_func=lambda h: f"Last {h}h",
    )

    if st.button("🔄 Refresh", key="api_monitor_refresh"):
        st.rerun()

    stats = api_monitor.get_stats(hours=hours)

    # ── Health banner ────────────────────────────────────────────────────────
    health = stats["health"]
    if stats["total_calls"] == 0:
        st.info(f"No API calls recorded in the last {hours}h. Make sure the app has been used.")
    elif health == "green":
        st.success(f"✅ API Healthy — {stats['success_rate_pct']}% success rate over last {hours}h")
    elif health == "yellow":
        st.warning(f"⚠️ Degraded — {stats['success_rate_pct']}% success rate over last {hours}h")
    else:
        st.error(f"🔴 Unhealthy — {stats['success_rate_pct']}% success rate over last {hours}h")

    st.markdown("---")

    # ── Key metrics ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Calls", stats["total_calls"])
    c2.metric("Successful", stats["success_calls"])
    c3.metric("Failed", stats["fail_calls"],
              delta=f"-{stats['fail_calls']}" if stats["fail_calls"] else None,
              delta_color="inverse")
    c4.metric("Avg Latency",
              f"{stats['avg_latency_ms']:.0f} ms" if stats["avg_latency_ms"] is not None else "—")
    c5.metric("Total Tokens", f"{stats['total_tokens']:,}" if stats["total_tokens"] else "0")

    st.markdown("---")

    # ── Token breakdown ──────────────────────────────────────────────────────
    col_in, col_out = st.columns(2)
    col_in.metric("Input Tokens",  f"{stats['total_input_tokens']:,}")
    col_out.metric("Output Tokens", f"{stats['total_output_tokens']:,}")

    if stats.get("p95_latency_ms") is not None:
        st.caption(f"p95 latency: {stats['p95_latency_ms']:.0f} ms")

    st.markdown("---")

    # ── Calls per hour chart ─────────────────────────────────────────────────
    if stats["calls_by_hour"]:
        st.subheader("Calls per Hour")
        try:
            import pandas as pd
            chart_df = pd.DataFrame(
                {"API Calls": list(stats["calls_by_hour"].values())},
                index=list(stats["calls_by_hour"].keys()),
            )
            st.bar_chart(chart_df)
        except ImportError:
            # Fallback: text-based bar
            max_count = max(stats["calls_by_hour"].values()) or 1
            for hour_label, count in stats["calls_by_hour"].items():
                bar = "█" * int(count / max_count * 20)
                st.text(f"{hour_label}  {bar} {count}")

    # ── Error breakdown ──────────────────────────────────────────────────────
    if stats["errors_by_type"]:
        st.markdown("---")
        st.subheader("Errors by Type")
        for etype, count in sorted(stats["errors_by_type"].items(), key=lambda x: -x[1]):
            st.markdown(f"- **{etype}**: {count} occurrence{'s' if count != 1 else ''}")

    # ── Recent failures ──────────────────────────────────────────────────────
    if stats["recent_errors"]:
        st.markdown("---")
        st.subheader(f"Recent Failures (last {len(stats['recent_errors'])})")
        for err in stats["recent_errors"]:
            ts = err.get("ts", "")[:19].replace("T", " ")
            personality = err.get("personality", "?")
            etype = err.get("error_type") or "Unknown"
            emsg = err.get("error_msg") or ""
            latency = err.get("latency_ms", "?")
            with st.expander(f"❌  {ts}  ·  {personality}  ·  {etype}"):
                st.markdown(f"**Time:** {ts}")
                st.markdown(f"**Personality:** {personality}")
                st.markdown(f"**Call type:** {err.get('call_type', '?')}")
                st.markdown(f"**Latency:** {latency} ms")
                st.markdown(f"**Session:** `{err.get('session_id', '—')}`")
                st.markdown(f"**Dialogue:** `{err.get('dialogue_id', '—')}`")
                if emsg:
                    st.code(emsg)
    else:
        st.success("No failures recorded in this window.")

    # ── Raw log download ─────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Download Raw Logs")
    log_dir = Path(__file__).parent / "research_data" / "api_logs"
    if log_dir.exists():
        log_files = sorted(log_dir.glob("*.json"), reverse=True)
        if log_files:
            selected_log = st.selectbox(
                "Select log file",
                [f.name for f in log_files],
            )
            log_path = log_dir / selected_log
            try:
                raw = log_path.read_text(encoding="utf-8")
                st.download_button(
                    label=f"⬇️ Download {selected_log}",
                    data=raw,
                    file_name=selected_log,
                    mime="application/json",
                )
            except Exception as e:
                st.error(f"Could not read log file: {e}")
        else:
            st.info("No log files yet.")
    else:
        st.info("Log directory not created yet — logs appear after the first API call.")


if __name__ == "__main__":
    admin_page()
