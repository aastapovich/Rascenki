"""Settings tab: global application preferences.

RU: Вкладка настроек: глобальные параметры приложения.

RU: Сейчас содержит выбор TTF-шрифта для печати.
"""

import os
from tkinter import Frame, Label, Button, StringVar, messagebox, ttk
from tkinter import filedialog
from ui_style import PADDING, SMALL_PADDING
import json

from .print_service import PrintService


def make_tab(parent, ctrl):
    """Create the Settings tab UI and wire persistence through the controller.

    The Settings tab exposes UI for selecting print font, collection options
    (batch size / max categories) and website/search settings. It uses
    `ctrl.save_settings` and `ctrl.load_settings` to persist values.

    Документация (RU):
    Создаёт вкладку «Настройки» и связывает сохранение/загрузку через
    контроллер. Вкладка предоставляет интерфейс для выбора шрифта печати,
    параметров сбора (batch_size / max_categories) и настроек сайта/поиска.
    Для сохранения/загрузки используется `ctrl.save_settings` / `ctrl.load_settings`.
    """
    frame = Frame(parent)

    lbl = Label(frame, text="Настройки")
    lbl.pack(anchor="w", padx=PADDING, pady=PADDING)

    # variables
    # RU: переменные (контролы состояния вкладки)
    font_path_var = StringVar(value=getattr(ctrl, "print_font_path", ""))
    base_url_var = StringVar(value=getattr(ctrl, "base_url", "https://rascenki.kz"))
    poisk_var = StringVar(value=getattr(ctrl, "poisk", "https://rascenki.kz/city/astana/"))
    batch_size_var = StringVar(value=str(getattr(ctrl, "collect_batch_size", 50) or 50))
    max_cat_var = StringVar(value=str(getattr(ctrl, "collect_max_categories", "") or ""))

    # --- Font group
    # RU: Группа настроек шрифта
    font_group = ttk.LabelFrame(frame, text="Шрифт для печати")
    font_group.pack(fill="x", padx=PADDING, pady=SMALL_PADDING)

    info = Label(font_group, textvariable=font_path_var, wraplength=600, justify="left")
    info.grid(row=0, column=0, columnspan=2, sticky="w", padx=PADDING, pady=2)

    def _choose_font():
        path = filedialog.askopenfilename(
            filetypes=[("TTF font", "*.ttf"), ("All files", "*.*")]
        )
        if not path:
            return
        font_path_var.set(path)
        try:
            ctrl.print_font_path = path
        except Exception:
            pass
        messagebox.showinfo(
            "Шрифт выбран", f"Шрифт сохранён для печати: {os.path.basename(path)}"
        )

    def _register_font():
        path = font_path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Ошибка", "Выберите корректный TTF-файл")
            return
        svc = PrintService()
        ok = svc.register_font(path)
        if ok:
            try:
                ctrl.print_font_path = path
            except Exception:
                pass
            messagebox.showinfo(
                "Успех",
                f"Шрифт {os.path.basename(path)} зарегистрирован и пригоден для печати",
            )
        else:
            messagebox.showerror(
                "Ошибка",
                "Не удалось зарегистрировать шрифт (возможно, файл не TTF или повреждён)",
            )

    btn_choose = Button(font_group, text="Выбрать шрифт...", command=_choose_font)
    btn_choose.grid(row=1, column=0, sticky="w", padx=PADDING, pady=2)
    btn_reg = Button(font_group, text="Зарегистрировать шрифт", command=_register_font)
    btn_reg.grid(row=1, column=1, sticky="w", padx=PADDING, pady=2)

    def _delete_font():
        path = font_path_var.get()
        if not path:
            messagebox.showinfo("Удаление шрифта", "Шрифт не выбран")
            return
        ok = messagebox.askyesno(
            "Подтвердите", f"Вы действительно хотите удалить путь к шрифту:\n{path}?"
        )
        if not ok:
            return
        # Try to clear settings and save
        # RU: Попробуем очистить настройки и сохранить
        # Load current settings via controller and clear font path
        try:
            cfg = {}
            cur = None
            try:
                cur = ctrl.load_settings()
            except Exception:
                cur = None
            if isinstance(cur, dict):
                cfg = cur
            cfg["print_font_path"] = ""
            ok = False
            try:
                ok = ctrl.save_settings(cfg)
            except Exception:
                ok = False
            if not ok:
                messagebox.showerror("Ошибка", "Не удалось обновить settings.json")
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить settings.json: {e}")
            return
        # Обновляем UI и controller/app
        font_path_var.set("")
        try:
            ctrl.print_font_path = None
        except Exception:
            pass
        messagebox.showinfo("Готово", "Путь к шрифту удалён из настроек")

    btn_del = Button(font_group, text="Удалить шрифт", command=_delete_font)
    btn_del.grid(row=1, column=2, sticky="w", padx=PADDING, pady=2)

    # --- Collection settings
    # RU: Группа параметров сбора
    collect_group = ttk.LabelFrame(frame, text="Параметры сбора")
    collect_group.pack(fill="x", padx=PADDING, pady=SMALL_PADDING)

    Label(collect_group, text="Размер пачки (batch_size):").grid(
        row=0, column=0, sticky="w", padx=PADDING, pady=2
    )
    ent_batch = ttk.Entry(collect_group, textvariable=batch_size_var, width=20)
    ent_batch.grid(row=0, column=1, sticky="w", padx=PADDING, pady=2)

    Label(
        collect_group, text="Макс. категорий (max_categories, пусто = без лимита):"
    ).grid(row=1, column=0, sticky="w", padx=PADDING, pady=2)
    ent_max = ttk.Entry(collect_group, textvariable=max_cat_var, width=20)
    ent_max.grid(row=1, column=1, sticky="w", padx=PADDING, pady=2)

    # --- Website settings
    # RU: Группа настроек сайта/поиска
    web_group = ttk.LabelFrame(frame, text="Сайт / Поиск")
    web_group.pack(fill="x", padx=PADDING, pady=SMALL_PADDING)

    Label(web_group, text="Адрес сайта:").grid(
        row=0, column=0, sticky="w", padx=PADDING, pady=2
    )
    ent_base = ttk.Entry(web_group, textvariable=base_url_var, width=80)
    ent_base.grid(row=0, column=1, sticky="w", padx=PADDING, pady=2)

    Label(web_group, text="Поиск по (поисковая подстрока в href):").grid(
        row=1, column=0, sticky="w", padx=PADDING, pady=2
    )
    ent_poisk = ttk.Entry(web_group, textvariable=poisk_var, width=80)
    ent_poisk.grid(row=1, column=1, sticky="w", padx=PADDING, pady=2)

    def _save_settings():
        # validate numeric settings
        # RU: проверяем числовые параметры перед сохранением
        bs = None
        mc = None
        try:
            bs = int(batch_size_var.get())
            if bs <= 0:
                raise ValueError("batch_size must be > 0")
        except Exception:
            messagebox.showerror(
                "Ошибка", "Введите корректный положительный integer для batch_size"
            )
            return
        try:
            mc_text = max_cat_var.get().strip()
            mc = int(mc_text) if mc_text != "" else None
            if isinstance(mc, int) and mc <= 0:
                messagebox.showerror(
                    "Ошибка",
                    "max_categories должен быть положительным числом или пустым",
                )
                return
        except Exception:
            messagebox.showerror(
                "Ошибка",
                "Введите корректное число для max_categories или оставьте пустым",
            )
            return

        cfg = {
            "print_font_path": font_path_var.get(),
            "base_url": base_url_var.get(),
            "poisk": poisk_var.get(),
            "collect_batch_size": bs,
            "collect_max_categories": mc,
        }
        try:
            ok = ctrl.save_settings(cfg)
            if ok:
                messagebox.showinfo("Сохранено", "Настройки сохранены в settings.json")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")

    def _load_settings():
        try:
            cfg = ctrl.load_settings()
            if not cfg:
                messagebox.showinfo("Настройки", "Файл settings.json не найден или пуст")
                return
            path = cfg.get("print_font_path", "")
            base = cfg.get("base_url", "")
            po = cfg.get("poisk", "")
            bs = cfg.get("collect_batch_size", 50)
            mc = cfg.get("collect_max_categories", None)
            font_path_var.set(path)
            base_url_var.set(base)
            poisk_var.set(po)
            batch_size_var.set(str(bs if bs is not None else ""))
            max_cat_var.set(str(mc) if mc is not None else "")
            # controller already applied values in load_settings
            messagebox.showinfo("Загружено", "Настройки загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {e}")

    # Bottom buttons row
    btn_row = Frame(frame)
    btn_row.pack(fill="x", padx=PADDING, pady=8)
    btn_save = Button(btn_row, text="Сохранить настройки", command=_save_settings)
    btn_save.pack(side="left", padx=6, pady=2)
    btn_load = Button(btn_row, text="Загрузить настройки", command=_load_settings)
    btn_load.pack(side="left", padx=6, pady=2)

    return frame
