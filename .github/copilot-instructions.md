## Коротко для AI-агента

- **Цель проекта**: настольный парсер с GUI (Tkinter) для сбора прайс-листов с сайта и экспорта в CSV.
- **Точка входа**: `main.py` — создаёт `App` из `ui/ui_tk.py`.

## Большая картина (архитектура)

- **UI (Tkinter)**: в `ui/ui_tk.py` реализован класс `App` — управляет окном, вкладками (`tabs/`), очередью и фоновой работой. Tabs регистрируют виджеты через `UIController` (см. `tabs/*.py`).
- **Парсер**: `scraper.py` — низкоуровневые функции: `open_web`, `get_all_links_stream`, `get_page_data`. Важно: используется модульный `requests.Session` `_SESSION` для переиспользования соединений.
- **Хранилище/экспорт**: `storage.py` — `save_categories`, `save_categories_partial`, `write_data_csv`. Формат CSV: заголовки `Название категории, Ссылка` и `num, name, price, unit`. Кодирует в `utf-8` и добавляет заголовок только при создании файла.
- **Настройки**: `config.py` читает `settings.json` и заполняет дефолты (используется при инициализации `App`).
- **UI ↔ Back-end взаимодействие**: фоновые задачи пишут в `queue.Queue()`; для перенаправления stdout используется `ui/queue_writer.py` (`QueueWriter`) — он кладёт строки в очередь как `('log', ...)` или `('status', ...)`.

## Ключевые шаблоны и контракты, которые нужно сохранить

- `get_all_links_stream(html, poisk, progress_callback=None, max_categories=None)`
  - Сигнатура: `progress_callback(processed, total, found)` — вызывается часто. При изменениях сохраняйте этот контракт и ранний выход при `max_categories`.
- `open_web(url)` возвращает пустую строку при ошибке — код на это полагается (см. `ui_tk._worker_collect`).
- `save_categories_partial(items, path='cat_a.csv')` открывает файл в режиме `w` при первом создании и записывает заголовок; при доработке логики сохранения сохраняйте поведение заголовка и возвращаемое количество добавленных записей.
- Потокобезопасность/UI: фоновые потоки общаются с UI через `queue.put(...)`. Никогда не вызывать Tk API из фоновых потоков напрямую — используйте очередь и `_poll_queue` в `App`.
- Tabs → controller pattern: `tabs/*.py` получают `ctrl` и записывают в него виджеты (например, `ctrl.btn_collect = Button(...)`). Не удаляйте этот механизм без полной миграции `UIController`.

## Интеграционные точки и примеры

- Для сбора ссылок: `ui.ui_tk.App._worker_collect` вызывает `open_web(base_url)` и затем `get_all_links_stream(...)`. Пример сохранения пачек:

  - `for link, title in get_all_links_stream(...): buffer.append((title, link)); if len(buffer)>=batch_size: save_categories_partial(buffer); buffer.clear()`

- Для записи результатов: `write_data_csv(blok)` ожидает итерируемый блок словарей с ключами `№`, `Наименование`, `Цена`, `Ед. изм`.

## Команды разработки и отладки (как запускать здесь)

- Создать виртуальное окружение и установить зависимости (см. `requirements.txt`). На macOS/Linux:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

- Запуск GUI:

```bash
python main.py
```

- Быстрая отладка в консоли:

```bash
python -m pdb main.py
```

## Особенности, замеченные в кодовой базе

- Код ориентирован на запуск из рабочей директории проекта — файлы CSV читаются/писатся относительно CWD (`ddmmyyyy.csv`, `cat_a.csv`, `price.csv`). Тесты/CI отсутствуют.
- Код ожидает `utf-8` при чтении/записи CSV (см. `storage.py`).
- Код устойчив к ошибкам: многие блоки ловят Exception и используют `queue` для логирования ошибок в UI.

## Что изменить осторожно (рекомендации)

- Существующие фоновые потоки кооперативно проверяют флаг `_collect_stop`; при остановке ставят `done_collect` в очередь — соблюдайте этот контракт.
- При рефакторинге парсера: не менять поведение по возврату пустой строки в `open_web` и не удалять `progress_callback`-вызовы.
- При оптимизации сетевого слоя можно заменить `_SESSION` на более продвинутый клиент, но убедитесь, что `open_web` всё ещё возвращает строку и не бросает исключения наружу.

## Быстрые ссылки по файлам (важные места для изменений)

- `main.py` — запуск приложения
- `ui/ui_tk.py` — App, очереди, потоковая логика
- `ui/queue_writer.py` — stdout → очередь
- `scraper.py` — `open_web`, `get_all_links_stream`, `get_page_data`
- `storage.py` — `save_categories`, `save_categories_partial`, `write_data_csv`
- `config.py` — загрузка `settings.json`
