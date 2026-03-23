"""
Locale / i18n strings for the Gerlach Research Platform.

Usage:
    from strings import T, APP_LANG

Set the APP_LANG environment variable to "ko" for Korean, or leave unset for English.
"""

import os

def _get_app_lang() -> str:
    lang = os.environ.get("APP_LANG")
    if lang:
        return lang
    try:
        import streamlit as st
        return st.secrets.get("APP_LANG", "en")
    except Exception:
        return "en"

APP_LANG = _get_app_lang()

# =============================================================================
# ENGLISH STRINGS
# =============================================================================

EN = {

    # ── Stage labels ─────────────────────────────────────────────────────────
    "stage_labels": {
        "registration":    "Step 1 of 3 — Questionnaires",
        "big5_assessment": "Step 1 of 3 — Questionnaires",
        "task_selection":  "Step 2 of 3 — Collaboration Task",
        "task_dialogue":   "Step 2 of 3 — Collaboration Task",
        "task_response":   "Step 2 of 3 — Collaboration Task",
        "post_survey":     "Step 3 of 3 — Follow-up Questionnaire",
        "completed":       "Completed",
    },

    # ── Registration ─────────────────────────────────────────────────────────
    "reg_header": "Welcome to Our Study",
    "reg_intro": (
        "Thank you for participating. In this study, you will be asked to:\n\n"
        "1. Answer a few questionnaires\n"
        "2. Collaborate on a task with a Large Language Model (LLM)\n"
        "3. Complete a brief follow-up questionnaire"
    ),
    "tab_new":               "New Participant",
    "tab_resume":            "Resume Session",
    "reg_id_instruction":    "**Enter the participant ID provided to you by the researcher.**",
    "reg_id_label":          "Participant ID:",
    "reg_id_placeholder":    "e.g., P001",
    "reg_id_help":           "This ID will be used to track and save your progress.",
    "reg_consent":           "I consent to participate in this research study",
    "reg_consent_help":      "Your data will be anonymised and used for research purposes only.",
    "reg_begin_btn":         "Begin Study",
    "reg_err_no_id":         "Please enter your participant ID.",
    "reg_err_no_consent":    "Please tick the consent box to continue.",
    "resume_instructions": (
        "If you started the study earlier and need to continue, "
        "enter your **Participant ID** below."
    ),
    "resume_btn":        "Resume My Session",
    "resume_success":    "Welcome back! Resuming from: **{stage_label}**",
    "resume_not_found": (
        "No active session found for that ID. "
        "If you have already completed the study, thank you for your participation. "
        "If you believe this is an error, please contact the researcher."
    ),

    # ── Big5 Assessment ───────────────────────────────────────────────────────
    "big5_header": "📋 About You",
    "big5_info": "This is to know more about you as a person.",
    "big5_instructions": (
        "For each statement, please indicate how much you agree or disagree based on how you generally are — "
        "there are no right or wrong answers.\n\n"
        "Please rate each statement on a scale of 1–5:\n\n"
        "- 1 = Strongly Disagree\n"
        "- 2 = Disagree\n"
        "- 3 = Neutral\n"
        "- 4 = Agree\n"
        "- 5 = Strongly Agree\n\n"
        "There are 50 statements in total. Please select one option for each statement before submitting."
    ),
    "big5_submit_btn":       "Submit Assessment",
    "big5_toast_unanswered": "Almost there! Please answer question(s): {nums_str}",
    "big5_warning_unanswered": (
        "**Almost there!** The following item(s) still need a response: "
        "**{nums_str}**. Please scroll up and rate each one before submitting."
    ),
    "big5_success": "✅ Assessment completed!",

    # ── Task Selection ────────────────────────────────────────────────────────
    "task_sel_header":      "📄 Your Assigned Task",
    "task_sel_subtitle":    "Please read the task description carefully before beginning.",
    "task_sel_no_content":  "Task document loaded. Please refer to any printed materials provided.",
    "task_sel_begin_info": (
        "When you have finished reading and are ready to begin, click the button below. "
        "An AI assistant will be available to help you work through the task."
    ),
    "task_sel_begin_btn":   "I have read the task — Begin",
    "task_sel_err_no_llm":        "LLM Manager not ready. Please set ANTHROPIC_API_KEY.",
    "task_sel_err_folder":        "Task folder not found. Please contact the researcher.",
    "task_sel_err_files_missing": "Required task files are missing. Please contact the researcher.",
    "task_sel_err_assign":        "Could not assign a task. Please contact the researcher.",
    "task_dial_err_not_found":    "Dialogue not found. Please contact the researcher.",
    "task_dial_err_llm":          "The AI assistant could not be reached. Please refresh the page to try again.",

    # ── Task Dialogue ─────────────────────────────────────────────────────────
    "task_dial_header":         "💬 Task Collaboration",
    "task_dial_expander":       "📄 Task Description (click to expand / collapse)",
    "task_dial_no_desc":        "Task description not available.",
    "task_dial_warning":        "⚠️ **ONLY click the button below when you and your LLM Partner have fully completed the task!**",
    "task_dial_messages_metric":"Messages exchanged",
    "task_dial_complete_btn":   "Complete Task",
    "task_dial_chat_placeholder":"Type your message to the LLM Partner…",
    "task_dial_spinner_welcome":"LLM Partner is preparing…",
    "task_dial_spinner_thinking":"LLM Partner is thinking…",
    "task_dial_welcome_prompt": (
        "Output the following text word for word, without changing anything:\n\n"
        "Did you get a chance to read the task carefully? How do you think we should go about solving this problem? "
        "Let's collaborate and share our thoughts with each other. But first, please take a moment to read the guidelines below carefully."
    ),
    "task_dial_guide_expander": "ℹ️ How to Collaborate (click to expand / collapse)",
    "task_dial_guide": """\
**How to Collaborate:**

✅ **DO:**
- Engage naturally, like talking to a colleague
- Share your genuine thoughts and opinions
- Ask questions if you're unsure
- Disagree with the AI if you think differently
- Take time to think through your responses
- Build on each other's ideas
- Express uncertainty when appropriate

❌ **DON'T:**
- Rush through the conversation
- Simply agree with everything the AI says
- Treat it like a test with "right answers"
- Worry about grammar or perfect phrasing
- Pretend to understand if confused

---

**Example Dialogue Flow:**

⭐ **AI:** Hello! I'm excited to help you with this task. Shall we start by reviewing the requirements?

👤 **You:** Yes, that sounds good. I think the main goal is to evaluate the candidates based on their experience and cultural fit.

⭐ **AI:** Great observation! Let's create a systematic approach. I suggest we evaluate each candidate on three criteria: leadership, technical skills, and cultural fit. Does that work for you?

👤 **You:** That makes sense, but I think we should also consider their potential for growth, not just current skills.

⭐ **AI:** Excellent point! You're right — growth potential is important. Let's add that as a fourth criterion...

*[Conversation continues...]*

---

**Tips:**
- Quality over quantity — thoughtful responses matter more than speed
- It's okay to change your mind during the conversation
- The AI is there to work with you, not to test you
- Take breaks if needed (but don't close the browser)
""",

    # ── Post-Task Survey ──────────────────────────────────────────────────────
    "survey_header":      "End of Study Survey",
    "survey_instructions": (
        "Please read each statement carefully and select the response that best reflects your experience. "
        "Use the scale: **1 = Strongly Disagree** &nbsp; **7 = Strongly Agree**"
    ),
    "survey_submit_btn":         "Submit Survey",
    "survey_toast_unanswered":   "Almost there! Please answer question(s): {nums_str}",
    "survey_warning_unanswered": (
        "**Almost there!** The following item(s) still need a response: "
        "**{nums_str}**. Please scroll up and rate each one before submitting."
    ),

    # ── Completed ─────────────────────────────────────────────────────────────
    "completed_header":         "✅ Session Completed!",
    "completed_success":        "Thank you for participating in this research study!",
    "completed_close_browser":  "You may now close the browser.",
    "completed_gen_btn":        "Generate Comprehensive Report",
    "completed_gen_spinner":    "Generating your research report...",
    "completed_report_id":      "Report generated! Report ID: {report_id}",
    "completed_report_header":  "## Your Research Report",
    "completed_tab_summary":    "📊 Summary",
    "completed_tab_full":       "📄 Full Report",
    "completed_tab_downloads":  "💾 Downloads",
    "completed_big5_header":    "### Your Big Five Profile",
    "completed_personality_type":"**Personality Type:** {gtype}",
    "completed_dl_header":      "### Download Your Report",
    "completed_dl_md_btn":      "📄 Download Markdown Report",
    "completed_dl_html_btn":    "🌐 Download HTML Report",
    "completed_new_session_btn":"Start New Session",

    # ── Sidebar ───────────────────────────────────────────────────────────────
    "sidebar_header":              "## Research Platform",
    "sidebar_participant_id_label":"**Participant ID:**",
    "sidebar_progress_label":      "**Progress:** {stage_label}",
    "sidebar_need_to_stop": (
        "**Need to stop?** Click the **Save & Exit** button below. "
        "Your progress will be saved automatically."
    ),
    "sidebar_returning": (
        "**Returning to the study?** Click the **Resume Session** tab "
        "on the home page and enter your ID **`{user_id}`** to continue where you left off."
    ),
    "sidebar_reload_btn":   "🔄 Reload Page",
    "sidebar_save_exit_btn":"💾 Save & Exit",
    "sidebar_saved_msg": (
        "**Your progress has been saved.**\n\n"
        "Your Participant ID is: **{user_id}**\n\n"
        "Write this down or take a screenshot. When you are ready to continue, "
        "return to this website and use the **Resume Session** tab to pick up where you left off."
    ),
    "sidebar_close_btn":    "Close",
    "sidebar_no_session":   "No active session",
    "sidebar_admin_btn":    "Admin",
    "sidebar_back_btn":     "← Back to Study",

    # ── LLM language instruction (empty for English) ──────────────────────────
    "llm_language_instruction": "",

    # ── Task content (Popcorn Brain) ──────────────────────────────────────────
    "task_popcorn_md": """\
Thank you for your participation. Please read the task description below carefully. You may want to read it \
twice to be clear. After that, start engaging a conversation with the LLM in discussing and collaborating for \
a most optimal solution. After you both have come to an agreement, click the 'complete' button on the bottom \
of the screen to finish the session. Your conversation will be saved for the researchers.

Please put in your best effort to generate a genuinely good and effective solution.

---

### Task Description

Los Angeles unified school district superintendent, Mr. Johnson is mulling over a new district-wide policy that will address the student-friendly and effective learning environment by utilizing digital technology, specifically AI-based applications and tools. The state governor's office is pushing for "smart classroom" initiative where the governor believes that it will strengthen the student scholastic achievement.

One of the initiative plans is to implement smart technologies such as AI-applications and devices in K-12 classroom. This includes replacing paperback textbook with digital device, interactive AI-based workbooks. The benefits of using AI in place of traditional materials are: 1) student can access dynamic 3D hyper-text, -image, -model, and moving images for better viewing and understanding, 2) student can interact with instructor and other students simultaneously for in-class group collaboration or for homework assignments, 3) it allows student to cover more materials and access more in-depth than the traditional approach.

On the other side, Parent-Teacher Organization (PTO) is raising a substantial concern about down side — *growing memory loss by depending too much on digital technologies' data storage service*. This syndrome speaks about how a human brain gradually lose its memory function and capacity as we continue to rely on digital devices in storing and retrieving much of our information. One of the recommendations is to use less of AI-based digital devices and technologies to balance the habitual dependency. The PTO is asking a more appropriate, implementable, and effective use of AI tools in the light of this concern.

Under these circumstances, you and your LLM are asked to work on a master plan to address this dilemma and find ways to enhance the student learning without sacrificing student's memory. Some questions to think about: What are some of creative ideas? Are the ideas realistic? With an idea, what are the action items? How do you satisfy the student's wish to use more AI but addressing the parents' concern? What is the teacher's role here? Should Math, Science, and English courses be different in the use of the AI devices? How? What about the school policies?
""",

    # ── Task content (Noble Industries) ──────────────────────────────────────
    "task_noble_md": """\
Thank you for your participation. Please read the task description below carefully. You may want to read it \
twice to be clear. After that, start engaging a conversation with the LLM in discussing and collaborating for \
a most optimal solution. After you both have come to an agreement, click the 'complete' button on the bottom \
of the screen to finish the session. Your conversation will be saved for the researchers. Please put in your \
best effort to generate a genuinely good and effective solution.

---

### Task Description

Noble Industries is a mid-sized, diversified manufacturing firm with corporate headquarters located in Columbus, Ohio. The company was founded in 1958 and has experienced steady and continuous growth for most of its forty-year history. Eight manufacturing facilities are located in different parts of the United States and each plant employs approximately 250 people. Gross revenues for Noble Industries in 1997 were $105 million.

The Information Systems Division (ISD) at Noble Industries is functionally distributed throughout the organization. Each plant is responsible for developing and supporting its own local IS operations (for example, ordering, production scheduling, quality assurance, decision support, etc.). All corporate-wide systems (human resources, sales forecasting, research, executive information, etc.) are managed from the central Information Systems Division at corporate headquarters. A total of 150 people are employed in the Information Systems Division (ISD).

After graduating from college in 1988 you were hired as a junior programmer at the Columbus, Ohio site. Five years later you were promoted to the position of systems analyst. Now you are a senior systems analyst in ISD. Your group is responsible for application development and software support for the Research and Development Division (RDD). There are two systems analysts, four applications programmers, and 2 clerical support staff who report directly to you.

This morning, you and the other senior systems analysts at corporate headquarters met with Bob Thompson, Vice President for Information Systems. He explained, "At yesterday's Executive Management meeting it was announced that some of our durable goods customers have found new suppliers. Based on the loss in sales, our V.P. for Finance has projected a 3-6% decline in gross revenue this year. The CEO said that unless sales increase very soon we will have to make staff reductions. All Division Vice Presidents have been asked to develop a preliminary list of people who would be laid off. For ISD, at least one and perhaps as many as ten staff members could be terminated. The final decision will be made next week."

Bob then distributed envelopes marked "Confidential". He said, "In each envelope you will find profile information on ten information systems employees. I want you to take the envelopes back to your office, read the profile and company management's comments, then rank the employees in the order that you think they should be laid off. Also write down the reasons for your ranking. The employees' real names don't appear on the profile page because I don't want you to have to make a decision about someone you know. As these are all good employees who have been performing well, management felt it wanted a rating by an impartial group of technical peers as input to their final decision. Use your best judgement. Then I want you to get together as a group later on today, discuss your individual rankings, and submit a final ranking and the reasons for the ranking to me by the end of the day."

Bob concluded the meeting by saying, "I understand this is not an easy task, but given the current situation we don't have any other choice." At that point, you and the other senior systems analysts went back to your offices to work on the ranking assignment.

---

### Employee Profile

| Name | Age | Title | Years with Co. | Education (highest degree) | School or College | Marital Status | Number of Dependents |
|------|:---:|-------|:--------------:|:--------------------------:|-------------------|:--------------:|:--------------------:|
| Barbara | 27 | Senior Systems Analyst | 2 | MBA | Stanford Univ. | Single | 0 |
| Chris | 35 | Systems Analyst | 10 | BS - MIS | U. of Oklahoma | Married | 4 |
| Fred | 61 | Systems Programmer | 27 | DP School | DeVry Tech. | Married | 1 |
| Harry | 27 | Applications Programmer | 4 | BS - CIS | Univ. of Bombay | Single | 3 |
| Joanne | 46 | Senior Systems Analyst | 15 | MS - MIS | Ohio State Univ. | Married | 2 |
| Lois | 54 | Database Administrator | 22 | AAS - DP | Miami Dade CC | Widowed | 0 |
| Phil | 26 | Systems Analyst | 3 | BS - CIS | Natl. Taiwan Univ. | Single | 1 |
| Sharon | 36 | Clerical | 12 | High Sch. | Harrison H.S. | Married | 6 |
| Susan | 51 | Applications Programmer | 9 | BS - CIS | Texas A&M Univ. | Divorced | 3 |
| Tom | 47 | Senior Systems Analyst | 18 | BS - Mgmt. | Purdue Univ. | Divorced | 4 |

---

### Company Management's Comments

**Barbara:** "Barbara is very ambitious and always asks for the most challenging assignments. She believes that hard work should be recognized and rewarded. For example, at both annual performance evaluations Barbara has wanted to know when she will be considered for a promotion. She defines success in terms of position and salary. Barbara is very competitive and I suspect that she will move up in the management ranks. My only concern is that sometimes she can be too assertive."

**Chris:** "Of all the people in my department, Chris responds the quickest when I give him an assignment and he never asks why I want something done. Chris respects authority and understands that everyone needs to know their place in the organizational hierarchy. He doesn't mind bureaucracy because he knows it improves efficiency. Maybe that's why Chris enjoyed being in the army for eight years."

**Fred:** "Fred has been with us for a long time. He enjoys his work and is grateful for the job security he's had here all these years. Fred gets along with everyone and gets a lot of satisfaction out of helping others, especially some of the newer employees when they have questions. He recognizes that it's important for people who work together to agree on things. Fred doesn't like controversy, so he is willing to compromise when others disagree with him."

**Harry:** "Harry is the most technically competent guy in my department. He reads every technical report he can get his hands on. However, Harry likes doing things his own way and prefers to work alone. In this way, Harry believes that it will be easier for me, his supervisor, to reward him for the work he does without anyone else getting any credit. His priorities are very clear, he puts himself and his family above everything else in his life."

**Joanne:** "Joanne has excellent organizational skills. She understands that we need to have rules and the rules need to be followed. Joanne is the department's quality assurance leader (QAL) because she believes that order and structure are necessary for productivity. She doesn't take any unnecessary risks, and thoroughly researches something before making a recommendation to me."

**Lois:** "Lois is a real team player. She really enjoys working with others and always puts the group's interests ahead of her own. In fact, when the new database conversion was completed she suggested that the whole group be recognized for the achievement even though Lois did most of the work. I know that community service is also important to Lois. She is a volunteer at the local shelter for the homeless."

**Phil:** "Although he's only twenty-six years old, Phil tends to live his life as if he were much older. He likes to study history and the way people lived in the past. Last year when Phil's mother became ill he moved back home to take care of her. Phil has a great respect for other people and will defend them when they are being criticized, whether the criticism is justified or not."

**Sharon:** "Sharon is very dedicated. She comes to work early, usually stays late, and always completes every assignment no matter how long it takes. Sharon places a great deal of emphasis on her relationships with others. Her long-term goal is to retire in Florida, so she tries to save as much money as she can."

**Susan:** "I have known Susan for about seven years, ever since she started working here. She gets her work done and thinks that everyone should do their fair share. In fact, Susan once told an assistant plant supervisor who was visiting our plant that he should try doing her job for a day. I give Susan a lot of credit, she speaks her mind and doesn't care if you're the CEO or the mail room clerk. To her, no one is any better than anybody else."

**Tom:** "Tom is always the first to try something new. It doesn't make any difference whether it's a radio station, a place to vacation, or a style of clothes. Tom does things his own way and he's not afraid to break the rules. With me, Tom is the same way. So I generally give him the assignments that have a big risk, but potentially a big payoff."
""",

    # ── Big5 assessment items (IPIP-50) ───────────────────────────────────────
    "big5_items": {
        "extraversion": [
            {"id": "E1",  "text": "I am the life of the party.",                       "reverse": False},
            {"id": "E2",  "text": "I don't talk a lot.",                               "reverse": True},
            {"id": "E3",  "text": "I feel comfortable around people.",                 "reverse": False},
            {"id": "E4",  "text": "I keep in the background.",                         "reverse": True},
            {"id": "E5",  "text": "I start conversations.",                            "reverse": False},
            {"id": "E6",  "text": "I have little to say.",                             "reverse": True},
            {"id": "E7",  "text": "I talk to a lot of different people at parties.",   "reverse": False},
            {"id": "E8",  "text": "I don't like to draw attention to myself.",         "reverse": True},
            {"id": "E9",  "text": "I don't mind being the center of attention.",       "reverse": False},
            {"id": "E10", "text": "I am quiet around strangers.",                      "reverse": True},
        ],
        "agreeableness": [
            {"id": "A1",  "text": "I feel little concern for others.",                 "reverse": True},
            {"id": "A2",  "text": "I am interested in people.",                        "reverse": False},
            {"id": "A3",  "text": "I insult people.",                                  "reverse": True},
            {"id": "A4",  "text": "I sympathize with others' feelings.",               "reverse": False},
            {"id": "A5",  "text": "I am not interested in other people's problems.",   "reverse": True},
            {"id": "A6",  "text": "I have a soft heart.",                              "reverse": False},
            {"id": "A7",  "text": "I am not really interested in others.",             "reverse": True},
            {"id": "A8",  "text": "I take time out for others.",                       "reverse": False},
            {"id": "A9",  "text": "I feel others' emotions.",                          "reverse": False},
            {"id": "A10", "text": "I make people feel at ease.",                       "reverse": False},
        ],
        "conscientiousness": [
            {"id": "C1",  "text": "I am always prepared.",                             "reverse": False},
            {"id": "C2",  "text": "I leave my belongings around.",                     "reverse": True},
            {"id": "C3",  "text": "I pay attention to details.",                       "reverse": False},
            {"id": "C4",  "text": "I make a mess of things.",                          "reverse": True},
            {"id": "C5",  "text": "I get chores done right away.",                     "reverse": False},
            {"id": "C6",  "text": "I often forget to put things back in their proper place.", "reverse": True},
            {"id": "C7",  "text": "I like order.",                                     "reverse": False},
            {"id": "C8",  "text": "I shirk my duties.",                                "reverse": True},
            {"id": "C9",  "text": "I follow a schedule.",                              "reverse": False},
            {"id": "C10", "text": "I am exacting in my work.",                         "reverse": False},
        ],
        "neuroticism": [
            {"id": "N1",  "text": "I get stressed out easily.",                        "reverse": False},
            {"id": "N2",  "text": "I am relaxed most of the time.",                   "reverse": True},
            {"id": "N3",  "text": "I worry about things.",                             "reverse": False},
            {"id": "N4",  "text": "I seldom feel blue.",                               "reverse": True},
            {"id": "N5",  "text": "I am easily disturbed.",                            "reverse": False},
            {"id": "N6",  "text": "I get upset easily.",                               "reverse": False},
            {"id": "N7",  "text": "I change my mood a lot.",                           "reverse": False},
            {"id": "N8",  "text": "I have frequent mood swings.",                      "reverse": False},
            {"id": "N9",  "text": "I get irritated easily.",                           "reverse": False},
            {"id": "N10", "text": "I often feel blue.",                                "reverse": False},
        ],
        "openness": [
            {"id": "O1",  "text": "I have a rich vocabulary.",                         "reverse": False},
            {"id": "O2",  "text": "I have difficulty understanding abstract ideas.",   "reverse": True},
            {"id": "O3",  "text": "I have a vivid imagination.",                       "reverse": False},
            {"id": "O4",  "text": "I am not interested in abstract ideas.",            "reverse": True},
            {"id": "O5",  "text": "I have excellent ideas.",                           "reverse": False},
            {"id": "O6",  "text": "I do not have a good imagination.",                 "reverse": True},
            {"id": "O7",  "text": "I am quick to understand things.",                  "reverse": False},
            {"id": "O8",  "text": "I use difficult words.",                            "reverse": False},
            {"id": "O9",  "text": "I spend time reflecting on things.",                "reverse": False},
            {"id": "O10", "text": "I am full of ideas.",                               "reverse": False},
        ],
    },

    # ── Survey questions ──────────────────────────────────────────────────────
    "survey_questions": {
        "q1": {
            "question": "I am confident that our work (output) is done correctly.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q3": {
            "question": "I believe that our output has effectively solved the given task.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q4": {
            "question": "I enjoyed the LLM-Human collaboration more than doing it alone.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q5": {
            "question": "In the LLM-Human collaboration, the LLM and I disagreed frequently in reaching a solution.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q6": {
            "question": "In the LLM-Human collaboration, I believe that I had an easier time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q7": {
            "question": "In the LLM-Human collaboration, I believe that we had a much longer time reaching the solutions.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q8": {
            "question": "In the LLM-Human collaboration, I did not like the LLM's suggestion or view, but I compromised to do (or follow) the LLM's way.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q9": {
            "question": "In the LLM-Human collaboration, the feeling of trusting the LLM grew stronger as the session went on.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q10": {
            "question": "The LLM showed things that I did not know about.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q11": {
            "question": "The LLM showed compassion towards me.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q12": {
            "question": "The LLM showed no emotion and only dealt with facts.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q13": {
            "question": "In the LLM-Human collaboration, I really enjoyed my LLM partner's partnership (willing to work as a team, open-minded, etc.).",
            "type": "likert",
            "scale": (1, 7),
        },
        "q14": {
            "question": "In the LLM-Human collaboration, my partner insisted on doing things his way and/or did not collaborate.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q15": {
            "question": "In the LLM-Human collaboration, I was NOT able to fully exercise my knowledge and skills.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q16": {
            "question": "In the LLM-Human collaboration, I believe that I am a compatible partner to the LLM.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q17": {
            "question": "In the LLM-Human collaboration, it was my politeness and etiquette that got me through the collaboration sessions, NOT my true self (personality).",
            "type": "likert",
            "scale": (1, 7),
        },
        "q18": {
            "question": "In the LLM-Human collaboration, I believe that I have a compatible personality with the LLM.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q19": {
            "question": "In the LLM-Human collaboration, I did NOT reveal my true self or personality during the whole session.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q20": {
            "question": "In the LLM-Human collaboration, the LLM was thoughtful and forgiving with my mistakes.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q21": {
            "question": "In the LLM-Human collaboration, there were times when I was withdrawn (or maybe upset) because of disagreements with the partner.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q22": {
            "question": "I think the LLM-Human collaboration is a form of cheating as it takes away from one's ability to truly learn on his or her own.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q23": {
            "question": "I don't think I can achieve higher productivity next time if I am paired with the LLM again.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q24": {
            "question": "In the LLM-Human collaboration, the LLM described his or her point very well and I was able to fully understand.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q25": {
            "question": "In the LLM-Human collaboration, the LLM did not express nor communicate much (too quiet), which made the collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q26": {
            "question": "In the LLM-Human collaboration, the LLM's message delivery was unclear, which made the collaboration very difficult.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q32": {
            "question": "Briefly describe any conflicts or negative impacts from the LLM that you experienced during the collaboration, which you think influenced or affected the collaboration session and its productivity.",
            "type": "text",
            "placeholder": "",
        },
        "q33": {
            "question": "Describe any positive impacts from the LLM that you experienced during the collaboration, which you think influenced or contributed to the collaboration productivity.",
            "type": "text",
            "placeholder": "",
        },
        "q34": {
            "question": "Discuss the compatibility (personality, communication, or other aspects) between you and the LLM. If it was good, why? If not, why not? Do you think you can achieve high productivity with the LLM again?",
            "type": "text",
            "placeholder": "",
        },
        "q35": {
            "question": "Besides the LLM's ability to contribute to the task, how did the LLM's personality play a role in your collaboration with the LLM? Was the personality compatible or not? Describe.",
            "type": "text",
            "placeholder": "",
        },
        "q36": {
            "question": "Besides the LLM's ability to contribute to the task, how did the LLM's communication skills play a role in your collaboration? Did the level of communication skill that the LLM exhibited bring a positive (or negative) feeling and impact to your collaboration with the LLM? Describe.",
            "type": "text",
            "placeholder": "",
        },
        "q38": {
            "question": "What is your gender?",
            "type": "text",
            "placeholder": "",
        },
        "q39": {
            "question": "What is your major?",
            "type": "text",
            "placeholder": "",
        },
    },
}


# =============================================================================
# KOREAN STRINGS
# =============================================================================

KO = {

    # ── Stage labels ─────────────────────────────────────────────────────────
    "stage_labels": {
        "registration":    "1단계 / 3 — 설문지",
        "big5_assessment": "1단계 / 3 — 설문지",
        "task_selection":  "2단계 / 3 — 협업 과제",
        "task_dialogue":   "2단계 / 3 — 협업 과제",
        "task_response":   "2단계 / 3 — 협업 과제",
        "post_survey":     "3단계 / 3 — 사후 설문지",
        "completed":       "완료",
    },

    # ── Registration ─────────────────────────────────────────────────────────
    "reg_header": "연구에 오신 것을 환영합니다",
    "reg_intro": (
        "참여해 주셔서 감사합니다. 이 연구에서 참여하시는분은 다음을 수행하게 됩니다:\n\n"
        "1. 몇 가지 설문지에 응답\n"
        "2. 대형 언어 모델(LLM)과 협력하여 과제 수행\n"
        "3. 연구 마침 설문지 작성"
    ),
    "tab_new":               "새 참여자",
    "tab_resume":            "세션 재개",
    "reg_id_instruction":    "**연구자가 제공한 참여자 ID를 입력하십시오.**",
    "reg_id_label":          "참여자 ID:",
    "reg_id_placeholder":    "예: P001",
    "reg_id_help":           "이 ID는 참여하시는분의 진행 상황을 추적하고 저장하는 데 사용됩니다.",
    "reg_consent":           "본 연구에 참여하는 것에 동의합니다",
    "reg_consent_help":      "참여하시는분의 데이터는 익명으로 처리되며 연구 목적으로만 사용됩니다.",
    "reg_begin_btn":         "실험 시작",
    "reg_err_no_id":         "참여자 ID를 입력하십시오.",
    "reg_err_no_consent":    "계속하려면 동의 체크박스를 선택하십시오.",
    "resume_instructions": (
        "이전에 연구를 시작했으며 계속해야 하는 경우, "
        "아래에 **참여자 ID**를 입력하십시오."
    ),
    "resume_btn":        "세션 재개",
    "resume_success":    "다시 오신 것을 환영합니다! 재개 위치: **{stage_label}**",
    "resume_not_found": (
        "해당 ID에 대한 활성 세션을 찾을 수 없습니다. "
        "이미 연구를 완료하셨다면 참여해 주셔서 감사합니다. "
        "오류라고 생각되시면 연구자에게 문의하십시오."
    ),

    # ── Big5 Assessment ───────────────────────────────────────────────────────
    "big5_header": "📋 참여하시는분에 관한 설문",
    "big5_info": "",
    "big5_instructions": (
        "각 진술에 대해 참여하시는분이 일반적으로 어떤지를 바탕으로 얼마나 동의하거나 동의하지 않는지를 표시하십시오 — "
        "옳거나 틀린 답은 없습니다.\n\n"
        "1–5점 척도로 각 진술을 평가하십시오:\n\n"
        "- 1 = 매우 동의하지 않음\n"
        "- 2 = 동의하지 않음\n"
        "- 3 = 보통\n"
        "- 4 = 동의함\n"
        "- 5 = 매우 동의함\n\n"
        "총 50개의 진술이 있습니다. 제출하기 전에 각 진술에 대해 하나의 옵션을 선택하십시오."
    ),
    "big5_submit_btn":       "다음 순서로 안내해주세요",
    "big5_toast_unanswered": "거의 다 됐습니다! 다음 문항에 응답하십시오: {nums_str}",
    "big5_warning_unanswered": (
        "**거의 다 됐습니다!** 다음 문항에 아직 응답이 필요합니다: "
        "**{nums_str}**. 위로 스크롤하여 제출 전에 각 문항을 평가하십시오."
    ),
    "big5_success": "✅ 평가가 완료되었습니다!",

    # ── Task Selection ────────────────────────────────────────────────────────
    "task_sel_header":     "📄 배정된 과제",
    "task_sel_subtitle":   "시작하기 전에 과제 설명을 주의 깊게 읽어 주십시오.",
    "task_sel_no_content": "과제 문서가 로드되었습니다. 제공된 인쇄 자료를 참조하십시오.",
    "task_sel_begin_info": (
        "읽기를 완료하고 시작할 준비가 되면 아래 버튼을 클릭하십시오. "
        "과제를 수행하는 데 도움이 되는 AI 어시스턴트가 제공됩니다."
    ),
    "task_sel_begin_btn":  "과제를 읽었습니다 — 시작",
    "task_sel_err_no_llm":        "LLM 관리자가 준비되지 않았습니다. ANTHROPIC_API_KEY를 설정하십시오.",
    "task_sel_err_folder":        "과제 폴더를 찾을 수 없습니다. 연구자에게 문의하십시오.",
    "task_sel_err_files_missing": "필수 과제 파일이 없습니다. 연구자에게 문의하십시오.",
    "task_sel_err_assign":        "과제를 배정할 수 없습니다. 연구자에게 문의하십시오.",
    "task_dial_err_not_found":    "대화를 찾을 수 없습니다. 연구자에게 문의하십시오.",
    "task_dial_err_llm":          "AI 어시스턴트에 연결할 수 없습니다. 페이지를 새로고침하여 다시 시도해 주세요.",

    # ── Task Dialogue ─────────────────────────────────────────────────────────
    "task_dial_header":          "💬 과제 협업",
    "task_dial_expander":        "📄 과제 설명 (클릭하여 펼치기 / 접기)",
    "task_dial_no_desc":         "과제 설명을 사용할 수 없습니다.",
    "task_dial_warning":         "⚠️ **참여하시는분과 LLM 파트너가 과제를 완전히 완료했을 때만 아래 버튼을 클릭하십시오!**",
    "task_dial_messages_metric": "교환된 메시지 수",
    "task_dial_complete_btn":    "과제 완료",
    "task_dial_chat_placeholder":"LLM 파트너에게 메시지를 입력하세요…",
    "task_dial_spinner_welcome": "LLM 파트너가 준비 중입니다…",
    "task_dial_spinner_thinking":"LLM 파트너가 생각 중입니다…",
    "task_dial_welcome_prompt": (
        "아래 텍스트를 한 글자도 바꾸지 말고 정확히 그대로 출력하세요:\n\n"
        "과제를 잘 읽어보셨나요? 그럼 당신은 이 문제를 어떻게 풀어나가면 좋을까요? "
        "저와 같이 협력해서 서로의 의견을 나누죠. 하지만 먼저, 아래의 가이드라인을 차분히 읽어보세요"
    ),
    "task_dial_guide_expander": "ℹ️ 협업 방법 (클릭하여 펼치기 / 접기)",
    "task_dial_guide": """\
**협업 방법:**

✅ **해야 할 것:**
- 동료와 이야기하듯 자연스럽게 대화하세요
- 진솔한 생각과 의견을 나누세요
- 확실하지 않으면 질문하세요
- AI와 다르게 생각한다면 동의하지 않아도 됩니다
- 응답을 충분히 생각할 시간을 가지세요
- 서로의 아이디어를 발전시키세요
- 불확실할 때는 솔직하게 표현하세요

❌ **하지 말아야 할 것:**
- 대화를 서둘러 마치지 마세요
- AI가 말하는 모든 것에 그냥 동의하지 마세요
- "정답"이 있는 시험처럼 생각하지 마세요
- 문법이나 완벽한 표현을 걱정하지 마세요
- 이해하지 못했는데 이해한 척하지 마세요

---

**대화 예시:**

⭐ **AI:** 안녕하세요! 이 과제를 함께 해결해 나가게 되어 기쁩니다. 요구사항을 검토하는 것부터 시작할까요?

👤 **나:** 네, 좋습니다. 주요 목표는 경험과 문화적 적합성을 바탕으로 후보자를 평가하는 것이라고 생각합니다.

⭐ **AI:** 좋은 관찰입니다! 체계적인 접근 방식을 만들어 봅시다. 리더십, 기술적 역량, 문화적 적합성의 세 가지 기준으로 각 후보자를 평가할 것을 제안합니다. 어떻게 생각하세요?

👤 **나:** 맞는 것 같은데, 현재 역량뿐만 아니라 성장 가능성도 고려해야 할 것 같습니다.

⭐ **AI:** 훌륭한 지적입니다! 맞아요 — 성장 가능성도 중요하죠. 네 번째 기준으로 추가해 봅시다...

*[대화 계속...]*

---

**도움말:**
- 양보다 질 — 빠르게 답하는 것보다 깊이 있는 응답이 더 중요합니다
- 대화 중에 의견을 바꿔도 괜찮습니다
- AI는 참여하시는분을 테스트하는 것이 아니라 함께 일하기 위해 있습니다
- 필요하면 잠시 멈춰도 됩니다 (단, 브라우저는 닫지 마세요)
""",

    # ── Post-Task Survey ──────────────────────────────────────────────────────
    "survey_header":      "연구 마침 설문지",
    "survey_instructions": (
        "각 진술을 주의 깊게 읽고 참여하시는분의 경험을 가장 잘 반영하는 응답을 선택하십시오. "
        "척도 사용: **1 = 매우 동의하지 않음** &nbsp; **7 = 매우 동의함**"
    ),
    "survey_submit_btn":         "설문지 제출",
    "survey_toast_unanswered":   "거의 다 됐습니다! 다음 문항에 응답하십시오: {nums_str}",
    "survey_warning_unanswered": (
        "**거의 다 됐습니다!** 다음 문항에 아직 응답이 필요합니다: "
        "**{nums_str}**. 위로 스크롤하여 제출 전에 각 문항을 평가하십시오."
    ),

    # ── Completed ─────────────────────────────────────────────────────────────
    "completed_header":          "✅ 세션 완료!",
    "completed_success":         "이 연구에 참여해 주셔서 감사합니다!",
    "completed_close_browser":   "이제 브라우저를 닫아도 됩니다.",
    "completed_gen_btn":         "종합 보고서 생성",
    "completed_gen_spinner":     "연구 보고서를 생성하는 중...",
    "completed_report_id":       "보고서가 생성되었습니다! 보고서 ID: {report_id}",
    "completed_report_header":   "## 참여하시는분의 연구 보고서",
    "completed_tab_summary":     "📊 요약",
    "completed_tab_full":        "📄 전체 보고서",
    "completed_tab_downloads":   "💾 다운로드",
    "completed_big5_header":     "### 참여하시는분의 빅파이브 프로필",
    "completed_personality_type":"**성격 유형:** {gtype}",
    "completed_dl_header":       "### 보고서 다운로드",
    "completed_dl_md_btn":       "📄 마크다운 보고서 다운로드",
    "completed_dl_html_btn":     "🌐 HTML 보고서 다운로드",
    "completed_new_session_btn": "새 세션 시작",

    # ── Sidebar ───────────────────────────────────────────────────────────────
    "sidebar_header":               "## 연구 플랫폼",
    "sidebar_participant_id_label": "**참여자 ID:**",
    "sidebar_progress_label":       "**진행 상황:** {stage_label}",
    "sidebar_need_to_stop": (
        "**중단해야 합니까?** 아래의 **저장 후 종료** 버튼을 클릭하십시오. "
        "참여하시는분의 진행 상황이 자동으로 저장됩니다."
    ),
    "sidebar_returning": (
        "**연구로 돌아오시나요?** 홈 페이지에서 **세션 재개** 탭을 클릭하고 "
        "ID **`{user_id}`**를 입력하여 중단한 곳에서 계속하십시오."
    ),
    "sidebar_reload_btn":    "🔄 페이지 새로고침",
    "sidebar_save_exit_btn": "💾 저장 후 종료",
    "sidebar_saved_msg": (
        "**참여하시는분의 진행 상황이 저장되었습니다.**\n\n"
        "참여하시는분의 참여자 ID는: **{user_id}**\n\n"
        "이것을 메모하거나 스크린샷을 찍으십시오. 계속할 준비가 되면 "
        "이 웹사이트로 돌아와 **세션 재개** 탭을 사용하여 중단한 곳에서 계속하십시오."
    ),
    "sidebar_close_btn":   "닫기",
    "sidebar_no_session":  "활성 세션 없음",
    "sidebar_admin_btn":   "관리자",
    "sidebar_back_btn":    "← 연구로 돌아가기",

    # ── LLM language instruction ──────────────────────────────────────────────
    "llm_language_instruction": (
        "LANGUAGE RULE (highest priority — never override):\n"
        "You MUST respond ONLY in Korean (한국어) in every single message.\n"
        "Never use English, not even one word. This rule overrides everything else.\n"
        "If the participant writes in English, still respond entirely in Korean.\n"
        "모든 응답은 반드시 한국어로만 작성하십시오."
    ),

    # ── Task content (Popcorn Brain — Korean) ─────────────────────────────────
    "task_popcorn_md": """\
참여해 주셔서 감사합니다. 아래 과제 설명을 주의 깊게 읽어 주십시오. 내용을 명확히 이해하기 위해 두 번 읽으시기를 권장합니다. 그런 다음 LLM과 대화를 시작하여 최적의 해결책을 함께 논의하고 협력하십시오. 합의에 도달한 후, 화면 하단의 '완료' 버튼을 클릭하여 세션을 종료하십시오. 참여하시는분의 대화는 연구자들을 위해 저장될 것입니다.

진정으로 좋고 효과적인 해결책을 도출하기 위해 최선을 다해 주십시오.

---

### 과제 설명

미국 로스엔젤레스(Los Angeles) 통합 교육구 교육감인 Johnson 씨는 디지털 기술, 특히 AI 기반 애플리케이션과 도구를 활용하여 학생 친화적이고 효과적인 학습 환경을 조성하는 새로운 교육구 전체 정책을 고민하고 있습니다. 주지사 사무실은 학생의 학업 성취도를 강화할 것이라고 믿는 "스마트 교실" 이니셔티브를 추진하고 있습니다.

이니셔티브 계획 중 하나는 유치원부터 12학년까지의 교실에 AI 애플리케이션과 기기 같은 스마트 기술을 도입하는 것입니다. 여기에는 종이 교과서를 디지털 기기와 AI 기반 대화형 학습지로 교체하는 것이 포함됩니다. 기존 교재 대신 AI를 사용하는 이점은 다음과 같습니다: 1) 학생들이 더 나은 이해를 위해 동적인 3D 하이퍼텍스트, 이미지, 모델, 동영상에 접근할 수 있습니다. 2) 학생들이 수업 중 그룹 협업이나 과제를 위해 교사 및 다른 학생들과 동시에 상호작용할 수 있습니다. 3) 학생들이 기존 방식보다 더 많은 자료를 다루고 더 심층적으로 접근할 수 있습니다.

반면에, 학부모-교사 조직(PTO)은 단점에 대한 실질적인 우려를 제기하고 있습니다 — *디지털 기술의 데이터 저장 서비스에 지나치게 의존함으로써 발생하는 기억력 감퇴*. 이 증후군은 우리가 정보의 저장과 검색을 디지털 기기에 지속적으로 의존할수록 인간의 뇌가 기억 기능과 용량을 점차 잃어가는 것을 말합니다. 권고 사항 중 하나는 이러한 습관적 의존성을 균형 잡기 위해 AI 기반 디지털 기기와 기술을 덜 사용하는 것입니다. PTO는 이러한 우려를 고려하여 AI 도구를 보다 적절하고, 실행 가능하며, 효과적으로 사용하는 방안을 요청하고 있습니다.

이러한 상황에서, 참여하시는분과 참여하시는분의 LLM은 이 딜레마를 해결하고 학생의 기억력을 희생하지 않으면서 학습을 향상시킬 방법을 찾기 위한 마스터 플랜을 작성해야 합니다. 고려해야 할 질문들: 창의적인 아이디어는 무엇입니까? 그 아이디어들은 현실적입니까? 하나의 아이디어가 있다면, 구체적인 실행 항목은 무엇입니까? AI를 더 많이 사용하고 싶어하는 학생들의 바람을 충족시키면서 부모들의 우려를 어떻게 해결할 수 있습니까? 교사의 역할은 무엇입니까? 수학, 과학, 영어 과목에서 AI 기기의 사용 방식이 달라야 합니까? 어떻게 다르게 접근해야 합니까? 학교 정책은 어떻게 해야 합니까?
""",

    # ── Task content (Noble Industries — Korean) ──────────────────────────────
    "task_noble_md": """\
참여해 주셔서 감사합니다. 아래 과제 설명을 주의 깊게 읽어 주십시오. 내용을 명확히 이해하기 위해 두 번 읽으시기를 권장합니다. 그런 다음 LLM과 대화를 시작하여 최적의 해결책을 함께 논의하고 협력하십시오. 합의에 도달한 후, 화면 하단의 '완료' 버튼을 클릭하여 세션을 종료하십시오. 참여하시는분의 대화는 연구자들을 위해 저장될 것입니다. 진정으로 좋고 효과적인 해결책을 도출하기 위해 최선을 다해 주십시오.

---

### 과제 설명

Noble Industries는 오하이오주 콜럼버스에 본사를 둔 중간 규모의 다각화된 제조 회사입니다. 이 회사는 1958년에 설립되었으며 40년의 역사 대부분 동안 꾸준하고 지속적인 성장을 경험해 왔습니다. 8개의 제조 시설이 미국 각지에 위치하며 각 공장은 약 250명의 직원을 고용하고 있습니다. 1997년 Noble Industries의 총 매출액은 1억 500만 달러였습니다.

Noble Industries의 정보 시스템 부서(ISD)는 조직 전체에 기능적으로 분산되어 있습니다. 각 공장은 자체 로컬 IS 운영(예: 주문, 생산 일정, 품질 보증, 의사결정 지원 등)을 개발하고 지원할 책임이 있습니다. 모든 기업 전체 시스템(인사, 판매 예측, 연구, 임원 정보 등)은 본사의 중앙 정보 시스템 부서에서 관리됩니다. 정보 시스템 부서(ISD)에는 총 150명이 고용되어 있습니다.

참여하시는분은 1988년 대학을 졸업한 후 콜럼버스 오하이오 사이트에서 주니어 프로그래머로 채용되었습니다. 5년 후 시스템 분석가 직책으로 승진했습니다. 현재 참여하시는분은 ISD의 수석 시스템 분석가입니다. 참여하시는분의 그룹은 연구개발부(RDD)의 애플리케이션 개발 및 소프트웨어 지원을 담당합니다. 참여하시는분에게 직접 보고하는 인원은 시스템 분석가 2명, 애플리케이션 프로그래머 4명, 사무 지원 직원 2명입니다.

오늘 아침, 참여하시는분과 다른 수석 시스템 분석가들은 본사에서 정보 시스템 부사장 Bob Thompson과 회의를 가졌습니다. 그는 다음과 같이 설명했습니다. "어제 임원 경영 회의에서 일부 내구재 고객들이 새로운 공급업체를 찾았다는 것이 발표되었습니다. 매출 손실을 바탕으로, 재무 부사장은 올해 총 매출이 3~6% 감소할 것으로 예측했습니다. CEO는 판매가 곧 증가하지 않으면 인력을 감축해야 한다고 말했습니다. 모든 부서 부사장들은 해고될 직원들의 예비 목록을 작성하도록 요청받았습니다. ISD의 경우, 최소 1명에서 최대 10명의 직원이 해고될 수 있습니다. 최종 결정은 다음 주에 내려질 것입니다."

Bob은 그 후 "기밀"이라고 표시된 봉투를 배포했습니다. 그는 "각 봉투에는 10명의 정보 시스템 직원에 대한 프로필 정보가 들어 있습니다. 봉투를 사무실로 가져가서 프로필과 회사 운영진의 의견을 읽은 다음, 해고되어야 한다고 생각하는 순서대로 직원들을 순위를 매기십시오. 순위의 이유도 적어 두십시오. 직원들의 실명은 프로필 페이지에 나타나지 않습니다. 왜냐하면 아는 사람에 대해 결정을 내려야 하는 상황을 원하지 않기 때문입니다. 이들은 모두 성과가 좋은 직원들이기 때문에, 경영진은 최종 결정에 대한 입력으로 공정한 기술 동료 그룹의 평가를 원했습니다. 최선의 판단을 사용하십시오. 그런 다음 오늘 나중에 그룹으로 모여 개별 순위를 논의하고 오늘 말까지 최종 순위와 순위 이유를 저에게 제출하십시오." 라고 말했습니다.

Bob은 "이것이 쉬운 일이 아니라는 것을 알고 있지만, 현재 상황을 감안할 때 다른 선택이 없습니다." 라고 말하며 회의를 마쳤습니다. 그 시점에서 참여하시는분과 다른 수석 시스템 분석가들은 순위 지정 작업을 수행하기 위해 각자의 사무실로 돌아갔습니다.

---

### 직원 프로필

| 이름 | 나이 | 직책 | 근속 연수 | 학력 (최고 학위) | 학교 또는 대학 | 결혼 여부 | 부양 가족 수 |
|------|:---:|-------|:--------------:|:--------------------------:|-------------------|:--------------:|:--------------------:|
| Barbara | 27 | 수석 시스템 분석가 | 2 | MBA | 스탠퍼드 대학교 | 미혼 | 0 |
| Chris | 35 | 시스템 분석가 | 10 | BS - MIS | 오클라호마 대학교 | 기혼 | 4 |
| Fred | 61 | 시스템 프로그래머 | 27 | DP 학교 | DeVry Tech. | 기혼 | 1 |
| Harry | 27 | 애플리케이션 프로그래머 | 4 | BS - CIS | 봄베이 대학교 | 미혼 | 3 |
| Joanne | 46 | 수석 시스템 분석가 | 15 | MS - MIS | 오하이오 주립 대학교 | 기혼 | 2 |
| Lois | 54 | 데이터베이스 관리자 | 22 | AAS - DP | 마이애미 데이드 CC | 사별 | 0 |
| Phil | 26 | 시스템 분석가 | 3 | BS - CIS | 국립 대만 대학교 | 미혼 | 1 |
| Sharon | 36 | 사무직 | 12 | 고등학교 졸업 | Harrison H.S. | 기혼 | 6 |
| Susan | 51 | 애플리케이션 프로그래머 | 9 | BS - CIS | 텍사스 A&M 대학교 | 이혼 | 3 |
| Tom | 47 | 수석 시스템 분석가 | 18 | BS - 경영학 | 퍼듀 대학교 | 이혼 | 4 |

---

### 회사 운영진의 의견

**Barbara:** "Barbara는 매우 야심차며 항상 가장 도전적인 업무를 요청합니다. 그녀는 열심히 일하면 인정받고 보상받아야 한다고 믿습니다. 예를 들어, 두 번의 연간 성과 평가에서 Barbara는 언제 승진을 고려받을 것인지 알고 싶어 했습니다. 그녀는 성공을 직위와 급여의 측면에서 정의합니다. Barbara는 매우 경쟁적이며 관리직으로 올라갈 것이라고 생각합니다. 저의 유일한 우려는 때때로 그녀가 너무 단호할 수 있다는 것입니다."

**Chris:** "우리 부서의 모든 사람들 중에서, Chris는 제가 업무를 부여할 때 가장 빠르게 반응하며 왜 그것을 원하는지 절대 묻지 않습니다. Chris는 권위를 존중하고 모든 사람이 조직 계층에서 자신의 위치를 알아야 한다는 것을 이해합니다. 그는 관료주의를 신경 쓰지 않는데, 왜냐하면 그것이 효율성을 향상시킨다는 것을 알기 때문입니다. 아마도 그 때문에 Chris가 8년 동안 군대에 있었던 것을 즐겼을 것입니다."

**Fred:** "Fred는 오랫동안 우리와 함께 있었습니다. 그는 자신의 일을 즐기며 이 모든 세월 동안 여기서의 직업 안정성에 감사합니다. Fred는 모든 사람과 잘 어울리며 특히 새로운 직원들이 질문이 있을 때 그들을 도움으로써 많은 만족감을 얻습니다. 그는 함께 일하는 사람들이 의견 일치를 하는 것이 중요하다는 것을 인식합니다. Fred는 논쟁을 좋아하지 않으므로 다른 사람들이 그와 동의하지 않을 때 기꺼이 타협합니다."

**Harry:** "Harry는 우리 부서에서 가장 기술적으로 능력 있는 사람입니다. 그는 손에 닿는 모든 기술 보고서를 읽습니다. 그러나 Harry는 자신만의 방식으로 일하는 것을 좋아하고 혼자 일하는 것을 선호합니다. 이런 방식으로 Harry는 다른 사람이 공로를 가져가지 않고 그의 상사인 내가 그가 하는 일에 대해 더 쉽게 보상할 수 있다고 믿습니다. 그의 우선순위는 매우 명확합니다. 그는 삶의 모든 것보다 자신과 가족을 먼저 생각합니다."

**Joanne:** "Joanne은 탁월한 조직 능력을 가지고 있습니다. 그녀는 우리가 규칙을 가져야 하고 규칙을 따라야 한다는 것을 이해합니다. Joanne은 질서와 구조가 생산성에 필요하다고 믿기 때문에 부서의 품질 보증 리더(QAL)입니다. 그녀는 불필요한 위험을 감수하지 않으며, 저에게 권고를 하기 전에 철저히 조사합니다."

**Lois:** "Lois는 진정한 팀 플레이어입니다. 그녀는 다른 사람들과 함께 일하는 것을 정말 즐기며 항상 자신의 이익보다 그룹의 이익을 먼저 생각합니다. 실제로 새 데이터베이스 변환이 완료되었을 때 Lois가 대부분의 작업을 했음에도 불구하고 전체 그룹이 그 성과를 인정받아야 한다고 제안했습니다. 저는 지역사회 봉사도 Lois에게 중요하다는 것을 알고 있습니다. 그녀는 노숙자 지역 쉼터에서 자원봉사를 하고 있습니다."

**Phil:** "비록 26세에 불과하지만, Phil은 훨씬 더 나이든 사람처럼 삶을 사는 경향이 있습니다. 그는 역사와 과거 사람들의 삶의 방식을 연구하는 것을 좋아합니다. 작년에 Phil의 어머니가 병에 걸렸을 때 그는 어머니를 돌보기 위해 집으로 돌아왔습니다. Phil은 다른 사람들에 대한 큰 존경심을 가지고 있으며 비판이 정당한지 여부에 관계없이 비판을 받을 때 그들을 옹호할 것입니다."

**Sharon:** "Sharon은 매우 헌신적입니다. 그녀는 일찍 출근하고 보통 늦게까지 남아 있으며 아무리 오래 걸려도 모든 임무를 항상 완료합니다. Sharon은 다른 사람들과의 관계에 큰 비중을 둡니다. 그녀의 장기적인 목표는 플로리다에서 은퇴하는 것이므로 가능한 한 많은 돈을 저축하려고 합니다."

**Susan:** "저는 Susan이 여기서 일하기 시작한 이래로 약 7년 동안 알고 있습니다. 그녀는 자신의 일을 하고 모든 사람이 공평한 몫을 해야 한다고 생각합니다. 실제로 Susan은 우리 공장을 방문하고 있던 보조 공장 감독관에게 그가 하루 동안 그녀의 일을 해보아야 한다고 말한 적이 있습니다. 저는 Susan을 많이 인정합니다. 그녀는 솔직하게 말하며 당신이 CEO이든 우편물 담당자이든 신경 쓰지 않습니다. 그녀에게 누구도 다른 사람보다 더 낫지 않습니다."

**Tom:** "Tom은 항상 새로운 것을 가장 먼저 시도합니다. 라디오 방송국이든, 휴가 장소든, 옷 스타일이든 상관없습니다. Tom은 자신만의 방식으로 일하며 규칙을 어기는 것을 두려워하지 않습니다. 저와의 관계에서도 Tom은 같은 방식입니다. 그래서 저는 일반적으로 큰 위험이 있지만 잠재적으로 큰 성과가 있는 임무를 그에게 줍니다."
""",

    # ── Big5 assessment items (IPIP-50 — Korean) ─────────────────────────────
    "big5_items": {
        "extraversion": [
            {"id": "E1",  "text": "나는 파티의 분위기를 이끈다.",                          "reverse": False},
            {"id": "E2",  "text": "나는 말을 많이 하지 않는다.",                           "reverse": True},
            {"id": "E3",  "text": "나는 사람들과 함께 있으면 편안함을 느낀다.",             "reverse": False},
            {"id": "E4",  "text": "나는 뒤에서 조용히 있는 편이다.",                       "reverse": True},
            {"id": "E5",  "text": "나는 대화를 먼저 시작한다.",                            "reverse": False},
            {"id": "E6",  "text": "나는 할 말이 별로 없다.",                               "reverse": True},
            {"id": "E7",  "text": "나는 파티에서 많은 다양한 사람들과 이야기를 나눈다.",    "reverse": False},
            {"id": "E8",  "text": "나는 주목받는 것을 좋아하지 않는다.",                   "reverse": True},
            {"id": "E9",  "text": "나는 관심의 중심이 되는 것이 괜찮다.",                  "reverse": False},
            {"id": "E10", "text": "나는 낯선 사람들과 함께 있으면 조용히 있는 편이다.",    "reverse": True},
        ],
        "agreeableness": [
            {"id": "A1",  "text": "나는 다른 사람들에 대한 관심이 별로 없다.",             "reverse": True},
            {"id": "A2",  "text": "나는 사람들에 대한 관심이 많다.",                       "reverse": False},
            {"id": "A3",  "text": "나는 사람들을 모욕한다.",                               "reverse": True},
            {"id": "A4",  "text": "나는 다른 사람들의 감정에 공감한다.",                   "reverse": False},
            {"id": "A5",  "text": "나는 다른 사람들의 문제에 관심이 없다.",                "reverse": True},
            {"id": "A6",  "text": "나는 마음이 따뜻하다.",                                 "reverse": False},
            {"id": "A7",  "text": "나는 다른 사람들에게 별로 관심이 없다.",                "reverse": True},
            {"id": "A8",  "text": "나는 다른 사람들을 위해 시간을 낸다.",                  "reverse": False},
            {"id": "A9",  "text": "나는 다른 사람들의 감정을 느낀다.",                     "reverse": False},
            {"id": "A10", "text": "나는 사람들이 편안함을 느끼게 만든다.",                 "reverse": False},
        ],
        "conscientiousness": [
            {"id": "C1",  "text": "나는 항상 준비되어 있다.",                              "reverse": False},
            {"id": "C2",  "text": "나는 물건들을 여기저기 두고 다닌다.",                   "reverse": True},
            {"id": "C3",  "text": "나는 세부 사항에 주의를 기울인다.",                     "reverse": False},
            {"id": "C4",  "text": "나는 일을 엉망으로 만드는 편이다.",                     "reverse": True},
            {"id": "C5",  "text": "나는 집안일을 즉시 처리한다.",                          "reverse": False},
            {"id": "C6",  "text": "나는 물건을 제자리에 돌려놓는 것을 자주 잊는다.",       "reverse": True},
            {"id": "C7",  "text": "나는 질서를 좋아한다.",                                 "reverse": False},
            {"id": "C8",  "text": "나는 의무를 회피한다.",                                 "reverse": True},
            {"id": "C9",  "text": "나는 일정을 따른다.",                                   "reverse": False},
            {"id": "C10", "text": "나는 일에서 꼼꼼하다.",                                 "reverse": False},
        ],
        "neuroticism": [
            {"id": "N1",  "text": "나는 쉽게 스트레스를 받는다.",                          "reverse": False},
            {"id": "N2",  "text": "나는 대부분의 시간에 편안하다.",                        "reverse": True},
            {"id": "N3",  "text": "나는 여러 가지 것들에 대해 걱정한다.",                  "reverse": False},
            {"id": "N4",  "text": "나는 우울함을 거의 느끼지 않는다.",                     "reverse": True},
            {"id": "N5",  "text": "나는 쉽게 동요된다.",                                   "reverse": False},
            {"id": "N6",  "text": "나는 쉽게 화가 난다.",                                  "reverse": False},
            {"id": "N7",  "text": "나는 기분이 자주 바뀐다.",                              "reverse": False},
            {"id": "N8",  "text": "나는 감정 기복이 심하다.",                              "reverse": False},
            {"id": "N9",  "text": "나는 쉽게 짜증을 낸다.",                                "reverse": False},
            {"id": "N10", "text": "나는 자주 우울함을 느낀다.",                            "reverse": False},
        ],
        "openness": [
            {"id": "O1",  "text": "나는 풍부한 어휘력을 가지고 있다.",                     "reverse": False},
            {"id": "O2",  "text": "나는 추상적인 개념을 이해하는 데 어려움을 느낀다.",     "reverse": True},
            {"id": "O3",  "text": "나는 생생한 상상력을 가지고 있다.",                     "reverse": False},
            {"id": "O4",  "text": "나는 추상적인 개념에 관심이 없다.",                     "reverse": True},
            {"id": "O5",  "text": "나는 훌륭한 아이디어를 가지고 있다.",                   "reverse": False},
            {"id": "O6",  "text": "나는 상상력이 풍부하지 않다.",                          "reverse": True},
            {"id": "O7",  "text": "나는 사물을 빠르게 이해한다.",                          "reverse": False},
            {"id": "O8",  "text": "나는 어려운 단어를 사용한다.",                          "reverse": False},
            {"id": "O9",  "text": "나는 여러 가지 것들에 대해 생각하는 시간을 갖는다.",    "reverse": False},
            {"id": "O10", "text": "나는 아이디어가 넘친다.",                               "reverse": False},
        ],
    },

    # ── Survey questions (Korean) ─────────────────────────────────────────────
    "survey_questions": {
        "q1": {
            "question": "우리의 작업(결과물)이 올바르게 완료되었다고 확신한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q3": {
            "question": "우리의 결과물이 주어진 과제를 효과적으로 해결했다고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q4": {
            "question": "LLM-인간 협업이 혼자 하는 것보다 더 즐거웠다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q5": {
            "question": "LLM-인간 협업에서, LLM과 나는 해결책을 찾는 과정에서 자주 의견이 달랐다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q6": {
            "question": "LLM-인간 협업에서, 나는 해결책에 도달하는 것이 더 쉬웠다고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q7": {
            "question": "LLM-인간 협업에서, 우리가 해결책에 도달하는 데 훨씬 더 오랜 시간이 걸렸다고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q8": {
            "question": "LLM-인간 협업에서, 나는 LLM의 제안이나 견해가 마음에 들지 않았지만, LLM의 방식을 따르기로 타협했다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q9": {
            "question": "LLM-인간 협업에서, 세션이 진행될수록 LLM에 대한 신뢰감이 커졌다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q10": {
            "question": "LLM은 내가 몰랐던 것들을 보여주었다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q11": {
            "question": "LLM은 나에게 공감을 나타냈다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q12": {
            "question": "LLM은 감정을 드러내지 않고 사실만을 다뤘다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q13": {
            "question": "LLM-인간 협업에서, 나는 LLM 파트너의 협력 방식(팀으로 기꺼이 일하는 태도, 개방적인 사고 등)이 정말 좋았다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q14": {
            "question": "LLM-인간 협업에서, 파트너는 자신의 방식을 고집하거나 협력하지 않으려 했다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q15": {
            "question": "LLM-인간 협업에서, 나는 내 지식과 기술을 충분히 발휘하지 못했다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q16": {
            "question": "LLM-인간 협업에서, 나는 LLM과 잘 맞는 파트너라고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q17": {
            "question": "LLM-인간 협업에서, 협업 세션을 이끌어 간 것은 내 진정한 자아(성격)가 아니라 나의 예의와 에티켓이었다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q18": {
            "question": "LLM-인간 협업에서, ��는 LLM과 성격이 잘 맞는다고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q19": {
            "question": "LLM-인간 협업에서, 나는 세션 내내 나의 진정한 자아나 성격을 드러내지 않았다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q20": {
            "question": "LLM-인간 협업에서, LLM은 내 실수에 대해 사려 깊고 너그러웠다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q21": {
            "question": "LLM-인간 협업에서, 파트너와의 의견 충돌로 인해 내가 위축되거나 화가 났던 순간이 있었다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q22": {
            "question": "나는 LLM-인간 협업이 스스로 진정으로 배울 수 있는 능력을 빼앗는 일종의 부정행위라고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q23": {
            "question": "다음 번에 다시 LLM과 짝을 이룬다면 더 높은 생산성을 달성할 수 없을 것이라고 생각한다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q24": {
            "question": "LLM-인간 협업에서, LLM은 자신의 요점을 매우 잘 설명했고 나는 완전히 이해할 수 있었다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q25": {
            "question": "LLM-인간 협업에서, LLM은 표현이나 소통이 부족했으며(너무 조용했으며), 이로 인해 협업이 매우 어려웠다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q26": {
            "question": "LLM-인간 협업에서, LLM의 메시지 전달이 불명확하여 협업이 매우 어려웠다.",
            "type": "likert",
            "scale": (1, 7),
        },
        "q32": {
            "question": "협업 중 경험한 LLM으로 인한 갈등이나 부정적 영향을 간략히 설명하세요. 이것이 협업 세션과 생산성에 어떤 영향을 미쳤다고 생각하십니까?",
            "type": "text",
            "placeholder": "",
        },
        "q33": {
            "question": "협업 중 경험한 LLM의 긍정적인 영향을 설명하세요. 이것이 협업 생산성에 어떤 영향을 미치거나 기여했다고 생각하십니까?",
            "type": "text",
            "placeholder": "",
        },
        "q34": {
            "question": "LLM과의 호환성(성격, 소통 또는 기타 측면)에 대해 논의하세요. 좋았다면 왜 그랬습니까? 좋지 않았다면 왜 그랬습니까? 다시 LLM과 협업하면 높은 생산성을 달성할 수 있다고 생각하십니까?",
            "type": "text",
            "placeholder": "",
        },
        "q35": {
            "question": "과제에 기여하는 LLM의 능력 외에도, LLM의 성격이 협업에서 어떤 역할을 했습니까? 성격이 잘 맞았습니까? 설명해 주세요.",
            "type": "text",
            "placeholder": "",
        },
        "q36": {
            "question": "과제에 기여하는 LLM의 능력 외에도, LLM의 의사소통 기술이 협업에서 어떤 역할을 했습니까? LLM이 보여준 의사소통 기술 수준이 협업에 긍정적(또는 부정적) 감정과 영향을 가져다 주었습니까? 설명해 주세요.",
            "type": "text",
            "placeholder": "",
        },
        "q38": {
            "question": "참여하시는분의 성별은 무엇입니까?",
            "type": "text",
            "placeholder": "",
        },
        "q39": {
            "question": "참여하시는분의 전공은 무엇입니까?",
            "type": "text",
            "placeholder": "",
        },
    },
}


# =============================================================================
# Active translation dict
# =============================================================================

T = KO if APP_LANG == "ko" else EN
