from tkinter import Toplevel, Message


class QueueWriter:
    def __init__(self, q):
        self.q = q
        self.buf = ""

    def write(self, s):
        if not s:
            return
        self.buf += s
        while True:
            idx_n = self.buf.find("\n")
            idx_r = self.buf.find("\r")
            if idx_n == -1 and idx_r == -1:
                break
            if idx_n == -1:
                idx = idx_r
                sep = "\r"
            elif idx_r == -1:
                idx = idx_n
                sep = "\n"
            else:
                if idx_n < idx_r:
                    idx = idx_n
                    sep = "\n"
                else:
                    idx = idx_r
                    sep = "\r"

            line = self.buf[:idx]
            self.buf = self.buf[idx + 1 :]
            if not line:
                continue
            if sep == "\r":
                # status-like line
                # RU: строка-подобная статусу (обновление в одну строку с \r)
                try:
                    self.q.put(("status", line.strip()))
                except Exception:
                    pass
            else:
                try:
                    self.q.put(("log", line))
                except Exception:
                    pass

    def flush(self):
        if self.buf.strip():
            try:
                self.q.put(("log", self.buf.strip()))
            except Exception:
                pass
        self.buf = ""


def shorten_name(name: str, max_chars: int = 80) -> str:
    if not name:
        return ""
    name = name.strip()
    if len(name) <= max_chars:
        return name
    cut = name[:max_chars]
    last_space = cut.rfind(" ")
    if last_space > max_chars // 2:
        return cut[:last_space].rstrip() + "..."
    return cut.rstrip() + "..."


class ProgressAnimator:
    def __init__(self, root, progress_widget):
        self.root = root
        self.progress = progress_widget
        self._anim_job = None

    def animate_to(self, target, max_duration_ms=3000):
        try:
            cur = float(self.progress["value"])
            target = float(target)
            if cur == target:
                return
            diff = abs(target - cur)
            duration = int(
                max(150, min(max_duration_ms, (diff / 100.0) * max_duration_ms))
            )
            step_ms = 500
            steps = max(1, duration // step_ms)
            delta = (target - cur) / steps

            if self._anim_job:
                try:
                    self.root.after_cancel(self._anim_job)
                except Exception:
                    pass

            i = {"count": 0}

            def _step():
                i["count"] += 1
                val = cur + delta * i["count"]
                if (delta > 0 and val > target) or (delta < 0 and val < target):
                    val = target
                try:
                    self.progress["value"] = val
                except Exception:
                    pass
                if i["count"] < steps:
                    self._anim_job = self.root.after(step_ms, _step)
                else:
                    self._anim_job = None

            _step()
        except Exception:
            try:
                self.progress["value"] = target
            except Exception:
                pass


class Tooltip:
    def __init__(self, root, wrap_width=400, delay_ms=300):
        self.root = root
        self.wrap_width = wrap_width
        self.delay_ms = delay_ms
        self._after_id = None
        self._tooltip = None
        self._tooltip_label = None
        self._row = None

    def bind_to(self, tree, get_full_func, column=2):
        # get_full_func: callable(item_id) -> text
        # RU: get_full_func: вызываемый объект(ид_элемента) -> текст (полное наименование)
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
                        self._tooltip.geometry(
                            f"+{event.x_root + 20}+{event.y_root + 10}"
                        )
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
