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
    def _on_collect_toggle():
        try:
            cur = ctrl.btn_collect.cget("text")
        except Exception:
            cur = ""
        # If currently in 'start' state -> start parsing and switch to Stop
        if "Собрать" in cur:
            try:
                ctrl.start_parsing()
            except Exception:
                pass
            try:
                ctrl.btn_collect.config(text="Остановить сбор (Stop)")
            except Exception:
                pass
        else:
            # Request stop via controller API if available
            try:
                if hasattr(ctrl, "stop_parsing"):
                    ctrl.stop_parsing()
                else:
                    # fallback: try to call request_stop_collect on app
                    getattr(ctrl, "request_stop_collect", lambda: None)()
            except Exception:
                pass
            try:
                ctrl.btn_collect.config(text="Собрать ссылки (Start)")
            except Exception:
                pass

    ctrl.btn_collect = Button(
        cat_control_frame, text="Собрать ссылки (Start)", command=_on_collect_toggle
    )
    ctrl.btn_collect.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_load_cat = Button(
        cat_control_frame, text="Загрузить файл категорий...", command=ctrl.load_categories_file
    )
    ctrl.btn_load_cat.pack(side=LEFT, padx=4, pady=2)

    def _on_mark_toggle():
        try:
            cur = ctrl.btn_mark_all.cget("text")
        except Exception:
            cur = ""
        if "Отметить" in cur:
            try:
                ctrl.mark_all()
            except Exception:
                pass
            try:
                ctrl.btn_mark_all.config(text="Снять отметки")
            except Exception:
                pass
        else:
            try:
                ctrl.unmark_all()
            except Exception:
                pass
            try:
                ctrl.btn_mark_all.config(text="Отметить все")
            except Exception:
                pass

    ctrl.btn_mark_all = Button(
        cat_control_frame, text="Отметить все", command=_on_mark_toggle, state="disabled"
    )
    ctrl.btn_mark_all.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_parse_selected = Button(
        cat_control_frame, text="Парсить отмеченные", command=ctrl.parse_selected, state="disabled"
    )
    ctrl.btn_parse_selected.pack(side=LEFT, padx=4, pady=2)

    ctrl.btn_save_selected = Button(
        cat_control_frame, text="Сохранить отмеченные...", command=ctrl.save_selected, state="disabled"
    )
    ctrl.btn_save_selected.pack(side=LEFT, padx=4, pady=2)

    # Exit button
    def _on_exit():
        try:
            # controller proxies to app methods
            getattr(ctrl, "_on_close", lambda: None)()
        except Exception:
            try:
                # fallback to direct app attribute
                getattr(ctrl, "_app", None) and getattr(ctrl._app, "_on_close", lambda: None)()
            except Exception:
                pass

    ctrl.btn_exit = Button(cat_control_frame, text="Выход", command=_on_exit)
    ctrl.btn_exit.pack(side=LEFT, padx=4, pady=2)

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
