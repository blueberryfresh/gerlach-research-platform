# Korean Deployment — Setup Instructions for Your Colleague

---

## What You Need Before Starting

- A **GitHub account**
- A **Streamlit Cloud account** (free at streamlit.io)
- The **Anthropic API key** from the study PI

---

## Step 1 — Fork the Repository

1. Go to the GitHub repository for this study (get the URL from the PI)
2. Click **Fork** (top-right corner) → **Create fork**
3. This creates your own copy of the codebase under your GitHub account
4. Do **not** rename or restructure any files

---

## Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
2. Click **New app**
3. Under **Repository**, select your forked repo
4. Under **Main file path**, enter:
   ```
   agent_research_app.py
   ```
5. Choose any **App URL** you like (this becomes your study link)
6. Click **Deploy** — wait about 1–2 minutes for it to build

---

## Step 3 — Add Your Secrets

This is the critical step that switches the app to Korean and connects it to the AI.

1. In Streamlit Cloud, open your app and click **⋮ (three dots)** → **Settings** → **Secrets**
2. Paste exactly the following, replacing `your-key-here` with the real API key:

```toml
ANTHROPIC_API_KEY = "your-key-here"
APP_LANG = "ko"
ADMIN_PASSWORD = "choose-your-own-admin-password-here"
```

Pick your own value for `ADMIN_PASSWORD` — this is what protects the admin data-download panel on **your** deployment specifically. It is independent of any other deployment of this app; write it down somewhere safe, since it isn't recoverable from the app itself.

3. Click **Save** — the app will automatically restart in Korean

---

## Step 4 — Verify the App Works

1. Open your app URL in a browser
2. Confirm the page is in **Korean** (welcome screen, buttons, all text)
3. Register a test participant (e.g., ID: `TEST01`) and walk through:
   - Big5 questionnaire appears in Korean ✓
   - Task description appears in Korean ✓
   - Chat with the AI — it should **respond in Korean** ✓
   - Post-task survey appears in Korean ✓
4. Delete the test data: go to your Streamlit Cloud **Files** tab → `research_data/` folder → delete any `TEST01` files

---

## Step 5 — Assign Participant IDs

Participant IDs are **whatever you choose** — the app does not pre-register them. Common formats:

- Sequential: `K001`, `K002`, `K003` …
- Date-based: `KR2026001`, `KR2026002` …

Give each participant their unique ID before they sit down. Write it down — they need it if they need to resume.

---

## Step 6 — Running a Session

Each participant:

1. Opens the app URL on any browser (laptop recommended)
2. Enters their assigned Participant ID on the **신규 참여자 (New Participant)** tab
3. Checks the consent box and clicks **연구 시작 (Begin Study)**
4. Proceeds through the study independently — no researcher action needed

If a participant needs to **pause and resume**:

- They use the **세션 재개 (Resume Session)** tab with their same ID
- Progress is saved automatically at every step

---

## Step 7 — Downloading the Data

1. Open the app URL and click **관리자 (Admin)** at the bottom of the left sidebar
2. Enter the admin password — the one **you** set as `ADMIN_PASSWORD` in Step 3, not a password from the PI
3. Click **Download All Data (ZIP)** to export all participant responses
4. The ZIP contains one folder per participant with:
   - Big5 assessment scores
   - Full chat transcript
   - Post-task survey responses

Send the ZIP file to the PI for merged analysis.

---

## Quick-Reference Checklist

| # | Task | Done? |
|---|------|-------|
| 1 | Fork the GitHub repo | ☐ |
| 2 | Deploy on Streamlit Cloud | ☐ |
| 3 | Add `ANTHROPIC_API_KEY` and `APP_LANG = "ko"` to Secrets | ☐ |
| 4 | Complete a test run and verify Korean language throughout | ☐ |
| 5 | Delete test participant data | ☐ |
| 6 | Prepare participant ID list | ☐ |
| 7 | Begin data collection | ☐ |

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| App is in English, not Korean | Check Secrets — confirm `APP_LANG = "ko"` is saved exactly as shown |
| AI responds in English | Same as above — the language instruction is controlled by `APP_LANG` |
| "LLM Manager initialization failed" error | API key is wrong or missing — re-check `ANTHROPIC_API_KEY` in Secrets |
| Participant cannot resume session | Confirm they are using the exact same Participant ID (case-sensitive) |
| App crashes on startup | Check Streamlit Cloud **Logs** tab and send the error to the PI |

---

> **Important:** Your deployment is completely independent from the English deployment.
> Data collected at your URL is stored only in your app's file system.
> Neither deployment can see the other's data.
