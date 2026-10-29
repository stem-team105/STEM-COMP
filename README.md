# Family AI Game Day — Team 105

A Python desktop prototype for the Advanced (Champions) track of the 2026 COE STEM Programming with AI Competition.

## Run on Windows

1. Download this repository using **Code → Download ZIP**, then **Extract all**.
2. Open the extracted folder in VS Code.
3. Open a terminal in that folder and run `py app.py`. Alternatively double-click `Start-Game-Day.bat`.
4. Python 3.11 or newer with Tkinter is required. There are **no pip dependencies**. If `py` is unavailable, use `python app.py`.
5. Enter your own Gemini API key in the app's Setup tab. Get/manage a key at https://aistudio.google.com/apikey . The account needs API access and available quota; usage may incur provider charges. Do not send keys in chat or commit them.
6. The default video-capable model is `gemini-3.8-flash`; the model field is editable if your account offers a different compatible Gemini model. `GEMINI_API_KEY` and `GEMINI_MODEL` environment variables are also supported.

## Play and demonstrate

- Select one of five games, set 1–10 rounds, and enter unique player IDs with team names, one per line (`P1, A`). Team games require exactly two teams; individual games rank players independently.
- Replace the identification guidance with **actual** shirt colours/numbers. For football, explicitly describe both goal locations and which team attacks which goal. Use distinguishable numbered shirts, a visible ball, a fixed camera and both goals in view.
- Click **Start new game**. Non-football turns last 30 seconds. The football host timer defaults to 60 seconds. The timer guides the human host; it does not start or stop a camera.
- Record gameplay **with audio** using a phone or Windows Camera. This prototype uses the brief's **upload option**, not direct camera capture. Keep clips short (preferably 15–30 seconds for the first test), at most 14 MB, and at most five minutes. Transfer the recording to the PC.
- Choose the clip and click **Judge video + audio**. The complete clip is sent to Google's Gemini API. Analysis runs on a worker thread so the interface remains responsive.
- Review timestamps, descriptions, confidence estimates, limitations and possession intervals. Uncertain results cannot be applied; improve the view/audio and try again. Confidence estimates are model self-assessments, not measured accuracy.
- Click **Apply verified evidence & next turn**. The app calculates points from fixed rules; it does not accept a model-supplied total. Events below 75% confidence do not score. Duplicate clips cannot score twice within the same game.
- Results include individual scores, team totals, football team possession and possession MVP (joint MVPs for ties). Finish all turns and use **Extra round / tie-break** if needed.
- Export results and evidence before starting another game or closing the app. Match state is in memory; automatic resume is not implemented.

## Five games

| Game | Mode | Scoring |
|---|---|---|
| Football | Team | +1 per observed goal; possession estimates by player and team; MVP by observed possession |
| Majlis Delivery | Team | +2 per delivery on a tray, −1 per drop |
| Falcon Freeze | Individual | +1 per complete 3-second freeze, −1 for movement during a freeze |
| Dune Steps | Individual | Sequence 1–3–2–1–2–3; +1 correct next step, −1 wrong step |
| Family Story Relay | Team | Up to 3 points per turn for distinct coherent sentences using family, desert and kindness |

Full rules, penalties and tie instructions are displayed before play. The four extra games are proposed team designs, not the four prohibited example games from the brief. The human host supplies movement/freeze cues and manages safe play.

## AI and report integrity

`judge.py` submits native video/audio to Gemini's `generateContent` endpoint and requests structured evidence. `core.py` validates players, event types, timestamps, numerical bounds and non-overlapping possession intervals, then calculates scores. Football uses multimodal model observation, **not** a trained custom object detector or frame-accurate sports tracker. Fast action, occlusions and similar shirts can cause misses; real footage tests are required.

Reports are signed with HMAC-SHA256 using an installation-local random secret in `.local/judge.key`. Import checks authenticity and setup compatibility before allowing application. Edited reports and reports from another installation are rejected. Keep the same local key for report reuse; do not publish it. This is a local tamper check, not independent certification: someone controlling the computer/key can forge a report.

API keys stay in application memory. Videos are read from the chosen local path; the app does not copy them into the repository. Only clicking Judge sends the selected footage to Google. Obtain participants' permission. Exported reports contain player IDs and spoken/visual evidence; review before sharing.

## Tests and current verification

Run `py -m unittest -v` from the project folder.

Automated tests use explicitly synthetic fixtures and mocked HTTP transport. They verify score calculation, confidence filtering, uncertain-result rejection, report tamper detection, invalid evidence rejection, and API response parsing. **They do not prove video-analysis accuracy.** Real API calls, real footage and Windows GUI testing must be completed with the team's account and recordings. No real-game test results are claimed yet.

Record expected and actual outcomes in `TESTING.md`. Verify at least one goal, a no-goal clip, possession attribution, one trial per original game, an uncertain/occluded clip and a repeated import.

## Files

- `app.py`: Tkinter host interface, timer, turn/round flow, evidence review and exports.
- `core.py`: rules, validation, scoring and report signatures.
- `judge.py`: video/audio API request and response handling.
- `test_core.py`: automated unit tests using synthetic fixtures.
- `TESTING.md`: real-world test checklist and limitations.

## Submission

Share a project folder through Google Drive or OneDrive with viewing and downloading enabled, including this source and README. A public GitHub repository is an additional source link. Do not include API keys, `.local`, private recordings or account credentials. Test the folder link while signed out.

Required separate PDFs: 30-slide presentation, 6-page technical report, all AI conversations; each ≤10 MB. Use actual verified results in the report and presentation. The demonstration video should show students testing the app and AI on real gameplay. Target confirmed submission by **5:45 PM UAE, 29 October 2026**.

Reference: https://ai.google.dev/gemini-api/docs/video-understanding
