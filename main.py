import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Pil_image, ImageTk as Pil_imageTk

class AppButton(ttk.Frame):
    def __init__(self, parent, text="", f_style=None, height=None, width=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=f_style)
        img_raw = Pil_image.open("/usr/share/icons/hicolor/128x128/apps/firefox-esr.png").resize((100, 100), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, image=self._photo, compound='top', *args, **kwargs)
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

def main():
    window = tk.Tk()
    window.configure(background='#f0f0f0')
    style = ttk.Style()
    style.configure('W.TButton', font=(25), foreground="#535353", background="white", relief='flat', highlightthickness=0)
    style.map('W.TButton', background=[('pressed', '#c3c3c3'), ('active', '#ececec')])
    style.configure('L.TFrame', background="#e7e7e7")
    style.configure('G.TLabel', foreground="#535353", font=(25))
    search_label = LabelBox(window, 'Start typing...', height=40, style='G.TLabel')
    search_label.grid(row=0, column=0, sticky="we", columnspan=3)
    rounded = RoundBox(window, 30, 539)
    rounded.grid(row=1, column=0, sticky="we", columnspan=3)
    #search = SearchBox(window, 'Start typing...')
    #search.grid(row=0, column=0, sticky="we", columnspan=3)
    #window.grid_columnconfigure(0, weight=2)
    #window.grid_columnconfigure(1, weight=1)
    #window.grid_columnconfigure(2, weight=3)
    for i in range(3):
        for j in range(3):
            #btn1 = ttk.Button(window, text='Chrome', style='W.TButton')
            #btn1.grid(row=i+1, column=j+1)
            btn = AppButton(window, 'Chrome', f_style='L.TFrame', width=180, height=200, style='W.TButton')
            btn.grid(row=i+2, column=j)
    window.mainloop()

if __name__ == "__main__":
    main()

