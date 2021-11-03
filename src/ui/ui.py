from tkinter.constants import FALSE
from infi.systray import SysTrayIcon
import tkinter as tk
import time
import re

window = tk.Tk()
window.title("Auto Join")
window.geometry("550x300")
window.resizable(width=False, height=False)
window.update()

window_geometry = window.winfo_geometry()
match = re.search(r"(\d+)x(\d+).+", window_geometry)
window_width, window_height = int(match.group(1)), int(match.group(2))

bottom_bar = tk.Frame(window,
    background="gray94",
    height=40,
    width=window_width
)
bottom_bar.update()
bottom_bar.place(
    anchor=tk.S,
    relx=0.5, rely=1
)

usable_area = tk.Frame(window,
    background="gray80",
    height=window_height-bottom_bar['height'],
    width=window_width
)
usable_area.place(
    anchor=tk.N,
    relx=0.5, rely=0
)

def busy_sleep(seconds_to_sleep):
    start = time.time()
    while (time.time() < start + seconds_to_sleep):
        pass

def make_indicator(relx, width):
    indicator = tk.Frame(bottom_bar,
        background="gray28",
        height=1, width=width,
    )
    indicator.place(
        anchor= tk.CENTER,
        relx=relx, rely=0.7
    )
    return indicator

indicator = None
active_button = None
def wrap_bottom_bar_command(command, button, button_x, isDefault=False):
    global indicator, active_button
    button_width = button.winfo_reqwidth()
    if isDefault:
        indicator = make_indicator(button_x, button_width - 8)
        active_button = button
    def wrapped():
        global indicator, active_button, usable_area
        if active_button == button:
            return
        # Clicked at new button
        active_button = button
        old_indicator = indicator
        old_indicator_original_width = old_indicator.winfo_reqwidth()
        indicator = make_indicator(button_x, 0)
        new_ind_current_width, new_ind_target_width = 0, button_width - 8
        indicator_tween_time = 0.01
        steps = 10
        indicator_resize_step = new_ind_target_width/steps
        old_indicator_resize_step = old_indicator_original_width/steps

        step = 1
        while step <= steps:
            indicator.configure(width=new_ind_current_width + step * indicator_resize_step)
            old_indicator.configure(width=old_indicator_original_width - step * old_indicator_resize_step)

            indicator.update()
            old_indicator.update()

            step += 1
            busy_sleep(indicator_tween_time/steps)
        old_indicator.destroy()
        indicator.lift()

        # Clean previous widgets
        for child in usable_area.winfo_children():
            child.destroy()

        command()
    return wrapped

def add_buttons_to_bottom_bar(buttons_info):
    for button_info in buttons_info:
        button_no = buttons_info.index(button_info)
        button_x = (button_no+1)/(len(buttons_info) + 1)
        button = tk.Button(bottom_bar,
            text=button_info[0], font=("Corbel", 12, "normal"), foreground="gray23",
            background=bottom_bar["background"], activebackground=bottom_bar["background"],
            relief="flat", overrelief="flat", bd=0,
        )
        button.configure(command=wrap_bottom_bar_command(button_info[1], button, button_x, len(button_info) > 2))
        button.place(
            anchor=tk.CENTER,
            relx=button_x, rely=0.4
        )
    indicator.lift()

last_group_end = 0
def add_group(group_type, group_data, first_group=False):
    global last_group_end
    if first_group:
        last_group_end = 0

    if group_type == "Cards":
        title_label = tk.Label(usable_area,
            text=title,
            font=("Corbel", 16, "bold"), foreground="gray30",
            background=usable_area["background"]
        )
        title_label.place(anchor=tk.NW, x=10, y=last_group_end+(10 if first_group else 15))
        title_label.update_idletasks()

        # Place cards
        last_card_end = title_label.winfo_y() + title_label.winfo_reqheight()
        for card_no in range(len(cards)):
            card = cards[card_no]
            card_container = tk.Frame(usable_area,
                background="white",
                height=30, width=window_width-20
            )
            card_container.place(anchor=tk.N, relx=0.5, y=last_card_end + (5 if card_no == 0 else 10))
            card_container.update_idletasks()

            title_label = tk.Label(card_container,
                background=card_container['background'],
                text=card[0]+":", font=("Corbel", 12, "bold"), foreground="gray23",
            )
            title_label.place(anchor=tk.W, x=5, rely=0.5)

            content_label = tk.Label(card_container,
                background=card_container['background'],
                text=card[1], font=("Arial", 11, "normal"), foreground="gray23",
            )
            content_label.place(anchor=tk.W, x=5 + title_label.winfo_reqwidth() + 3 , rely=0.5)

            print(last_card_end)
            last_card_end = card_container.winfo_y() + card_container.winfo_reqheight()
            print(last_card_end)
        last_group_end = last_card_end
    elif group_type == "Buttons":
        container = tk.Frame(usable_area,
            background="white",
            height=30, width=window_width-20
        )
        container.place(anchor=tk.N, relx=0.5, y=last_group_end+(10 if first_group else 15))
        container.update_idletasks()

def on_home():
    add_group("Cards", {
        "title": "Schedule",
        "cards": [
            {"title": "Current event", "content": "[2020 GRADE XII E MATHS] MATHS"}
        ]
    }, True)
    add_group("Cards", {
        "title": "Upcoming Refreshes",
        "cards": [
            {"title": "Next cache refresh", "content": "13 seconds"},
            {"title": "Next join check", "content": "33 seconds"},
        ]
    })

def on_settings(): pass
def on_conflict(): pass

add_buttons_to_bottom_bar([
    ("Conflicts", on_conflict),
    ("Home", on_home, True),
    ("Settings", on_settings)
])

window.mainloop()
'''
def display_window(systray):
    print("Displaying now")

menu_options = (("Show Menu", None, display_window),)
systray = SysTrayIcon("images/calendar.ico", "Auto Join", menu_options)
# systray.start()
'''