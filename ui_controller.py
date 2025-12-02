"""Compatibility shim: re-export UIController from `ui.ui_controller`.

Keeps `from ui_controller import UIController` working while the
implementation now lives in `ui/ui_controller.py`.
"""
from ui.ui_controller import *  # noqa: F401,F403

