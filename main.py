import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Pil_image, ImageTk as Pil_imageTk
from pynput.keyboard import Key, Listener

#def on_press(key):


class AppButton(ttk.Frame):
    def __init__(self, parent, text="", f_style=None, height=None, width=None, img_width=100, compound='top', *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=f_style)
        img_raw = Pil_image.open("/usr/share/icons/hicolor/128x128/apps/firefox-esr.png").resize((img_width, img_width), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, image=self._photo, compound=compound, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1, padx=1, pady=1)
        #label = ttk.Label(self._btn, image=photo)
        #label.pack(side=tk.RIGHT)

class SearchBox(ttk.Combobox):
    def __init__(self, parent, text="", style=None, height=None, width=None, *args, **kwargs):
        ttk.Combobox.__init__(self, parent, height=height, width=width, style=style, *args, **kwargs)
        self.pack_propagate(0)

class LabelBox(ttk.Frame):
    def __init__(self, parent, text="", s_style=None, height=None, width=None, style=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=s_style)
        self._label = ttk.Label(self, text=text, style=style, justify=tk.CENTER)
        img_raw = Pil_image.open("./search.png").resize((25, 25), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self._photoLabel = ttk.Label(self, image=self._photo, justify=tk.LEFT, *args, **kwargs)
        self.pack_propagate(0)
        self._photoLabel.pack(side=tk.LEFT, padx=30, pady=5)
        self._label.pack(side=tk.LEFT, padx=130, pady=5)

class RoundBox(ttk.Label):
    def __init__(self, parent, height=None, width=None, style=None, *args, **kwargs):
        img_raw = Pil_image.open("./rounded.png").resize((width, height), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        ttk.Label.__init__(self, parent, image=self._photo, *args, **kwargs)
        self.pack_propagate(0)

class CanvasBox(tk.Canvas):
    def __init__(self, parent, posx, posy, height, width, i_height, i_width):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg='white')
        self.place(x=posx, y=posy)
        self.c_width = width
        self.c_height = height
        #img_raw = Pil_image.open("./rounded2.png")#.resize((i_width, i_height), Pil_image.ANTIALIAS)
        #self._photo = Pil_imageTk.PhotoImage(img_raw)
        #self.create_image(i_width, i_height, image=self._photo)
        # self.rect = self.create_rectangle(0, 0, 539, 40, fill='white', outline='white')
        # self.oval = self.create_oval(0, 20, 539, 60, fill='white', outline='white')
        #self.create_rectangle(0, 0, width, height//2, fill='white')
        #self.create_oval(width, height//2, width, height, fill='red')
    
    def create_roundbox(self):
        self.rect = self.create_rectangle(0, 0, 539, 80, fill='white', outline='white')
        #self.oval = self.create_oval(0, 20, 539, 60, fill='white', outline='red')

    def create_entries(self):
        self.buttons_list = []
        for i in range(15):
            btn = AppButton(self, 'Chrome', f_style='L.TFrame', width=539, height=40, img_width=20, compound='left', style='W.TButton')
            btn.place(x=0, y=80+i*40)
            self.buttons_list.append(btn)

    def destroy_entries(self):
        for i in self.buttons_list:
            i.destroy()

    def move_to(self, parent, posx, posy, delay):
        # x1 = self.coords_x
        # x2 = self.coords_y
        (x1, y1, x2, y2) = self.coords(self.rect)
        dx = 0
        dy = 0
        if posx == int(x1) and posy == int(y1):
            return
        if posx > x1:
            dx = 1
        elif posx < x1:
            dx = -1
        if posy > y1:
            dy = 1
        elif posy < y1:
            dy = -1
        self.move(self.rect, dx, dy)
        self.c_width += dx
        self.c_height += dy
        self.config(width=self.c_width, height=self.c_height)
        #self.move(self.oval, dx, dy)
        parent.after(delay, self.move_to, parent, posx, posy, delay)

def main():
    window = tk.Tk()
    window.configure(background='#f0f0f0')
    window.geometry("540x672")
    style = ttk.Style()
    style.configure('W.TButton', font=(25), foreground="#535353", background="white", relief='flat', highlightthickness=0)
    style.map('W.TButton', background=[('pressed', '#c3c3c3'), ('active', '#ececec')])
    style.configure('L.TFrame', background="#e7e7e7")
    style.configure('G.TLabel', foreground="#535353", font=(25))
    # animBox.move_to(window, 0, 700, 5)
    window.grid_rowconfigure(0, minsize=80)
    for i in range(3):
        for j in range(3):
            #btn1 = ttk.Button(window, text='Chrome', style='W.TButton')
            #btn1.grid(row=i+1, column=j+1)
            btn = AppButton(window, 'Chrome', f_style='L.TFrame', width=180, height=200, style='W.TButton')
            btn.grid(row=i+2, column=j)
    canvas = CanvasBox(window, 0, 0, 80, 539, 1, 1)
    canvas.create_roundbox()
    canvas.move_to(window, 0, 672, 1)
    window.after(870, canvas.create_entries)
    window.after(1870, canvas.destroy_entries)
    window.after(1900, canvas.move_to, window, 0, 0, 1)
    search_label = LabelBox(canvas, 'Start typing...', width=539, height=40, style='G.TLabel')
    #search_label.grid(row=0, column=0, sticky="we", columnspan=3)
    search_label.place(x=0, y=0)
    rounded = RoundBox(canvas, 40, 539)
    #rounded.grid(row=1, column=0, sticky="we", columnspan=3)
    rounded.place(x=0, y=40)
    window.mainloop()

if __name__ == "__main__":
    main()

