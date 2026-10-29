# Lamatna — Team 105

A family-first desktop game host built for the Advanced (Champions) track of the 2026 COE STEM Programming with AI Competition.

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

## Daily family features

Lamatna (لمّتنا) follows Sila's ivory, palm-green and brass visual direction with an Emirati courtyard illustration and a new transparent palm-and-home logo. The app and window icon use the new artwork in `assets/lamatna-mark.svg` and `.png`. This is Lamatna's own implementation; no NoteMind application code or assets are imported.

- **Today, together:** select energy, indoor/outdoor space and available time for a game recommendation.
- **Our next gathering:** add dated family plans and tick them off when done. These are local plans, not background notification/reminder services.
- **Our memories:** save Arabic/English text notes and revisit them in Moments.
- **We enjoyed this:** after a completed game, explicit feedback adapts future game suggestions.
- **Arabic / English:** a header control switches main labels and mirrors layout for Arabic. Detailed rules, some secondary controls and model evidence remain English; English is the supported speech-recognition language.

Planner, journal and feedback are saved in `.local/family.sqlite3`. Game sessions keep the same signed storage as previous versions. `Update-RALLY.bat` is retained for compatibility; `Update-Lamatna.bat` is the current named updater. Neither deletes saved data, downloaded models or installed packages.

The new recommendation model is a categorical Naive Bayes classifier fitted on 20 disclosed synthetic seed examples plus explicit local family feedback. It is small and runs entirely in the Python standard library. It is separate from the upstream-pretrained gameplay vision and speech models. Read `MODEL-CARD.md` for data, limitations and training attribution.

## Everyday family flow

The main interface uses plain family language. It opens on Home with a quick game suggestion, colourful game cards, favourites and game filters. Select a game to see a pre-play suggestion, equipment, safety tip and a blue duration badge. Family names and teams are edited in a simple table. The Play page contains a timer, camera and results review. Moments contains scores, replay and saved games. Settings lives in the top bar.

The sidebar is removed. Four bottom tabs provide tablet-style navigation on a desktop. Light/dark appearance and reduced animation are supported. Timer digits turn amber at 15 seconds and red at five, with text and a progress bar alongside the colour.

Local processing is the default. The family does not select a model or enter a key in the normal flow. Optional cloud controls are hidden under Settings → Advanced connection options. The app asks for a one-time camera-view calibration when a local game requires it. Uncertain local points still require honest host review.

## Updating without repeating setup

Close the app, place `Update-Lamatna.bat` in the existing extracted application folder, and run it. It downloads source from this team's public GitHub repository and updates app files while preserving `.venv`, `models/` and `.local/`. Reopen `Start-Game-Day.bat`. The same folder retains your installed dependencies and saved games.

## Desktop features

- Game home, family setup, play, moments and settings pages.
- Animated page fades, dark/light themes, reduced motion, scrollable panels and compact bottom navigation.
- Team and individual modes, player roster, rounds, timed turns and tie-break rounds.
- Camera preview and recording **with microphone audio** using Qt Multimedia.
- Local video upload, playback, external opening and turn replay.
- On-device models with a one-time download; optional cloud connection lives in advanced settings.
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
4. In local mode click **Set up camera view** (or follow the prompt when finding results). Click each player at their starting position. Mark the top-left and bottom-right of each goal. **Goal A is the goal where team A scores**, not the goal A defends. Goal rectangles must describe the actual goal mouth.
5. Click **Find this round’s results**. Local mode proposes candidates; it does not certify goals. Review the video before confirming the checkbox and applying.
6. Check possession identities, team scores and goal timestamps. If any listed event is false, do not confirm the entire report: improve the camera/calibration, retry, or use cloud judging.
7. Capture actual test evidence for the competition. Never present synthetic unit-test fixtures as gameplay results.

For Dune Steps, calibrate all three markers. For local Majlis Delivery, use a **soft sports ball** so the pretrained object class is detectable, and mark the delivery zone. Falcon Freeze requires audible English MOVE/FREEZE cues. Story Relay requires clear English speech from the active player. Record the participant's actual play and avoid setup speech inside the gameplay clip.

## Efficiency profiles

Settings offers Eco (2 sampled frames/second at 384-pixel inference size, up to two CPU threads), Balanced (4 at 512, up to four threads) and Detail (6 at 640, up to four threads). Balanced is the default. Lower processing can miss fast or small events; no profile guarantees accuracy.

The application does not load a neural model just to browse games. Speech-only turns avoid importing PyTorch. Speech runs before vision on freeze turns rather than holding both models together. Video frames are decoded sequentially and file hashes are streamed instead of loading entire recordings into memory. One nano vision model is referenced per task and released afterward. Libraries/allocators can retain memory; **peak RAM has not been benchmarked on the team's laptop**. These changes reduce unnecessary work but do not promise a fixed memory ceiling.

## Local AI implementation and limitations

`local_ai.py` runs pretrained YOLO11n object detection, YOLO11n Pose landmarks and the small Vosk English speech model on the user's CPU. Models are **pretrained**, not trained by this team. Sources:

- https://docs.ultralytics.com/models/yolo11/
- https://docs.ultralytics.com/usage/python/
- https://alphacephei.com/vosk/models

Football identity uses host-calibrated positions followed by one-to-one nearest-neighbour matching. Ball proximity estimates possession. Ball-centre entry into a calibrated goal rectangle proposes a goal for host review; it **cannot prove whole-ball crossing of a physical goal line**. Crossing players, occlusion, fast action and a moving camera can cause wrong identities and missed balls. Event confidence values are heuristic, not calibrated accuracy.

Dune Steps uses visible ankle landmarks (or a bounding-box foot estimate) near calibrated markers. Falcon Freeze compares pose movement after speech-recognized cues. Majlis Delivery detects a sports ball entering a target zone; the host must verify tray support and drops. Story Relay finds assigned words in recognized speech; the host must verify coherent distinct sentences. These are experimental observation pipelines with documented limitations. Every local report starts uncertain and requires explicit human review. Approved exports record `human_reviewed: true`.

This prototype does not claim fully autonomous or production-grade sports refereeing.

## Optional cloud mode

Enter your own Gemini API key and choose the cloud connection under Settings → Advanced connection options before starting a new match. The key stays in memory. No key is needed in local mode. Never commit or send credentials in chat.

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

40 automated checks pass at this revision: core scoring/validation/signatures and offscreen Qt checks for match setup, scoring, turn advancement, autosave, duplicate rejection, local review gating, favourites, pre-play guidance, timer colours, saved-match restoration, efficient hashing and speech-only execution without a vision import, planner/journal persistence, feedback deduplication, recommendation adaptation and Arabic label switching with the logo preserved. Test fixtures are explicitly synthetic; cloud transport is mocked.

The Qt interface was launched and visually inspected in a Linux offscreen environment at 1240×900 and 850×720, in light and dark modes. **Windows camera/microphone recording, real model inference on footage, model download on the team's connection, and real AI judging accuracy still need student acceptance testing.** Use `TESTING.md` to record actual expected/observed results. No camera or real-game accuracy pass is claimed.

## Submission

Share a Google Drive/OneDrive project folder allowing signed-out viewing and downloading, with source and this README. GitHub is an additional source link. Include dependencies/setup instructions. For an offline evaluation package, include downloaded `models/` separately if permitted by their licences; do not include `.venv`, API keys, `.local` signing keys or private recordings. Public source alone requires first-run package/model downloads.

Submit separate PDFs: exactly 30 presentation slides, six report pages, and all AI conversations; each PDF ≤10 MB. Use real verified results. The demo video must show students using/testing the app and AI. Target confirmed submission by **5:45 PM UAE, 29 October 2026**.

## Source layout

`app.py` launches Lamatna; `studio.py` builds the family-facing experience; `ui_kit.py` holds shared appearance and vector game illustrations; `session_ui.py` retains the validated match/evidence engine and the earlier interface. `local_ai.py` runs local observation pipelines; `judge.py` handles the optional cloud connection; `core.py` defines game rules, validation and signatures. `assets/` contains Lamatna’s transparent courtyard-and-palm identity. Figma reached the connected Starter-plan tool limit during this revision, so the new branding and illustration were completed as native vector/Qt assets.

Visual direction: warm ivory, palm green and quiet brass accents. The application assets are included in this repository.

`family.py`, `daily_features.py`, `recommendation.py` and `locale_ui.py` implement the daily family features, lightweight recommendations and main Arabic labels. `VIDEO-PLAN.md` contains the two-minute demonstration outline.

## Licensing

Ultralytics packages/weights have their own AGPL-3.0 or commercial licensing terms; review https://www.ultralytics.com/license before redistribution. Vosk's small English model is listed as Apache 2.0. Qt/PySide6 and FFmpeg have their own applicable licence terms. The team must transparently credit pretrained models and AI-generated assistance.
