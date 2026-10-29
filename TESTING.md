# Lamatna verification

45 automated checks pass in the current revision. Synthetic fixtures check scoring, validation, HMAC signatures, duplicate rejection, explicit local review, turn progression, autosave/resume, game guidance, timer colours, favourites, main Arabic labels, planner/journal persistence, recommendation behaviour, isolated launcher setup/recovery and reuse without network installation. They do not measure gameplay-model accuracy.

The Qt interface was launched offscreen on Linux. Home, teams and results were inspected; plans and notes are collapsed, football leads the home page, and scores lead Results. English/Arabic and light/dark rendering have been inspected. No Windows launcher, desktop-shortcut, camera or microphone pass is claimed from this environment.

## Student acceptance checks

| Test | Expected | Actual / status |
|---|---|---|
| Extract ZIP, double-click Lamatna.bat | Setup window, interface installation if needed, app opens | Pending on Windows |
| Existing installed app | No repeated package/model download | Automated recovery/reuse logic passed; Windows pending |
| Desktop shortcut | Lamatna opens from its actual folder, including paths with spaces | Pending on Windows |
| Settings → Set up offline game support | Missing packages install, model files download, app reopens | Pending on team connection |
| Camera + microphone recording | Playable clip with audible instructions | Pending |
| Football: one visible goal | Correct candidate team +1, timestamp and reason, host review required | Pending real model/footage |
| Football: shot misses/obscured ball | No invented goal; uncertainty stated | Pending |
| Football: players exchange possession | Plausible intervals and correct identity/team totals/MVP | Pending |
| Calibration | Correct player anchors, scoring-team goal rectangles and markers | Pending |
| Majlis Delivery: delivery + drop | +1 net after host checks tray support and drop | Pending |
| Falcon Freeze: success + movement | 0 net with clear audible English cues | Pending |
| Dune Steps: six correct markers | +6 | Pending |
| Family Story Relay | Up to +3 for distinct coherent assigned-word sentences, checked by host | Pending |
| Review unchecked | Local suggestions cannot change scores | Automated synthetic check passed |
| Duplicate clip / altered signature | Duplicate scoring / modified evidence rejected | Automated synthetic checks passed |
| Finish and restart | Saved match restores points, roster, turn and history | Automated synthetic check passed; Windows pending |
| Family sports flow | Home → Teams → Play → Results, all five games available | Automated/offscreen checks passed; Windows pending |
| Arabic switch | Main labels and RTL change, logo remains visible | Automated/offscreen checks passed; full translation not claimed |
| Peak RAM and processing time | Record actual device/profile/clip/duration/peak-memory observations | Pending real hardware |
| Public prototype and video links | Play/view/download signed out | Pending before submission |

## Limits to explain

Local vision/speech integrates pretrained models, not models trained by the team. Its heuristic event estimates are experimental; calibrated confidence or autonomous referee accuracy is not claimed. Verify goal crossing, player identity, tray support/drops and sentence coherence against the actual video. The small recommendation model uses disclosed synthetic seed examples and explicit local feedback.

The host must stop recording; the timer does not automatically cut a clip. Optional cloud review needs the family's own key, internet and quota. Local review needs the one-time package/model installation but no API key afterward. HMAC detects changes relative to one installation's key; it does not prevent forgery by someone who controls that computer/key.

Use real student footage and observed results in the submission. Keep untested rows pending until actually checked.
