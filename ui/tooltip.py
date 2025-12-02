"""Tooltip helper for Treeview-like widgets.

Contains the `Tooltip` class previously located in `ui_utils.py`.
"""
from __future__ import annotations

from tkinter import Toplevel, Message
from typing import Any


class Tooltip:
    def __init__(self, root, wrap_width: int = 400, delay_ms: int = 300):
        self.root = root
        self.wrap_width = wrap_width
        self.delay_ms = delay_ms
        self._after_id = None
        self._tooltip = None
        self._tooltip_label = None
        self._row = None

    def bind_to(self, tree, get_full_func, column=2):
        def _motion(event):
            try:
                rowid = tree.identify_row(event.y)
                col = tree.identify_column(event.x)
                if not rowid or col != f"#{column}":
                    if self._after_id:
                        try:
                            self.root.after_cancel(self._after_id)
                        except Exception:
                            pass
                        self._after_id = None
                    self._destroy()
                    return
                if self._row == rowid and self._tooltip:
                    try:
                        self._tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
                    except Exception:
                        pass
                    return
                if self._after_id:
                    try:
                        self.root.after_cancel(self._after_id)
                    except Exception:
                        pass
                    self._after_id = None

                    self._row = rowid

                def _deferred(r=rowid, xr=event.x_root, yr=event.y_root):
                    try:
                        if self._row != r:
                            return
                        full = get_full_func(r)
                        if not full:
                            return
                        self._show(full, xr + 20, yr + 10)
                    except Exception:
                        pass

                try:
                    self._after_id = self.root.after(self.delay_ms, _deferred)
                except Exception:
                    try:
                        _deferred()
                    except Exception:
                        pass
            except Exception:
                pass

        def _leave(event):
            if self._after_id:
                try:
                    self.root.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None
            self._row = None
            self._destroy()

        tree.bind("<Motion>", _motion)
        tree.bind("<Leave>", _leave)

    def _show(self, full_text, x, y):
        self._destroy()
        try:
            self._tooltip = Toplevel(self.root)
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
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
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
        except Exception:
            self._destroy()

    def _destroy(self):
        if self._tooltip:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
        self._tooltip = None
        self._tooltip_label = None
