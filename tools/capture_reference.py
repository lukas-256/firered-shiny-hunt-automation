from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shiny_hunt.config import default_app_config
from shiny_hunt.reference_tools import save_full_frame


if __name__ == "__main__":
    cfg = default_app_config()
    output = Path("images") / "switch_frame_new.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    saved = save_full_frame(output, cfg.capture)
    print(f"Saved {saved}")
