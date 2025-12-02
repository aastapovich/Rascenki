from tkinter import Frame, LEFT
from tkinter import Button
from tkinter import ttk
from ui.ui_style import PADDING, SMALL_PADDING


def make_tab(notebook, ctrl):
    """Create the 'price.csv viewer' tab and bind widgets through the controller.

    The tab uses the controller API to load/export `price.csv` and registers
    the Treeview via `ctrl.register_price_tree` so the controller can
    attach tooltip handlers and other bindings.

    Документация (RU):
    Создаёт вкладку 'Просмотр price.csv' и привязывает виджеты к контроллеру
    `ctrl`. Вкладка использует API контроллера для загрузки/экспорта данных
    и регистрирует Treeview через `ctrl.register_price_tree`, чтобы
    контроллер мог настроить тултипы и обработчики событий.
    """
    frame = Frame(notebook)

    price_control = Frame(frame)
    price_control.grid(row=0, column=0, sticky="ew", padx=PADDING, pady=SMALL_PADDING)

    ctrl.btn_reload_price = Button(
        price_control, text="Перезагрузить price.csv", command=ctrl.load_price_csv
    )
    ctrl.btn_reload_price.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_export_price = Button(
        price_control, text="Экспорт CSV...", command=ctrl.export_price_csv
    )
    ctrl.btn_export_price.pack(side=LEFT, padx=4, pady=2)

    # Treeview for price.csv
    # RU: Treeview для price.csv
    cols = ("№", "Наименование", "Цена", "Ед. изм")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)

    tree.column("№", width=50, anchor="center", stretch=False)
    tree.column("Наименование", width=500, anchor="w", stretch=True)
    tree.column("Цена", width=100, anchor="e", stretch=False)
    tree.column("Ед. изм", width=80, anchor="center", stretch=False)

    tree.grid(row=1, column=0, sticky="nsew", padx=PADDING, pady=SMALL_PADDING)
    try:
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns", padx=(0, 4))
    except Exception:
        pass

    # Регистрируем Treeview через контроллер — контроллер свяжет тултип и обработчики
    try:
        ctrl.register_price_tree(tree)
    except Exception:
        # fallback: записать прямо
        try:
            ctrl.price_tree = tree
        except Exception:
            pass

    return frame
