from tkinter import Frame, LEFT, RIGHT, BOTH, Y, MULTIPLE
from tkinter import Scrollbar, Listbox
from tkinter import Button
from ui.ui_style import PADDING, SMALL_PADDING


def make_tab(notebook, ctrl):
    """Create the 'Categories' tab and attach widgets to the controller.

    The tab uses the controller for actions (e.g. `start_parsing`) and
    assigns widgets through the controller onto the real `App` via
    `UIController.__setattr__`. This simplifies gradual migration towards
    fully decoupled tabs.

    Документация (RU):
    Создаёт вкладку 'Категории' и привязывает виджеты к контроллеру `ctrl`.
    Вкладка использует контроллер для вызовов действий (например,
    `start_parsing`) и записывает виджеты через контроллер в реальный
    `App` (через `UIController.__setattr__`). Это упрощает постепенную
    миграцию к полной изоляции вкладок.
    """
    frame = Frame(notebook)

    cat_control_frame = Frame(frame)
    cat_control_frame.pack(fill="x", pady=SMALL_PADDING, padx=PADDING)

    # Buttons — commands are invoked on the controller (delegated to App)
    # RU: Кнопки — команды вызывает контроллер (делегируются в App)
    ctrl.btn_collect = Button(
        cat_control_frame, text="Собрать ссылки (Start)", command=ctrl.start_parsing
    )
    ctrl.btn_collect.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_load_cat = Button(
        cat_control_frame, text="Загрузить файл категорий...", command=ctrl.load_categories_file
    )
    ctrl.btn_load_cat.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_mark_all = Button(
        cat_control_frame, text="Отметить все", command=ctrl.mark_all, state="disabled"
    )
    ctrl.btn_mark_all.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_unmark = Button(
        cat_control_frame, text="Снять отметки", command=ctrl.unmark_all, state="disabled"
    )
    ctrl.btn_unmark.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_parse_selected = Button(
        cat_control_frame, text="Парсить отмеченные", command=ctrl.parse_selected, state="disabled"
    )
    ctrl.btn_parse_selected.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_save_selected = Button(
        cat_control_frame, text="Сохранить отмеченные...", command=ctrl.save_selected, state="disabled"
    )
    ctrl.btn_save_selected.pack(side=LEFT, padx=4, pady=2)

    # Categories list
    # RU: Список категорий
    list_frame = Frame(frame)
    list_frame.pack(fill=BOTH, expand=True, padx=PADDING, pady=SMALL_PADDING)

    ctrl.cat_listbox = Listbox(list_frame, selectmode=MULTIPLE)
    ctrl.cat_listbox.pack(side=LEFT, fill=BOTH, expand=True)

    sb = Scrollbar(list_frame, orient="vertical", command=ctrl.cat_listbox.yview)
    sb.pack(side=RIGHT, fill=Y, padx=(0, 4))
    ctrl.cat_listbox.config(yscrollcommand=sb.set)

    return frame
