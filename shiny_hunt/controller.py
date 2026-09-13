from __future__ import annotations

import time
from typing import Optional

import serial


class ProMicroController:
    """Serial controller for Nintendo Switch Input Emulator firmware."""

    COMMAND_SYNC_START = 0xFF
    COMMAND_SYNC_1 = 0x33
    COMMAND_SYNC_2 = 0xCC

    RESP_USB_ACK = 0x90
    RESP_SYNC_START = 0xFF
    RESP_SYNC_1 = 0xCC
    RESP_SYNC_OK = 0x33

    DPAD_CENTER = 0x08
    STICK_CENTER = 0x80
    STICK_MIN = 0x00
    STICK_MAX = 0xFF
    DPAD_CODES = {
        "UP": 0x00,
        "UP_RIGHT": 0x01,
        "RIGHT": 0x02,
        "DOWN_RIGHT": 0x03,
        "DOWN": 0x04,
        "DOWN_LEFT": 0x05,
        "LEFT": 0x06,
        "UP_LEFT": 0x07,
        "CENTER": DPAD_CENTER,
    }

    BUTTON_MASKS = {
        "Y": 0x0001,
        "B": 0x0002,
        "A": 0x0004,
        "X": 0x0008,
        "L": 0x0010,
        "R": 0x0020,
        "ZL": 0x0040,
        "ZR": 0x0080,
        "MINUS": 0x0100,
        "PLUS": 0x0200,
        "LCLICK": 0x0400,
        "RCLICK": 0x0800,
        "HOME": 0x1000,
        "CAPTURE": 0x2000,
    }
    LEFT_STICK_DIRECTIONS = {
        "CENTER": (STICK_CENTER, STICK_CENTER),
        "UP": (STICK_CENTER, STICK_MIN),
        "DOWN": (STICK_CENTER, STICK_MAX),
        "LEFT": (STICK_MIN, STICK_CENTER),
        "RIGHT": (STICK_MAX, STICK_CENTER),
    }

    def __init__(
        self,
        port: str,
        baud_rate: int = 19200,
        timeout: float = 0.2,
        connect_delay_seconds: float = 1.0,
        tap_hold_seconds: float = 0.08,
        release_delay_seconds: float = 0.03,
    ) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.connect_delay_seconds = connect_delay_seconds
        self.tap_hold_seconds = tap_hold_seconds
        self.release_delay_seconds = release_delay_seconds
        self.connected = False
        self._serial: Optional[serial.Serial] = None

    def connect(self) -> None:
        if not self.port:
            raise RuntimeError(
                "Controller serial port is not configured. "
                "Set the SHINY_HUNT_SERIAL_PORT environment variable."
            )

        if self._serial is not None and self._serial.is_open:
            self._serial.close()

        self._serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
        self.connected = False

        try:
            time.sleep(self.connect_delay_seconds)

            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

            # extra drain, just to be safe
            time.sleep(0.05)
            while self._serial.in_waiting:
                self._serial.read(self._serial.in_waiting)

            self._sync_controller()
            self.connected = True
        except Exception:
            try:
                if self._serial is not None and self._serial.is_open:
                    self._serial.close()
            finally:
                self._serial = None
                self.connected = False
            raise

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                if self._serial.is_open:
                    self._serial.reset_input_buffer()
                    self._serial.reset_output_buffer()
                    self._serial.close()
            finally:
                self._serial = None
                self.connected = False

    def _require_serial(self) -> serial.Serial:
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Controller is not connected.")
        return self._serial

    def _read_byte(self, timeout: float = 1.0) -> int | None:
        ser = self._require_serial()
        start = time.time()
        while time.time() - start < timeout:
            b = ser.read(1)
            if b:
                return b[0]
        return None

    def _write_byte(self, value: int) -> None:
        ser = self._require_serial()
        ser.write(bytes([value]))

    @staticmethod
    def _crc8_ccitt(old_crc: int, new_data: int) -> int:
        data = old_crc ^ new_data
        for _ in range(8):
            if (data & 0x80) != 0:
                data = (data << 1) ^ 0x07
            else:
                data = data << 1
            data &= 0xFF
        return data

    def _sync_controller(self) -> None:
        self._write_byte(self.COMMAND_SYNC_START)

        deadline = time.time() + 1.0
        r = None
        while time.time() < deadline:
            r = self._read_byte(timeout=0.1)
            print("sync1 got:", r)
            if r is None:
                continue
            if r == self.RESP_USB_ACK:
                continue
            break

        if r != self.RESP_SYNC_START:
            raise RuntimeError(f"sync stage 1 failed: got {r}")

        self._write_byte(self.COMMAND_SYNC_1)
        r = self._read_byte()
        print("sync2 got:", r)
        if r != self.RESP_SYNC_1:
            raise RuntimeError(f"sync stage 2 failed: got {r}")

        self._write_byte(self.COMMAND_SYNC_2)
        r = self._read_byte()
        print("sync3 got:", r)
        if r != self.RESP_SYNC_OK:
            raise RuntimeError(f"sync stage 3 failed: got {r}")

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open and self.connected

    def _send_packet(self, packet: list[int]) -> None:
        if len(packet) != 8:
            raise ValueError("packet must be 8 bytes")

        crc = 0
        for byte in packet:
            crc = self._crc8_ccitt(crc, byte)

        ser = self._require_serial()
        ser.write(bytes(packet + [crc]))
        ack = self._read_byte()
        if ack != self.RESP_USB_ACK:
            raise RuntimeError("controller did not ACK packet")

    def _send_state(
        self,
        button_mask: int,
        dpad: int,
        left_x: int = STICK_CENTER,
        left_y: int = STICK_CENTER,
        right_x: int = STICK_CENTER,
        right_y: int = STICK_CENTER,
    ) -> None:
        low = button_mask & 0xFF
        high = (button_mask >> 8) & 0xFF
        packet = [
            high,
            low,
            dpad,
            left_x,
            left_y,
            right_x,
            right_y,
            0x00,
        ]
        self._send_packet(packet)

    def _send_buttons(self, button_mask: int) -> None:
        self._send_state(button_mask, self.DPAD_CENTER)

    def release_all(self) -> None:
        self._send_state(0x0000, self.DPAD_CENTER)

    def tap(self, button: str, hold_seconds: float | None = None) -> None:
        if not self.connected:
            return

        button_mask = self.BUTTON_MASKS.get(button.upper())
        if button_mask is None:
            raise ValueError(f"Unsupported button: {button}")

        hold = hold_seconds if hold_seconds is not None else self.tap_hold_seconds
        self._send_buttons(button_mask)
        time.sleep(hold)
        self.release_all()
        time.sleep(self.release_delay_seconds)

    def tap_dpad(self, direction: str, hold_seconds: float | None = None) -> None:
        if not self.connected:
            return

        dpad_code = self.DPAD_CODES.get(direction.upper())
        if dpad_code is None:
            raise ValueError(f"Unsupported dpad direction: {direction}")

        hold = hold_seconds if hold_seconds is not None else self.tap_hold_seconds
        self._send_state(0x0000, dpad_code)
        time.sleep(hold)
        self.release_all()
        time.sleep(self.release_delay_seconds)

    def tilt_left_stick(self, direction: str, hold_seconds: float = 0.10) -> None:
        if not self.connected:
            return

        coords = self.LEFT_STICK_DIRECTIONS.get(direction.upper())
        if coords is None:
            raise ValueError(f"Unsupported left stick direction: {direction}")

        self._send_state(0x0000, self.DPAD_CENTER, left_x=coords[0], left_y=coords[1])
        time.sleep(hold_seconds)
        self.release_all()
        time.sleep(self.release_delay_seconds)

    def run_action(self, action_name: str) -> None:
        action_map = {
            "press_a": self.press_a,
            "press_b": self.press_b,
            "press_down": self.press_down,
            "press_x": self.press_x,
            "press_y": self.press_y,
            "press_abxy": self.press_abxy,
            "buy_dratini_sequence": self.buy_dratini_sequence,
            "open_menu_eevee": self.open_menu_eevee,
            "open_first_pokemon_status_sequence": self.open_first_pokemon_status_sequence,
            "start_run_sequence": self.start_run_sequence,
            "press_a_to_continue": self.press_a_to_continue,
            "wait_or_press_a": self.wait_or_press_a,
            "soft_reset_sequence": self.soft_reset_sequence,
            "capture_or_alert": self.capture_or_alert,
            "choose_charmander": self.choose_charmander,
        }
        action = action_map.get(action_name, self.noop)
        action()

    def tap_buttons(self, buttons: tuple[str, ...], hold_seconds: float | None = None) -> None:
        if not self.connected:
            return

        button_mask = 0
        for button in buttons:
            mask = self.BUTTON_MASKS.get(button.upper())
            if mask is None:
                raise ValueError(f"Unsupported button: {button}")
            button_mask |= mask

        hold = hold_seconds if hold_seconds is not None else self.tap_hold_seconds
        self._send_buttons(button_mask)
        time.sleep(hold)
        self.release_all()
        time.sleep(self.release_delay_seconds)

    def press_a_to_continue(self) -> None:
        self.tap("A")

    def wait_or_press_a(self) -> None:
        self.tap("A")

    def press_a(self) -> None:
        self.tap("A")

    def press_b(self) -> None:
        self.tap("B")

    def press_down(self) -> None:
        self.tilt_left_stick("DOWN", hold_seconds=0.10)

    def press_x(self) -> None:
        self.tap("X")

    def press_y(self) -> None:
        self.tap("Y")

    def press_abxy(self) -> None:
        self.tap_buttons(("A", "B", "X", "Y"), hold_seconds=0.12)

    def start_run_sequence(self) -> None:
        # Battle menu navigation for Magikarp: right, down, confirm.
        self.tilt_left_stick("RIGHT", hold_seconds=0.10)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.press_a()

    def buy_dratini_sequence(self) -> None:
        # Prize menu navigation: down, down, confirm.
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.press_a()

    def open_first_pokemon_status_sequence(self) -> None:
        # Party/status navigation: open menu, Pokemon, move to first Dratini, open summary.
        self.press_x()
        time.sleep(1.0)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.press_a()
        time.sleep(1.0)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        time.sleep(1.0)
        self.press_a()
        time.sleep(1.0)
        self.press_a()
    
    def open_menu_eevee(self) -> None:
        self.press_x()
        time.sleep(1.0)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        time.sleep(1.0)
        self.press_a()
        time.sleep(1.0)
        self.tilt_left_stick("DOWN", hold_seconds=0.10)
        self.press_a()
        time.sleep(0.2)
        self.press_a()

    def soft_reset_sequence(self) -> None:
        for button in ("HOME", "X", "A"):
            self.tap(button, hold_seconds=0.12)

    def capture_or_alert(self) -> None:
        # TODO: add sound alert / screenshot save / stop loop.
        pass

    def choose_charmander(self) -> None:
        # TODO: add D-pad and A-press sequence for starter selection.
        pass

    def noop(self) -> None:
        pass
