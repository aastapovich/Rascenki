Rascenki — парсер и GUI для экспорта прайс-листов

Кратко
- GUI: `main.py` → запускает `App` из `ui_tk.py` (Tkinter).
- Scraper: `scraper.py` — загрузка страниц и парсинг контента.
- Хранилище и экспорт: `storage.py` работает с `cat_*.csv` и `price.csv`.

Быстрый старт

1. Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Запуск GUI:

```bash
python3 main.py
```

Проектная структура (основные файлы)

- `main.py` — точка входа приложения (запускает `App`).
- `ui_tk.py` — реализация класса `App` (UI + логика взаимодействия с парсером).
- `config.py` — загрузчик настроек из `settings.json` с дефолтами.
- `scraper.py` — функции `open_web`, `get_all_links_stream`, `get_page_data`.
- `storage.py` — чтение/запись `cat_*.csv` и `price.csv`.
- `ui_utils.py` — общие мелкие утилиты (например, `shorten_name`).
- `ui_animator.py` — `ProgressAnimator` для плавной анимации прогресса.
- `ui/` — пакет с UI‑вспомогательными компонентами: `Tooltip`, `QueueWriter`.
- `tabs/` — реализация вкладок интерфейса (`categories_tab.py`, `price_tab.py`, `print_tab.py`, `settings_tab.py`).

Ключевые изменения и рекомендации (рефакторинг)

- Ветка с правками: `refactor/small-cleanups` — содержит безопасные рефакторинги:
	- `storage.py` — использует `pathlib.Path`, явное кодирование `utf-8` и типы.
	- `scraper.py` — использует `requests.Session` и небольшие типизации.
	- Вынесены помощники UI: `ProgressAnimator` → `ui_animator.py`, `Tooltip` и `QueueWriter` → пакет `ui/`, логика TreeView → `ui_price_helpers.py`.
	- `config.py` добавлен для централизованной загрузки `settings.json`.
	- Добавлен `main.py` как единая точка запуска.

Текущий рабочий процесс разработки

- Запуск приложения: `python3 main.py`.
- Для отладки: запустите `python3 -m pdb main.py` или откройте проект в IDE.

Тесты и CI

В репозитории пока нет покрывающих unit‑тестов. Рекомендую добавить тесты для:
- `scraper.get_page_data` (парсинг HTML в структуры данных),
- `storage.save_categories_partial` / `write_data_csv`,
- `config.load_settings`.

Лицензия и вклад

Если хотите, я могу подготовить PR из `refactor/small-cleanups` в `main` с описанием изменений и добавить базовый CI (GitHub Actions) и тесты. Откройте issue или напишите, какие дополнительные функции нужны.

---
RU: README обновлён — содержит инструкции по установке, запуску, структуре и примечания к рефакторингу.

## Changelog / Recent fixes

- PR: Fix tooltip binding overwrite and BS4 deprecation — https://github.com/aastapovich/Rascenki/pull/1
	- Preserve Tooltip handlers by appending legacy binds where needed.
	- Replace deprecated BeautifulSoup.findNextSiblings with find_next_siblings in `scraper.py`.
	- Centralized Treeview tooltip logic in `ui/ui_price_helpers.py` via `PriceViewHelper`.

