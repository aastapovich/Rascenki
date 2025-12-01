"""UI Controller adapter to decouple tabs from App implementation.

Tabs may receive an instance of `UIController` instead of a full
`App`. The controller forwards calls/attributes to the real `App` and
exposes stable helper methods for posting events to the UI queue.

Документация (RU):
Адаптер UI-контроллера для ослабления связи вкладок с реализацией
`App`. Вкладки могут получать экземпляр `UIController` вместо полного
объекта `App`. Контроллер перенаправляет вызовы/атрибуты на реальный
`App` и предоставляет удобные методы для отправки событий в очередь UI.
"""
from typing import Any


class UIController:
    def __init__(self, app: Any):
        # store real app under a private name
        # RU: сохраняем реальный объект app под приватным именем
        object.__setattr__(self, "_app", app)

    # Basic attribute forwarding: read-through to the underlying app
    # Basic attribute forwarding: read-through to the underlying app
    # RU: Проксирование чтения атрибутов к реальному App
    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_app"), name)

    # Writes are forwarded to the underlying app as well (so tabs can assign widgets)
    # RU: Запись атрибутов также перенаправляется на реальный App (чтобы вкладки могли присваивать виджеты)
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_app":
            object.__setattr__(self, name, value)
        else:
            setattr(object.__getattribute__(self, "_app"), name, value)

    # Queue helpers
    # Queue helpers
    # RU: Помощники для постановки сообщений в очередь UI
    def post_log(self, msg: str) -> None:
        try:
            self._app.queue.put(("log", msg))
        except Exception:
            pass

    def post_status(self, msg: str) -> None:
        try:
            self._app.queue.put(("status", msg))
        except Exception:
            pass

    def post_new_category(self, title: str, link: str, idx: int | None = None) -> None:
        try:
            if idx is None:
                self._app.queue.put(("new_category", title, link))
            else:
                self._app.queue.put(("new_category", title, link, idx))
        except Exception:
            pass

    def post_progress(self, processed: int, total: int, found: int) -> None:
        try:
            self._app.queue.put(("progress", processed, total, found))
        except Exception:
            pass

    def post_done_collect(self, ok: bool) -> None:
        try:
            self._app.queue.put(("done_collect", ok))
        except Exception:
            pass

    def post_progress_parse(self, idx: int, total: int) -> None:
        try:
            self._app.queue.put(("progress_parse", idx, total))
        except Exception:
            pass

    def post_done_parse(self, ok: bool) -> None:
        try:
            self._app.queue.put(("done_parse", ok))
        except Exception:
            pass

    # Helper accessors for common app actions (delegates)
    # Helper accessors for common app actions (delegates)
    # RU: Утилитарные делегаты для стандартных действий приложения
    def start_parsing(self) -> None:
        try:
            return self._app.start_parsing()
        except Exception:
            return None

    def load_price_csv(self) -> None:
        try:
            return self._app.load_price_csv()
        except Exception:
            return None

    def export_price_csv(self) -> None:
        try:
            return self._app.export_price_csv()
        except Exception:
            return None

    def parse_selected(self) -> None:
        try:
            return self._app.parse_selected()
        except Exception:
            return None

    def save_selected(self) -> None:
        try:
            return self._app.save_selected()
        except Exception:
            return None

    # Additional small wrappers for common UI actions
    def load_categories_file(self) -> None:
        try:
            return self._app.load_categories_file()
        except Exception:
            return None

    def mark_all(self) -> None:
        try:
            return self._app.mark_all()
        except Exception:
            return None

    def unmark_all(self) -> None:
        try:
            return self._app.unmark_all()
        except Exception:
            return None

    # Register a price Treeview with the app: assign and wire tooltip/handlers
    # Register a price Treeview with the app: assign and wire tooltip/handlers
    # RU: Регистрация Treeview для price: присвоение и привязка тултипа/обработчиков
    def register_price_tree(self, tree) -> None:
        try:
            # attach to app
            self._app.price_tree = tree
        except Exception:
            pass
        try:
            # Attach tooltip manager if available (create if needed)
            # RU: Подключаем менеджер тултипов, если он доступен (создаем при необходимости)
            if not getattr(self._app, "_tooltip_mgr", None):
                try:
                    from ui_utils import Tooltip

                    self._app._tooltip_mgr = Tooltip(self._app.root, wrap_width=400, delay_ms=getattr(self._app, "_tooltip_delay_ms", 300))
                except Exception:
                    self._app._tooltip_mgr = None
            if getattr(self._app, "_tooltip_mgr", None):
                try:
                    self._app._tooltip_mgr.bind_to(
                        tree,
                        lambda item: self._app._full_names.get(item, tree.set(item, "Наименование")),
                        column=2,
                    )
                except Exception:
                    pass
            # bind mouse motion/leave handlers if present on app
            # RU: привязываем обработчики движения мыши/ухода, если они есть в app
            try:
                tree.bind('<Motion>', getattr(self._app, '_on_price_motion', lambda e=None: None))
            except Exception:
                pass
            try:
                tree.bind('<Leave>', getattr(self._app, '_on_price_leave', lambda e=None: None))
            except Exception:
                pass
            # selection and double-click handlers
            try:
                tree.bind('<<TreeviewSelect>>', getattr(self._app, '_on_price_row_select', lambda e=None: None))
            except Exception:
                pass
            try:
                tree.bind('<Double-1>', getattr(self._app, '_on_price_double_click', lambda e=None: None))
            except Exception:
                pass
        except Exception:
            pass

    # Settings persistence helpers
    def save_settings(self, cfg: dict) -> bool:
        """Persist settings dict to settings.json and apply to app state.

        Returns True on success, False otherwise.
        """
        try:
            import os, json

            p = os.path.join(os.getcwd(), "settings.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            # apply to app
            # RU: применяем значения к атрибутам app
            try:
                self._app.print_font_path = cfg.get("print_font_path")
            except Exception:
                pass
            try:
                self._app.base_url = cfg.get("base_url", getattr(self._app, "base_url", "https://rascenki.kz"))
            except Exception:
                pass
            try:
                self._app.poisk = cfg.get("poisk", getattr(self._app, "poisk", "https://rascenki.kz/city/astana/"))
            except Exception:
                pass
            try:
                self._app.collect_batch_size = cfg.get("collect_batch_size", getattr(self._app, "collect_batch_size", 50))
            except Exception:
                pass
            try:
                self._app.collect_max_categories = cfg.get("collect_max_categories", getattr(self._app, "collect_max_categories", None))
            except Exception:
                pass
            return True
        except Exception:
            return False

    def load_settings(self) -> dict | None:
        """Load settings.json and return dict (or None on error).

        Also applies values to app attributes.
        """
        try:
            import os, json

            p = os.path.join(os.getcwd(), "settings.json")
            if not os.path.exists(p):
                return None
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # apply
            try:
                self._app.print_font_path = cfg.get("print_font_path")
            except Exception:
                pass
            try:
                self._app.base_url = cfg.get("base_url", getattr(self._app, "base_url", "https://rascenki.kz"))
            except Exception:
                pass
            try:
                self._app.poisk = cfg.get("poisk", getattr(self._app, "poisk", "https://rascenki.kz/city/astana/"))
            except Exception:
                pass
            try:
                self._app.collect_batch_size = cfg.get("collect_batch_size", getattr(self._app, "collect_batch_size", 50))
            except Exception:
                pass
            try:
                self._app.collect_max_categories = cfg.get("collect_max_categories", getattr(self._app, "collect_max_categories", None))
            except Exception:
                pass
            return cfg
        except Exception:
            return None
