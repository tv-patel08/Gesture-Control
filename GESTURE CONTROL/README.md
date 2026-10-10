# AI Hand Gesture PC Controller 🖐️💻

Control your Windows PC / Laptop mouse, clicks, scrolling, and audio volume using your webcam and real-time hand gestures.

---

## 📁 Project Structure

- [`hand_tracking.py`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/hand_tracking.py): Core hand landmark detector using Google MediaPipe (tracks 21 hand joints).
- [`virtual_mouse.py`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/virtual_mouse.py): Complete virtual mouse (cursor movement, left click, right click, dragging, scrolling).
- [`volume_controller.py`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/volume_controller.py): Audio control using thumb-to-index finger distance and mute toggle.
- [`requirements.txt`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/requirements.txt): List of dependencies.

---

## 🚀 Getting Started

### 1. Install Dependencies
Open PowerShell or your terminal in this directory and run:

```powershell
py -m pip install -r requirements.txt
```

### 2. Run the Virtual Mouse
```powershell
py virtual_mouse.py
```

### 3. Run the Volume Controller
```powershell
py volume_controller.py
```

---

## 🖐️ Gesture Reference Guide

### Virtual Mouse Controls

| Action | Hand Gesture |
| :--- | :--- |
| **Move Cursor** | Point **Index Finger UP** (keep other fingers down). Cursor smoothly follows your fingertip. |
| **Left Click** | **Pinch Index + Thumb** together. |
| **Click & Drag** | **Hold Index + Thumb pinch** for >0.4 seconds, move hand, release pinch to drop. |
| **Right Click** | **Pinch Middle Finger + Thumb** together. |
| **Scroll Up / Down** | **Index & Middle Fingers UP** (spread apart) — move hand up/down to scroll. |
| **Quit** | Press <kbd>q</kbd> or <kbd>ESC</kbd> on your keyboard. |

### Volume Controller Controls

| Action | Hand Gesture |
| :--- | :--- |
| **Volume Up** | Spread Thumb and Index wide apart |
| **Volume Down** | Bring Thumb and Index close together |
| **Mute / Unmute** | Raise Pinky Finger alone |

---

## ⚙️ Customization & Tuning

In [`virtual_mouse.py`](file:///C:/Users/tirth/.gemini/antigravity/scratch/gesture-control-pc/virtual_mouse.py), you can fine-tune:
- `SMOOTHENING = 5`: Increase (e.g. `7` or `9`) for rock-solid cursor stability; decrease (e.g. `2` or `3`) for ultra-fast flick response.
- `FRAME_MARGIN = 100`: Size of the active bounding box inside the camera frame.
- `CLICK_DISTANCE = 35`: Pinch sensitivity threshold.
