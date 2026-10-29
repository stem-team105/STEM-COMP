# Real gameplay acceptance tests

Status: **pending** until students execute with an enabled API key and real recordings.
Do not replace pending with passed without checking the actual result.

| Test | Expected | Actual / status |
|---|---|---|
| Launch on Windows with `py app.py` | All three tabs usable | Pending |
| Football: one visible goal | Correct team +1, timestamp and reason | Pending |
| Football: shot misses | No goal awarded | Pending |
| Football: two numbered players exchange possession | Plausible intervals, correct team totals and MVP | Pending |
| Football: obscured goal or ball | Uncertainty/limitation, no invented goal | Pending |
| Majlis Delivery: one delivery and one drop | +1 net | Pending |
| Falcon Freeze: successful freeze then movement | 0 net | Pending |
| Dune Steps: six correct targets | +6 | Pending |
| Family Story Relay: three valid distinct word sentences | +3 | Pending |
| Unclear speech / wrong words | No unsupported story points | Pending |
| Repeat same clip | Cannot apply twice in same game | Pending |
| Edit exported signed report | Import rejected | Pending |
| No API key / network / quota | Useful error; scores unchanged | Pending |
| Full round and tied game | Next turns, final results, extra round | Pending |
| Export and inspect results JSON | Scores plus evidence retained | Pending |

## Honest limitations

- Upload-only capture workflow; use a phone or Windows Camera to record audio and video.
- Cloud inference requires an enabled Gemini account, quota, internet, and a supported video model.
- Multimodal estimates can miss rapid ball movement or confuse identities. No precision tracking claim.
- Local HMAC prevents accidental/unauthorised editing without the secret, not a malicious machine owner.
- Match state is not automatically saved. Export before closing.
- The timer is host guidance; the host must stop recording and obey the game time limit.

## Modern desktop revision

20 automated checks passed, including six offscreen Qt behaviour checks. These do not replace Windows hardware/footage tests.

| Additional acceptance test | Expected | Actual / status |
|---|---|---|
| Run Start-Game-Day.bat in fresh extracted folder | Creates venv, installs UI and launches | Pending on Windows |
| Install-Local-AI.bat | CPU packages + all three pretrained models ready | Pending on team connection |
| Camera preview and recording | MP4 recording includes microphone audio | Pending |
| First-frame calibration | Clicks save correct normalized player/goal/marker positions | Pending |
| Local football inference | Candidate goals/possession shown for review | Pending real model/footage |
| Local approval | No score until host confirms; human_reviewed recorded | Automated synthetic check passed |
| Restart and resume | Session scores/history/round restored | Pending Windows user test |
| Dark/light themes and small window | Readable, scrollable controls | Visually inspected offscreen; Windows pending |
