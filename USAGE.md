# ShinyHunting Usage Guide

This document explains:
- what the main program does
- what each script in `tools/` does
- how to run everything

## 1. Setup

From the project root:

```bash
source venv/bin/activate
```

Most scripts assume you run them from the project root (`/Users/lukas/Desktop/ShinyHunting`).

## 2. Main Program

### Start the hunt loop

```bash
python3 run_hunt.py
```

### How it works

1. `run_hunt.py` loads default config and starts `run_hunt_loop`.
2. `run_hunt_loop` creates:
- a frame grabber (`shiny_hunt/capture.py`)
- an image matcher (`shiny_hunt/matching.py`)
- a serial controller (`shiny_hunt/controller.py`)
3. It loads reference screenshots from `images/` based on states in `shiny_hunt/states.py`.
4. Each loop:
- grabs a frame from the capture card
- compares frame against each state reference
- picks the best match
- if similarity is above threshold, runs the state's action (button press sequence).

### Main config defaults

Defined in `shiny_hunt/config.py`:
- Capture: device `0`, `1280x720`, `60 fps`
- Matching: pixel tolerance `1`, similarity threshold `0.99`
- Runtime: check interval `0.5s`
- Controller serial: `/dev/cu.usbserial-BG03S8AW`, `19200` baud

## 3. Tools Folder

All helper/testing scripts are in `tools/`.

### `tools/reference_tools_cli.py`

CLI for capture utilities.

```bash
python3 -m tools.reference_tools_cli list-devices
python3 -m tools.reference_tools_cli save-full --out images/switch_frame_game_freak.png
python3 -m tools.reference_tools_cli save-crop --out images/example.png --x 350 --y 140 --w 50 --h 50
```

Commands:
- `list-devices`: shows working capture indices
- `save-full`: saves one full frame
- `save-crop`: saves cropped region from one frame

### `tools/controller_gui.py`

Visual controller tester (GUI) for serial button taps.

```bash
python3 -m tools.controller_gui
```

Features:
- Connect/Disconnect to controller
- On-screen button taps: `A B X Y L R ZL ZR HOME PLUS MINUS`
- D-pad buttons: `UP DOWN LEFT RIGHT`
- Keyboard binds:
- `J=A`, `K=B`, `U=X`, `I=Y`
- `Q=L`, `E=R`
- `1=ZL`, `3=ZR`
- `H=HOME`, `+=PLUS`, `-=MINUS`
- Arrow keys for D-pad

### `tools/switch_buttons.py`

Quick serial test sequence:
- sync/connect
- taps `A`, `B`, `X`, `Y`
- then taps `A+B+X+Y` together

Run:

```bash
python3 -m tools.switch_buttons
```

### `tools/capture_reference.py`

Captures one full frame and saves:
- `images/switch_frame_new.png`

Run:

```bash
python3 -m tools.capture_reference
```

### `tools/get_id.py`

Scans device indices `0..9` and prints which capture devices return frames.

Run:

```bash
python3 tools/get_id.py
```

### `tools/test_id.py`

Opens a chosen capture device index and displays live video (press `q` to close).

Run:

```bash
python3 tools/test_id.py
```

### `tools/screenshot.py`

Grabs one frame from `DEVICE_INDEX=0`, takes a filename argument, and saves to `images/<filename>`.

Run:

```bash
python3 tools/screenshot.py switch_frame_dark_blue_bg.png
```

### `tools/specific_screenshot.py`

Grabs one frame, crops a fixed rectangle (`x=350, y=140, w=50, h=50`), saves:
- `switch_crop.png`

Run:

```bash
python3 tools/specific_screenshot.py
```

### `tools/read_pixels.py`

Live capture with pixel inspection:
- prints RGB values at a fixed coordinate (`x=100, y=100`)
- shows marker on preview
- press `q` to quit

Run:

```bash
python3 tools/read_pixels.py
```

### `tools/test_screenshot.py`

Continuously compares live capture to a reference image and prints match status.

Current hardcoded reference:
- `switch_frame_game_freak.png`

Run:

```bash
python3 tools/test_screenshot.py
```

### `tools/test_serial.py`

Minimal serial open/close test for:
- `/dev/cu.usbserial-BG03S8AW` at `19200` baud

Run:

```bash
python3 tools/test_serial.py
```

## 4. Quick Start

If you want the shortest path:

1. `source venv/bin/activate`
2. `python3 -m tools.reference_tools_cli list-devices`
3. `python3 run_hunt.py`
