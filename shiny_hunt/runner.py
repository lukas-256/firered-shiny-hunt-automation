from __future__ import annotations

import math
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

from .capture import FrameGrabber
from .config import AppConfig
from .controller import ProMicroController
from .matching import ImageMatcher
from .states import build_default_states

RESET_COLOR = "\033[1;93m"
RESET_COLOR_END = "\033[0m"
ODDS_COLOR = "\033[1;96m"
ODDS_COLOR_END = "\033[0m"


def send_ntfy_notification(topic: str, message: str) -> None:
    if not topic:
        return
    url = f"https://ntfy.sh/{quote(topic)}"
    request = Request(
        url=url,
        data=message.encode("utf-8"),
        method="POST",
        headers={"Title": "Shiny Hunt", "Priority": "urgent", "Tags": "star"},
    )
    with urlopen(request, timeout=10):
        pass


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
    reset_count = max(0, config.runtime.reset_counter_initial)
    no_match_streak = 0
    last_reset_time: float | None = None

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

            is_match = best_state.screenshot_path is not None and best_similarity >= config.match.similarity_threshold
            if is_match:
                no_match_streak = 0
                if best_state.match_text:
                    print(f"[match] {best_state.match_text}")
                if best_state.action_name == "press_abxy":
                    now = time.time()
                    reset_count += 1
                    print(f"{RESET_COLOR}[resets] {reset_count}{RESET_COLOR_END}")
                    p = min(max(config.runtime.success_probability_per_try, 0.0), 1.0)
                    success_probability = 1.0 - math.pow(1.0 - p, reset_count)
                    print(
                        f"{ODDS_COLOR}[odds] P(at least one success) = 1-(1-{p:.8f})^{reset_count} = "
                        f"{success_probability * 100.0:.4f}%{ODDS_COLOR_END}"
                    )
                    if last_reset_time is None:
                        print("[delta] first reset (no previous delta)")
                    else:
                        delta_seconds = now - last_reset_time
                        print(f"[delta] {delta_seconds:.2f}s since previous reset")
                    last_reset_time = now
                controller.run_action(best_state.action_name)
            else:
                no_match_streak += 1
                print(f"[no-match] streak {no_match_streak}/{config.runtime.shiny_no_match_streak_threshold}")
                if no_match_streak >= config.runtime.shiny_no_match_streak_threshold:
                    print("[shiny] no state matched for threshold streak; sending notification and exiting")
                    try:
                        send_ntfy_notification(config.runtime.ntfy_topic, "Shiny Found!")
                        print(f"[ntfy] notification sent to topic '{config.runtime.ntfy_topic}'")
                    except Exception as exc:
                        print(f"[ntfy] failed to send notification: {exc}")
                    break

            if config.runtime.max_loops is not None and loop_count >= config.runtime.max_loops:
                break

            time.sleep(config.runtime.check_interval_seconds)

    except KeyboardInterrupt:
        print("stopped by user")
    finally:
        grabber.close()
        controller.disconnect()
