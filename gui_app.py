import tkinter as tk
from tkinter import ttk
from ctypes import windll

def button_clicked(text):
    
    print(text)

try:
    text = "to sie zmieni"
    windll.shcore.SetProcessDpiAwareness(1) # MAKES BLUR GO AWAY
    
    root = tk.Tk()
    root.title("Shiro Control Panel")
    root.iconbitmap("./pictures/shiro_icon.ico")
    window_width = 900
    window_height = 600

    # get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # find the center point
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)

    # set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    ttk.Button(root, text='Click Me',command=lambda: button_clicked("nowy tekst")).pack()
    

    message = ttk.Label(root, 
                    text=text,
                    font=("Helvetica", 16))
    
    message.pack()
  

    #keep window display
finally:
    root.mainloop()