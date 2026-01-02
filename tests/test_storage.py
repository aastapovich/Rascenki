import csv
from pathlib import Path
from storage import save_categories_partial, write_data_csv


def test_save_categories_partial(tmp_path):
    p = tmp_path / "cat_a.csv"
    items = [("Name1", "http://a"), ("Name2", "http://b")]
    appended = save_categories_partial(items, path=str(p))
    assert appended == 2
    with p.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0] == ["Название категории", "Ссылка"]
    assert rows[1] == ["Name1", "http://a"]


def test_write_data_csv(tmp_path):
    p = tmp_path / "price.csv"
    blok = [{"№": 1, "Наименование": "Item", "Цена": "50", "Ед. изм": "kg"}]
    write_data_csv(blok, path=str(p))
    with p.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0] == ["1", "Item", "50", "kg"]
