"""QueueWriter: redirect stdout-like output into a Queue as log/status lines.

RU: Вспомогательный класс, который перенаправляет вывод в очередь.
"""
from typing import Any


class QueueWriter:
    def __init__(self, q: Any):
        self.q = q
        self.buf = ""

    def write(self, s: str) -> None:
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
                try:
                    self.q.put(("status", line.strip()))
                except Exception:
                    pass
            else:
                try:
                    self.q.put(("log", line))
                except Exception:
                    pass

    def flush(self) -> None:
        if self.buf.strip():
            try:
                self.q.put(("log", self.buf.strip()))
            except Exception:
                pass
        self.buf = ""
