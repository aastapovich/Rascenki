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
