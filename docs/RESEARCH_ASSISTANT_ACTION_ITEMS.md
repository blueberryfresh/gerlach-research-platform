# Research Assistant Action Items
## Gerlach Research Platform — Facilitation & Monitoring Checklist

**Audience:** The research assistant (RA) responsible for day-to-day facilitation and monitoring while the study is live.
**Scope:** Both live deployments — English (https://gerlach-research.streamlit.app/) and Korean (https://blueberryfresh-research-ko.streamlit.app/) — are served from the same `main` branch (Korean via the `APP_LANG=ko` secret) and need to be checked separately. They are two separate Streamlit apps with two separate admin dashboards and two separate participant pools.

---

## ⚠️ Special Attention Items

Read this section first. These are the things most likely to cause confusion, lost time, or a bad participant experience if missed.

1. **GitHub sync is throttled and fails silently.** Dialogue messages only sync to the persistent GitHub-backed store on the 1st message, every 5th message after that, and always when the participant clicks Complete. If a sync attempt fails (network hiccup, rate limit), the app does **not** show an error — it just keeps going with the local copy. Streamlit Cloud's own filesystem is **ephemeral** — it does not survive an app restart or redeploy — so GitHub is the actual backup. **Action:** periodically run the connection test in the **🔌 GitHub Test** admin tab to confirm writes are actually landing, especially after any redeploy.

2. **Stalled-session follow-up is manual, not automatic.** There is no email/alert system currently wired up for stalled sessions. The **📈 Study Progress** tab flags anyone idle for 48+ hours (adjustable), but nobody is notified — you have to go look. **Action:** check this tab at least once per day during active recruitment.

3. **Friction Analysis is a new, unvalidated heuristic — don't over-read it.** The **⚡ Friction Analysis** tab (added Aug 2026) flags "pushback" and "override attempt" language using a coarse keyword/regex match, not a validated classifier. Treat its numbers as directional signals for aggregate patterns once you have real participant data, not as evidence about any single participant's behavior. As of this writing the dataset contains only test/simulation entries, so the numbers there mean nothing yet.

4. **English and Korean follow the same workflow.** Both apps run the same workflow from `main`, including the "Final Step — Data Consent" re-consent screen between the survey and completion. Only the language differs. (The old `korean` branch app is suspended and must not be used.)

5. **Stage Navigator is a testing tool, not a shortcut for real participants.** The 🔀 Stage Navigator tab lets you manually move any session to any workflow stage. It exists to let you test the flow with a dummy ID (e.g. `test01`). **Never** use it to fast-track a real participant past a stage — it bypasses whatever data that stage would have captured, and breaks the integrity of their dataset.

6. **Admin password hygiene.** Log out of the admin dashboard when you're done, especially on a shared or public computer. Do not share the password outside the authorized research team. *(Separately flagged to the PI: `docs/ADMINISTRATOR_USER_GUIDE.md` currently contains the admin password in plain text and is committed to the repository — worth rotating the password and removing it from that file if the repo is or could become public.)*

7. **Balance monitoring has a real limit.** Task and AI-personality assignment auto-balance within each Gerlach type as data comes in (minimization algorithm) — but nothing in the system can control *which* Gerlach types actually show up. If the always-visible "Personality Type & Task Assignment" panel shows one type badly underrepresented, that's a **recruitment** issue, not a system bug — flag it to the PI rather than expecting the dashboard to fix it.

8. **Never use the Stage Navigator or admin ZIP downloads on a public/shared machine without logging out afterward** — participant dialogue transcripts are full free-text and are the most sensitive data in the export.

---

## Daily / Regular Monitoring Checklist

Do this once per day (more often during active recruitment pushes), **on both the English and Korean apps**:

- [ ] Log in to the admin dashboard (sidebar → Admin Tools → Admin Download Center)
- [ ] Check the **👥 Activity Log** tab for recent participant activity
- [ ] Check the **📈 Study Progress** tab:
  - [ ] Stage funnel — anyone piling up at one stage?
  - [ ] Stalled Sessions panel — anyone idle past the threshold?
  - [ ] Enrollment/completion trend chart looks sane
- [ ] Check the always-visible **🧬 Personality Type & Task Assignment** panel at the top of the page for balance across Gerlach types, tasks, and AI personalities
- [ ] Check the **🤖 API Monitor** tab for elevated error rates or latency spikes on Claude API calls
- [ ] Log out when finished

---

## Real-Time Participant Support Playbook

When a participant reports a problem (in person, by email, etc.), these are the known issues and their fixes — confirm with the participant before escalating:

| Symptom | What to tell the participant | Why it's safe |
|---|---|---|
| Blank or frozen page | Open the left sidebar → press **🔄 Reload Page** | Progress is always saved server-side; reload just re-renders |
| Needs to stop and come back later | Sidebar → **💾 Save & Exit**, then write down their **Participant ID** | Resume Session tab picks up exactly where they left off — never register a new ID for the same person |
| Duplicate/repeated messages in the chat | This is a display glitch only — press **🔄 Reload Page** | Confirmed data-integrity issue is cosmetic only; the underlying JSON record is correct |
| AI not responding | Wait 10–15 seconds, then Reload Page | Conversation state is saved before/after each call; a reload resumes cleanly |
| Lost their Participant ID | Check **👤 Download by Participant** or the Activity Log to help them locate the right session | Don't guess — a mismatched ID creates an orphaned session |
| Wants to withdraw consent | Direct them to the re-consent step (same in both languages) | Consent handling is identical in both apps |

If a fix above doesn't resolve it, or you see anything you don't recognize, escalate rather than experiment on a live participant session (see Escalation, below).

---

## Weekly Tasks

- [ ] Download a full data backup (ZIP) from **📥 Download All Data**, both apps
- [ ] Export CSV snapshot from **📊 Export to CSV**
- [ ] Save both with a date-stamped filename in your backup location
- [ ] Spot-check one or two recently completed dialogues for obvious data-quality problems (near-empty transcript, <5 minute duration, etc.)

---

## Escalation — When to Contact the PI / Technical Admin

Contact the PI/technical admin rather than handling it yourself when:

- GitHub Test tab shows a connection failure
- API Monitor shows a sustained spike in errors (not a single transient failure)
- A participant reports data loss that a page reload doesn't fix
- You're not sure whether a session is a real participant or leftover test data before running an export
- Anything involving consent withdrawal that isn't cleanly handled by the existing re-consent flow
- You're about to use the Stage Navigator on anything other than a test ID

---

## Quick Reference — Admin Dashboard Tabs

| Tab | Use it for |
|---|---|
| 👥 Activity Log | Recent participant activity feed |
| 📈 Study Progress | Funnel, stalled sessions, enrollment trend, time-per-stage |
| ⚡ Friction Analysis | Behavioral friction by AI personality (heuristic, see caveat above) |
| 📥 Download All Data | Full ZIP backup, all participants |
| 👤 Download by Participant | Individual participant lookup/export |
| 📊 Export to CSV | Spreadsheet-ready summary for analysis |
| 🔀 Stage Navigator | **Testing only** — manually move a session between stages |
| 🔌 GitHub Test | Verify the persistent backup connection is actually working |
| 🤖 API Monitor | Claude API health, latency, token usage, error log |

---

*Last updated: August 2026 — reflects the admin dashboard as of the Friction Analysis tab addition.*
