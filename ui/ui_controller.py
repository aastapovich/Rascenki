"""UI Controller adapter moved into `ui` package.

This is the same `UIController` class but now lives under `ui.ui_controller`.
"""
from typing import Any


class UIController:
    def __init__(self, app: Any):
        object.__setattr__(self, "_app", app)

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_app"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_app":
            object.__setattr__(self, name, value)
        else:
            setattr(object.__getattribute__(self, "_app"), name, value)

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

    def register_price_tree(self, tree) -> None:
        try:
            self._app.price_tree = tree
        except Exception:
            pass
        try:
            # use helper from same package
            from .ui_price_helpers import PriceViewHelper

            try:
                PriceViewHelper(self._app, tree, wrap_width=400, delay_ms=getattr(self._app, "_tooltip_delay_ms", 300))
            except Exception:
                try:
                    def _sel(e=None):
                        try:
                            sel = tree.selection()
                            if not sel:
                                return
                            item = sel[0]
                            full = self._app._full_names.get(item, tree.set(item, "Наименование"))
                            if full:
                                self._app.progress_log.config(text=full)
                        except Exception:
                            pass

                    tree.bind('<<TreeviewSelect>>', _sel)
                except Exception:
                    pass
        except Exception:
            pass

    def save_settings(self, cfg: dict) -> bool:
        try:
            import os, json

            p = os.path.join(os.getcwd(), "settings.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
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
        try:
            import os, json

            p = os.path.join(os.getcwd(), "settings.json")
            if not os.path.exists(p):
                return None
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
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
