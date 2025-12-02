from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple


def save_categories(glava: Iterable[str], links: Iterable[str], out_dir: str | Path = ".") -> str:
    """Save categories to a dated CSV file in `out_dir` and return the filename.

    RU: Сохранить категории в файл с датой в `out_dir` и вернуть имя файла.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%d%m%Y")
    filename = f"{date_str}.csv"
    path = out_dir / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Название категории", "Ссылка"])
        for name, link in zip(glava, links):
            writer.writerow([name, link])
    return filename


def write_data_csv(blok: Iterable[dict], path: str | Path = "price.csv") -> None:
    """Append `blok` (iterable of dicts) to CSV at `path`.

    RU: Дописать блок (итерируемый list словарей) в CSV по пути `path`.
    """
    p = Path(path)
    with p.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for i in blok:
            num = str(i.get("№", "")).strip()
            name = str(i.get("Наименование", "")).strip()
            price = str(i.get("Цена", "")).strip()
            unit = str(i.get("Ед. изм", "")).strip()
            writer.writerow([num, name, price, unit])


def save_categories_partial(items: Iterable[Tuple[str, str]], path: str | Path = "cat_a.csv") -> int:
    """Append list of (name, link) items to CSV `path`. Create with header if not exists.

    Returns number of items appended.
    RU: Дописывает список (name, link) в CSV `path`. Создаёт файл с заголовком, если не существует.
    """
    p = Path(path)
    mode = "a" if p.exists() else "w"
    appended = 0
    with p.open(mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(["Название категории", "Ссылка"])
        for name, link in items:
            writer.writerow([name, link])
            appended += 1
    return appended
