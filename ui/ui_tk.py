import threading
import queue
import csv
from datetime import datetime
from tkinter import (
    Tk,
    Text,
    END,
    filedialog,
    Label,
    BOTH,
    Frame,
    Toplevel,
)
from tkinter import ttk
from scraper import open_web, get_all_links_stream, get_page_data
from storage import save_categories, save_categories_partial, write_data_csv
from .tooltip import Tooltip
from .queue_writer import QueueWriter
from .ui_utils import shorten_name
from .ui_animator import ProgressAnimator
from .ui_style import PADDING, SMALL_PADDING, PROGRESS_WIDTH, LOG_HEIGHT
from tabs.print_tab import make_tab as make_print_tab
from tabs.settings_tab import make_tab as make_settings_tab
from .ui_controller import UIController
from tabs.print_service import cleanup_temp_files
import os
import sys

# from rascenki_kz import open_web, get_all_links, save_categories, get_page_data, write_data_csv
# RU: используем функции из rascenki_kz


class App:
    def __init__(self):
        """Initialize the main application window and user interface.

        This constructs the main Tk window, sets up the Notebook with tabs,
        initializes the queue and background worker threads, and prepares
        UI helpers (progress animator, tooltip manager, log widget).

        Документация (RU):
        Инициализация главного окна и интерфейса приложения. Создаёт
        главное окно Tk, Notebook с вкладками, очередь и фоновые
        потоки, а также вспомогательные компоненты (анимация прогресса,
        менеджер тултипов, виджет лога).
        """
        # Load settings using the dedicated config loader (see `config.py`)
        try:
            from config import load_settings

            cfg = load_settings()
            self.print_font_path = cfg.get("print_font_path")
            self.base_url = cfg.get("base_url", "https://rascenki.kz")
            self.poisk = cfg.get("poisk", "https://rascenki.kz/city/astana/")
            # collection settings
            self.collect_batch_size = cfg.get("collect_batch_size", 50)
            self.collect_max_categories = cfg.get("collect_max_categories", None)
        except Exception:
            # Fallback defaults
            self.print_font_path = None
            self.base_url = "https://rascenki.kz"
            self.poisk = "https://rascenki.kz/city/astana/"
            self.collect_batch_size = 50
            self.collect_max_categories = None

        # Initialize UI and worker subsystems in dedicated methods to keep
        # __init__ concise and readable.
        self._init_ui()
        self._init_workers()

    def _load_or_collect_categories_on_start(self):
        """Загружает последний файл категорий формата ddmmyyyy.csv если есть,
        иначе пробует загрузить legacy `cat_a.csv`, если ни одного файла нет — запускает сбор.
        """
        import os
        import re

        files = os.listdir(os.getcwd())
        # Ищем файлы формата ddmmyyyy.csv (8 цифр перед .csv)
        date_files = []
        for fn in files:
            if re.match(r"^\d{8}\.csv$", fn):
                date_files.append(fn)
        chosen = None
        if date_files:
            # выбрать последний по дате, парся из имени (формат ddmmyyyy)
            def file_date_key(name):
                try:
                    return datetime.strptime(name[:-4], "%d%m%Y")
                except Exception:
                    return datetime.min

            date_files.sort(key=file_date_key, reverse=True)
            chosen = date_files[0]
        elif "cat_a.csv" in files:
            chosen = "cat_a.csv"

        if chosen:
            try:
                if self._load_categories_from_file(chosen):
                    self.lbl.config(
                        text=f"Состояние: загружено {len(self.glava)} категорий из {chosen}"
                    )
                    self.log.insert(END, f"Загружены категории из {chosen}\n")
                    self.progress["value"] = 100
                    return
            except Exception as e:
                self.log.insert(END, f"Ошибка загрузки {chosen}: {e}\n")

        # Ни одного файла нет — запускаем сбор ссылок
        self.log.insert(END, "Каталога ссылок не найдено — запущен сбор...\n")
        self.start_parsing()

    def run(self):
        """Запускает главный цикл приложения."""
        self.root.mainloop()

    def _init_ui(self):
        """Initialize the Tk UI: root window, notebook, tabs, status and log widgets.

        RU: Инициализация UI: главное окно, вкладки, панель состояния и лог.
        """
        self.root = Tk()
        self.root.title("Parser")
        self.root.geometry("1200x600")

        # Notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=PADDING, pady=SMALL_PADDING)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # controller adapter to decouple tabs from App
        try:
            self.controller = UIController(self)
        except Exception:
            self.controller = None

        # Create tabs (each tab registers widgets via controller)
        try:
            from tabs.categories_tab import make_tab as make_categories_tab

            self.tab_cat = make_categories_tab(self.notebook, self.controller)
            self.notebook.add(self.tab_cat, text="Категории")
        except Exception:
            pass

        try:
            from tabs.price_tab import make_tab as make_price_tab

            self.tab_price = make_price_tab(self.notebook, self.controller or self)
            self.notebook.add(self.tab_price, text="Просмотр price.csv")
        except Exception:
            pass

        # Top status/progress panel
        top_frame = Frame(self.root)
        top_frame.pack(fill="x", padx=PADDING, pady=SMALL_PADDING)

        self.lbl = Label(top_frame, text="Состояние: готов")
        self.lbl.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(
            top_frame, orient="horizontal", length=PROGRESS_WIDTH, mode="determinate"
        )
        self.progress.grid(row=0, column=1, sticky="w", padx=8)

        self.progress_log = Label(top_frame, text="", width=60, anchor="w")
        self.progress_log.grid(row=0, column=2, sticky="w", padx=8)

        self._animator = ProgressAnimator(self.root, self.progress)

        # Print / Settings tabs
        try:
            self.tab_print = make_print_tab(self.notebook, self.controller or self)
            self.notebook.add(self.tab_print, text="Печать / PDF")
        except Exception:
            pass
        try:
            self.tab_settings = make_settings_tab(self.notebook, self.controller or self)
            self.notebook.add(self.tab_settings, text="Настройки")
        except Exception:
            pass

        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # Log widget
        self.log = Text(self.root, height=LOG_HEIGHT)
        self.log.pack(fill="both", expand=False, padx=PADDING, pady=SMALL_PADDING)

        # Helper fields
        self.queue = queue.Queue()
        self.worker_thread = None
        self.parse_thread = None
        self.links = []
        self.glava = []
        self._full_names = {}
        self._tooltip = None
        self._tooltip_label = None
        self._tooltip_after_id = None
        self._tooltip_row = None
        self._tooltip_delay_ms = 300

        # Tooltip manager (attach to price_tree if present)
        try:
            self._tooltip_mgr = Tooltip(
                self.root, wrap_width=400, delay_ms=self._tooltip_delay_ms
            )
            if hasattr(self, "price_tree"):
                try:
                    self._tooltip_mgr.bind_to(
                        self.price_tree,
                        lambda item: self._full_names.get(item, self.price_tree.set(item, "Наименование")),
                        column=2,
                    )
                except Exception:
                    pass
                try:
                    self.price_tree.bind("<Motion>", self._on_price_motion)
                    self.price_tree.bind("<Leave>", self._on_price_leave)
                except Exception:
                    pass
        except Exception:
            self._tooltip_mgr = None

    def _init_workers(self):
        """Initialize worker-related scheduling and start queue polling.

        RU: Инициализация вспомогательных потоков/планировщика и запуск опроса очереди.
        """
        # Attempt to load categories on startup; if not found — start collection
        self._load_or_collect_categories_on_start()
        # Start polling the queue for events from background threads
        self.root.after(100, self._poll_queue)

    # ----- Сбор ссылок (как ранее)
    def start_parsing(self):
        """Запускает процесс сбора ссылок."""
        if self.worker_thread and self.worker_thread.is_alive():
            return
        self.log.delete(1.0, END)
        self.progress["value"] = 0
        self.lbl.config(text="Состояние: запускается сбор ссылок...")
        self.links = []
        self.glava = []
        self.btn_collect.config(state="disabled")
        self.disable_selection_controls()
        self.cat_listbox.delete(0, END)

        self.worker_thread = threading.Thread(target=self._worker_collect, daemon=True)
        self.worker_thread.start()

    def _worker_collect(self):
        """Фоновый рабочий поток для сбора ссылок."""
        try:
            start = datetime.now()
            self.queue.put(("log", f"Начало сбора: {start.isoformat()}"))
            url = (
                getattr(self, "base_url", "https://rascenki.kz")
                or "https://rascenki.kz"
            )
            poisk = (
                getattr(self, "poisk", "https://rascenki.kz/city/astana/")
                or "https://rascenki.kz/city/astana/"
            )

            html = open_web(url)
            if not html:
                self.queue.put(("log", "Не удалось получить главную страницу"))
                self.queue.put(("done_collect", False))
                return

            def progress_cb(processed, total, found):
                self.queue.put(("progress", processed, total, found))

            self.queue.put(("log", "Сбор ссылок..."))

            # Параметры частичного сохранения
            batch_size = getattr(self, "collect_batch_size", 50)
            buffer = []
            found_total = 0

            # Перехват stdout — используем QueueWriter из ui_utils (на случай print в парсере)
            orig_stdout = sys.stdout
            qwriter = QueueWriter(self.queue)
            try:
                sys.stdout = qwriter
                # Проход по streaming-генератору
                maxc = getattr(self, "collect_max_categories", None)
                for link, title in get_all_links_stream(
                    html, poisk, progress_callback=progress_cb, max_categories=maxc
                ):
                    try:
                        buffer.append((title, link))
                        self.links.append(link)
                        self.glava.append(title)
                        found_total += 1
                        # Push incremental update to UI
                        try:
                            self.queue.put(("new_category", title, link, found_total))
                        except Exception:
                            pass
                        # Флешим пачки на диск
                        if len(buffer) >= batch_size:
                            try:
                                appended = save_categories_partial(buffer)
                                self.queue.put(
                                    (
                                        "log",
                                        f"Сохранено {appended} категорий (частично)",
                                    )
                                )
                            except Exception as e:
                                self.queue.put(
                                    ("log", f"Ошибка частичного сохранения: {e}")
                                )
                            buffer.clear()
                    except Exception:
                        # не прерываем весь поток при ошибке отдельной записи
                        pass
            finally:
                sys.stdout = orig_stdout
                qwriter.flush()

            # Сохранить остаток
            try:
                if buffer:
                    appended = save_categories_partial(buffer)
                    self.queue.put(("log", f"Сохранено {appended} категорий (остаток)"))
                    buffer.clear()
            except Exception as e:
                self.queue.put(("log", f"Ошибка сохранения остатка: {e}"))

            duration = datetime.now() - start
            self.queue.put(("log", f"Найдено {len(self.glava)} категорий — {duration}"))
            # Если вообще ничего не найдено — возможно ошибка
            if not self.glava:
                self.queue.put(("done_collect", False))
            else:
                # Сохраняем итоговый файл с датой (копия полного списка)
                try:
                    saved_name = save_categories(self.glava, self.links)
                    self.queue.put(("log", f"Итоговый файл сохранён: {saved_name}"))
                except Exception as e:
                    self.queue.put(("log", f"Ошибка сохранения итогового файла: {e}"))
                self.queue.put(("done_collect", True))
        except Exception as e:
            self.queue.put(("log", f"Ошибка: {e}"))
            self.queue.put(("done_collect", False))

    def _on_collect_done(self, ok: bool):
        """Обработчик завершения сбора ссылок."""
        self.btn_collect.config(state="normal")
        if ok and self.glava:
            # заполнить список
            self.cat_listbox.delete(0, END)
            for name, link in zip(self.glava, self.links):
                display = f"{name} — {link}"
                self.cat_listbox.insert(END, display)
            self.enable_selection_controls()
            self.lbl.config(
                text=f"Состояние: готов — найдено {len(self.glava)} категорий"
            )
            self.progress["value"] = 100
        else:
            self.lbl.config(text="Состояние: ошибка сбора")

    # ----- Управление отметками
    def enable_selection_controls(self):
        """Включает кнопки управления отметками."""
        self.btn_mark_all.config(state="normal")
        self.btn_unmark.config(state="normal")
        self.btn_parse_selected.config(state="normal")
        self.btn_save_selected.config(state="normal")

    def disable_selection_controls(self):
        """Отключает кнопки управления отметками."""
        self.btn_mark_all.config(state="disabled")
        self.btn_unmark.config(state="disabled")
        self.btn_parse_selected.config(state="disabled")
        self.btn_save_selected.config(state="disabled")

    def mark_all(self):
        """Отмечает все категории в списке."""
        self.cat_listbox.select_set(0, END)

    def unmark_all(self):
        """Снимает отметки со всех категорий в списке."""
        self.cat_listbox.select_clear(0, END)

    # ----- Сохранение отмеченных категорий
    def save_selected(self):
        """Сохраняет отмеченные категории в файл."""
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="selected_cat.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Название категории", "Ссылка"])
                for i in sel:
                    writer.writerow([self.glava[i], self.links[i]])
            self.log.insert(END, f"Отмеченные сохранены в {path}\n")
        except Exception as e:
            self.log.insert(END, f"Ошибка сохранения: {e}\n")

    def load_categories_file(self):
        """Загружает категории из файла."""
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            if self._load_categories_from_file(path):
                self.log.insert(END, f"Загружены категории из {path}\n")
                self.lbl.config(
                    text=f"Состояние: загружено {len(self.glava)} категорий из {path}"
                )
                self.progress["value"] = 100
        except Exception as e:
            self.log.insert(END, f"Ошибка загрузки {path}: {e}\n")

    def _load_categories_from_file(self, path):
        """Читает CSV с форматом (Название категории, Ссылка) и заполняет Listbox.
        Возвращает True при успехе.
        """
        import csv

        glava = []
        links = []
        with open(path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if row[0] == "Название категории":
                    continue
                name = row[0]
                link = row[1] if len(row) > 1 else ""
                glava.append(name)
                links.append(link)
        if not glava:
            return False
        self.glava = glava
        self.links = links
        self.cat_listbox.delete(0, END)
        for name, link in zip(self.glava, self.links):
            display = f"{name} — Ок!"
            self.cat_listbox.insert(END, display)
        self.enable_selection_controls()
        return True

    # ----- Парсинг отмеченных категорий (фоновый)
    def parse_selected(self):
        """Запускает парсинг отмеченных категорий."""
        sel = self.cat_listbox.curselection()
        if not sel:
            self.log.insert(END, "Нет отмеченных категорий для парсинга\n")
            return
        if self.parse_thread and self.parse_thread.is_alive():
            return
        self.parse_thread = threading.Thread(
            target=self._worker_parse_selected, args=(list(sel),), daemon=True
        )
        self.parse_thread.start()
        self.btn_parse_selected.config(state="disabled")
        self.btn_collect.config(state="disabled")

    def _worker_parse_selected(self, indices):
        """Фоновый рабочий поток для парсинга отмеченных категорий."""
        try:
            total = len(indices)
            self.queue.put(("log", f"Начало парсинга {total} категорий..."))
            # Перед началом парсинга очищаем/перезаписываем файл price.csv,
            # чтобы результат текущего запуска был в новом файле.
            try:
                # Создаём новый price.csv с заголовком
                with open("price.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["№", "Наименование", "Цена", "Ед. изм"])
                self.queue.put(
                    ("log", "price.csv создан и очищен (заголовок добавлен)")
                )
            except Exception as e:
                self.queue.put(("log", f"Не удалось очистить price.csv: {e}"))
            # Локальный счётчик парсированных категорий для этого запуска
            parsed_counter = 0
            for idx, i in enumerate(indices, start=1):
                name = self.glava[i]
                link = self.links[i]
                self.queue.put(("log", f"[{idx}/{total}] {name} -> {link}"))
                self.queue.put(("progress_parse", idx, total))
                html = open_web(link)
                if not html:
                    self.queue.put(("log", f"Не удалось получить {link}"))
                    continue
                try:
                    blok = get_page_data(html, name)
                    parsed_counter += 1
                    write_data_csv(blok)
                    self.queue.put(("log", f"{parsed_counter}. {name} - PARSED!"))
                except Exception as e:
                    self.queue.put(("log", f"Ошибка парсинга {name}: {e}"))
            self.queue.put(("done_parse", True))
        except Exception as e:
            self.queue.put(("log", f"Ошибка в парсере: {e}"))
            self.queue.put(("done_parse", False))

    # ----- Просмотр и экспорт price.csv
    def load_price_csv(self):
        """Загружает данные из price.csv и отображает их в Treeview."""
        path = os.path.join(os.getcwd(), "price.csv")
        if not os.path.exists(path):
            self.log.insert(END, "price.csv не найден\n")
            return
        # Очистка дерева
        for i in self.price_tree.get_children():
            self.price_tree.delete(i)
        # Очистить кэш полных имён
        self._full_names.clear()
        try:
            with open(path, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    # если строка пустая - пропускаем
                    if not row:
                        continue
                    # Пропускаем строку-заголовок, если она есть
                    if (
                        len(row) >= 2
                        and row[0].strip() == "№"
                        and row[1].strip() == "Наименование"
                    ):
                        continue
                    # Попытка привести до 4 столбцов
                    while len(row) < 4:
                        row.append("")
                    # Очищаем поля от лишних пробелов
                    r0 = row[0].strip()
                    r1 = row[1].strip()
                    r2 = row[2].strip()
                    r3 = row[3].strip()
                    # Сокращённая версия для отображения
                    display = shorten_name(r1, max_chars=100)
                    item_id = self.price_tree.insert(
                        "", END, values=(r0, display, r2, r3)
                    )
                    # Сохраняем полное наименование отдельно
                    self._full_names[item_id] = r1
            self.log.insert(END, "price.csv загружен\n")
        except Exception as e:
            self.log.insert(END, f"Ошибка чтения price.csv: {e}\n")

    # Shorten helper moved to ui_utils.shorten_name

    def _on_price_row_select(self, event=None):
        """Legacy hook left for compatibility; most behavior is handled by PriceViewHelper."""
        try:
            sel = self.price_tree.selection()
            if not sel:
                return
            item = sel[0]
            full = self._full_names.get(item, self.price_tree.set(item, "Наименование"))
            if full:
                self.progress_log.config(text=full)
        except Exception:
            pass

    def _on_price_double_click(self, event):
        # kept for backward compatibility; PriceViewHelper handles double-click
        try:
            item_id = self.price_tree.identify_row(event.y)
            if not item_id:
                return
            full = self._full_names.get(item_id, self.price_tree.set(item_id, "Наименование"))
            if not full:
                return
            top = Toplevel(self.root)
            top.title("Наименование")
            txt = Text(top, wrap="word", height=10, width=80)
            txt.pack(fill=BOTH, expand=True)
            txt.insert(END, full)
            txt.config(state="disabled")
        except Exception:
            pass

    # Tooltip handlers for Treeview rows
    def _on_price_motion(self, event):
        # legacy hook — behavior provided by PriceViewHelper
        return

    def _on_price_leave(self, event):
        # legacy hook — behavior provided by PriceViewHelper
        return

    def _show_tooltip(self, full_text, x, y):
        # legacy hook — behavior provided by PriceViewHelper
        return

    def _destroy_tooltip(self):
        # legacy hook — behavior provided by PriceViewHelper
        try:
            if getattr(self, "_tooltip", None):
                try:
                    self._tooltip.destroy()
                except Exception:
                    pass
        except Exception:
            pass

    def export_price_csv(self):
        """Экспортирует данные из price.csv в выбранный файл."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="price_export.csv",
        )
        if not path:
            return
        src = os.path.join(os.getcwd(), "price.csv")
        if not os.path.exists(src):
            self.log.insert(END, "price.csv не найден для экспорта\n")
            return
        try:
            with open(src, "rb") as fin, open(path, "wb") as fout:
                fout.write(fin.read())
            self.log.insert(END, f"Экспортировано в {path}\n")
        except Exception as e:
            self.log.insert(END, f"Ошибка экспорта: {e}\n")

    def _update_status_line(self, text: str):
        """Обновляет однострочный статус в верхней панели (не добавляет в основной лог)."""
        try:
            # Используем выделенный Label `self.progress_log` для однострочного состояния
            self.progress_log.config(text=text)
        except Exception:
            # Ничего не делаем при ошибке обновления виджета
            pass

    def _on_tab_changed(self, event):
        """Вызывается при смене вкладки; если выбрана вкладка просмотра price.csv — загружаем файл."""
        try:
            widget = event.widget
            cur_index = widget.index("current")
            tab_text = widget.tab(cur_index, "text")
            if tab_text == "Просмотр price.csv":
                # При открытии вкладки автоматически загружаем последний price.csv
                self.load_price_csv()
        except Exception:
            pass

    def _on_close(self):
        """Обработчик закрытия приложения — выполняет очистку временных файлов, затем закрывает окно."""
        try:
            cleanup_temp_files()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            try:
                import sys

                sys.exit(0)
            except Exception:
                pass

    # Progress animation handled by ui_utils.ProgressAnimator

    # ----- Очередь событий из потоков
    def _poll_queue(self):
        """Опрашивает очередь событий из потоков и обновляет интерфейс."""
        try:
            while True:
                item = self.queue.get_nowait()
                tag = item[0]
                if tag == "log":
                    self.log.insert(END, item[1] + "\n")
                    self.log.see(END)
                elif tag == "status":
                    # Однострочный статус — перезаписываем
                    self._update_status_line(item[1])
                    self.log.see(END)
                elif tag == "new_category":
                    # incremental category discovered during collection
                    title = item[1]
                    link = item[2]
                    idx = item[3] if len(item) > 3 else None
                    try:
                        display = f"{title} — {link}"
                        self.cat_listbox.insert(END, display)
                        # ensure controls enabled once we have at least one
                        self.enable_selection_controls()
                        # update small status line
                        if idx:
                            self._update_status_line(f"Найдено {idx} категорий")
                    except Exception:
                        pass
                elif tag == "progress":
                    processed, total, found = item[1], item[2], item[3]
                    if total and total > 0:
                        percent = max(0.0, min(100.0, processed / total * 100))
                        # Анимируем прогрессбар (макс. время перехода 3000ms)
                        try:
                            self._animator.animate_to(percent, max_duration_ms=3000)
                        except Exception:
                            pass
                        # Перезаписываем однострочный прогресс в логе
                        self._update_status_line(
                            f"Сканирование: {processed}/{total} ({percent:.1f}%) — найдено {found}"
                        )
                        self.lbl.config(text="Состояние: сбор ссылок")
                    else:
                        self._update_status_line(f"Найдено {found} категорий")
                        self.lbl.config(text="Состояние: сбор ссылок")
                elif tag == "done_collect":
                    ok = item[1]
                    self._on_collect_done(ok)
                elif tag == "progress_parse":
                    idx, total = item[1], item[2]
                    percent = idx / total * 100 if total else 0
                    # Анимируем прогресс при парсинге (быстрее, но не дольше 2000ms)
                    try:
                        self._animator.animate_to(percent, max_duration_ms=2000)
                    except Exception:
                        pass
                    # Перезаписываем однострочный прогресс парсинга в логе
                    self._update_status_line(f"Парсинг: {idx}/{total} ({percent:.1f}%)")
                    self.lbl.config(text="Состояние: парсинг")
                elif tag == "done_parse":
                    ok = item[1]
                    self.btn_parse_selected.config(state="normal")
                    self.btn_collect.config(state="normal")
                    if ok:
                        self.lbl.config(text="Парсинг завершён")
                        self._update_status_line("Готово")
                        self.log.insert(END, "Парсинг отмеченных категорий завершён\n")
                    else:
                        self.lbl.config(text="Парсинг завершён с ошибкой")
                else:
                    self.log.insert(END, f"Неизвестное сообщение: {item}\n")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

# `ui_tk.py` теперь содержит только реализацию `App` —
# запуск приложения выполняется из `main.py`.

