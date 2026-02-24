# Step 4: Task Dialogue - Detailed Elaboration

## Overview

**Step 4: Task Dialogue** is the core collaborative problem-solving session where the participant works with their selected LLM personality to complete the chosen task. This is the primary data collection point for studying human-LLM collaboration dynamics.

---

## Purpose & Objectives

### Research Objectives
1. **Observe collaboration patterns** between humans and different LLM personalities
2. **Capture authentic problem-solving dialogue** in a naturalistic setting
3. **Measure interaction quality** across personality types
4. **Collect behavioral data** for later analysis

### Participant Objectives
1. Work with the LLM to solve the given task
2. Engage in natural conversation and collaboration
3. Leverage the LLM's capabilities while maintaining their own perspective
4. Complete the task to the best of their ability

---

## Pre-Dialogue Setup

### Context Loading
When the dialogue begins, the system automatically:

1. **Loads the selected task document** (Noble Industries.pdf or Popcorn Brain.pdf)
2. **Initializes the LLM personality** with its specific system prompt
3. **Prepends task context** to every LLM message as shared context
4. **Creates a dialogue record** with timestamp and metadata

### Task Context Integration
```python
# Example: Task document is prepended to every message
claude_messages = [
    {
        "role": "user",
        "content": "Task document (shared context):\n\n{task_text}"
    },
    # ... followed by actual conversation messages
]
```

This ensures the LLM always has the task context available without the user needing to repeat it.

---

## Interface Components

### Chat Interface Elements

1. **Task Display**
   - Shows task name at the top
   - Indicates which LLM personality is active
   - Displays personality emoji and name

2. **Message History**
   - User messages appear on the right (standard chat convention)
   - LLM messages appear on the left with personality avatar
   - Timestamps for each message
   - Scrollable history

3. **Input Area**
   - Text input box for user messages
   - Send button
   - Real-time character count (optional)

4. **Dialogue Controls**
   - Message counter (shows total messages exchanged)
   - Time elapsed indicator
   - **"End Dialogue" button** (advances to next stage)

### Visual Design
```
┌─────────────────────────────────────────────────────┐
│ 💬 Task Dialogue: Noble Industries.pdf             │
│ 🤖 Chatting with: ⭐ Role Model                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⭐ Role Model: [10:15:23]                         │
│  ┌───────────────────────────────────────┐         │
│  │ Hello! I'm excited to help you with   │         │
│  │ this candidate evaluation task...     │         │
│  └───────────────────────────────────────┘         │
│                                                     │
│                        User: [10:15:45]  👤        │
│         ┌───────────────────────────────────────┐  │
│         │ Great! Let's start by reviewing the  │  │
│         │ candidates' qualifications...        │  │
│         └───────────────────────────────────────┘  │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Messages: 24                    [End Dialogue]     │
└─────────────────────────────────────────────────────┘
```

---

## Dialogue Dynamics

### LLM Personality Behaviors

Each personality exhibits distinct communication patterns:

#### ⚖️ Average (Balanced & Practical)
- **Tone**: Neutral, balanced, pragmatic
- **Approach**: Considers multiple perspectives
- **Communication**: Clear and straightforward
- **Example**: "Let's look at both the pros and cons of each candidate objectively."

#### ⭐ Role Model (Optimistic & Organized)
- **Tone**: Positive, encouraging, structured
- **Approach**: Systematic and methodical
- **Communication**: Supportive and motivating
- **Example**: "Great thinking! Let's organize our evaluation into clear criteria."

#### 🎯 Self-Centred (Direct & Competitive)
- **Tone**: Confident, assertive, goal-focused
- **Approach**: Efficiency-driven, decisive
- **Communication**: Direct and sometimes challenging
- **Example**: "I think we should focus on the top performer and move quickly."

#### 🤫 Reserved (Calm & Conventional)
- **Tone**: Cautious, traditional, risk-averse
- **Approach**: Conservative and careful
- **Communication**: Measured and thoughtful
- **Example**: "Let's take our time and make sure we follow established procedures."

### Collaboration Patterns

**Typical Dialogue Flow**:
1. **Opening** (1-3 messages)
   - LLM greets and establishes rapport
   - User states initial thoughts or questions
   - Mutual understanding of task

2. **Exploration** (5-15 messages)
   - Discuss task requirements
   - Share perspectives and ideas
   - Ask clarifying questions
   - Explore different approaches

3. **Analysis** (10-20 messages)
   - Deep dive into task specifics
   - Evaluate options or candidates
   - Debate pros and cons
   - Build toward solutions

4. **Synthesis** (5-10 messages)
   - Consolidate findings
   - Reach conclusions
   - Finalize decisions
   - Confirm agreement

5. **Closure** (1-3 messages)
   - Summarize outcomes
   - Express satisfaction/concerns
   - Prepare to end dialogue

**Average Dialogue Length**: 20-40 messages  
**Average Duration**: 15-30 minutes

---

## Data Capture During Dialogue

### Real-Time Recording

Every interaction is captured with:

```json
{
  "message_id": "msg_abc123",
  "timestamp": "2026-02-24T12:30:45Z",
  "role": "user",  // or "assistant"
  "content": "Let's evaluate Candidate A first...",
  "metadata": {
    "message_number": 5,
    "elapsed_seconds": 127
  }
}
```

### Captured Metrics

1. **Message-Level**
   - Content of each message
   - Precise timestamp
   - Message length (characters)
   - Role (user vs assistant)

2. **Dialogue-Level**
   - Total messages exchanged
   - User message count
   - Assistant message count
   - Total duration (seconds)
   - Start and end timestamps

3. **Behavioral Indicators** (for later analysis)
   - Turn-taking patterns
   - Response times
   - Message length distributions
   - Topic transitions
   - Agreement/disagreement markers

---

## Task-Specific Dialogue Characteristics

### Noble Industries Task

**Focus**: Candidate evaluation and ranking

**Typical Discussion Points**:
- Candidate qualifications and experience
- Cultural fit and soft skills
- Technical competencies
- Leadership potential
- Comparison between candidates
- Ranking rationale development

**Expected Dialogue Patterns**:
- Systematic review of each candidate
- Comparative analysis
- Weighing of different criteria
- Justification of rankings
- Debate over close calls

**Key Moments to Capture**:
- Initial impressions
- Changing opinions
- Consensus building
- Final ranking decisions

### Popcorn Brain Task

**Focus**: Creative brainstorming and idea generation

**Typical Discussion Points**:
- Problem understanding
- Idea generation
- Alternative approaches
- Elaboration on concepts
- Synthesis of ideas
- Refinement and iteration

**Expected Dialogue Patterns**:
- Rapid idea exchange
- Building on each other's suggestions
- Exploring multiple directions
- Combining and refining ideas
- Evaluating feasibility

**Key Moments to Capture**:
- Novel idea emergence
- Idea combinations
- Creative leaps
- Elaboration instances
- Flexibility in thinking

---

## Participant Experience

### What Participants Should Do

✅ **DO**:
- Engage naturally as if talking to a colleague
- Share your genuine thoughts and opinions
- Ask questions when unclear
- Challenge the LLM when you disagree
- Take time to think through responses
- Use the LLM's suggestions as input, not commands
- Express uncertainty when appropriate

❌ **DON'T**:
- Rush through the dialogue
- Simply agree with everything the LLM says
- Treat it as a test with "right answers"
- Worry about grammar or perfect phrasing
- Feel pressured to reach a specific conclusion
- Pretend to understand if confused

### Common Participant Behaviors

**Engaged Collaboration** (Ideal):
- Active back-and-forth exchange
- Building on LLM's ideas
- Offering own perspectives
- Asking clarifying questions
- Expressing agreement and disagreement

**Passive Acceptance**:
- Minimal responses ("ok", "yes", "sounds good")
- Not challenging LLM suggestions
- Letting LLM drive entirely
- May indicate personality mismatch

**Active Resistance**:
- Frequent disagreement
- Dismissing LLM suggestions
- Insisting on own approach
- May indicate personality clash

**Confused/Lost**:
- Repeated clarification requests
- Off-topic responses
- Short, uncertain messages
- May need intervention

---

## Technical Implementation

### Message Flow

```python
def render_task_dialogue():
    """Stage 4: Task Dialogue"""
    dialogue_id = st.session_state.current_dialogue_id
    dialogue = agents['dialogue'].get_dialogue(dialogue_id)
    
    # Display message history
    for msg in dialogue.messages:
        if msg.role == "user":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant").write(msg.content)
    
    # Chat input
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # Record user message
        agents['dialogue'].record_message(
            dialogue_id, "user", user_input
        )
        
        # Get LLM response
        response = personality.chat(messages)
        
        # Record assistant message
        agents['dialogue'].record_message(
            dialogue_id, "assistant", response
        )
        
        st.rerun()
```

### LLM API Integration

**Request Structure**:
```python
{
    "model": "claude-3-sonnet",
    "max_tokens": 1024,
    "system": personality_system_prompt,
    "messages": [
        {"role": "user", "content": task_context},
        {"role": "user", "content": "User message 1"},
        {"role": "assistant", "content": "LLM response 1"},
        {"role": "user", "content": "User message 2"},
        # ... conversation continues
    ]
}
```

**Response Handling**:
- Extract text from API response
- Record with timestamp
- Display in chat interface
- Save to dialogue record
- Update message counters

---

## Quality Assurance

### Monitoring During Dialogue

**System Checks**:
- ✅ Messages saving correctly
- ✅ Timestamps accurate
- ✅ LLM responding within 5 seconds
- ✅ No message loss
- ✅ Dialogue record updating

**Potential Issues**:
- ⚠️ LLM API timeout (retry logic)
- ⚠️ Network interruption (auto-save)
- ⚠️ Very long messages (truncation warning)
- ⚠️ Inappropriate content (flagging)

### Data Validation

After dialogue ends:
1. Verify all messages saved
2. Check timestamp sequence
3. Validate duration calculation
4. Confirm dialogue record completeness
5. Link to session properly

---

## Transition to Next Stage

### Ending the Dialogue

When participant clicks **"End Dialogue"**:

1. **Finalize Dialogue Record**
   ```python
   dialogue.end_dialogue()  # Sets end timestamp, calculates duration
   dialogue.save(data_dir)
   ```

2. **Update Session**
   ```python
   session.dialogue_records.append(dialogue_id)
   session.save(data_dir)
   ```

3. **Advance Workflow**
   ```python
   supervisor.advance_stage(
       session_id, 
       WorkflowStage.TASK_RESPONSE  # Go to task-specific data capture
   )
   ```

4. **Route to Task-Specific Interface**
   - Noble Industries → Ranking interface
   - Popcorn Brain → Creative assessment

---

## Research Value

### What We Learn from Task Dialogue

1. **Collaboration Dynamics**
   - How different personalities affect interaction
   - Turn-taking patterns
   - Influence and persuasion
   - Conflict resolution

2. **Task Performance**
   - Quality of solutions reached
   - Efficiency of collaboration
   - Creativity of outputs
   - Decision-making processes

3. **Personality Effects**
   - Which personalities work best for which users
   - Personality-task fit
   - User satisfaction by personality
   - Behavioral adaptations

4. **Communication Patterns**
   - Message lengths and complexity
   - Question-asking frequency
   - Agreement/disagreement expressions
   - Emotional tone

---

## Best Practices for Researchers

### Before Data Collection

1. **Pilot Test** with 5-10 participants
2. **Verify** all dialogue data is captured correctly
3. **Test** all 4 personalities × 2 tasks = 8 scenarios
4. **Prepare** intervention protocols for stuck participants

### During Data Collection

1. **Monitor** active dialogues for issues
2. **Track** completion rates by personality/task
3. **Note** any technical problems
4. **Be available** for participant questions

### After Data Collection

1. **Backup** all dialogue records immediately
2. **Verify** data integrity (no corrupted files)
3. **Export** for analysis
4. **Anonymize** for sharing/publication

---

## Example Dialogue Excerpt

### Noble Industries - Role Model Personality

```
⭐ Role Model: Hello! I'm excited to help you evaluate these candidates 
for the Noble Industries position. I think we can do a thorough and 
fair assessment together. Shall we start by reviewing the job 
requirements?

👤 User: Yes, that sounds good. The position requires strong leadership 
and technical skills in manufacturing.

⭐ Role Model: Perfect! Let's create a systematic approach. I suggest 
we evaluate each candidate on three key criteria: 1) Leadership 
experience, 2) Technical expertise, and 3) Cultural fit. Does that 
framework work for you?

👤 User: That makes sense. Let's start with Candidate A.

⭐ Role Model: Great choice! Looking at Candidate A's profile, I see 
they have 10 years of manufacturing experience and led a team of 50. 
That's impressive! What stands out to you about their background?

👤 User: I'm impressed by their track record of process improvements, 
but I'm concerned about their limited experience with our specific 
industry segment.

⭐ Role Model: That's an excellent observation! You're right to consider 
both strengths and potential gaps. Let's note that as we compare them 
to the other candidates...

[Dialogue continues for 25 more messages...]
```

---

## Summary

**Step 4: Task Dialogue** is where the magic happens - authentic human-LLM collaboration captured in real-time. This stage:

- ✅ Provides the primary research data
- ✅ Reveals personality effects on collaboration
- ✅ Captures natural problem-solving processes
- ✅ Generates rich qualitative and quantitative data
- ✅ Sets up task-specific data capture in Step 5

**Duration**: 15-30 minutes  
**Output**: Complete dialogue transcript with 20-40 messages  
**Next**: Task-specific response (rankings or creative assessment)
