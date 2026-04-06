from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QPushButton

from gui.styles import Colors, StyleEngine
from utils.path_utils import get_runtime_base_dir


class ReceiptDialog(QDialog):
    """Simple dialog to display the receipt text and auto-save it as a PDF."""

    def __init__(self, receipt_text: str, transaction_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Receipt")
        self.setFixedSize(450, 700)
        self.setModal(True)
        self._setup_ui(receipt_text, transaction_id)

    def _setup_ui(self, receipt_text: str, transaction_id: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Receipt")
        header.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {Colors.TEXT};"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        receipt_lbl = QLabel(receipt_text)
        receipt_lbl.setFont(StyleEngine.get_mono_font())
        receipt_lbl.setStyleSheet(
            f"color: {Colors.TEXT}; background-color: {Colors.BG_PRIMARY}; "
            f"padding: 16px; border-radius: 8px; "
            f"font-family: 'Consolas', 'Courier New', monospace; "
            f"font-size: 15px; border: 1px solid {Colors.BORDER};"
        )
        receipt_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        receipt_lbl.setWordWrap(False)

        scroll = QScrollArea()
        scroll.setWidget(receipt_lbl)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # PDF save status
        self._pdf_status = QLabel()
        self._pdf_status.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 20px;")
        self._pdf_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._pdf_status)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Auto-save PDF
        self._save_pdf(receipt_text, transaction_id)

    def _save_pdf(self, receipt_text: str, transaction_id: int):
        """Save receipt as PDF in receipts/YYYYMMDD/ folder."""

        try:
            from PySide6.QtPrintSupport import QPrinter
            from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
            from PySide6.QtCore import QSizeF, QMarginsF

            # Create dated folder and PDF path
            date_str = datetime.now().strftime("%Y%m%d")
            base_dir = get_runtime_base_dir()
            folder = base_dir / "receipts" / date_str
            folder.mkdir(parents=True, exist_ok=True)
            pdf_path = folder / f"receipt_{transaction_id}.pdf"
            RECEIPT_WIDTH_MM = 140.0
            MARGIN_MM = 10.0

            # Build HTML once
            escaped = receipt_text.replace("&", "&amp;").replace("<", "&lt;")
            html = (
                    '<pre style="font-family: Courier New, Consolas, monospace; '
                    'font-size: 10pt; line-height: 1.00; margin: 0; padding: 0;">'
                    + escaped + '</pre>'
            )

            # Estimate page height using usable width
            usable_width_pt = (RECEIPT_WIDTH_MM - 2 * MARGIN_MM) * 72.0 / 25.4
            doc = QTextDocument()
            doc.setHtml(html)
            doc.setPageSize(QSizeF(usable_width_pt, 1e9))
            est_height_pt = doc.size().height()
            est_total_mm = est_height_pt * 25.4 / 72.0 + 2 * MARGIN_MM

            # Configure printer with estimated size so we can read its real page rect
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(str(pdf_path))
            printer.setPageMargins(
                QMarginsF(MARGIN_MM, MARGIN_MM, MARGIN_MM, MARGIN_MM),
                QPageLayout.Unit.Millimeter,
            )
            printer.setPageSize(
                QPageSize(QSizeF(RECEIPT_WIDTH_MM, est_total_mm), QPageSize.Unit.Millimeter, "Receipt")
            )

            # Re-measure at the ACTUAL printer page width
            actual_page_rect = printer.pageRect(QPrinter.Unit.Point)
            doc.setPageSize(QSizeF(actual_page_rect.width(), 1e9))
            actual_height_pt = doc.size().height()
            #Small safety buffer (+5 mm) guards against any residual rounding
            actual_total_mm = actual_height_pt * 25.4 / 72.0 + 2 * MARGIN_MM + 5.0

            #Reconfigure printer with the accurate page height
            printer.setPageSize(
                QPageSize(QSizeF(RECEIPT_WIDTH_MM, actual_total_mm), QPageSize.Unit.Millimeter, "Receipt")
            )
            printer.setPageMargins(
                QMarginsF(MARGIN_MM, MARGIN_MM, MARGIN_MM, MARGIN_MM),
                QPageLayout.Unit.Millimeter,
            )

            # Set doc page size to exactly match the final printer page rect and print
            final_rect = printer.pageRect(QPrinter.Unit.Point)
            doc.setPageSize(QSizeF(final_rect.width(), final_rect.height()))
            doc.print_(printer)

            self._pdf_status.setText(f"Saved: receipts/{date_str}/receipt_{transaction_id}.pdf")
            self._pdf_status.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 11px;")
        except Exception as e:
            self._pdf_status.setText(f"PDF save failed: {e}")
            self._pdf_status.setStyleSheet(f"color: {Colors.DANGER}; font-size: 11px;")
