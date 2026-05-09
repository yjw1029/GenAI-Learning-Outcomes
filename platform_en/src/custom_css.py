from pathlib import Path

THIS_DIR = Path(__file__).parent
CSS_FILE_PATH = THIS_DIR / "custom.css"
CUSTOM_CSS = open(CSS_FILE_PATH).read()
