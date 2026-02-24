"""
Streamlit Interface for Gerlach Personality Validation
Run validation tests and view/download results
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from gerlach_personality_llms import GerlachPersonalityManager
from gerlach_validation_suite import GerlachValidationSuite, ValidationReport

st.set_page_config(
    page_title="Gerlach Validation Suite",
    page_icon="🧪",
    layout="wide"
)

# Initialize
if 'manager' not in st.session_state:
    try:
        st.session_state.manager = GerlachPersonalityManager()
        st.session_state.manager_ready = True
    except Exception as e:
        st.session_state.manager_ready = False
        st.session_state.manager_error = str(e)

if 'validation_report' not in st.session_state:
    st.session_state.validation_report = None

if 'validation_running' not in st.session_state:
    st.session_state.validation_running = False

st.title("🧪 Gerlach Personality Validation Suite")

if not st.session_state.manager_ready:
    st.error(f"❌ Failed to initialize: {st.session_state.manager_error}")
    st.info("Please set your ANTHROPIC_API_KEY environment variable and restart.")
    st.stop()

st.markdown("""
This validation suite tests each of the four Gerlach (2018) personality types to ensure they 
accurately represent the characteristics described in the research paper.
""")

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Test Configuration")
    
    tests_per_personality = st.slider(
        "Tests per personality",
        min_value=3,
        max_value=15,
        value=8,
        help="Number of test prompts to run for each personality type"
    )
    
    st.markdown("---")
    st.markdown("## 📊 Expected Traits")
    
    with st.expander("Average"):
        st.markdown("- Balanced, moderate responses\n- Practical, common sense\n- Flexible, adaptable")
    
    with st.expander("Role model"):
        st.markdown("- Enthusiastic, positive\n- Organized, disciplined\n- Creative, curious\n- Cooperative, empathetic")
    
    with st.expander("Self-centred"):
        st.markdown("- Focus on self (I, me, my)\n- Conventional, practical\n- Direct, competitive\n- Skeptical of others")
    
    with st.expander("Reserved"):
        st.markdown("- Quiet, calm\n- Routine, familiar\n- Conventional, traditional\n- Brief, straightforward")

# Main content
tab1, tab2, tab3 = st.tabs(["🚀 Run Validation", "📊 Results", "📥 Download"])

with tab1:
    st.markdown("### Run Validation Tests")
    
    st.info(f"""
    **Test Plan:**
    - {tests_per_personality} tests per personality type
    - Total tests: {tests_per_personality * 4}
    - Estimated time: ~{tests_per_personality * 4 * 2} seconds
    """)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("▶️ Start Validation", type="primary", use_container_width=True, disabled=st.session_state.validation_running):
            st.session_state.validation_running = True
            st.rerun()
    
    with col2:
        if st.session_state.validation_running:
            st.warning("⏳ Validation in progress... Please wait.")
    
    # Run validation
    if st.session_state.validation_running:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        suite = GerlachValidationSuite(st.session_state.manager)
        
        # Progress tracking
        total_tests = tests_per_personality * 4
        current_test = 0
        
        # Custom run with progress updates
        all_tests = []
        summary_scores = {}
        detailed_analysis = {}
        
        all_prompts = []
        for category_prompts in suite.TEST_PROMPTS.values():
            all_prompts.extend(category_prompts)
        
        for personality_type in st.session_state.manager.list_personalities():
            status_text.text(f"Testing {personality_type.upper()} personality...")
            
            personality_tests = []
            
            for i in range(min(tests_per_personality, len(all_prompts))):
                prompt = all_prompts[i]
                test_id = f"{personality_type}_{i+1:02d}"
                
                test = suite.run_single_test(personality_type, prompt, test_id)
                personality_tests.append(test)
                all_tests.append(test)
                
                current_test += 1
                progress_bar.progress(current_test / total_tests)
                status_text.text(f"Testing {personality_type.upper()}: {i+1}/{tests_per_personality} (Score: {test.trait_match_score:.2f})")
            
            avg_score = sum(t.trait_match_score for t in personality_tests) / len(personality_tests)
            summary_scores[personality_type] = avg_score
            
            detailed_analysis[personality_type] = {
                "average_score": avg_score,
                "total_tests": len(personality_tests),
                "high_scoring_tests": len([t for t in personality_tests if t.trait_match_score > 0.3]),
                "low_scoring_tests": len([t for t in personality_tests if t.trait_match_score < 0.15]),
                "most_common_traits": suite._get_most_common_traits(personality_tests),
            }
        
        report = ValidationReport(
            test_date=datetime.now().isoformat(),
            total_tests=len(all_tests),
            personalities_tested=list(st.session_state.manager.list_personalities()),
            test_results=all_tests,
            summary_scores=summary_scores,
            detailed_analysis=detailed_analysis
        )
        
        st.session_state.validation_report = report
        st.session_state.validation_running = False
        
        progress_bar.progress(1.0)
        status_text.text("✅ Validation complete!")
        
        st.success("Validation completed successfully! Check the Results tab.")
        st.balloons()

with tab2:
    st.markdown("### Validation Results")
    
    if st.session_state.validation_report is None:
        st.info("No validation results yet. Run validation in the first tab.")
    else:
        report = st.session_state.validation_report
        
        st.markdown(f"**Test Date:** {report.test_date}")
        st.markdown(f"**Total Tests:** {report.total_tests}")
        
        # Summary scores
        st.markdown("### Summary Scores")
        
        score_data = []
        for ptype, score in report.summary_scores.items():
            status = "✅ Good" if score > 0.25 else "⚠️ Review" if score > 0.15 else "❌ Poor"
            score_data.append({
                "Personality": ptype.title(),
                "Score": f"{score:.3f}",
                "Status": status
            })
        
        df_scores = pd.DataFrame(score_data)
        st.dataframe(df_scores, use_container_width=True, hide_index=True)
        
        # Detailed analysis
        st.markdown("### Detailed Analysis")
        
        cols = st.columns(2)
        for idx, ptype in enumerate(report.personalities_tested):
            analysis = report.detailed_analysis[ptype]
            
            with cols[idx % 2]:
                st.markdown(f"#### {ptype.title()}")
                st.metric("Average Score", f"{analysis['average_score']:.3f}")
                st.metric("High-scoring Tests", f"{analysis['high_scoring_tests']}/{analysis['total_tests']}")
                st.markdown(f"**Common Traits:** {', '.join(analysis['most_common_traits'][:3])}")
        
        # Sample responses
        st.markdown("### Sample Test Responses")
        
        for ptype in report.personalities_tested:
            with st.expander(f"{ptype.title()} - Sample Responses"):
                ptype_tests = [t for t in report.test_results if t.personality_type == ptype]
                ptype_tests.sort(key=lambda x: x.trait_match_score, reverse=True)
                
                for i, test in enumerate(ptype_tests[:3], 1):
                    st.markdown(f"**Test {i}** (Score: {test.trait_match_score:.3f})")
                    st.markdown(f"*Prompt:* {test.prompt}")
                    st.markdown(f"*Response:* {test.response[:400]}...")
                    st.markdown(f"*Observed Traits:* {', '.join(test.observed_traits[:5])}")
                    st.markdown("---")

with tab3:
    st.markdown("### Download Validation Results")
    
    if st.session_state.validation_report is None:
        st.info("No validation results to download. Run validation first.")
    else:
        report = st.session_state.validation_report
        suite = GerlachValidationSuite(st.session_state.manager)
        
        st.markdown("#### Available Formats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_data = json.dumps(report.to_dict(), indent=2)
            st.download_button(
                "📄 Download JSON",
                data=json_data,
                file_name=f"gerlach_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Markdown download
            md_data = suite.generate_markdown_report(report)
            st.download_button(
                "📝 Download Markdown Report",
                data=md_data,
                file_name=f"gerlach_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # CSV of test results
        st.markdown("#### Test Results (CSV)")
        
        csv_data = []
        for test in report.test_results:
            csv_data.append({
                "Test ID": test.test_id,
                "Personality": test.personality_type,
                "Prompt": test.prompt,
                "Response": test.response[:200],
                "Score": test.trait_match_score,
                "Observed Traits": ", ".join(test.observed_traits[:5])
            })
        
        df_csv = pd.DataFrame(csv_data)
        csv_string = df_csv.to_csv(index=False)
        
        st.download_button(
            "📊 Download Test Results (CSV)",
            data=csv_string,
            file_name=f"gerlach_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### Preview")
        st.dataframe(df_csv, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("Gerlach et al. (2018) Personality Validation Suite | Powered by Claude Sonnet 4.5")
