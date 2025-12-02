"""Configuration loader for the Parser application.

Provides a small helper to read `settings.json` and return a dict
with defaults. This isolates file IO from the UI code and simplifies
testing.

RU: Загрузчик конфигурации для приложения парсера.
Возвращает словарь настроек с разумными значениями по умолчанию.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULTS: Dict[str, Any] = {
    "print_font_path": None,
    "base_url": "https://rascenki.kz",
    "poisk": "https://rascenki.kz/city/astana/",
    "collect_batch_size": 50,
    "collect_max_categories": None,
}


def load_settings(path: str | Path = "settings.json") -> Dict[str, Any]:
    """Load settings from JSON file and merge with defaults.

    Returns a dictionary with keys present in `DEFAULTS`. On error
    returns the defaults.

    RU: Загружает настройки из JSON и сливает с значениями по умолчанию.
    При ошибке возвращает словарь с дефолтными значениями.
    """
    p = Path(path)
    if not p.exists():
        return DEFAULTS.copy()
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = DEFAULTS.copy()
        if isinstance(data, dict):
            cfg.update({k: data.get(k, cfg[k]) for k in cfg.keys()})
        return cfg
    except Exception:
        return DEFAULTS.copy()
