import csv
from datetime import datetime


def save_categories(glava, links, out_dir="."):
    """Save categories to ddmmyyyy.csv in `out_dir` and return filename.

    RU: Сохранить категории в файл ddmmyyyy.csv в `out_dir` и вернуть имя файла.
    """
    date_str = datetime.now().strftime("%d%m%Y")
    filename = f"{date_str}.csv"
    path = f"{out_dir}/{filename}" if out_dir != "." else filename
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Название категории", "Ссылка"])
        for name, link in zip(glava, links):
            writer.writerow([name, link])
    return filename


def write_data_csv(blok, path="price.csv"):
    """Append blok (list of dicts) to CSV at `path`.

    RU: Дописать блок (list of dicts) в CSV по пути `path`.
    """
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        for i in blok:
            num = str(i.get("№", "")).strip()
            name = str(i.get("Наименование", "")).strip()
            price = str(i.get("Цена", "")).strip()
            unit = str(i.get("Ед. изм", "")).strip()
            writer.writerow([num, name, price, unit])


def save_categories_partial(items, path="cat_a.csv"):
    """Append list of (name, link) items to CSV `path`. Create with header if not exists.

    Returns number of items appended.
    """
    # RU: Дописывает список (name, link) в CSV `path`. Создаёт файл с заголовком, если не существует.
    # RU: Возвращает количество добавленных элементов.
    import os

    mode = "a" if os.path.exists(path) else "w"
    appended = 0
    with open(path, mode, newline="") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(["Название категории", "Ссылка"])
        for name, link in items:
            writer.writerow([name, link])
            appended += 1
    return appended
