"""Progress animation helper for tkinter progress bars.

Contains the `ProgressAnimator` class.
"""
from __future__ import annotations


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
