
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\111111.PROGRAMOWANIE\AI W PYTHONIE\tkinter desinger projekts\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1200x800")
window.configure(bg = "#4B98E0")


canvas = Canvas(
    window,
    bg = "#4B98E0",
    height = 800,
    width = 1200,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    600.0,
    400.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    959.0,
    400.0,
    image=image_image_2
)

canvas.create_text(
    508.0,
    185.0,
    anchor="nw",
    text="logs from logs",
    fill="#12D4FF",
    font=("Inter Bold", 10 * -1)
)

canvas.create_text(
    257.0,
    12.0,
    anchor="nw",
    text="ShiroAi-chan Control Panel",
    fill="#12D4FF",
    font=("Inter Bold", 48 * -1)
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=52.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=204.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=356.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_4 clicked"),
    relief="flat"
)
button_4.place(
    x=508.0,
    y=91.0,
    width=127.0,
    height=51.0
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_5 clicked"),
    relief="flat"
)
button_5.place(
    x=52.0,
    y=165.0,
    width=127.0,
    height=51.0
)

button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_6 clicked"),
    relief="flat"
)
button_6.place(
    x=204.0,
    y=165.0,
    width=127.0,
    height=51.0
)

button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_7 clicked"),
    relief="flat"
)
button_7.place(
    x=356.0,
    y=165.0,
    width=127.0,
    height=51.0
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    571.0,
    175.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    571.0,
    175.0,
    image=image_image_4
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    113.0,
    52.0,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#7FD7EC",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=52.0,
    y=35.0,
    width=122.0,
    height=32.0
)

canvas.create_text(
    58.0,
    5.0,
    anchor="nw",
    text="Your name:",
    fill="#7FD5EA",
    font=("Inter Bold", 20 * -1)
)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    207.0,
    65.0,
    image=image_image_5
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    207.0,
    43.0,
    image=image_image_6
)

button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_8 clicked"),
    relief="flat"
)
button_8.place(
    x=3.0,
    y=217.0,
    width=30.0,
    height=18.0
)

button_image_9 = PhotoImage(
    file=relative_to_assets("button_9.png"))
button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_9 clicked"),
    relief="flat"
)
button_9.place(
    x=40.0,
    y=217.0,
    width=30.0,
    height=18.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    265.0,
    354.0,
    image=entry_image_2
)
entry_2 = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=93.0,
    y=240.0,
    width=344.0,
    height=226.0
)

canvas.create_text(
    16.0,
    479.0,
    anchor="nw",
    text="guzik do wymazania okienka na dole zeby wprowadzic input",
    fill="#FFFFFF",
    font=("Inter", 12 * -1)
)

canvas.create_text(
    104.0,
    440.0,
    anchor="nw",
    text="guzik do pokazania tabelki z opisami wszystkich uzytych characterow w dolnym oknie",
    fill="#00719F",
    font=("Inter", 12 * -1)
)

canvas.create_text(
    274.0,
    470.0,
    anchor="nw",
    text="guzik do zatwierdzenia zmiany w opisie characteru w obecnej tableki dla teog uzytkownika",
    fill="#FFFFFF",
    font=("Inter", 12 * -1)
)

canvas.create_text(
    8.0,
    282.0,
    anchor="nw",
    text="guzik do pokazania obecnego opisu charakteru moze byc na gorze",
    fill="#FFFFFF",
    font=("Inter", 12 * -1)
)

button_image_10 = PhotoImage(
    file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_10 clicked"),
    relief="flat"
)
button_10.place(
    x=3.0,
    y=240.0,
    width=42.0,
    height=42.0
)

button_image_11 = PhotoImage(
    file=relative_to_assets("button_11.png"))
button_11 = Button(
    image=button_image_11,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_11 clicked"),
    relief="flat"
)
button_11.place(
    x=133.0,
    y=545.0,
    width=42.0,
    height=42.0
)

button_image_12 = PhotoImage(
    file=relative_to_assets("button_12.png"))
button_12 = Button(
    image=button_image_12,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_12 clicked"),
    relief="flat"
)
button_12.place(
    x=211.0,
    y=545.0,
    width=42.0,
    height=42.0
)

button_image_13 = PhotoImage(
    file=relative_to_assets("button_13.png"))
button_13 = Button(
    image=button_image_13,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_13 clicked"),
    relief="flat"
)
button_13.place(
    x=289.0,
    y=545.0,
    width=42.0,
    height=42.0
)

canvas.create_rectangle(
    10.0,
    590.0,
    460.0,
    790.0,
    fill="#D9D9D9",
    outline="")
window.resizable(False, False)
window.mainloop()
