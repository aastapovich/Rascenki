"""Helpers to manage Treeview interactions for the price viewer.

Provides `PriceViewHelper` which wires tooltip-on-hover, double-click to
open full name, and selection handler for the `ttk.Treeview`.
"""
from __future__ import annotations
from tkinter import Toplevel, Text, BOTH, END, Message
from typing import Any


class PriceViewHelper:
    def __init__(self, app: Any, tree, wrap_width: int = 400, delay_ms: int = 300):
        self.app = app
        self.tree = tree
        self.wrap_width = wrap_width
        # store as private to avoid accidental shadowing by property
        self._delay_ms = delay_ms
        self._after_id = None
        self._tooltip = None
        self._tooltip_label = None
        self._row = None

        # bind events
        try:
            tree.bind("<Motion>", self._on_motion)
            tree.bind("<Leave>", self._on_leave)
            tree.bind("<<TreeviewSelect>>", self._on_select)
            tree.bind("<Double-1>", self._on_double_click)
        except Exception as e:
            try:
                print(f"ui_price_helpers: error binding tree events: {e}")
            except Exception:
                pass

    def _on_select(self, event=None):
        try:
            sel = self.tree.selection()
            if not sel:
                return
            item = sel[0]
            full = self.app._full_names.get(item, self.tree.set(item, "Наименование"))
            if not full:
                return
            self.app.progress_log.config(text=full)
        except Exception as e:
            try:
                print(f"ui_price_helpers: error in _on_select: {e}")
            except Exception:
                pass

    def _on_double_click(self, event):
        try:
            item_id = self.tree.identify_row(event.y)
            if not item_id:
                return
            full = self.app._full_names.get(item_id, self.tree.set(item_id, "Наименование"))
            if not full:
                return
            top = Toplevel(self.app.root)
            top.title("Наименование")
            txt = Text(top, wrap="word", height=10, width=80)
            txt.pack(fill=BOTH, expand=True)
            txt.insert(END, full)
            txt.config(state="disabled")
        except Exception as e:
            try:
                print(f"ui_price_helpers: error in _on_double_click: {e}")
            except Exception:
                pass

    def _on_motion(self, event):
        try:
            rowid = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if not rowid or col != "#2":
                if self._after_id:
                    try:
                        self.app.root.after_cancel(self._after_id)
                    except Exception as e:
                        try:
                            print(f"ui_price_helpers: error cancelling after_id: {e}")
                        except Exception:
                            pass
                    self._after_id = None
                self._destroy_tooltip()
                return

            if self._row == rowid and self._tooltip and getattr(self, "_tooltip_label", None):
                try:
                    self._tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
                except Exception as e:
                    try:
                        print(f"ui_price_helpers: error in deferred tooltip show: {e}")
                    except Exception:
                        pass
                return

            if self._after_id:
                try:
                    self.app.root.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None

            self._row = rowid

            def _deferred(r=rowid, xr=event.x_root, yr=event.y_root):
                try:
                    if self._row != r:
                        return
                    full = self.app._full_names.get(r, self.tree.set(r, "Наименование"))
                    if not full:
                        return
                    self._show_tooltip(full, xr + 20, yr + 10)
                except Exception:
                    pass
            try:
                self._after_id = self.app.root.after(self._delay_ms, _deferred)
            except Exception as e:
                try:
                    _deferred()
                except Exception as e2:
                    try:
                        print(f"ui_price_helpers: error scheduling/deferred: {e} / {e2}")
                    except Exception:
                        pass
        except Exception as e:
            try:
                print(f"ui_price_helpers: error in _on_motion: {e}")
            except Exception:
                pass

    @property
    def delay_ms(self) -> int:
        return self._delay_ms

    def _on_leave(self, event):
        if self._after_id:
            try:
                self.app.root.after_cancel(self._after_id)
            except Exception as e:
                try:
                    print(f"ui_price_helpers: error positioning tooltip: {e}")
                except Exception:
                    pass
            self._after_id = None
        self._row = None
        self._destroy_tooltip()

    def _show_tooltip(self, full_text: str, x: int, y: int):
        self._destroy_tooltip()
        try:
            self._tooltip = Toplevel(self.app.root)
            self._tooltip.wm_overrideredirect(True)
            try:
                self._tooltip.attributes("-topmost", True)
            except Exception:
                pass
            msg = Message(
                self._tooltip,
                text=full_text,
                justify="left",
                background="#ffffe0",
                foreground="black",
                relief="solid",
                borderwidth=1,
                width=self.wrap_width,
            )
            msg.pack(ipadx=6, ipady=4)
            self._tooltip_label = msg
            try:
                self._tooltip.update_idletasks()
                tw = self._tooltip.winfo_width()
                th = self._tooltip.winfo_height()
                sw = self.app.root.winfo_screenwidth()
                sh = self.app.root.winfo_screenheight()
                nx = x
                ny = y
                if nx + tw + 10 > sw:
                    nx = max(10, sw - tw - 10)
                if ny + th + 10 > sh:
                    ny = max(10, sh - th - 10)
                self._tooltip.geometry(f"+{nx}+{ny}")
            except Exception:
                try:
                    self._tooltip.geometry(f"+{x}+{y}")
                except Exception:
                    pass
        except Exception as e:
            try:
                print(f"ui_price_helpers: error showing tooltip: {e}")
            except Exception:
                pass
            self._destroy_tooltip()

    def _destroy_tooltip(self):
        if getattr(self, "_tooltip", None):
            try:
                self._tooltip.destroy()
            except Exception as e:
                try:
                    print(f"ui_price_helpers: error destroying tooltip: {e}")
                except Exception:
                    pass
        self._tooltip = None
        self._tooltip_label = None
