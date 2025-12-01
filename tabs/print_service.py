"""Service for exporting CSV to PDF with wrapping, multi-page support and settings.

RU: Сервис для экспорта CSV в PDF с поддержкой обёртки, мультистраничности и настроек.
"""

import csv
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


_TEMP_FILES = []


def _register_cyrillic_font(preferred_names=None, font_path=None):
    """Попытка зарегистрировать TTF-шрифт с поддержкой кириллицы.

    Ищем шрифты по распространённым путям на разных платформах.
    Возвращаем имя зарегистрированного шрифта или None.
    """
    if preferred_names is None:
        preferred_names = [
            (
                "DejaVuSans",
                [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/local/share/fonts/DejaVuSans.ttf",
                    "/Library/Fonts/DejaVuSans.ttf",
                ],
            ),
            (
                "FreeSans",
                [
                    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                    "/Library/Fonts/FreeSans.ttf",
                ],
            ),
            (
                "ArialUnicode",
                [
                    "/Library/Fonts/Arial Unicode.ttf",
                    "/Library/Fonts/Arial Unicode MS.ttf",
                    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                ],
            ),
            ("Roboto", ["/Library/Fonts/Roboto-Regular.ttf"]),
        ]

    # If an explicit TTF path is provided — try to register it first
    # RU: Если передан явный путь к TTF — попробуем его зарегистрировать первым
    if font_path:
        try:
            if os.path.exists(font_path):
                name = os.path.splitext(os.path.basename(font_path))[0]
                pdfmetrics.registerFont(TTFont(name, font_path))
                return name
        except Exception:
            pass

    for font_name, paths in preferred_names:
        for p in paths:
            try:
                if os.path.exists(p):
                    pdfmetrics.registerFont(TTFont(font_name, p))
                    return font_name
            except Exception:
                continue
    return None


def cleanup_temp_files():
    """Удаляет временные PDF, созданные сервисом печати."""
    global _TEMP_FILES
    import traceback

    for p in list(_TEMP_FILES):
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            traceback.print_exc()
    _TEMP_FILES = []


def remove_temp_file(path):
    """Удаляет единичный временный файл и убирает его из списка."""
    global _TEMP_FILES
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    try:
        if path in _TEMP_FILES:
            _TEMP_FILES.remove(path)
    except Exception:
        pass


class PrintService:
    def __init__(
        self,
        page_size=A4,
        orientation="portrait",
        font_name="Helvetica",
        font_size=9,
        font_path=None,
    ):
        self.page_size = page_size
        self.orientation = orientation
        self.font_name = font_name
        self.font_size = font_size
        self.font_path = font_path
            # Попытка зарегистрировать явный шрифт или системный с поддержкой кириллицы
            # RU: Попытка зарегистрировать явный шрифт или системный с поддержкой кириллицы
        registered = _register_cyrillic_font(font_path=font_path)
        if registered:
            self.font_name = registered

    def _adjust_page(self):
        if self.orientation == "landscape":
            return landscape(self.page_size)
        return self.page_size

    def export_csv_to_pdf(self, src_csv_path, dest_pdf_path, col_widths=None):
        """Экспортирует весь CSV в PDF.

        Поддерживает переносы в колонке 'Наименование' используя Paragraph.
        Автоматически разбивает таблицу на страницы.
        """
        if not os.path.exists(src_csv_path):
            raise FileNotFoundError(src_csv_path)

        rows = []
        # Read CSV as UTF-8 (important for Cyrillic)
        # RU: Читаем CSV в UTF-8 (важно для кириллицы)
        with open(src_csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                rows.append([c.strip() for c in row])

        if not rows:
            raise RuntimeError("CSV is empty")

        page = self._adjust_page()
        doc = SimpleDocTemplate(
            dest_pdf_path,
            pagesize=page,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        # Try to register a Cyrillic-capable font and use it (respecting font_path)
        # RU: Попытка зарегистрировать шрифт с кириллицей и использовать его (учитывая font_path)
        registered = _register_cyrillic_font(font_path=self.font_path)
        chosen_font = registered or self.font_name
        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            "body",
            parent=styles["Normal"],
            fontName=chosen_font,
            fontSize=self.font_size,
            leading=self.font_size + 2,
        )
        header_style = ParagraphStyle(
            "header",
            parent=styles["Normal"],
            fontName=chosen_font,
            fontSize=self.font_size,
            leading=self.font_size + 2,
            alignment=1,
        )

        # Ensure uniform column count
        colcount = max(len(r) for r in rows)
        table_data = []
        for r_idx, r in enumerate(rows):
            row_cells = []
            for c_idx in range(colcount):
                cell = r[c_idx] if c_idx < len(r) else ""
                    # For header (first row) and for Наименование (second column) use Paragraph to enable wrapping
                    # RU: Для заголовка (первой строки) и колонки "Наименование" используем Paragraph для переноса текста
                if r_idx == 0:
                    row_cells.append(Paragraph(cell, header_style))
                else:
                    if c_idx == 1:  # Наименование
                        row_cells.append(
                            Paragraph(cell.replace("\n", "<br/>"), body_style)
                        )
                    else:
                        row_cells.append(Paragraph(cell, body_style))
            table_data.append(row_cells)

        # Column widths: if not provided, attempt to allocate sensible widths
        if not col_widths:
            # Total printable width (mm to points)
            # RU: Общая доступная ширина для печати (mm -> точки)
            total_width = doc.width
            # Default heuristic: № small, Наименование wide, Цена small, Ед. изм small
            if colcount >= 4:
                col_widths = [40, total_width - 160, 80, 40]
                # If computed negative, fallback to even split
                # RU: Если расчёт дал отрицательное значение, используем равное распределение
                if col_widths[1] < 60:
                    col_widths = [total_width / colcount] * colcount
            else:
                col_widths = [total_width / colcount] * colcount

        tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
        tbl_style = TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
        tbl.setStyle(tbl_style)

        story = []
        story.append(tbl)

        doc.build(story)

    def create_temp_pdf(self, src_csv_path):
        """Создаёт временный PDF (зарегистрированный для последующей очистки) и возвращает путь."""
        import tempfile

        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tf.close()
        self.export_csv_to_pdf(src_csv_path, tf.name)
        # register for deletion on close
        # RU: регистрируем для удаления при закрытии
        global _TEMP_FILES
        _TEMP_FILES.append(tf.name)
        return tf.name

    def register_font(self, font_path):
        """Регистрирует указанный TTF и обновляет используемое имя шрифта."""
        name = None
        try:
            name = _register_cyrillic_font(font_path=font_path)
        except Exception:
            name = None
        if name:
            self.font_name = name
            self.font_path = font_path
            return True
        return False
