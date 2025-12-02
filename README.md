Rascenki parser

Коротко
- GUI: `ui_tk.py` — Tkinter приложение для сбора ссылок и парсинга категорий.
- Scraper: `rascenki_kz.py` — функции для загрузки страниц и записи CSV.

Зависимости
```bash
pip3 install -r requirements.txt
```

Запуск
- Запустить GUI: `python3 ui_tk.py`
- CLI-парсинг (базовый): `python3 rascenki_kz.py`

Особенности
- При старте `ui_tk.py` пытается загрузить последний `ddmmyyyy.csv` (или `cat_a.csv`). Если не найден — автоматически собирает ссылки.
- Формат CSV категорий: `Название категории,Ссылка`.
- Результат парсинга дописывается в `price.csv`.

Конвенция комментариев / docstrings
- Все новые и отредактированные inline‑комментарии и docstrings должны быть bilingual: сначала English, затем Russian.
- Пример:

```python
# Brief English description
# RU: Краткое описание на русском
def foo():
		pass
```

Controller / Tab contract
- Tabs are created via `make_tab(notebook, ctrl)` where `ctrl` is an instance of `UIController`.
- `UIController` delegates attribute access to the real `App` and exposes helpers:
	- `post_log(msg)`, `post_status(msg)`, `post_new_category(title, link, idx=None)`,
	- `post_progress(processed, total, found)`, `post_done_collect(ok)`,
	- `start_parsing()`, `load_price_csv()`, `export_price_csv()`, `parse_selected()`, `save_selected()`,
	- `load_categories_file()`, `mark_all()`, `unmark_all()`,
	- `register_price_tree(tree)` — register and wire Treeview for tooltip/handlers.

Development / formatting
- Recommended: create and activate the virtualenv from repo root, then install dev tools and runtime deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install black ruff
```

- Run formatters before committing:

```bash
ruff format .
black .
```

Советы для разработчика
- `get_all_links` печатает прогресс с `\r` — UI перехватывает stdout и отображает однострочный статус.
- `get_page_data` возвращает `(blok, index)` — индекс увеличивается автоматически внутри функции, глобальных переменных избегаем.

Если нужны дополнительные функции (кнопка выбора выходной папки, переключение формата CSV) — откройте issue или предложите изменения.
