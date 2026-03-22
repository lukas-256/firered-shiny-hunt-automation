from __future__ import annotations

import tkinter as tk
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shiny_hunt.config import default_app_config
from shiny_hunt.controller import ProMicroController


class ControllerGui:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Switch Controller Panel")
        self.root.geometry("460x360")
        self.root.configure(bg="#10151f")

        self.status_var = tk.StringVar(value="Disconnected")

        cfg = default_app_config().controller
        self.controller = ProMicroController(
            port=cfg.port,
            baud_rate=cfg.baud_rate,
            timeout=cfg.timeout,
            connect_delay_seconds=cfg.connect_delay_seconds,
            tap_hold_seconds=cfg.tap_hold_seconds,
            release_delay_seconds=cfg.release_delay_seconds,
        )

        self._build_ui()
        self._bind_keys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        button_text_color = "#111111"

        title = tk.Label(
            self.root,
            text="Nintendo Switch Input Tester",
            bg="#10151f",
            fg="#f4f8ff",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=(16, 8))

        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#10151f",
            fg="#8dd3ff",
            font=("Helvetica", 11),
        )
        status.pack(pady=(0, 12))

        row = tk.Frame(self.root, bg="#10151f")
        row.pack(pady=(0, 12))

        connect = tk.Button(
            row,
            text="Connect",
            width=12,
            command=self.connect,
            bg="#1f8b4c",
            fg=button_text_color,
            activebackground="#2aa35b",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        )
        connect.grid(row=0, column=0, padx=6)

        disconnect = tk.Button(
            row,
            text="Disconnect",
            width=12,
            command=self.disconnect,
            bg="#9b2b3a",
            fg=button_text_color,
            activebackground="#b33445",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        )
        disconnect.grid(row=0, column=1, padx=6)

        grid = tk.Frame(self.root, bg="#10151f")
        grid.pack(pady=8)

        for idx, button in enumerate(("A", "B", "X", "Y", "L", "R", "ZL", "ZR", "HOME", "PLUS", "MINUS")):
            r = idx // 4
            c = idx % 4
            b = tk.Button(
                grid,
                text=button,
                width=9,
                height=2,
                command=lambda bname=button: self.tap_button(bname),
                bg="#263445",
                fg=button_text_color,
                activebackground="#35506e",
                activeforeground=button_text_color,
                relief=tk.RAISED,
                bd=2,
            )
            b.grid(row=r, column=c, padx=6, pady=6)

        dpad = tk.Frame(self.root, bg="#10151f")
        dpad.pack(pady=(6, 6))
        tk.Button(
            dpad,
            text="UP",
            width=9,
            command=lambda: self.tap_dpad("UP"),
            bg="#2d3f55",
            fg=button_text_color,
            activebackground="#35506e",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(
            dpad,
            text="LEFT",
            width=9,
            command=lambda: self.tap_dpad("LEFT"),
            bg="#2d3f55",
            fg=button_text_color,
            activebackground="#35506e",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        ).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(
            dpad,
            text="DOWN",
            width=9,
            command=lambda: self.tap_dpad("DOWN"),
            bg="#2d3f55",
            fg=button_text_color,
            activebackground="#35506e",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        ).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(
            dpad,
            text="RIGHT",
            width=9,
            command=lambda: self.tap_dpad("RIGHT"),
            bg="#2d3f55",
            fg=button_text_color,
            activebackground="#35506e",
            activeforeground=button_text_color,
            relief=tk.RAISED,
            bd=2,
        ).grid(row=1, column=2, padx=5, pady=5)

        help_text = (
            "Keyboard: J=A, K=B, U=X, I=Y, Q=L, E=R, 1=ZL, 3=ZR, H=HOME, +=PLUS, -=MINUS, arrows=D-pad"
        )
        help_label = tk.Label(
            self.root,
            text=help_text,
            wraplength=420,
            justify="center",
            bg="#10151f",
            fg="#c8d2e3",
            font=("Helvetica", 10),
        )
        help_label.pack(pady=(12, 8))

    def _bind_keys(self) -> None:
        keymap = {
            "j": "A",
            "k": "B",
            "u": "X",
            "i": "Y",
            "q": "L",
            "e": "R",
            "1": "ZL",
            "3": "ZR",
            "h": "HOME",
            "plus": "PLUS",
            "equal": "PLUS",
            "minus": "MINUS",
        }
        for key, button in keymap.items():
            self.root.bind(f"<KeyPress-{key}>", lambda _event, b=button: self.tap_button(b))
        self.root.bind("<Up>", lambda _event: self.tap_dpad("UP"))
        self.root.bind("<Down>", lambda _event: self.tap_dpad("DOWN"))
        self.root.bind("<Left>", lambda _event: self.tap_dpad("LEFT"))
        self.root.bind("<Right>", lambda _event: self.tap_dpad("RIGHT"))

    def connect(self) -> None:
        try:
            self.controller.connect()
            self.status_var.set("Connected")
        except Exception as exc:
            self.status_var.set(f"Connect failed: {exc}")

    def disconnect(self) -> None:
        try:
            self.controller.disconnect()
        finally:
            self.status_var.set("Disconnected")

    def tap_button(self, button: str) -> None:
        if not self.controller.is_connected:
            self.status_var.set("Not connected")
            return
        try:
            self.controller.tap(button)
            self.status_var.set(f"Tapped {button}")
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def tap_dpad(self, direction: str) -> None:
        if not self.controller.is_connected:
            self.status_var.set("Not connected")
            return
        try:
            self.controller.tap_dpad(direction)
            self.status_var.set(f"D-pad {direction}")
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def _on_close(self) -> None:
        self.disconnect()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    app = ControllerGui()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
