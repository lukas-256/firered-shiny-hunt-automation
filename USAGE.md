# ShinyHunting setup and usage

This project automates shiny hunting in Pokémon FireRed by reading the game
video, recognizing screen states from reference images, and sending controller
inputs back to the console.

The setup documented here was tested with:

- Nintendo Switch 2 running Pokémon FireRed
- Arduino Pro Micro with an ATmega32U4
- UGREEN HDMI-to-USB capture card
- USB-to-UART adapter connected to the Pro Micro hardware serial pins
- macOS using the AVFoundation capture backend

Similar ATmega32U4 boards, capture cards, USB-to-UART adapters, operating
systems, and consoles may work, but they have not been tested with this
project. Capture resolution, color conversion, and latency can differ between
devices, so another capture card may require new reference images.

## How the system works

```text
Switch 2 HDMI output
        |
        v
UGREEN capture card ----USB----> Mac / OpenCV / Python
                                      |
                                      | serial packets at 19200 baud
                                      v
                              USB-to-UART adapter
                                      |
                                      | UART TX/RX/GND
                                      v
                                 Pro Micro
                                      |
                                      | USB HID controller reports
                                      v
                                  Switch 2
```

The capture card is the input side of the loop. The Python program captures a
frame every 0.5 seconds, compares parts of it with images under
`images/<profile>/`, and chooses the best matching screen state. The state then
runs a button press or a short controller sequence.

The USB-to-UART adapter is not the controller itself. It gives the laptop a
serial connection to the Pro Micro. The Pro Micro runs SwitchInputEmulator
firmware and presents itself to the Switch as a wired HORIPAD-compatible USB
controller.

Controller packets contain button bits, D-pad state, both analog stick
positions, and a CRC byte. The firmware acknowledges packets and turns them
into USB HID reports for the Switch.

Image matching is intentionally strict: the default requires 99% of the
compared pixels to match with a pixel tolerance of 1. Cropped references are
therefore usually more reliable and faster than full-screen references, but
they must be captured at the same resolution and placed at the same screen
coordinates.

## Required hardware

- Nintendo Switch 2 and a dock or other compatible HDMI output method
- HDMI cable
- UGREEN HDMI capture card or a similar UVC-compatible capture device
- Arduino Pro Micro, 5 V/16 MHz, ATmega32U4
- USB-to-UART adapter compatible with the Pro Micro logic voltage
- Jumper wires for UART and ground
- USB cables/adapters for the capture card, USB-to-UART adapter, and Pro Micro
- A computer; this repository has only been tested on macOS

Wire the serial connection as follows:

| USB-to-UART adapter | Pro Micro |
| --- | --- |
| TX | RX / RXI / pin 0 |
| RX | TX / TXO / pin 1 |
| GND | GND |

TX and RX are crossed. Do not connect the adapter VCC pin when the Pro Micro is
already powered over USB unless you know that your particular boards require
it. Both devices must share ground.

After the controller firmware has been flashed, connect the Pro Micro USB port
to the Switch. Connect the USB-to-UART adapter to the computer and leave its
TX, RX, and GND wires attached to the Pro Micro.

## Clone and install Python dependencies

Python 3.9.1 and the versions in `requirements.txt` were used for the tested
setup. Newer Python 3 versions may also work.

```bash
git clone <your-repository-url> ShinyHunting
cd ShinyHunting
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

On first use, macOS may ask for camera permission because capture cards are
exposed as camera devices. Grant that permission to the terminal application
running Python.

## Build the Pro Micro firmware

The controller firmware is based on
[wchill/SwitchInputEmulator](https://github.com/wchill/SwitchInputEmulator),
which is MIT-licensed. It uses
[LUFA](https://github.com/abcminiuser/lufa), which has its own permissive
license. These projects are not copied into this repository. Clone the
original sources so their history, attribution, and license files remain
intact.

The tested local copies use SwitchInputEmulator commit
`397c14977dac8f3094f093852b44af5a47ae4559` and LUFA release `LUFA-170418`.

From the ShinyHunting project root:

```bash
git clone https://github.com/wchill/SwitchInputEmulator.git
git -C SwitchInputEmulator checkout 397c14977dac8f3094f093852b44af5a47ae4559
git clone --branch LUFA-170418 --depth 1 https://github.com/abcminiuser/lufa.git lufa
```

On macOS, install an AVR compiler and flashing tool:

```bash
xcode-select --install
brew tap osx-cross/avr
brew install avr-gcc
brew install avrdude
```

Edit `SwitchInputEmulator/Arduino/Makefile` for the tested Pro Micro:

```make
MCU          = atmega32u4
LUFA_PATH    = ../../lufa/LUFA
```

Then build the firmware:

```bash
cd SwitchInputEmulator/Arduino
make clean
make
```

The important output is `SwitchInputEmulator/Arduino/Joystick.hex`.

### Flash the Pro Micro

The exact serial device name changes between computers and may change while
the Pro Micro bootloader is active. Find the port with:

```bash
python3 -m serial.tools.list_ports
```

Put the Pro Micro into its Caterina bootloader by quickly resetting it twice,
then immediately run a command like this with the bootloader port:

```bash
avrdude -p atmega32u4 -c avr109 \
  -P /dev/cu.usbmodemXXXX -b 57600 -D \
  -U flash:w:SwitchInputEmulator/Arduino/Joystick.hex:i
```

Replace `/dev/cu.usbmodemXXXX` with the port shown on your system. The
bootloader is only available for a few seconds, so flashing can require more
than one attempt. Flashing replaces the normal Arduino application; double
reset still enters the bootloader so the board can be reflashed later.

## Configure the hunt

Personal serial device names and notification topics are deliberately not
stored in the public configuration. Create a local environment file:

```bash
cp .env.example .env.local
```

Edit `.env.local`, then load it in every new terminal session:

```bash
source .env.local
```

Available settings:

| Variable | Meaning | Default |
| --- | --- | --- |
| `SHINY_HUNT_PROFILE` | State profile to load | `snorlax` |
| `SHINY_HUNT_CAPTURE_DEVICE` | OpenCV capture index | `0` |
| `SHINY_HUNT_SERIAL_PORT` | USB-to-UART serial port | required |
| `SHINY_HUNT_RESET_COUNTER_INITIAL` | Starting reset count | `0` |
| `SHINY_HUNT_NTFY_TOPIC` | ntfy.sh topic; empty disables alerts | empty |

Find likely serial ports with:

```bash
python3 -m serial.tools.list_ports
```

An example macOS configuration might look like:

```bash
export SHINY_HUNT_PROFILE="snorlax"
export SHINY_HUNT_CAPTURE_DEVICE="0"
export SHINY_HUNT_SERIAL_PORT="/dev/cu.usbserial-XXXX"
export SHINY_HUNT_RESET_COUNTER_INITIAL="0"
export SHINY_HUNT_NTFY_TOPIC="use-a-long-random-topic-or-leave-empty"
```

Anyone who knows an ntfy.sh topic name can subscribe to it. Treat the topic as
a private value and do not commit `.env.local`.

## Verify each connection

Test the capture card first:

```bash
python3 -m tools.reference_tools_cli list-devices
python3 tools/test_id.py
```

The second command asks for the capture device number and opens a live preview.
Press `q` to close it.

Test firmware synchronization through the USB-to-UART adapter:

```bash
python3 -m tools.test_serial
```

Test controller buttons with either the GUI or a short automated sequence:

```bash
python3 -m tools.controller_gui
python3 -m tools.switch_buttons
```

`switch_buttons` presses A, B, X, Y, then all four together. Only run it when
those inputs are safe on the current game screen.

## Run a hunt

With `.env.local` loaded and the game at the expected starting screen:

```bash
python3 run_hunt.py
```

Temporarily select another profile without editing files:

```bash
SHINY_HUNT_PROFILE="eevee" python3 run_hunt.py
```

Resume a Snorlax hunt at reset 250 for one run:

```bash
SHINY_HUNT_PROFILE="snorlax" \
SHINY_HUNT_RESET_COUNTER_INITIAL="250" \
python3 run_hunt.py
```

Stop safely with `Ctrl-C`. The program releases the capture device and closes
the serial connection before exiting.

### Snorlax behavior

The Snorlax profile intentionally identifies the non-shiny color rather than
requiring a shiny reference. When `shiny_not_found.png` matches, the program
performs the reset and returns to runtime state `s0`. In runtime state `s1`, 40
consecutive checks without any known screen match are treated as a shiny; at
the default 0.5-second interval this is roughly 20 seconds. The program then
sends an optional notification and exits without pressing another button.

Because no-match detection is intentional, verify that the capture card is
stable before leaving the hunt unattended. A disconnected or frozen capture
source can otherwise look like an unknown/shiny state.

## Capture reference images

List capture devices:

```bash
python3 -m tools.reference_tools_cli list-devices
```

Save a complete 1920x1080 frame from the configured device:

```bash
python3 -m tools.reference_tools_cli save-full \
  --out images/snorlax/new_full_frame.png
```

Use a different capture device for one command:

```bash
python3 -m tools.reference_tools_cli save-full \
  --device 1 \
  --out images/snorlax/device_1_frame.png
```

Save a 50x50 crop beginning at screen coordinate `(1210, 330)`:

```bash
python3 -m tools.reference_tools_cli save-crop \
  --out images/snorlax/example_color.png \
  --x 1210 --y 330 --w 50 --h 50
```

The crop coordinates in the command must also be used as `match_x` and
`match_y` in the corresponding profile state. Reference width and height are
used automatically when the live frame is cropped.

## Helper tools

| Command | Purpose |
| --- | --- |
| `python3 -m tools.reference_tools_cli list-devices` | Scan capture indices 0 through 9 |
| `python3 -m tools.reference_tools_cli save-full ...` | Save one full frame |
| `python3 -m tools.reference_tools_cli save-crop ...` | Save a coordinate-based crop |
| `python3 -m tools.capture_reference` | Save `switch_frame_new.png` for the selected profile |
| `python3 -m tools.controller_gui` | Interactive controller and keyboard tester |
| `python3 -m tools.switch_buttons` | Test serial sync and common face buttons |
| `python3 -m tools.test_serial` | Test serial connection and firmware synchronization |
| `python3 tools/get_id.py` | Basic capture-device scanner |
| `python3 tools/test_id.py` | Live preview for a selected capture index |
| `python3 tools/screenshot.py FILE.png` | Save a frame under the selected profile |
| `python3 tools/specific_screenshot.py` | Save the legacy fixed 50x50 crop |
| `python3 tools/read_pixels.py` | Display video and print one pixel's RGB values |
| `python3 tools/test_screenshot.py` | Legacy standalone full-frame matching experiment |

`reference_tools_cli` is the recommended capture workflow. Some older helper
scripts contain fixed coordinates or filenames and are mainly useful as small
experiments.

## Profiles and project layout

Supported profiles are `charmander`, `dratini`, `eevee`, `magikarp`, and
`snorlax`.

```text
run_hunt.py                 program entry point
shiny_hunt/config.py        shared configuration and environment variables
shiny_hunt/capture.py       OpenCV capture-card access
shiny_hunt/matching.py      pixel comparison
shiny_hunt/controller.py    serial protocol and controller actions
shiny_hunt/runner.py        detection loop, runtime states, reset count, alerts
shiny_hunt/*_states.py      per-Pokémon screen states and actions
images/<profile>/           reference screenshots and cropped color samples
tools/                      capture, serial, and controller diagnostics
```

Run commands from the repository root because image paths are resolved from
the current working directory.

## Troubleshooting

- `Controller serial port is not configured`: load `.env.local` or export
  `SHINY_HUNT_SERIAL_PORT`.
- `Could not open capture device`: run `list-devices`, change
  `SHINY_HUNT_CAPTURE_DEVICE`, and check macOS camera permission.
- Controller synchronization fails: verify 19200 baud, crossed TX/RX, shared
  ground, correct adapter voltage, and that the Pro Micro is running
  `Joystick.hex`.
- Buttons do nothing on the Switch: reconnect the Pro Micro, check wired
  controller support in the console settings, and try the controller pairing
  screen.
- Every image is a no-match: confirm 1920x1080 capture, recapture references,
  and check that the game display is not being scaled, filtered, or covered by
  an overlay.
- `avrdude` cannot find the Pro Micro: double-reset the board and use the
  temporary bootloader port rather than the USB-to-UART port.

## Third-party licensing

Do not remove or replace the license files in cloned third-party projects.
SwitchInputEmulator's Arduino firmware is MIT-licensed, and LUFA release
170418 includes its own redistribution terms in `LUFA/License.txt`. Keeping
them as separately cloned upstream dependencies avoids presenting their code
as original work from this repository.
