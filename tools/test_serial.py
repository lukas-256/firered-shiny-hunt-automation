from shiny_hunt.config import default_app_config
from shiny_hunt.controller import ProMicroController


controller_config = default_app_config().controller
controller = ProMicroController(
    port=controller_config.port,
    baud_rate=controller_config.baud_rate,
    timeout=controller_config.timeout,
    connect_delay_seconds=controller_config.connect_delay_seconds,
    tap_hold_seconds=controller_config.tap_hold_seconds,
    release_delay_seconds=controller_config.release_delay_seconds,
)

try:
    controller.connect()
    print("Serial connection and controller synchronization succeeded.")
finally:
    controller.disconnect()
