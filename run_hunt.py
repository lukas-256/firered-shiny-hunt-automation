from shiny_hunt.config import default_app_config
from shiny_hunt.runner import run_hunt_loop


if __name__ == "__main__":
    cfg = default_app_config()
    run_hunt_loop(cfg)
