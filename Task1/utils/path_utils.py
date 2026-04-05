import pathlib
import sys


def get_resource_base_dir() -> pathlib.Path:
    """Path for bundled read-only files (icons, assets)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return pathlib.Path(sys._MEIPASS)
    return pathlib.Path(__file__).resolve().parents[1]


def get_runtime_base_dir() -> pathlib.Path:
    """Path for writable runtime files (db, receipts, logs)."""
    if getattr(sys, "frozen", False):
        exe_path = pathlib.Path(sys.executable).resolve()

        # macOS .app: move out of bundle and write beside SmartPOS.app
        if sys.platform == "darwin":
            for p in exe_path.parents:
                if p.suffix == ".app":
                    return p.parent

        # Windows/Linux frozen: next to executable
        return exe_path.parent

    return pathlib.Path(__file__).resolve().parents[1]
