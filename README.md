# JARVIS Neural Gesture Control OS 🖐️💻

Control your Windows PC / Laptop mouse, clicks, scrolling, and audio volume using your webcam and real-time hand gestures.

## 📁 Repository Structure

```
Gesture-Control/
├── RUN_GESTURE_CONTROL.bat         # One-click launcher for the gesture control system
└── GESTURE CONTROL/                # Main application folder
    ├── scifi_gesture_controller.py # Neural gesture controller engine
    ├── gesture_mouse_infinite.py   # High-precision virtual mouse controller
    ├── virtual_mouse.py            # Basic virtual mouse script
    ├── volume_controller.py        # Hand gesture volume controller
    ├── hand_tracking.py            # MediaPipe hand tracking pipeline
    ├── hand_landmarker.task        # MediaPipe landmarker vision model
    ├── requirements.txt            # Python dependencies
    ├── START_GESTURE_CONTROL.bat   # Startup batch script
    ├── STOP_GESTURE_CONTROL.bat    # Process terminator batch script
    ├── reset_desktop_icons.bat     # Windows icon layout helper
    ├── turn_off_camera.bat         # Camera release helper
    ├── MANUAL.md                   # Full user guide & gesture manual
    ├── README.md                   # Application-specific documentation
    └── DESKTOP FILES/              # Supplementary scripts & utilities
```

## 🚀 Quick Start

### 1. Requirements
Ensure you have Python 3.9+ installed. Install the dependencies inside the `GESTURE CONTROL` directory:

```bash
cd "GESTURE CONTROL"
pip install -r requirements.txt
```

### 2. Launching
Double-click `RUN_GESTURE_CONTROL.bat` from the root directory or run:

```bash
.\RUN_GESTURE_CONTROL.bat
```

## 🖐️ Gesture Reference Guide

| Action | Hand Gesture |
| :--- | :--- |
| **Move Cursor** | Point **Index Finger UP** (keep other fingers down). Cursor smoothly follows your fingertip. |
| **Left Click** | **Pinch Index + Thumb** together. |
| **Click & Drag** | **Hold Index + Thumb pinch** for >0.4 seconds, move hand, release pinch to drop. |
| **Right Click** | **Pinch Middle Finger + Thumb** together. |
| **Scroll Up / Down** | **Index & Middle Fingers UP** (spread apart) — move hand up/down to scroll. |
| **Volume Up / Down** | Thumb & Index distance adjustment in volume mode. |
| **Quit** | Press <kbd>q</kbd> or <kbd>ESC</kbd> on your keyboard. |
