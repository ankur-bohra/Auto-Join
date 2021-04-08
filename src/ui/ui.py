from SysTrayIcon import SysTrayIcon # type: ignore

def display_window():
    print("Display window... NOW!")

menu_options = (("Open Auto-Join", None, display_window),)

SysTrayIcon(
    "images/calendar.ico",
    "Auto-Join",
    menu_options,
    default_menu_index=1
)