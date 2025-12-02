"""Compatibility shim: re-export PriceViewHelper from `ui.ui_price_helpers`.

Keeps `from ui_price_helpers import PriceViewHelper` working while the
implementation now lives in `ui/ui_price_helpers.py`.
"""
from ui.ui_price_helpers import *  # noqa: F401,F403
