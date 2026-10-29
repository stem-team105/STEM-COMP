# Lamatna — model and training disclosure

## Gameplay models

- YOLO11n: pretrained object detector used to find people and sports balls.
- YOLO11n Pose: pretrained body-landmark estimator used for movement and steps.
- Vosk small English: pretrained offline speech recognizer used for spoken cues and story words.

These models were trained by their upstream providers, **not by Team 105**. We integrate them with calibration, event rules, evidence validation and host review. No custom football-training run is claimed. Fast action and overlapping players can produce incorrect results; recorded evidence must be reviewed. Speech challenges currently use English, even with Arabic interface labels.

## Daily game recommender

`recommendation.py` implements a categorical Naive Bayes classifier in the Python standard library. Fitting estimates class and feature counts with Laplace smoothing. Three input categories are energy, indoor/outdoor space and available time. The label is one of the five games. Indoor recommendations exclude football as a suitability constraint.

The initial training set contains **20 hand-authored synthetic preference examples** in `SEEDS`. These are prototype assumptions, not observations from real families and not evidence of general accuracy. There is no external validation dataset or claimed accuracy percentage. The classifier is fitted when a suggestion is requested; this small count-based fit does not require large weights or a GPU.

After a completed match, explicit **We enjoyed this** feedback adds a locally stored labelled example. Each session contributes at most once. Feedback never leaves the device in this workflow. A unit test demonstrates that repeated positive context-specific feedback can change the recommended game; that is a functional test, not a real-world quality benchmark.

## Efficiency and independent operation

The recommender, planner and journal use no cloud service. Gameplay models require a one-time package/model download, then local analysis needs no API key. Eco/Balanced/Detail settings sample 2/4/6 video frames per second with 384/512/640-pixel inference sizes. One vision model is used per task, speech precedes vision on freeze turns, and video hashing/decoding avoids loading whole clips into RAM. Runtime libraries can retain memory: peak RAM and real-game accuracy have not been measured on the team's laptop.
