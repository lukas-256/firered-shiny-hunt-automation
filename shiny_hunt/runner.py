from __future__ import annotations

import time

from .capture import FrameGrabber
from .config import AppConfig
from .controller import ProMicroController
from .matching import ImageMatcher
from .states import build_default_states

RESET_COLOR = "\033[1;93m"
RESET_COLOR_END = "\033[0m"


def run_hunt_loop(config: AppConfig) -> None:
    states = build_default_states(config.project_root)
    matcher = ImageMatcher(config.match)
    controller = ProMicroController(
        port=config.controller.port,
        baud_rate=config.controller.baud_rate,
        timeout=config.controller.timeout,
        connect_delay_seconds=config.controller.connect_delay_seconds,
        tap_hold_seconds=config.controller.tap_hold_seconds,
        release_delay_seconds=config.controller.release_delay_seconds,
    )
    grabber = FrameGrabber(config.capture)

    references = {
        state.name: matcher.load_reference(state.screenshot_path)
        if state.screenshot_path is not None
        else None
        for state in states
    }

    controller.connect()
    grabber.open()

    if config.runtime.startup_press_a_seconds > 0:
        print(f"[startup] pressing A for {config.runtime.startup_press_a_seconds:.1f}s before detection")
        startup_deadline = time.time() + config.runtime.startup_press_a_seconds
        startup_presses = 0
        while time.time() < startup_deadline:
            controller.press_a()
            startup_presses += 1
            remaining = max(0.0, startup_deadline - time.time())
            print(f"[startup] A press {startup_presses} (remaining {remaining:.1f}s)")
            if time.time() < startup_deadline:
                time.sleep(config.runtime.startup_press_a_interval_seconds)

    loop_count = 0
    reset_count = 0

    try:
        while True:
            loop_count += 1

            frame = grabber.read()
            if frame is None:
                print("[loop] no frame")
                if config.runtime.max_loops is not None and loop_count >= config.runtime.max_loops:
                    break
                time.sleep(config.runtime.check_interval_seconds)
                continue

            best_state = None
            best_similarity = -1.0

            for state in states:
                reference = references[state.name]
                if reference is not None:
                    h, w = reference.shape[:2]
                    x0 = state.match_x
                    y0 = state.match_y
                    x1 = x0 + w
                    y1 = y0 + h

                    if x0 < 0 or y0 < 0 or x1 > frame.shape[1] or y1 > frame.shape[0]:
                        region = None
                    else:
                        region = frame[y0:y1, x0:x1]
                else:
                    region = frame

                result = matcher.compare(reference, region)
                if result.similarity > best_similarity:
                    best_state = state
                    best_similarity = result.similarity

            if best_state is None:
                time.sleep(config.runtime.check_interval_seconds)
                continue

            if config.runtime.log_similarity:
                print(f"[detect] {best_state.name} similarity={best_similarity:.5f}")

            if best_state.screenshot_path is not None and best_similarity >= config.match.similarity_threshold:
                if best_state.match_text:
                    print(f"[match] {best_state.match_text}")
                if best_state.action_name == "press_abxy":
                    reset_count += 1
                    print(f"{RESET_COLOR}[resets] {reset_count}{RESET_COLOR_END}")
                controller.run_action(best_state.action_name)

            if config.runtime.max_loops is not None and loop_count >= config.runtime.max_loops:
                break

            time.sleep(config.runtime.check_interval_seconds)

    except KeyboardInterrupt:
        print("stopped by user")
    finally:
        grabber.close()
        controller.disconnect()
