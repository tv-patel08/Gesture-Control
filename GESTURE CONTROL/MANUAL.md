# 🛸 JARVIS Neural Gesture OS — Complete User Manual Guide

Welcome to the definitive user manual for the **JARVIS Neural Gesture OS (Continuous Stream Edition)**. This system allows you to control your PC/laptop with zero-lag index finger tracking, full gesture automation, and an interactive sci-fi HUD.

---

## 📋 Table of Contents
1. [Quick Start & Launch](#1-quick-start--launch)
2. [How the New Engine Works](#2-how-the-new-engine-works)
3. [Complete Gesture Directory (All 11 Features)](#3-complete-gesture-directory-all-11-features)
   - [1. Laser Cursor Movement](#1-laser-cursor-movement)
   - [2. Kinetic Left Click](#2-kinetic-left-click)
   - [3. Rapid Double Click](#3-rapid-double-click)
   - [4. Force-Drag & Drop](#4-force-drag--drop)
   - [5. Tactical Right Click](#5-tactical-right-click)
   - [6. Quantum Kinetic Scroll](#6-quantum-kinetic-scroll)
   - [7. Holographic Zoom In / Out](#7-holographic-zoom-in--out)
   - [8. Holographic Master Volume Slider](#8-holographic-master-volume-slider)
   - [9. Instant Windows Screenshot / Snip](#9-instant-windows-screenshot--snip)
   - [10. Minimize All / Show Desktop](#10-minimize-all--show-desktop)
   - [11. Media Play / Pause Toggle](#11-media-play--pause-toggle)
4. [Holographic HUD Decoder](#4-holographic-hud-decoder)
5. [Live In-App Sensitivity Tuning](#5-live-in-app-sensitivity-tuning)
6. [Safety Protocols & Instant Camera Shutdown](#6-safety-protocols--instant-camera-shutdown)
7. [Pro Tips & Troubleshooting](#7-pro-tips--troubleshooting)

---

## 1. Quick Start & Launch

### Prerequisites:
Make sure your terminal is inside the project folder:
```powershell
cd C:\Users\tirth\.gemini\antigravity\scratch\gesture-control-pc
```

### Launch Command:
```powershell
python scifi_gesture_controller.py
```
*(Or `.\venv\Scripts\python.exe scifi_gesture_controller.py`)*

---

## 2. How the New Engine Works

* **Continuous Video Stream Engine:** Uses MediaPipe’s temporal tracking engine (`VisionRunningMode.VIDEO`) with continuous millisecond timestamps. Once your hand is in view, the model locks on and **never drops into STANDBY during movement**.
* **Unblocked Cursor Pipeline:** Cursor movement runs continuously on every single frame following your **Index Fingertip (#8)**. Gestures (like clicks and drags) execute in parallel without freezing mouse movement.
* **Dual Windows Hardware Driver:** Uses both Windows kernel `SetCursorPos` and hardware-queue `mouse_event(0x8001)` to ensure instantaneous, reliable cursor movement across all monitors and DPI scaling settings.

---

## 3. Complete Gesture Directory (All 11 Features)

---

### 1. Laser Cursor Movement
* **Hand Posture:** Point your **Index Finger** forward naturally (like a laser pointer).
* **Tracking Target:** Locked directly to your **Index Fingertip (#8)**.
* **How It Moves:** Wherever you point in the camera feed, the cursor snaps to that exact position on your display with **zero reaction lag**.
* **HUD Indicator:** `INDEX TRACKING` in **Neon Cyan**.

---

### 2. Kinetic Left Click
* **Hand Posture:** Tap your **Thumb Tip and Index Fingertip** together quickly and release (a standard pinch).
* **Action:** Fires an instantaneous Windows left mouse click.
* **Visual Effect:** A glowing **Green Kinetic Shockwave** ripples from your fingertip.
* **HUD Indicator:** `LEFT CLICK` in **Neon Green**.

---

### 3. Rapid Double Click
* **Hand Posture:** Double-tap your **Thumb + Index pinch twice rapidly** (within 0.32 seconds).
* **Action:** Double-clicks to open desktop icons, launch applications, or open folders.
* **HUD Indicator:** `DOUBLE CLICK` in **Neon Cyan**.

---

### 4. Force-Drag & Drop
* **Hand Posture:** Pinch **Thumb + Index together and HOLD** for more than 0.35 seconds.
* **Action:** Locks the left mouse button down (`mouseDown`). Move your hand across the screen to drag files, select text, or move application windows.
* **How to Drop:** Simply **release the pinch** (open your fingers) to drop the item.
* **Visual Effect:** A glowing **Neon Magenta laser tether** links your thumb and index fingertips.
* **HUD Indicator:** `FORCE-DRAG` in **Neon Magenta**.

---

### 5. Tactical Right Click
* **Hand Posture:** Pinch your **Thumb Tip and Middle Fingertip** together.
* **Action:** Opens the Windows right-click context menu.
* **Visual Effect:** An **Orange Kinetic Shockwave** expands from your hand.
* **HUD Indicator:** `RIGHT CLICK` in **Neon Orange**.

---

### 6. Quantum Kinetic Scroll
* **Hand Posture:** Raise your **Index and Middle fingers UP (✌️)** (peace sign, slightly spread apart). Keep ring and pinky fingers folded.
* **Action:**
  * Move hand **ABOVE** the camera center line $\rightarrow$ Scrolls **UP**.
  * Move hand **BELOW** the camera center line $\rightarrow$ Scrolls **DOWN**.
* **HUD Indicator:** `SCROLL MODE` in **Neon Magenta**.

---

### 7. Holographic Zoom In / Out
* **Hand Posture:** In Scroll Mode (Index + Middle fingers UP), **spread your Thumb wide** as well.
* **Action:**
  * Move hand **UP** $\rightarrow$ Zooms **IN** (`Ctrl + Scroll Up`).
  * Move hand **DOWN** $\rightarrow$ Zooms **OUT** (`Ctrl + Scroll Down`).
* **Compatible With:** Web browsers (Chrome, Edge), Google Maps, PDF readers, image viewers, and Word.
* **HUD Indicator:** `HOLOGRAPHIC ZOOM` in **Neon Yellow**.

---

### 8. Holographic Master Volume Slider
* **Hand Posture:** Extend your **Thumb and Pinky fingers WIDE** while keeping index, middle, and ring fingers folded (the classic "Shaka" / Spider-Man web gesture 🤙).
* **Action:** A vertical **Neon Yellow Volume Slider** appears on the right edge of your camera window:
  * Spread Thumb & Pinky **further apart** $\rightarrow$ Increases Windows volume.
  * Bring Thumb & Pinky **closer together** $\rightarrow$ Decreases Windows volume.
* **HUD Indicator:** `HOLOGRAPHIC VOLUME` in **Neon Yellow** with a real-time percentage readout (`0% - 100%`).

---

### 9. Instant Windows Screenshot / Snip
* **Hand Posture:** Raise your **Pinky Finger ALONE** (keep thumb, index, middle, and ring fingers curled down).
* **Hold Time:** Hold for 0.35 seconds.
* **Action:** Triggers a camera shutter flash on the HUD and immediately launches the **Windows Snipping Tool (`Win + Shift + S`)** so you can crop and capture any part of your screen.
* **HUD Indicator:** `PINKY // SCREENSHOT SNIP` in **Pure White**.

---

### 10. Minimize All / Show Desktop
* **Hand Posture:** Form a tight **Closed Fist (✊)** (all 5 fingertips curled tightly toward your palm).
* **Hold Time:** Hold for 0.45 seconds.
* **Action:** Instantly minimizes all open windows to reveal your clean desktop (`Win + D`). Making the fist again restores all windows.
* **Visual Effect:** An expanding **Red Shockwave** radiates from your hand.
* **HUD Indicator:** `FIST // SHOW DESKTOP` in **Neon Red**.

---

### 11. Media Play / Pause Toggle
* **Hand Posture:** Make a **Thumbs-Up (👍)** (thumb pointing straight up, all other fingers curled down).
* **Hold Time:** Hold for 0.40 seconds.
* **Action:** Toggles Play/Pause for any active media stream (works globally with **Spotify, YouTube, VLC, Netflix, Apple Music**, etc.).
* **HUD Indicator:** `THUMBS UP // PLAY/PAUSE` in **Neon Green**.

---

## 4. Holographic HUD Decoder

Your HUD window displays a high-tech tactical overlay with real-time diagnostics:

```text
┌────────────────────────────────────────────────────────┐
│  JARVIS // ZERO-LAG TRACKING ENGINE                    │
│  FPS: 60 | SENS: 100% (+/-)                            │  <-- Telemetry Glass Panel
│  MODE: INDEX TRACKING                                  │
└────────────────────────────────────────────────────────┘

  ┌─                                                  ─┐
  │                                                    │  <-- Expanded Sensing Boundary
  │                       ◎                            │      (Covers 90% of camera frame)
  │                  (Index Tip)                       │
  │                                                    │
  └─                                                  ─┘
                                                          [===]  <-- Live Volume Gauge
                                                          [80%]      (Visible in Shaka Mode)
```

### Color Codes
| Color | Mode Name | Meaning |
| :---: | :--- | :--- |
| **Cyan** | `INDEX TRACKING` | Active pointer tracking; cursor follows index fingertip. |
| **Green** | `LEFT CLICK` | Single left mouse click executed. |
| **Cyan** | `DOUBLE CLICK` | Rapid double-click executed. |
| **Magenta** | `FORCE-DRAG` | Left mouse button locked down for dragging items. |
| **Orange** | `RIGHT CLICK` | Context menu opened. |
| **Magenta** | `SCROLL MODE` | Kinetic page scrolling active. |
| **Yellow** | `HOLOGRAPHIC ZOOM` | Zooming page/document. |
| **Yellow** | `HOLOGRAPHIC VOLUME`| Master volume slider active. |
| **Red** | `SHOW DESKTOP` | All windows minimized via fist. |
| **White** | `SCREENSHOT SNIP` | Screen snip initiated with shutter flash. |
| **Grey** | `STANDBY` | Hand is currently out of camera view. |

---

## 5. Live In-App Sensitivity Tuning

You never need to edit Python code to change cursor speed. While the HUD window is active, press these keys on your keyboard:

* <kbd>+</kbd> or <kbd>=</kbd> $\rightarrow$ **Increase Sensitivity:** Expands cursor travel for smaller physical finger movements.
* <kbd>-</kbd> or <kbd>_</kbd> $\rightarrow$ **Decrease Sensitivity:** Gives you higher micro-precision for fine clicking.
* <kbd>r</kbd> $\rightarrow$ **Reset Baseline:** Restores sensitivity back to the 100% factory default.

---

## 6. Safety Protocols & Instant Camera Shutdown

* **Instant Hardware Cut-off:** Uses direct Windows DirectShow (`cv2.CAP_DSHOW`), immediately cutting power to the webcam sensor and LED the moment you exit.
* **Anti-Stuck Click Shield:** Even if you terminate the program in the middle of dragging a file, the script automatically executes `mouseUp` so files never remain stuck.
* **3 Safe Ways to Stop:**
  1. Press <kbd>q</kbd> or <kbd>ESC</kbd> on your keyboard.
  2. Click the window's close **[X]** button.
  3. Press <kbd>Ctrl</kbd> + <kbd>C</kbd> in your terminal.
* **1-Click Emergency Release:** If any other Windows application ever locks your camera in the future, double-click [`turn_off_camera.bat`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/turn_off_camera.bat) in your folder to force-release it in under 1 second.

---

## 7. Pro Tips & Troubleshooting

1. **Reaching the Taskbar Easily:**
   * The bottom mapping is **asymmetric** — the taskbar at the bottom of your screen is reached while your hand is still in the comfortable upper-middle area of the camera frame. You **never need to dip your hand down toward your desk**.
2. **Smooth Pointing:**
   * Rest your elbow on your desk and move your hand using your **wrist**. This gives you effortless, fatigue-free control for hours.
3. **Pinching Precision:**
   * Bring your thumb and index fingertip together cleanly. Because the cursor follows your index finger tip, aim first, then tap your thumb to click.
