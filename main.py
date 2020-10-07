import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Pil_image, ImageTk as Pil_imageTk
from importlib import import_module
import time
import re
import os
import argparse
import variables

#def on_press(key):

class Config():
    def __init__(self):
        self.parser = variables.EXPORT_CONFIG
        
        argparser = argparse.ArgumentParser("launcher")
        argparser.add_argument("-c", "--config", help="Path to the configuration file")
        args = argparser.parse_args()
        if args.config != None:
            self.custom_settings = import_module(args.config)
            self.parser = {**self.parser, **self.custom_settings.CONFIG}
        
        self.width = self.parser['ButtonWidth'] * self.parser['ButtonsAmountX']
        self.height = self.parser['SearchLabelHeight'] + self.parser['RoundBoxHeight'] + self.parser['ButtonHeight'] * self.parser['ButtonsAmountY']
        self.top_panel_height = self.parser['SearchLabelHeight'] + self.parser['RoundBoxHeight']

config = Config()

class AppButton(ttk.Frame):
    def __init__(self, parent, text="", f_style=None, height=None, width=None, img_width=config.parser['ButtonImageSize'], compound='top', *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=f_style)
        img_raw = Pil_image.open("/usr/share/icons/hicolor/128x128/apps/firefox-esr.png").resize((img_width, img_width), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, image=self._photo, compound=compound, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1, padx=config.parser['ButtonFramePaddingX'], pady=config.parser['ButtonFramePaddingY']) 
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
        img_raw = Pil_image.open(config.parser['SearchLabelIconPath']).resize((config.parser['SearchLabelIconSize'], config.parser['SearchLabelIconSize']), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        self._photoLabel = ttk.Label(self, image=self._photo, justify=tk.LEFT, *args, **kwargs)
        self.pack_propagate(0)
        self._photoLabel.pack(side=tk.LEFT, padx=config.parser['SearchLabelIconPaddingX'], pady=config.parser['SearchLabelIconPaddingY'])
        self._label.pack(side=tk.LEFT, padx=config.parser['SearchLabelInputPaddingX'], pady=config.parser['SearchLabelInputPaddingY'])

    def changeText(self, text):
        self.labeltext = text
        if len(text) >= config.parser['SearchLabelInputTruncate']:
            text = str(text[::-1][:config.parser['SearchLabelInputTruncate']] + '..')[::-1]
        self._label.configure(text=text)

class RoundBox(ttk.Label):
    def __init__(self, parent, height=None, width=None, style=None, *args, **kwargs):
        img_raw = Pil_image.open(config.parser['RoundBoxPath']).resize((width, height), Pil_image.ANTIALIAS)
        self._photo = Pil_imageTk.PhotoImage(img_raw)
        ttk.Label.__init__(self, parent, image=self._photo, *args, **kwargs)
        self.pack_propagate(0)

class CanvasBox(tk.Canvas):
    def __init__(self, parent, posx, posy, height, width):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=config.parser['CanvasBackgroundColor'])
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
        self.entries_amount = (config.height - config.top_panel_height)//config.parser['DropdownButtonHeight']
        for i in range(self.entries_amount):
            btn = AppButton(self, 'Chrome', f_style='L.TFrame', width=config.width, height=config.parser['DropdownButtonHeight'], img_width=config.parser['DropdownButtonIconSize'], compound='left', style='W.TButton')
            btn.place(x=0, y=config.top_panel_height+i*config.parser['DropdownButtonHeight'])
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
        self.cur_focus_pos = (config.parser['ButtonsAmountX']//2, config.parser['ButtonsAmountY']//2)
        self.cur_drop_focus_pos = 0

def main():
    window = tk.Tk()
    window.configure(background=config.parser['WindowBackground'])
    window.geometry(str(config.width) + "x" + str(config.height))
    window.resizable(False, False)
    style = ttk.Style()
    style.configure('W.TButton', font=(config.parser['ButtonFontSize']), foreground=config.parser['ButtonForegroundColor'], background=config.parser['ButtonBackgroundColor'], relief='flat', highlightthickness=0)
    style.map('W.TButton', background=[('pressed', config.parser['ButtonPressedBackgroundColor']), ('active', config.parser['ButtonActiveBackgroundColor'])])
    style.configure('WF.TButton', font=(config.parser['ButtonFontSize']), foreground=config.parser['FocusedButtonForegroundColor'], background=config.parser['FocusedButtonBackgroundColor'], relief='flat', highlightthickness=0)
    style.map('WF.TButton', background=[('pressed', config.parser['FocusedButtonPressedForegroundColor']), ('active', config.parser['FocusedButtonActiveForegroundColor'])])
    style.configure('L.TFrame', background=config.parser['ButtonFrameBorderColor'])
    style.configure('G.TLabel', foreground=config.parser['SearchLabelForegroundColor'], font=(config.parser['SearchLabelFontSize']))

    def set_focus_color(event):
        event.widget.set_style('WF.TButton')
    
    def unset_focus_color(event):
        event.widget.set_style('W.TButton')

    def launch_app(event):
        event.widget.exec_launch()
        window.destroy()

    window.grid_rowconfigure(0, minsize=config.top_panel_height)
    buttons = []
    for i in range(config.parser['ButtonsAmountY']):
        buttons.append([])
        for j in range(config.parser['ButtonsAmountX']):
            btn = AppButton(window, 'Chrome', f_style='L.TFrame', width=config.parser['ButtonWidth'], height=config.parser['ButtonHeight'], style='W.TButton')
            btn.grid(row=i+2, column=j)
            btn.bind("<FocusIn>", set_focus_color)
            btn.bind("<FocusOut>", unset_focus_color)
            btn._btn.bind("<Button-1>", launch_app)
            buttons[i].append(btn)

    canvas = CanvasBox(window, 0, 0, config.top_panel_height, config.width)
    canvas.create_roundbox()

    search_label = LabelBox(canvas, 'Start typing...', width=config.width, height=config.parser['SearchLabelHeight'], style='G.TLabel')
    search_label.place(x=0, y=0)
    rounded = RoundBox(canvas, config.parser['RoundBoxHeight'], config.width)
    rounded.place(x=0, y=config.parser['SearchLabelHeight'])
    
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
            canvas.move_to_non_recursive(window, config.width, config.height, 1, step=1, speed=config.parser['CanvasDropdownSpeed'], frame_skip=config.parser['CanvasDropdownFrameSkip'])
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
            buttons[config.parser['ButtonsAmountX']//2][config.parser['ButtonsAmountY']//2].focus_on_btn()
            canvas.move_to_non_recursive(window, config.width, config.top_panel_height, 1, step=1, speed=config.parser['CanvasDropdownReturnSpeed'], frame_skip=config.parser['CanvasDropdownReturnFrameSkip'])

    def esc(event):
        window.destroy()
    
    fMgr = FocusManager()
    
    def move_focus(event):
        if event.keycode not in [*config.parser['ButtonKeyUp'], *config.parser['ButtonKeyDown'], *config.parser['ButtonKeyLeft'], *config.parser['ButtonKeyRight']]:
            return
        if canvas.dropdown:
            if event.keycode in config.parser['ButtonKeyUp']: # UP
                fMgr.cur_drop_focus_pos -= 1
                if fMgr.cur_drop_focus_pos < 0:
                    fMgr.cur_drop_focus_pos = canvas.entries_amount - 1
            elif event.keycode in config.parser['ButtonKeyDown']: # DOWN
                fMgr.cur_drop_focus_pos += 1
                if fMgr.cur_drop_focus_pos >= canvas.entries_amount:
                # move to the first elem
                    fMgr.cur_drop_focus_pos = 0
            canvas.buttons_list[fMgr.cur_drop_focus_pos].focus_on_btn()
        else:
            increment = lambda x,v: (x+1)%config.parser['ButtonsAmount'+v]
            decrement = lambda x,v: (x+config.parser['ButtonsAmount'+v]-1)%config.parser['ButtonsAmount'+v]
            if event.keycode in config.parser['ButtonKeyLeft']: # LEFT
                fMgr.cur_focus_pos = (fMgr.cur_focus_pos[0], decrement(fMgr.cur_focus_pos[1], 'X'))
            elif event.keycode in config.parser['ButtonKeyRight']: # RIGHT
                fMgr.cur_focus_pos = ((fMgr.cur_focus_pos[0], increment(fMgr.cur_focus_pos[1], 'X')))
            elif event.keycode in config.parser['ButtonKeyUp']: # UP
                fMgr.cur_focus_pos = ((decrement(fMgr.cur_focus_pos[0], 'Y')), fMgr.cur_focus_pos[1])
            elif event.keycode in config.parser['ButtonKeyDown']: # DOWN
                fMgr.cur_focus_pos = ((increment(fMgr.cur_focus_pos[0], 'Y')), fMgr.cur_focus_pos[1])
            buttons[fMgr.cur_focus_pos[0]][fMgr.cur_focus_pos[1]].focus_on_btn()

    def launch_on_enter(event):
        if canvas.dropdown:
            canvas.buttons_list[fMgr.cur_drop_focus_pos]._btn.exec_launch()
        else:
            buttons[fMgr.cur_focus_pos[0]][fMgr.cur_focus_pos[1]]._btn.exec_launch()
        window.destroy()

    window.bind("<Key>", lambda event:[move_focus(event), key(event)])
    window.bind("<BackSpace>", delete)
    window.bind("<Escape>", esc)
    window.bind("<Return>", launch_on_enter)
    window.mainloop()

if __name__ == "__main__":
    main()

