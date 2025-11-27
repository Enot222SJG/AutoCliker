import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyautogui

pyautogui.FAILSAFE = True

clicking = False
stop_event = threading.Event()
worker = None
current_interval = 0.1  # по умолчанию 100 мс

def interval_seconds():
    global current_interval
    try:
        ms = int(interval_var.get())
        if ms <= 0:
            ms = 1
    except ValueError:
        ms = 100
    current_interval = ms / 1000.0
    status_lbl.config(text=f"Интервал: {current_interval:.3f} сек")
    return current_interval

def map_button(b):
    return {"Левая": "left", "Правая": "right", "Средняя": "middle"}.get(b, "left")

def set_ui_running(r):
    def _():
        if r:
            start_btn.config(state=tk.DISABLED)
            stop_btn.config(state=tk.NORMAL)
            status_lbl.config(text="Статус: Работает")
        else:
            start_btn.config(state=tk.NORMAL)
            stop_btn.config(state=tk.DISABLED)
            status_lbl.config(text="Статус: Остановлен")
    root.after(0, _)

def click_loop():
    global clicking
    i = 0
    if repeat_mode.get() == "Повторить":
        limit = int(repeat_count_var.get()) if repeat_count_var.get().isdigit() else 1
    else:
        limit = float("inf")

    while not stop_event.is_set() and i < limit:
        interval = current_interval
        if pos_mode.get() == "Текущая позиция":
            x, y = pyautogui.position()
        else:
            try:
                x = int(x_var.get())
                y = int(y_var.get())
            except ValueError:
                x, y = pyautogui.position()

        btn = map_button(button_var.get())
        try:
            if click_type_var.get() == "Одиночный":
                pyautogui.click(x=x, y=y, button=btn)
            else:
                pyautogui.click(x=x, y=y, button=btn, clicks=2, interval=0.05)
        except Exception as e:
            root.after(0, lambda msg=str(e): messagebox.showerror("Ошибка", msg))
            break

        i += 1
        if stop_event.wait(interval):
            break

    clicking = False
    set_ui_running(False)

def start_clicking():
    global clicking, worker, stop_event
    if clicking:
        return
    stop_event.clear()
    clicking = True
    set_ui_running(True)
    worker = threading.Thread(target=click_loop, daemon=True)
    worker.start()

def stop_clicking():
    global clicking, stop_event
    if not clicking:
        return
    stop_event.set()
    clicking = False
    set_ui_running(False)

def toggle_start_stop(event=None):
    if clicking:
        stop_clicking()
    else:
        start_clicking()

def pick_point():
    info_label.config(text="Наведи курсор... через 2 сек будет захват")
    root.after(2000, capture_mouse_pos)

def capture_mouse_pos():
    x, y = pyautogui.position()
    x_var.set(str(x))
    y_var.set(str(y))
    info_label.config(text="")

root = tk.Tk()
root.title("Автокликер")
root.geometry("444x400")
root.resizable(False, False)

# ---------- Интервал клика ----------
frame_interval = tk.LabelFrame(root, text="Интервал клика (мс)")
frame_interval.place(x=10, y=10, width=424, height=60)

interval_var = tk.StringVar(value="100")
tk.Entry(frame_interval, width=10, textvariable=interval_var, justify="center").grid(row=0, column=0, padx=6, pady=6)
apply_btn = tk.Button(frame_interval, text="Применить", command=interval_seconds)
apply_btn.grid(row=0, column=1, padx=6, pady=6)

# ---------- Параметры клика ----------
frame_click = tk.LabelFrame(root, text="Параметры клика")
frame_click.place(x=10, y=80, width=424, height=60)

button_var = tk.StringVar(value="Левая")
click_type_var = tk.StringVar(value="Одиночный")

tk.Label(frame_click, text="Кнопка:").grid(row=0, column=0, padx=(6,2))
ttk.Combobox(frame_click, textvariable=button_var, values=["Левая", "Правая", "Средняя"], state="readonly", width=12).grid(row=0, column=1, padx=6)
tk.Label(frame_click, text="Тип:").grid(row=0, column=2, padx=(8,2))
ttk.Combobox(frame_click, textvariable=click_type_var, values=["Одиночный", "Двойной"], state="readonly", width=12).grid(row=0, column=3, padx=6)

# ---------- Повтор ----------
frame_repeat = tk.LabelFrame(root, text="Повтор")
frame_repeat.place(x=10, y=150, width=424, height=70)

repeat_mode = tk.StringVar(value="До остановки")
repeat_count_var = tk.StringVar(value="1")

tk.Radiobutton(frame_repeat, text="Повторить", variable=repeat_mode, value="Повторить").grid(row=0, column=0, sticky="w", padx=(6,2))
tk.Spinbox(frame_repeat, from_=1, to=1000000, textvariable=repeat_count_var, width=8).grid(row=0, column=1, padx=6)
tk.Radiobutton(frame_repeat, text="Повторять до остановки", variable=repeat_mode, value="До остановки").grid(row=1, column=0, columnspan=2, sticky="w", padx=(6,2))

# ---------- Позиция ----------
frame_pos = tk.LabelFrame(root, text="Позиция курсора")
frame_pos.place(x=10, y=230, width=424, height=90)

pos_mode = tk.StringVar(value="Текущая позиция")
x_var = tk.StringVar(value="0")
y_var = tk.StringVar(value="0")

tk.Radiobutton(frame_pos, text="Текущая позиция", variable=pos_mode, value="Текущая позиция").grid(row=0, column=0, columnspan=3, sticky="w", padx=6)
tk.Radiobutton(frame_pos, text="Указать", variable=pos_mode, value="Указать").grid(row=1, column=0, sticky="w", padx=(6,2))
tk.Label(frame_pos, text="X:").grid(row=1, column=1, sticky="e")
tk.Entry(frame_pos, width=7, textvariable=x_var, justify="center").grid(row=1, column=2, padx=(4,8))
tk.Label(frame_pos, text="Y:").grid(row=1, column=3, sticky="e")
tk.Entry(frame_pos, width=7, textvariable=y_var, justify="center").grid(row=1, column=4, padx=(4,6))
ttk.Button(frame_pos, text="Выбрать точку", command=pick_point).grid(row=1, column=5, padx=6)

info_label = tk.Label(frame_pos, text="", fg="gray")
info_label.grid(row=2, column=0, columnspan=6, sticky="w", padx=6)

# ---------- Кнопки Старт/Стоп ----------
start_btn = tk.Button(root, text="Старт (F2)", command=start_clicking)
start_btn.place(x=30, y=335, width=180, height=40)

stop_btn = tk.Button(root, text="Стоп (F2)", command=stop_clicking, state=tk.DISABLED)
stop_btn.place(x=234, y=335, width=180, height=40)

status_lbl = tk.Label(root, text="Статус: Остановлен", anchor="w")
status_lbl.place(x=10, y=380, width=424, height=18)

root.bind_all("<F2>", toggle_start_stop)

set_ui_running(False)
interval_seconds()  # применяем стартовое значение
root.mainloop()
