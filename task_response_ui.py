"""
Task-Specific Response UI Components
Noble Industries and Popcorn Brain interfaces
"""

import streamlit as st
from pathlib import Path


def render_task_response(agents, session, dialogue_id):
    """Advance immediately to POST_SURVEY — task assessment is admin-only."""
    from agents import WorkflowStage
    agents['supervisor'].advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
    st.rerun()


def render_noble_industries(agents, session, dialogue):
    """Noble Industries: Candidate Ranking Interface"""
    st.header("📊 Noble Industries - Candidate Rankings")
    
    st.markdown(f"""
    **Task Completed**: {dialogue.task_name.replace('.pdf', '')}
    **Messages Exchanged**: {dialogue.total_messages}
    """)

    st.markdown("---")

    st.markdown("""
    ### Instructions
    Please rank the candidates you discussed with the AI assistant and provide your rationale for each ranking.
    
    - **Rank 1** = Top choice (best candidate)
    - **Rank 2** = Second choice
    - And so on...
    """)
    
    # Define candidates (these should ideally be extracted from the PDF)
    candidates = [
        "Candidate A",
        "Candidate B", 
        "Candidate C",
        "Candidate D",
        "Candidate E"
    ]
    
    with st.form("noble_rankings_form"):
        st.subheader("Rank the Candidates")
        
        rankings_data = []
        
        for i, candidate in enumerate(candidates):
            st.markdown(f"#### {candidate}")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                rank = st.number_input(
                    "Rank",
                    min_value=1,
                    max_value=len(candidates),
                    value=i+1,
                    key=f"rank_{i}",
                    help=f"Rank for {candidate} (1 = best)"
                )
            
            with col2:
                rationale = st.text_area(
                    "Rationale",
                    placeholder=f"Why did you rank {candidate} at this position? What were the key factors?",
                    key=f"rationale_{i}",
                    height=100
                )
            
            rankings_data.append({
                'candidate': candidate,
                'rank': rank,
                'rationale': rationale
            })
            
            if i < len(candidates) - 1:
                st.markdown("---")
        
        submit = st.form_submit_button("Submit Rankings", use_container_width=True, type="primary")
        
        if submit:
            # Validate rankings
            ranks = [r['rank'] for r in rankings_data]
            if len(set(ranks)) != len(ranks):
                st.error("⚠️ Each candidate must have a unique rank. Please check for duplicates.")
            elif any(not r['rationale'].strip() for r in rankings_data):
                st.error("⚠️ Please provide a rationale for each candidate.")
            else:
                # Capture rankings
                formatted_rankings = [
                    {
                        'rank': r['rank'],
                        'candidate_name': r['candidate'],
                        'rationale': r['rationale']
                    }
                    for r in rankings_data
                ]
                
                task_response = agents['task_response'].capture_noble_rankings(
                    user_id=session.user_id,
                    session_id=session.session_id,
                    dialogue_id=dialogue.dialogue_id,
                    rankings=formatted_rankings
                )
                
                # Update session
                session.task_response_ids.append(task_response.task_response_id)
                session.save(Path(agents['supervisor'].data_dir))
                
                # Advance to survey
                from agents import WorkflowStage
                agents['supervisor'].advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
                
                st.success("✅ Rankings submitted successfully!")
                st.rerun()


def render_popcorn_brain(agents, session, dialogue):
    """Popcorn Brain: Creative Performance Assessment"""
    st.header("🧠 Popcorn Brain - Creative Performance Assessment")
    
    st.markdown(f"""
    **Task Completed**: {dialogue.task_name.replace('.pdf', '')}
    **Messages Exchanged**: {dialogue.total_messages}
    """)

    st.markdown("---")

    st.markdown("""
    ### Instructions
    Please assess your creative performance during the task-solving dialogue.
    
    Rate each dimension on a scale of **1-7**:
    - **1** = Strongly Disagree
    - **4** = Neutral
    - **7** = Strongly Agree
    """)
    
    with st.form("popcorn_assessment_form"):
        st.subheader("Creative Dimensions Self-Assessment")
        
        # Originality
        st.markdown("#### 1. Originality (Uniqueness of Ideas)")
        originality = st.slider(
            "**I created unique ideas to solve the given problem**",
            min_value=1,
            max_value=7,
            value=4,
            help="Rate how unique and novel your ideas were",
            key="originality"
        )
        
        st.markdown("---")
        
        # Flexibility
        st.markdown("#### 2. Flexibility (Alternative Approaches)")
        flexibility = st.slider(
            "**I presented alternative ideas to other group members' ideas**",
            min_value=1,
            max_value=7,
            value=4,
            help="Rate how many alternative approaches you considered",
            key="flexibility"
        )
        
        st.markdown("---")
        
        # Elaboration
        st.markdown("#### 3. Elaboration (Detail and Synthesis)")
        elaboration = st.slider(
            "**I created details to add to other members' ideas**",
            min_value=1,
            max_value=7,
            value=4,
            help="Rate how much you elaborated and added details to ideas",
            key="elaboration"
        )
        
        st.markdown("---")
        
        # Fluency
        st.markdown("#### 4. Fluency (Quantity of Ideas)")
        fluency = st.slider(
            "**I created many ideas to solve the given problem**",
            min_value=1,
            max_value=7,
            value=4,
            help="Rate the quantity of ideas you generated",
            key="fluency"
        )
        
        st.markdown("---")
        
        submit = st.form_submit_button("Submit Assessment", use_container_width=True, type="primary")
        
        if submit:
            self_ratings = {
                'originality': originality,
                'flexibility': flexibility,
                'elaboration': elaboration,
                'fluency': fluency
            }

            task_response = agents['task_response'].capture_popcorn_assessment(
                user_id=session.user_id,
                session_id=session.session_id,
                dialogue_id=dialogue.dialogue_id,
                self_ratings=self_ratings,
                dialogue_agent=agents['dialogue']
            )

            # Update session
            session.task_response_ids.append(task_response.task_response_id)
            session.save(Path(agents['supervisor'].data_dir))

            # Advance to survey silently — metrics recorded for admin report only
            from agents import WorkflowStage
            agents['supervisor'].advance_stage(session.session_id, WorkflowStage.POST_SURVEY)
            st.rerun()
