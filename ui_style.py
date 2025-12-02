"""Compatibility shim: re-export UI style constants from `ui.ui_style`.

Keeps `from ui_style import ...` working while the canonical values are
defined in `ui/ui_style.py`.
"""
from ui.ui_style import *  # noqa: F401,F403
