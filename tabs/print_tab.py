"""Print tab — export `price.csv` to PDF.

Uses `reportlab` to generate a simple tabular PDF. If `reportlab` is
not installed, the UI will prompt to install the package.

RU: Вкладка 'Печать' — экспорт `price.csv` в PDF.

RU: Использует `reportlab` для генерации простого табличного PDF.
RU: Если `reportlab` не установлен, показывает подсказку установить пакет.
"""

import os
import subprocess
from tkinter import Frame, Label, Button, messagebox, IntVar, StringVar
from tkinter import filedialog
from tkinter import ttk
from ui.ui_style import PADDING, SMALL_PADDING

from .print_service import PrintService


def make_tab(parent, ctrl):
    """Create the 'Print / PDF' tab for exporting `price.csv` to PDF.

    Uses `PrintService` to generate a PDF from `price.csv`. The tab exposes
    options for orientation and font size and supports export, preview, and
    print actions. If a font path is set on the controller, it will be used
    for PDF rendering.

    Документация (RU):
    Создаёт вкладку «Печать / Экспорт в PDF» для экспорта `price.csv` в PDF.
    Использует `PrintService` для генерации PDF. Вкладка предоставляет
    параметры ориентации и размера шрифта, а также действия: экспорт,
    предпросмотр и печать. Если путь к шрифту задан в контроллере,
    он будет использован при генерации PDF.
    """
    frame = Frame(parent)

    lbl = Label(frame, text="Печать / Экспорт в PDF")
    lbl.pack(anchor="w", padx=PADDING, pady=PADDING)

    help_lbl = Label(
        frame,
        text="Экспортирует `price.csv` в PDF. Длинные наименования автоматически переносятся.",
    )
    help_lbl.pack(anchor="w", padx=PADDING)

    # Layout / formatting settings
    # RU: Настройки оформления
    settings_frame = Frame(frame)
    settings_frame.pack(fill="x", padx=PADDING, pady=SMALL_PADDING)

    orientation_var = StringVar(value="portrait")
    Label(settings_frame, text="Ориентация:").pack(side="left")
    or_portrait = ttk.Radiobutton(
        settings_frame, text="Портрет", variable=orientation_var, value="portrait"
    )
    or_landscape = ttk.Radiobutton(
        settings_frame, text="Ландшафт", variable=orientation_var, value="landscape"
    )
    or_portrait.pack(side="left", padx=4, pady=2)
    or_landscape.pack(side="left", padx=4, pady=2)

    Label(settings_frame, text="Шрифт, размер:").pack(side="left", padx=8)
    font_size_var = IntVar(value=9)
    font_size_spin = ttk.Spinbox(
        settings_frame, from_=6, to=20, width=4, textvariable=font_size_var
    )
    font_size_spin.pack(side="left", pady=2)

    btn_frame = Frame(frame)
    btn_frame.pack(fill="x", padx=PADDING, pady=8)

    def _do_export(dest):
        src = os.path.join(os.getcwd(), "price.csv")
        if not os.path.exists(src):
            messagebox.showerror(
                "Ошибка", "Файл price.csv не найден в текущей директории"
            )
            return False
        # Use font path from settings if provided
        # RU: Используем выбранный в настройках путь шрифта, если он есть
        font_path = getattr(ctrl, "print_font_path", None)
        svc = PrintService(
            orientation=orientation_var.get(),
            font_size=font_size_var.get(),
            font_path=font_path,
        )
        try:
            svc.export_csv_to_pdf(src, dest)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))
            return False

    def _on_export_pdf():
        dest = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="price.pdf",
        )
        if not dest:
            return
        if _do_export(dest):
            messagebox.showinfo("Готово", f"Экспорт в PDF завершён: {dest}")

    def _on_preview():
        try:
            src = os.path.join(os.getcwd(), "price.csv")
            if not os.path.exists(src):
                messagebox.showerror(
                    "Ошибка", "Файл price.csv не найден в текущей директории"
                )
                return
            font_path = getattr(ctrl, "print_font_path", None)
            svc = PrintService(
                orientation=orientation_var.get(),
                font_size=font_size_var.get(),
                font_path=font_path,
            )
            tmp = svc.create_temp_pdf(src)
            # macOS: open (attempt) — fallback to platform specific opener
            # RU: macOS: open
            try:
                subprocess.run(["open", tmp], check=False)
            except Exception:
                try:
                    os.startfile(tmp)
                except Exception:
                    messagebox.showinfo("Готово", f"Временный PDF создан: {tmp}")
            # schedule removal after short delay to allow viewer to open the file
            try:
                import threading
                import time

                def _delayed_remove(path):
                    time.sleep(30)
                    try:
                        from .print_service import remove_temp_file

                        remove_temp_file(path)
                    except Exception:
                        try:
                            os.remove(path)
                        except Exception:
                            pass

                threading.Thread(
                    target=_delayed_remove, args=(tmp,), daemon=True
                ).start()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Ошибка предпросмотра", str(e))

    def _on_print():
        try:
            src = os.path.join(os.getcwd(), "price.csv")
            if not os.path.exists(src):
                messagebox.showerror(
                    "Ошибка", "Файл price.csv не найден в текущей директории"
                )
                return
            font_path = getattr(ctrl, "print_font_path", None)
            svc = PrintService(
                orientation=orientation_var.get(),
                font_size=font_size_var.get(),
                font_path=font_path,
            )
            tmp = svc.create_temp_pdf(src)
            try:
                subprocess.run(["lpr", tmp], check=True)
                messagebox.showinfo("Печать", "Файл отправлен на печать (lpr)")
                # remove temp immediately after successful send
                try:
                    from .print_service import remove_temp_file

                    remove_temp_file(tmp)
                except Exception:
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
            except Exception as e:
                messagebox.showerror(
                    "Ошибка печати", f"Не удалось отправить файл на печать: {e}"
                )
        except Exception as e:
            messagebox.showerror("Ошибка печати", str(e))

    btn_export = Button(
        btn_frame, text="Экспорт price.csv -> PDF", command=_on_export_pdf
    )
    btn_export.pack(side="left", padx=4, pady=2)

    btn_preview = Button(btn_frame, text="Предпросмотр", command=_on_preview)
    btn_preview.pack(side="left", padx=4, pady=2)

    btn_print = Button(btn_frame, text="Печать (lpr)", command=_on_print)
    btn_print.pack(side="left", padx=4, pady=2)

    return frame
