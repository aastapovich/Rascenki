"""Entry point for the Parser application.

Keeps application startup separate from UI implementation in `ui_tk.py`.

RU: Точка входа для запуска приложения. Отделяет запуск от реализации UI в `ui_tk.py`.
"""
from __future__ import annotations
from ui.ui_tk import App

def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()
