# From Personality Assessment to Task Assignment: A Process Transparency Document

**Prepared for**: Ethics review / IRB judging panel
**Scope**: Everything that happens between a participant submitting the Big5 personality assessment and being paired with a task and an AI conversational partner.
**Basis**: This document is a direct account of the application's executed code, not a design intention. Every claim below is traceable to a specific file and line number in the live codebase, verified on **2026-08-03** against the `main` branch (see repository commit history for the exact revision).
**Revision note**: This is revision 4 of this document. Earlier revisions described one or both pairing draws as plain, personality-independent random choices; both have since been superseded. Revision 4 adds an [Addendum](#addendum-end-of-study-completion-notification) on a related but out-of-scope data-handling event — see [Revision History](#revision-history) at the bottom for details.

---

## Summary

After a participant finishes the personality questionnaire, the system (1) scores their responses, (2) classifies them into one of four fixed personality types using a deterministic rule, and (3) saves that result. It then pairs the participant with a task and an AI conversational personality. **Both pairings work the same way by design**: to keep the study's four-personality-type × two-task structure, and its four-personality-type × four-AI-personality structure, from becoming badly imbalanced by chance, the system looks at the participant's already-computed Gerlach type and assigns whichever task — and, separately, whichever AI personality — is currently under-represented for that type. This is a standard trial-design technique sometimes called "minimization" or covariate-adaptive randomization. Whenever a given type's options are equally represented so far, the choice is still made at random, so no single participant's pairing is predictable in advance; it is simply no longer statistically independent of personality type, and that dependency is intentional. The task draw and the AI-personality draw are balanced independently of each other (each only against Gerlach type, not against one another). No researcher makes or reviews any individual pairing in the normal flow. The participant is not shown their personality type, the AI personality label, or the fact that a second task existed.

---

## Step 1 — Participant submits the assessment

- The assessment is the IPIP-50 questionnaire: 50 items, 10 per Big5 trait (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism), answered on a 1–5 Likert scale.
- Each question renders with no default selection (`index=None`), so a participant cannot accidentally submit an unintended answer.
- Submission is blocked until **all 50 items** are answered — if any are missing, the participant sees which item numbers are unanswered and must complete them; there is no partial or forced submission.
- *Source: `agent_research_app.py:302-329` (`render_big5_assessment`)*

## Step 2 — Automated scoring (no human involvement)

- `calculate_scores()` reverse-scores the items flagged `reverse: True` (`score = 6 - raw_score`), sums the 10 item scores per trait, and rescales to a 0–100 range: `((trait_sum − 10) / 40) × 100`.
- This is pure arithmetic — no LLM, no human rater, and no subjective judgment is involved in scoring.
- *Source: `agents/big5_assessment_agent.py:163-196` (`calculate_scores`)*

## Step 3 — Gerlach personality-type classification

- `classify_gerlach_type()` assigns the participant to whichever of four fixed types best matches their trait scores, using a deterministic rule-based distance calculation (not machine learning, not an LLM, not human judgment):

| Type | Rule (0–100 trait scale) |
|---|---|
| Average | Best fit when all five trait scores sit close to the midpoint (50) — scored as the average absolute deviation from 50, smaller = better fit |
| Role Model | Best fit when Neuroticism < 40, Extraversion > 60, Openness > 60, Agreeableness > 60, Conscientiousness > 60 |
| Self-Centred | Best fit when Openness < 40, Agreeableness < 40, Conscientiousness < 40 |
| Reserved | Best fit when Neuroticism < 40, Openness < 40 |

- The participant is assigned to the type with the closest fit; the "confidence" value stored alongside it reflects how well the scores matched that type's criteria (100 = perfect match on all criteria) — it is a fit metric, not a statistical significance value.
- *Source: `agents/big5_assessment_agent.py:198-247` (`classify_gerlach_type`)*

## Step 4 — Assessment record is saved

- A record is created containing: the five trait scores, every raw item response, the assigned Gerlach type, the confidence value, and a timestamp. It is written to `research_data/assessments/{assessment_id}.json` and mirrored to a private GitHub repository as durable backup.
- The participant's session record is updated with a pointer (`big5_assessment_id`) to this record.
- **This entire step completes and is saved to disk before the task-pairing step below begins.** The personality classification exists as a finished, immutable fact before any task assignment happens.
- **This ordering is not incidental — it is what makes the balancing mechanism in Step 6 possible.** The task-assignment logic reads this saved Gerlach type back off disk to decide which task is currently under-represented for participants of that type.
- *Source: `agents/big5_assessment_agent.py:267-288`; `agents/data_models.py:69-116`; `agent_research_app.py:331-339`*

## Step 5 — Workflow stage advances

- The session's stage moves from `BIG5_ASSESSMENT` to `TASK_SELECTION`; the completed stage is logged, and the session file is re-saved.
- *Source: `agents/supervisor_agent.py:62-78`; `agent_research_app.py:341`*

## Step 6 — Task and AI-personality pairing (the randomization event)

This is the step most relevant to ethical review of the pairing process. Both draws now use the **same balancing technique**, applied independently to two different pairings, so they are described together below.

- **Why not plain independent randomization for either draw.** With four Gerlach types, two tasks, and four AI personalities, a purely independent random draw for each participant can — purely by chance, especially at this study's target scale (~100 participants split unevenly across four types) — produce badly unbalanced cells (e.g. far more "Self-Centred" participants doing one task than the other, or paired with one AI personality far more than another). That imbalance would weaken later statistical comparisons, which is the reason both draws were built this way.
- **Mechanism — task (`_assign_balanced_task`).** By the time this runs, the participant's Gerlach type is already known and saved (Steps 3–4). The system counts, among all previously-assigned participants who share that same Gerlach type, how many were given each task, and assigns whichever task currently has the lower count *for that type*. If both tasks are equally represented so far for that type, the task is still chosen uniformly at random between them.
- **Mechanism — AI personality (`_assign_balanced_personality`).** Identical logic, applied to the AI conversational personality (`average`, `role_model`, `self_centred`, `reserved`) instead of the task: the system counts, among previously-assigned participants sharing the same Gerlach type, how many received each AI personality, and assigns whichever is currently under-represented *for that type*, again resolving ties at random.
- **The two draws don't coordinate with each other.** Each is balanced only against the participant's Gerlach type — the task draw doesn't look at AI-personality counts and vice versa. The full three-way combination (Gerlach type × task × AI personality) is therefore not directly balanced, only each of the two two-way relationships (type × task, and type × AI personality) independently.
- **What this is, technically.** This is a standard, widely used trial-design technique sometimes called "minimization" or covariate-adaptive randomization: a known participant characteristic is deliberately used to balance group sizes across strata, while keeping each individual assignment a coin-flip whenever the running counts are tied. It is a departure from pure independent randomization by design, not an accidental bias — its explicit purpose is to counteract small-sample imbalance, which independent randomization alone cannot guarantee against.
- **The participant still cannot influence or predict either assignment.** Nothing about a participant's behavior, responses, or preferences feeds into either decision beyond the fixed Gerlach type computed once from the standard IPIP-50 questionnaire in Step 3 — before the participant has any awareness that task or AI-personality assignment is happening at all.
- **Known limitation — honestly stated.** Gerlach type is intrinsic to each participant; it cannot be assigned or balanced by this mechanism. This algorithm can only balance the task split and the AI-personality split *within* each type as participants arrive — it cannot force the *overall* number of participants per type to be equal. That side of the balance depends on recruitment, which the research team monitors via the admin dashboard's live per-type participant counts (a separate, password-protected internal tool — see below).
- **Not concurrency-safe against simultaneous completions.** Both counts are computed by reading current on-disk data at assignment time; two participants finishing their assessment at the exact same instant could theoretically both be counted against the same "before" state for either draw. At this study's expected pace (participants arriving over days/weeks, not simultaneously), this is a documented but practically negligible limitation, not a hidden one.
- **No human/researcher involvement in the normal flow.** Both draws execute automatically within the same page load that follows assessment submission. There is no researcher-facing approval, review, or override step for either assignment. (A separate admin "Stage Navigator" tool exists purely to move a stuck session's stage marker for troubleshooting — it does not re-run or alter either draw.)
- **One-time and non-repeatable.** Both draws are gated by `if "assigned_task" not in session.metadata` — they run exactly once per participant. If a participant's browser refreshes, disconnects, or they resume the study later, the already-assigned task and personality are reloaded from the saved session file rather than re-randomized. A participant cannot obtain a different task or AI personality by refreshing or restarting their session.
- Neither the `random` module nor this balancing logic is ever seeded with a fixed value anywhere in the codebase, so outcomes are not reproducible or presettable by the research team on a per-participant basis.
- *Source: `agent_research_app.py:427-442` (`_load_gerlach_type`), `:445-481` (`_counts_by_gerlach_type`), `:484-491` (`_minimize_choice`), `:494-510` (`_assign_balanced_task`), `:513-524` (`_assign_balanced_personality`), `:527-548` (`_get_or_assign`)*

## Step 7 — Assignment is persisted

- `assigned_task` and `assigned_personality` are written into the session's `metadata` and saved to `research_data/sessions/{session_id}.json` (and mirrored to GitHub). This creates a permanent, timestamped record of exactly which task and AI personality each participant received.
- *Source: `agent_research_app.py:544-546`; `agents/data_models.py:26-57`*

## Step 8 — Dialogue created and participant handed off

- A dialogue record is created binding the participant's ID, session ID, the assigned task, and the assigned AI personality.
- The first message the participant sees is a single, fixed, pre-written welcome text — identical for every participant regardless of which task or personality they were assigned. It is not generated by the LLM, so no variation is introduced at the hand-off itself.
- The workflow stage advances to `TASK_DIALOGUE` and the participant is redirected. Steps 6–8 happen within one page load; the only thing the participant sees is a brief loading indicator. **There is no on-screen "task selection" step where the participant chooses, or is shown, either option.**
- *Source: `agent_research_app.py:551-592` (`render_task_selection`)*

---

## What the participant does and does not see

| Shown to participant | Hidden from participant |
|---|---|
| The task document itself, once in the dialogue stage | Their own Gerlach personality type and confidence score |
| — | That an "AI personality" condition exists or which one they received |
| — | That a second task existed at all |

This concealment is an intentional design choice, documented internally, to reduce demand effects — i.e., to prevent participants from behaving differently because they know their classified "type" or know they are in a personality-conditioned AI experiment.

## Where this data is stored and who can access it

- Per-participant records (assessment, session, dialogue) are stored as JSON files under `research_data/`, with a mirrored copy on a private GitHub repository as backup.
- An admin dashboard exists separately from the participant-facing app, is password-protected, and is not reachable by participants. It lets the research team view aggregate counts (including live balance checks across personality types × tasks and personality types × AI personalities) and export data for analysis. **No assignment can be created, edited, or reassigned from this dashboard** — the only session-level control available is manually moving a stuck session's stage marker for troubleshooting, which does not touch `assigned_task` or `assigned_personality`.

## Verifiability

Every factual claim above cites the exact file and line range implementing it. A reviewer with access to the repository can open each cited location and confirm the described behavior directly, independent of this document's prose. Primary files referenced:

- `agent_research_app.py`
- `agents/big5_assessment_agent.py`
- `agents/data_models.py`
- `agents/supervisor_agent.py`

---

## Revision History

- **Revision 1** (earlier draft): Described task assignment as a plain, uniform random draw made independently of the participant's Gerlach type — i.e., `random.choice()` over the two tasks with no knowledge of the assessment result. This was accurate for the code at the time.
- **Revision 2** (2026-08-03): Task assignment was reworked to strive for balance across the four Gerlach types × two tasks, since pure independent randomization offered no protection against chance imbalance at this study's scale. The new mechanism (`_assign_balanced_task`) deliberately reads the participant's already-computed Gerlach type to keep each type's task split as even as possible, while still making an unpredictable random choice whenever counts are tied. This document was revised alongside the code change so that it continues to accurately describe actual system behavior rather than a superseded version of it.
- **Revision 3** (2026-08-03): AI-personality assignment was reworked the same way. It had still been a plain, personality-independent random draw after Revision 2 — described accurately as such at the time. Per explicit request to also balance participant-personality × AI-personality matching, `_assign_balanced_personality` now applies the identical minimization technique used for the task, balancing each Gerlach type's AI-personality split independently of the task balancing. The shared counting logic was refactored into `_counts_by_gerlach_type` / `_minimize_choice` so both draws use one audited implementation rather than two near-duplicate ones. The admin dashboard gained a matching Gerlach type × AI personality cross-tab alongside its existing type × task view. This document's Step 6 and Summary were rewritten accordingly.
- **Revision 4** (this version, 2026-08-03): Added the [Addendum](#addendum-end-of-study-completion-notification) below, describing an automated investigator email that was discovered to be documented (in `docs/EMAIL_SETUP_GUIDE.md`, `docs/ADMIN_DEPLOYMENT_INSTRUCTIONS.md`) as already happening but was, on inspection, never actually wired into the app — `send_completion_notification()` existed but had no caller anywhere. It has now been wired in and extended to include the same balance data described in Step 6/this document. This event happens at the end of a session (after the post-experiment survey), not between assessment and task pairing, so it sits outside this document's stated Scope — it's included as an addendum rather than folded into the Scope line or the numbered steps above, to keep the original step-by-step account precise.

---

## Addendum: End-of-Study Completion Notification

This section covers a related data-handling event that occurs at the very end of a participant's session — well after the task pairing this document otherwise covers — added because it transmits the same balance data described in Step 6 to a new audience via a new channel, which reviewers evaluating data-handling transparency would reasonably want to know about.

- **What happens.** Immediately after a session reaches the `COMPLETED` stage — on `main`, right after the participant answers the re-consent question that follows the post-experiment survey; on `korean`, which has no separate re-consent step, directly from the post-survey submission handler — an automated email is sent to two named investigators: `kchoi29@gmu.edu` and `il.im@yonsei.ac.kr` (`utils/email_notifier.py: INVESTIGATOR_EMAILS`).
- **What it contains.** The completing participant's ID, session ID, completion timestamp, Gerlach type, assigned task, assigned AI personality, and (on `main` only) whether they withdrew data consent at re-consent — plus the current study-wide balance snapshot (participants per Gerlach type, a type × task table, and a type × AI-personality table), computed fresh at that moment by `_compute_balance_snapshot()`. This mirrors what the admin dashboard shows, so investigators see it without logging in.
- **Delivery mechanism.** Plain SMTP via Gmail (`smtp.gmail.com`), authenticated with credentials read only from Streamlit Cloud secrets (`SENDER_EMAIL` / `SENDER_PASSWORD`) — never hardcoded in the repository. **As of this writing, those secrets are not yet configured on the live deployment** (confirmed directly by the researcher), so `EmailNotifier.is_configured()` currently returns `False` and every send attempt is silently skipped — no email is actually being sent yet. This addendum documents the mechanism as built, not as a claim that it is presently active.
- **Never blocks the participant.** The call is wrapped in a `try`/`except` in the calling code; any failure — misconfigured or unreachable SMTP, a network error — is swallowed and never surfaces to the participant or interrupts their session.
- **Consideration for reviewers.** This is the first point in the pipeline where a participant's ID and personality classification leave the application's own access-controlled storage (`research_data/` + the password-protected admin dashboard) and are transmitted via standard, non-end-to-end-encrypted email to individual inboxes outside that access control. The recipient list and sending account are configuration values documented in `docs/EMAIL_SETUP_GUIDE.md`, not secrets embedded in this document.
- *Source: `utils/email_notifier.py`; `agent_research_app.py` → `render_re_consent()` (`main`) or the post-survey submission handler (`korean`) → `_compute_balance_snapshot()`.*
