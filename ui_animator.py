"""Compatibility shim: re-export ProgressAnimator from `ui.ui_animator`.

Old import path `from ui_animator import ProgressAnimator` is preserved.
"""
from ui.ui_animator import *  # noqa: F401,F403
