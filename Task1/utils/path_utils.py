import pathlib
import sys


def get_app_base_dir() -> pathlib.Path:
    """Returns the base directory of the application, whether running from source or as a PyInstaller executable."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return pathlib.Path(sys._MEIPASS)
        return pathlib.Path(sys.executable).resolve().parent
    return pathlib.Path(__file__).resolve().parents[1]