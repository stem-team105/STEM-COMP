# Family AI Game Day — Team 105

A desktop game host built for the Advanced (Champions) track of the 2026 COE STEM Programming with AI Competition.

## Start on Windows

1. On GitHub choose **Code → Download ZIP**, then **Extract all**. Open the inner folder containing this README and the `.bat` files.
2. Double-click **Start-Game-Day.bat**. It creates an isolated `.venv`, installs PySide6 the first time, and opens the modern app.
3. For **built-in local AI**, run **Install-Local-AI.bat** once while connected to the internet. It installs CPU PyTorch, Ultralytics, OpenCV, Vosk and FFmpeg and downloads pretrained vision and English speech models. This can take several minutes, depends on internet speed, and requires disk space for the packages.
4. Reopen **Start-Game-Day.bat**. Select **Local AI** in Match setup. No API key is needed for local mode after setup.

Python 3.11+ (64-bit) with the `py` launcher is required. This is a source distribution, not a packaged Windows EXE. Keep the console open if an error appears.

VS Code terminal after installation:

```powershell
.\.venv\Scripts\python.exe app.py
```

The original minimal Tkinter interface remains available as `py legacy_app.py`.

## Desktop features

- Five-game library, match setup, arena, results/replay, and AI/settings pages.
- Animated page fades, dark/light themes, scrollable panels, and a fixed sidebar.
- Team and individual modes, player roster, rounds, timed turns and tie-break rounds.
- Camera preview and recording **with microphone audio** using Qt Multimedia.
- Local video upload, playback, external opening and turn replay.
- Local AI models with a one-time model download and optional Gemini cloud judge.
- Click-to-calibrate first-frame player positions, goal rectangles, floor markers and delivery zone.
- Timestamped evidence, transcript and possession intervals with explicit review controls.
- Rules-based scores, team standings, football team/player possession estimates and joint MVPs for ties.
- Signed evidence imports/exports, duplicate clip rejection, signed session autosave and resume.
- Preferences save without API keys. Match records and recordings stay in `.local/`.

## Five games

| Game | Mode | Rules summary |
|---|---|---|
| Football | Team | One point per observed goal; possession estimates by player/team; possession MVP |
| Majlis Delivery | Team | Two points per delivery while carried on a tray; minus one per drop |
| Falcon Freeze | Individual | Hold still for three seconds after FREEZE: +1 success, −1 movement |
| Dune Steps | Individual | Follow markers 1–3–2–1–2–3: +1 correct next step, −1 wrong step |
| Family Story Relay | Team | Up to three distinct coherent sentences using family, desert and kindness |

Complete rules and tie handling appear in setup. The four extra games are proposed original designs, distinct from the prohibited example games.

## First real test

1. Start with **two players**, one on each team, one round, and a short fixed-camera football recording. Clearly distinguish people, the ball and both goals. Start with all players standing apart.
2. Set the roster and actual player/goal identification details in Match setup.
3. Choose a clip or record through the arena. Stop the camera after recording before replaying. The host timer does not automatically stop recording.
4. In local mode click **Calibrate local AI**. Click each player at their starting position. Mark the top-left and bottom-right of each goal. **Goal A is the goal where team A scores**, not the goal A defends. Goal rectangles must describe the actual goal mouth.
5. Click **Analyse gameplay**. Local mode proposes candidates; it does not certify goals. Review the video before confirming the checkbox and applying.
6. Check possession identities, team scores and goal timestamps. If any listed event is false, do not confirm the entire report: improve the camera/calibration, retry, or use cloud judging.
7. Capture actual test evidence for the competition. Never present synthetic unit-test fixtures as gameplay results.

For Dune Steps, calibrate all three markers. For local Majlis Delivery, use a **soft sports ball** so the pretrained object class is detectable, and mark the delivery zone. Falcon Freeze requires audible English MOVE/FREEZE cues. Story Relay requires clear English speech from the active player. Record the participant's actual play and avoid setup speech inside the gameplay clip.

## Local AI implementation and limitations

`local_ai.py` runs pretrained YOLO11n object detection, YOLO11n Pose landmarks and the small Vosk English speech model on the user's CPU. Models are **pretrained**, not trained by this team. Sources:

- https://docs.ultralytics.com/models/yolo11/
- https://docs.ultralytics.com/usage/python/
- https://alphacephei.com/vosk/models

Football identity uses host-calibrated positions followed by one-to-one nearest-neighbour matching. Ball proximity estimates possession. Ball-centre entry into a calibrated goal rectangle proposes a goal for host review; it **cannot prove whole-ball crossing of a physical goal line**. Crossing players, occlusion, fast action and a moving camera can cause wrong identities and missed balls. Event confidence values are heuristic, not calibrated accuracy.

Dune Steps uses visible ankle landmarks (or a bounding-box foot estimate) near calibrated markers. Falcon Freeze compares pose movement after speech-recognized cues. Majlis Delivery detects a sports ball entering a target zone; the host must verify tray support and drops. Story Relay finds assigned words in recognized speech; the host must verify coherent distinct sentences. These are experimental observation pipelines with documented limitations. Every local report starts uncertain and requires explicit human review. Approved exports record `human_reviewed: true`.

This prototype does not claim fully autonomous or production-grade sports refereeing.

## Optional cloud mode

Enter your own Gemini API key in AI/settings, then select Cloud AI in Match setup. The key stays in memory. No key is needed in local mode. Never commit or send credentials in chat.

Cloud mode sends the complete selected clip to Google only when Analyse is clicked and needs internet, API permissions, quota and a supported video model. The model name is editable (default `gemini-3.8-flash`). Cloud clips must be MP4, WebM or MOV, up to 14 MB. Both modes limit clips to five minutes. Cloud failures leave scores unchanged.

Reference: https://ai.google.dev/gemini-api/docs/video-understanding

## Evidence, storage and privacy

`core.py` validates event kinds, players, times, numerical bounds and non-overlapping possession intervals. Score totals come from fixed game rules, not a model-supplied total. Evidence below 75% confidence does not score. The same clip cannot be applied twice within a match.

Evidence and sessions use HMAC-SHA256 with `.local/judge.key`. Changed reports or reports from another installation fail verification. The key proves origin within one installation; a person controlling that key/computer can forge reports. Keep the key for local session recovery and never publish it.

Matches autosave after each applied/skipped turn. Use Results → Resume saved match after reopening. Files remain in `.local/sessions`. Original clip paths are retained for replay, so keep the recordings in place. Settings → Open saved sessions folder opens the local workspace folder. Export results before submission.

Obtain participants' permission before recording. Local mode does not intentionally send footage to an AI provider. Model downloads require internet. Exported reports can contain spoken/visual evidence and local file paths; inspect them before sharing.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

20 automated checks pass at this revision: core scoring/validation/signatures and offscreen Qt checks for match setup, scoring, turn advancement, autosave, duplicate rejection and local review gating. Test fixtures are explicitly synthetic; cloud transport is mocked.

The Qt interface was launched and visually inspected in a Linux offscreen environment. **Windows camera/microphone recording, real model inference on footage, model download on the team's connection, and real AI judging accuracy still need student acceptance testing.** Use `TESTING.md` to record actual expected/observed results. No camera or real-game accuracy pass is claimed.

## Submission

Share a Google Drive/OneDrive project folder allowing signed-out viewing and downloading, with source and this README. GitHub is an additional source link. Include dependencies/setup instructions. For an offline evaluation package, include downloaded `models/` separately if permitted by their licences; do not include `.venv`, API keys, `.local` signing keys or private recordings. Public source alone requires first-run package/model downloads.

Submit separate PDFs: exactly 30 presentation slides, six report pages, and all AI conversations; each PDF ≤10 MB. Use real verified results. The demo video must show students using/testing the app and AI. Target confirmed submission by **5:45 PM UAE, 29 October 2026**.

## Licensing

Ultralytics packages/weights have their own AGPL-3.0 or commercial licensing terms; review https://www.ultralytics.com/license before redistribution. Vosk's small English model is listed as Apache 2.0. Qt/PySide6 and FFmpeg have their own applicable licence terms. The team must transparently credit pretrained models and AI-generated assistance.
