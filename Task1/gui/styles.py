from functools import lru_cache

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from config import STORE_NAME


# ─── Color Palette ─────────────────────────────────────────────────────────────

class Colors:
    BG_PRIMARY = "#F2F2F7"  # System background
    BG_SECONDARY = "#FFFFFF"  # Secondary grouped background
    BG_TERTIARY = "#F2F2F7"  # Tertiary grouped background
    BG_SURFACE = "#FFFFFF"  # Cards / panels
    BG_SIDEBAR = "#F7F7F7"  # Sidebar background
    BG_INPUT = "#FFFFFF"
    ACCENT = "#007AFF"  # System blue
    ACCENT_HOVER = "#0071E3"
    ACCENT_LIGHT = "#EBF4FF"  # Tinted blue bg
    DANGER = "#FF3B30"
    DANGER_HOVER = "#E0352B"
    DANGER_LIGHT = "#FFF1F0"
    SUCCESS = "#34C759"
    SUCCESS_LIGHT = "#F0FFF4"
    WARNING = "#FF9500"
    TEXT = "#1D1D1F"
    TEXT_SECONDARY = "#3C3C43"
    TEXT_MUTED = "#6E6E73"
    TEXT_ON_ACCENT = "#FFFFFF"
    TEXT_GREY = "#888888"
    BORDER = "#E5E5EA"  # Light separator
    BORDER_STRONG = "#C6C6C8"
    SIDEBAR_ITEM_ACTIVE_BG = "#DCEEFF"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    STATUS_ONLINE = "#30D158"


# ─── StyleEngine ───────────────────────────────────────────────────────────────

class StyleEngine:
    """
    Generates and applies the global QSS stylesheet.
    """

    @staticmethod
    def get_stylesheet() -> str:
        """Return the complete QSS stylesheet string."""
        c = Colors
        return f"""
        /* ── Global ── */
        QWidget {{
            background-color: {c.BG_PRIMARY};
            color: {c.TEXT};
            font-family: "SF Pro Text", "SF Pro Display", "-apple-system", "Segoe UI", Arial;
            font-size: 13px;
        }}

        /* ── Main Window ── */
        QMainWindow {{
            background-color: {c.BG_PRIMARY};
        }}

        /* ── Push Buttons — Primary (blue) ── */
        QPushButton {{
            background-color: {c.ACCENT};
            color: {c.TEXT_ON_ACCENT};
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            min-height: 34px;
            border-radius: 8px;
            padding: 0px 14px;
        }}
        QPushButton:hover {{
            background-color: {c.ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {c.ACCENT};
        }}
        QPushButton:disabled {{
            background-color: {c.BORDER};
            color: {c.TEXT_MUTED};
        }}
        
        /* ── Push Buttons for Panel*/
        QPushButton[manager="true"] {{
            color: {c.TEXT_ON_ACCENT};
            background-color: {Colors.ACCENT};
            border-radius: 8px;
            padding: 0px 14px;
        }}
        QPushButton[manager="true"]:hover {{
             background-color: {c.ACCENT_HOVER};
             color: {Colors.TEXT_ON_ACCENT};
         }}


        /* ── Push Buttons — Secondary (light gray) ── */
        QPushButton[secondary="true"] {{
            background-color: #E8E8ED;
            color: {c.TEXT};
            border: none;
            border-radius: 8px;
            font-weight: 500;
        }}
        QPushButton[secondary="true"]:hover {{
            background-color: #D1D1D6;
        }}

        /* ── Push Buttons — Danger (red) ── */
        QPushButton[danger="true"] {{
            background-color: {c.DANGER};
            color: {c.TEXT_ON_ACCENT};
            border: none;
            border-radius: 8px;
            font-weight: 500;
            border-radius: 8px;
            padding: 0px 14px;
        }}
        QPushButton[danger="true"]:hover {{
            background-color: {Colors.DANGER_HOVER};
        }}

        /* ── Small buttons ── */
        QPushButton[small="true"] {{
            min-height: 28px;
            padding: 4px 12px;
            font-size: 12px;
            border-radius: 6px;
        }}

        /* ── Category Pills ── */
        QPushButton[category="true"] {{
            background-color: #E5E5EA;
            color: {c.TEXT_MUTED};
            border: none;
            border-radius: 14px;
            padding: 4px 12px;
            min-height: 30px;
            font-size: 12px;
        }}
        QPushButton[category="true"]:hover {{
            background-color: #D1D1D6;
            color: {c.TEXT};
        }}
        QPushButton[category_active="true"] {{
            background-color: {c.ACCENT};
            color: {c.TEXT_ON_ACCENT};
            border: none;
            border-radius: 14px;
            padding: 4px 12px;
            min-height: 30px;
            font-size: 12px;
            font-weight: bold;
        }}

        /* ── Line Edit ── */
        QLineEdit {{
            background-color: {c.BG_INPUT};
            color: {c.TEXT};
            border: 1px solid {c.BORDER_STRONG};
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 13px;
            min-height: 36px;
        }}
        QLineEdit:focus {{
            border: 2px solid {c.ACCENT};
        }}
        QLineEdit:disabled {{
            color: {c.TEXT_MUTED};
            background-color: {c.BG_PRIMARY};
        }}

        /* ── Combo Box ── */
        QComboBox {{
            background-color: {c.BG_INPUT};
            color: {c.TEXT};
            border: 1px solid {c.BORDER_STRONG};
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 13px;
            min-height: 36px;
        }}
        QComboBox:focus {{
            border: 2px solid {c.ACCENT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {c.TEXT_MUTED};
            margin-right: 6px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c.BG_SURFACE};
            color: {c.TEXT};
            border: 1px solid {c.BORDER};
            selection-background-color: {c.ACCENT};
            selection-color: {c.TEXT_ON_ACCENT};
        }}

        /* ── Table Widget ── */
        QTableWidget {{
            background-color: {c.BG_SURFACE};
            alternate-background-color: {c.BG_TERTIARY};
            color: {c.TEXT};
            border: 1px solid {c.BORDER};
            border-radius: 8px;
            gridline-color: transparent;
            selection-background-color: {c.ACCENT_LIGHT};
            selection-color: {c.TEXT};
        }}
        QTableWidget::item {{
            padding: 2px 5px;
            border: none;
            min-height: 40px;
        }}
        QTableWidget::item:selected {{
            background-color: {c.ACCENT_LIGHT};
            color: {c.TEXT};
        }}
        QHeaderView::section {{
            background-color: {c.BG_PRIMARY};
            color: {c.TEXT_MUTED};
            font-size: 11px;
            font-weight: bold;
            padding: 8px 10px;
            border: none;
            border-bottom: 1px solid {c.BORDER};
        }}
        QTableWidget QScrollBar:vertical {{
            background: transparent;
            width: 6px;
        }}
        QTableWidget QScrollBar::handle:vertical {{
            background: {c.BORDER_STRONG};
            border-radius: 3px;
        }}

        /* ── Sidebar QListWidget ── */
        QListWidget[sidebar="true"] {{
            background-color: {c.BG_SIDEBAR};
            border: none;
            border-right: 1px solid {c.BORDER};
            outline: none;
        }}
        QListWidget[sidebar="true"]::item {{
            padding: 10px 16px;
            border-radius: 8px;
            margin: 2px 8px;
            color: {c.TEXT};
            font-size: 13px;
        }}
        QListWidget[sidebar="true"]::item:selected {{
            background-color: {c.SIDEBAR_ITEM_ACTIVE_BG};
            color: {c.ACCENT};
            font-weight: bold;
        }}
        QListWidget[sidebar="true"]::item:hover:!selected {{
            background-color: {c.BORDER};
        }}

        /* ── Tab Widget ── */
        QTabWidget::pane {{
            border: none;
            background-color: {c.BG_PRIMARY};
        }}
        QTabBar {{
            background-color: {c.BG_SURFACE};
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {c.TEXT_MUTED};
            padding: 10px 20px;
            font-size: 13px;
            border: none;
            border-bottom: 2px solid transparent;
            margin-right: 4px;
        }}
        QTabBar::tab:selected {{
            color: {c.ACCENT};
            border-bottom: 2px solid {c.ACCENT};
            font-weight: bold;
        }}
        QTabBar::tab:hover:!selected {{
            color: {c.TEXT};
        }}

        /* ── Scroll Area ── */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {c.BORDER_STRONG};
            border-radius: 3px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c.BORDER_STRONG};
            border-radius: 3px;
        }}

        /* ── Labels ── */
        QLabel{{
            background: transparent;
        }}
        QLabel[heading="true"] {{
            font-size: 15px;
            font-weight: bold;
            color: {c.TEXT};
        }}
        QLabel[muted="true"] {{
            color: {c.TEXT_MUTED};
            font-size: 12px;
        }}
        QLabel[danger="true"] {{
            color: {c.DANGER};
        }}
        QLabel[success="true"] {{
            color: {c.SUCCESS};
        }}
        QLabel[accent="true"] {{
            color: {c.ACCENT};
            font-weight: bold;
        }}
        QLabel[form-label="true"] {{
            color: {c.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
        }}

        /* ── Frame / Card ── */
        QFrame[card="true"] {{
            background-color: {c.BG_SURFACE};
            border-radius: 20px;
            border: 1px solid {c.BORDER};
        }}

        /* ── Dialog ── */
        QDialog {{
            background-color: {c.BG_SURFACE};
        }}

        /* ── Spin Box ── */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c.BG_INPUT};
            color: {c.TEXT};
            border: 1px solid {c.BORDER_STRONG};
            border-radius: 8px;
            padding: 4px 8px;
            min-height: 36px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c.ACCENT};
        }}
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background-color: {c.BORDER};
            border: none;
            width: 18px;
        }}

        /* ── Date Edit ── */
        QDateEdit {{
            background-color: {c.BG_INPUT};
            color: {c.TEXT};
            border: 1px solid {c.BORDER_STRONG};
            border-radius: 8px;
            padding: 4px 8px;
            min-height: 36px;
        }}
        QDateEdit:focus {{
            border: 2px solid {c.ACCENT};
        }}
        
         /* ── Scroll Bar ── */
        QScrollArea[scrollbar="true"] {{
                border: none;
        }}
        QScrollArea[scrollbar="true"] QScrollBar:vertical {{
                background: transparent;
            width: 8px;
            margin: 4px 2px 4px 2px;
        }}
        QScrollArea[scrollbar="true"] QScrollBar::handle:vertical {{
                background: rgba(0, 0, 0, 0.35);
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollArea[scrollbar="true"] QScrollBar::handle:vertical:hover {{
                background: rgba(0, 0, 0, 0.55);
        }}
        QScrollArea[scrollbar="true"] QScrollBar::handle:vertical:pressed {{
                background: rgba(0, 0, 0, 0.65);
        }}
        QScrollArea[scrollbar="true"] QScrollBar::add-line:vertical,
        QScrollArea[scrollbar="true"] QScrollBar::sub-line:vertical {{
                height: 0px;
        }}
        QScrollArea[scrollbar="true"] QScrollBar::add-page:vertical,
        QScrollArea[scrollbar="true"] QScrollBar::sub-page:vertical {{
                background: transparent;
        }}

        /* ── Radio Button ── */
        QRadioButton {{
            color: {c.TEXT};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {c.BORDER_STRONG};
            background-color: transparent;
        }}
        QRadioButton::indicator:checked {{
            background-color: {c.ACCENT};
            border-color: {c.ACCENT};
        }}

        /* ── Status Bar ── */
        QStatusBar {{
            background-color: {c.BG_SURFACE};
            color: {c.TEXT_MUTED};
            font-size: 12px;
            border-top: 1px solid {c.BORDER};
        }}

        /* ── Menu Bar ── */
        QMenuBar {{
            background-color: {c.BG_SURFACE};
            color: {c.TEXT};
            border-bottom: 1px solid {c.BORDER};
        }}
        QMenuBar::item:selected {{
            background-color: {c.ACCENT};
            color: {c.TEXT_ON_ACCENT};
        }}

        /* ── Tool Tip ── */
        QToolTip {{
            background-color: {c.BG_SURFACE};
            color: {c.TEXT};
            border: 1px solid {c.BORDER};
            padding: 4px 8px;
        }}

        /* ── Splitter ── */
        QSplitter::handle {{
            background: {c.BORDER};
        }}
        
        QTableWidget[select="true"]::item:selected {{
        background-color: #007AFF;   /* Colors.ACCENT */
        color: #FFFFFF;              /* Colors.TEXT_ON_ACCENT */
        font-weight: 600;
        border: none;
        }}
        
        QTableWidget[select="true"]::item:selected:!active {{
                background-color: #2B8CFF;   /* slightly softer when window not focused */
            color: #FFFFFF;
        }}
        
        QTableWidget[select="true"]::item:hover:!selected {{
                background-color: #EBF4FF;   /* keep hover lighter than selected */
        }}
        """

    @staticmethod
    def apply(app: QApplication):
        """Apply the global stylesheet to the application."""
        font = QFont()
        font.setFamily("-apple-system")  # macOS native
        font.setFamilies(["-apple-system", "SF Pro Display", "SF Pro Text",
                          "Helvetica Neue", "Segoe UI", "Arial", "sans-serif"])
        font.setPixelSize(13)
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        app.setFont(font)
        app.setStyleSheet(StyleEngine.get_stylesheet())

    @staticmethod
    def make_logo_label_text() -> str:
        """Return the store logo text."""
        return STORE_NAME

    @staticmethod
    def logo_stylesheet() -> str:
        return (
            f"color: {Colors.TEXT};"
            "font-size: 25px;"
            "font-weight: bold;"
            'font-family: "SF Pro Display", "Segoe UI", Arial;'
        )
    @staticmethod
    def get_mono_font() -> QFont:
        font = QFont("Consolas")
        font.setPointSize(10)
        return font

    @staticmethod
    @lru_cache(maxsize=16)
    def product_card_stylesheet(category_color: str = Colors.ACCENT) -> str:
        c = Colors
        return (
            f"QFrame {{ background-color: {c.BG_SURFACE}; border-radius: 12px; "
            f"border: 1px solid {category_color}; }}"
            f"QFrame:hover {{ border: 2px solid {c.ACCENT}; "
            f"background-color: {c.ACCENT_LIGHT}; }}"
            f"QFrame[pressed=true] {{ border: 2px solid rgba(0,0,0,0.18); " 
            f"background-color: rgba(0,0,0,0.06); }}"                     
            f"QFrame QLabel {{ background: transparent; border: none; }}"
            f"QFrame:hover QLabel {{ background: transparent; border: none; }}"
        )
