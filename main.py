import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Pil_image, ImageTk as Pil_imageTk
import time
import re
import os
import configparser
import variables

#def on_press(key):

class Config():
    def __init__(self):
        self.parser = configparser.ConfigParser()
        parser['DEFAULT'] = variables.EXPORT_CONFIG

class AppButton(ttk.Frame):
    def __init__(self, parent, text="", f_style=None, height=None, width=None, img_width=100, compound='top', *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=f_style)
        img_raw = Pil_image.open("/usr/share/icons/hicolor/128x128/apps/firefox-esr.png").resize((img_width, img_width), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, image=self._photo, compound=compound, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1, padx=1, pady=1) 
        def exec_launch():
            self.launch()
        self._btn.exec_launch = exec_launch

    def focus_on_btn(self):
        self.focus_set()
        self._btn.focus_set()

    def set_style(self, style):
        self._btn.configure(style=style)

    def configure_btn(self):
        pass

    def launch(self):
        #os.system("nohup " + "firefox")
        os.system("nohup " + "firefox" + " > /dev/null")

class SearchBox(ttk.Combobox):
    def __init__(self, parent, text="", style=None, height=None, width=None, *args, **kwargs):
        ttk.Combobox.__init__(self, parent, height=height, width=width, style=style, *args, **kwargs)
        self.pack_propagate(0)

class LabelBox(ttk.Frame):
    def __init__(self, parent, text="", s_style=None, height=None, width=None, style=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=s_style)
        self.labeltext = text
        self.emptyQuery = True
        self._label = ttk.Label(self, text=self.labeltext, style=style, justify=tk.CENTER)
        img_raw = Pil_image.open("./search.png").resize((25, 25), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self._photoLabel = ttk.Label(self, image=self._photo, justify=tk.LEFT, *args, **kwargs)
        self.pack_propagate(0)
        self._photoLabel.pack(side=tk.LEFT, padx=30, pady=5)
        self._label.pack(side=tk.LEFT, padx=130, pady=5)

    def changeText(self, text):
        self.labeltext = text
        if len(text) >= 17:
            text = str(text[::-1][:17] + '..')[::-1]
        self._label.configure(text=text)

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

        self.dropdown = False
        self.moving = False
        self.change_direction = False
        self.new_direction = (0, 0)
    
    def create_roundbox(self):
        pass

    def create_entries(self, focus_func, unfocus_func):
        self.buttons_list = []
        self.entries_amount = 10
        for i in range(10):
            btn = AppButton(self, 'Chrome', f_style='L.TFrame', width=539, height=60, img_width=25, compound='left', style='W.TButton')
            btn.place(x=0, y=80+i*60)
            btn.bind("<FocusIn>", focus_func)
            btn.bind("<FocusOut>", unfocus_func)
            self.buttons_list.append(btn)

    def destroy_entries(self):
        for i in self.buttons_list:
            i.destroy()

    def get_delta(self, curx, cury, posx, posy, step):
        dx = 0
        dy = 0
        if posx > curx:
            dx = step
        elif posx < curx:
            dx = -step
        if posy > cury:
            dy = step
        elif posy < cury:
            dy = -step
        return dx, dy

    def move_to_non_recursive(self, parent, posx, posy, delay, step=1, speed=1, frame_skip=10):
        if self.moving:
            self.change_direction = True
            self.new_direction = (posx, posy)
            return
        self.moving = True
        x1 = self.c_width
        y1 = self.c_height
        dx = 0
        dy = 0
        if posx == int(x1) and posy == int(y1):
            return
        (dx, dy) = self.get_delta(x1, y1, posx, posy, step)
        
        if speed < 1:
            speed = 1
        if frame_skip < 1:
            frame_skip = 1

        i = 0
        while True:
            if posx == int(self.c_width) and posy == int(self.c_height):
                break
            if self.change_direction:
                (posx, posy) = self.new_direction
                (dx, dy) = self.get_delta(self.c_width, self.c_height, posx, posy, step)
                self.change_direction = False
            self.c_width += dx
            self.c_height += dy
            if i % speed == 0:
                time.sleep(0.001)
            try:
                self.config(width=self.c_width, height=self.c_height)
            except tk._tkinter.TclError:
                break
            if i % frame_skip == 0:
                parent.update()
            i += 1
        self.moving = False

class FocusManager:
    def __init__(self):
        self.cur_focus_pos = (1, 1)
        self.cur_drop_focus_pos = 0

def main():
    window = tk.Tk()
    window.configure(background='#f0f0f0')
    window.geometry("540x672")
    window.resizable(False, False)
    style = ttk.Style()
    style.configure('W.TButton', font=(25), foreground="#535353", background="white", relief='flat', highlightthickness=0)
    style.map('W.TButton', background=[('pressed', '#c3c3c3'), ('active', '#ececec')])
    style.configure('WF.TButton', font=(25), foreground="#535353", background="#c1c1c1", relief='flat', highlightthickness=0)
    style.map('WF.TButton', background=[('pressed', '#b3b3b3'), ('active', '#c1c1c1')])
    style.configure('L.TFrame', background="#e7e7e7")
    style.configure('G.TLabel', foreground="#535353", font=(25))

    def set_focus_color(event):
        event.widget.set_style('WF.TButton')
    
    def unset_focus_color(event):
        event.widget.set_style('W.TButton')

    def launch_app(event):
        event.widget.exec_launch()
        window.destroy()

    window.grid_rowconfigure(0, minsize=80)
    buttons = []
    for i in range(3):
        buttons.append([])
        for j in range(3):
            btn = AppButton(window, 'Chrome', f_style='L.TFrame', width=180, height=200, style='W.TButton')
            btn.grid(row=i+2, column=j)
            btn.bind("<FocusIn>", set_focus_color)
            btn.bind("<FocusOut>", unset_focus_color)
            btn._btn.bind("<Button-1>", launch_app)
            buttons[i].append(btn)
    canvas = CanvasBox(window, 0, 0, 80, 539, 1, 1)
    canvas.create_roundbox()

    search_label = LabelBox(canvas, 'Start typing...', width=539, height=40, style='G.TLabel')
    search_label.place(x=0, y=0)
    rounded = RoundBox(canvas, 40, 539)
    rounded.place(x=0, y=40)
    
    canvas.create_entries(set_focus_color, unset_focus_color)

    is_special = re.compile(r'[\ \.@\-\+=\_!\#\$%\^&\*\(\)\<\>\?\\\/\|\}\{~\:`\[\]]')

    def key(event):
        if not True in [str.isalnum(str(event.char)), is_special.search(str(event.char)) is not None]:
            return
        if search_label.emptyQuery and not search_label.labeltext == "":
            search_label.changeText("")
            search_label.emptyQuery = False
            search_label.changeText(search_label.labeltext + str(event.char))
            canvas.dropdown = True
            canvas.buttons_list[0].focus_on_btn()
            canvas.move_to_non_recursive(window, 539, 672, 1, step=1, speed=5)
        else:
            search_label.changeText(search_label.labeltext + str(event.char))

    def delete(event):
        text = search_label.labeltext
        if len(text) == 1:
            text = ""
        elif search_label.emptyQuery:
            pass
        else:
            text = text[:-1]
        search_label.changeText(text)
        if not search_label.emptyQuery and search_label.labeltext == "":
            search_label.changeText("Start typing...")
            search_label.emptyQuery = True
            canvas.dropdown = False
            buttons[1][1].focus_on_btn()
            canvas.move_to_non_recursive(window, 539, 80, 1, step=1, speed=7) 

    def esc(event):
        window.destroy()
    
    fMgr = FocusManager()
    
    def move_focus(event):
        if event.keycode not in [111, 116, 113, 114]:
            return
        if canvas.dropdown:
            if event.keycode == 111: # UP
                fMgr.cur_drop_focus_pos -= 1
                if fMgr.cur_drop_focus_pos < 0:
                    fMgr.cur_drop_focus_pos = canvas.entries_amount - 1
            elif event.keycode == 116: # DOWN
                fMgr.cur_drop_focus_pos += 1
                if fMgr.cur_drop_focus_pos >= canvas.entries_amount:
                # move to the first elem
                    fMgr.cur_drop_focus_pos = 0
            canvas.buttons_list[fMgr.cur_drop_focus_pos].focus_on_btn()
        else:
            increment = lambda x: (x+1)%3
            decrement = lambda x: (x+2)%3
            if event.keycode == 113: # LEFT
                fMgr.cur_focus_pos = (fMgr.cur_focus_pos[0], decrement(fMgr.cur_focus_pos[1]))
            elif event.keycode == 114: # RIGHT
                fMgr.cur_focus_pos = ((fMgr.cur_focus_pos[0], increment(fMgr.cur_focus_pos[1])))
            elif event.keycode == 111: # UP
                fMgr.cur_focus_pos = ((decrement(fMgr.cur_focus_pos[0])), fMgr.cur_focus_pos[1])
            elif event.keycode == 116: # DOWN
                fMgr.cur_focus_pos = ((increment(fMgr.cur_focus_pos[0])), fMgr.cur_focus_pos[1])
            buttons[fMgr.cur_focus_pos[0]][fMgr.cur_focus_pos[1]].focus_on_btn()

    def launch_on_enter(event):
        if canvas.dropdown:
            canvas.buttons_list[fMgr.cur_drop_focus_pos]._btn.exec_launch()
        else:
            buttons[fMgr.cur_focus_pos[0]][fMgr.cur_focus_pos[1]]._btn.exec_launch()
        window.destroy()

    window.bind("<Key>", key)
    window.bind("<BackSpace>", delete)
    window.bind("<Escape>", esc)
    window.bind("<Up>", move_focus)
    window.bind("<Down>", move_focus)
    window.bind("<Left>", move_focus)
    window.bind("<Right>", move_focus)
    window.bind("<Return>", launch_on_enter)
    window.mainloop()

if __name__ == "__main__":
    main()

