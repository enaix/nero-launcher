import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Pil_image, ImageTk as Pil_imageTk
from importlib import import_module, util
from fuzzywuzzy import fuzz, process
import time
import re
import os
import configparser
import operator
import argparse
import variables
import json

class Config():
    def __init__(self):
        self.parser = variables.EXPORT_CONFIG
        
        self.argparser = argparse.ArgumentParser("nero-launcher")
        self.argparser.add_argument("-c", "--config", help="Path to the configuration file")
        self.argparser.add_argument("-d", "--directory", help="Nero installation folder")
        self.argparser.add_argument("-f", "--folder", help="Config folder")
        self.args = self.argparser.parse_args()
        if self.args.config != None:
            self.custom_settings = import_module(self.args.config)
            self.parser = {**self.parser, **self.custom_settings.CONFIG}
        
        if self.args.directory == None:
            os.chdir(self.parser['DefaultInstallationFolder'])
        else:
            os.chdir(self.args.directory)

        if self.args.folder == None:
            self.config_dir = self.parser['DefaultConfigFolder']
        else:
            self.config_dir = self.args.folder

        if os.path.exists(self.config_dir):
            mod_file = self.importModule(self.config_dir, "main", "main.py")
            for mod in mod_file.MODULES:
                self.parser = {**self.parser, **self.importModule(self.config_dir, mod, mod + ".py").CONFIG}

        self.width = self.parser['ButtonWidth'] * self.parser['ButtonsAmountX']
        self.height = self.parser['SearchLabelHeight'] + self.parser['RoundBoxHeight'] + self.parser['ButtonHeight'] * self.parser['ButtonsAmountY']
        self.top_panel_height = self.parser['SearchLabelHeight'] + self.parser['RoundBoxHeight']

        update_meta = False

        if os.path.exists(self.parser['AppCacheFileLocation']):
            self.importApps(self.parser['AppCacheFileLocation'])
        else:
            self.rescan()
            update_meta = True

        if os.path.exists(self.parser['AppMetaFileLocation']):
            self.importMeta(self.parser['AppMetaFileLocation'])
        else:
            self.createMeta()

        if update_meta:
            self.updateMeta()

    def importModule(self, folder, name, path):
        spec = util.spec_from_file_location(name, folder + "/" + path)
        foo = util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo

    def exportApps(self, dest):
        with open(dest, 'w') as out:
            json.dump(self.apps, out)

    def importApps(self, src):
        with open(src) as inp:
            data = json.load(inp)
            self.apps = data

    def exportMeta(self, dest):
        with open(dest, 'w') as out:
            json.dump(self.app_meta, out)

    def importMeta(self, src):
        with open(src) as inp:
            data = json.load(inp)
            self.app_meta = data

    def createMeta(self):
        self.app_meta = {}
        for i in range(len(self.apps)):
            self.app_meta[self.apps[i]['Name']] = {'Launchs': 0, 'App': self.apps[i]}

    def updateMeta(self):
        for i in range(len(self.apps)):
            if self.app_meta.get(self.apps[i]['Name']) is None:
                self.app_meta[self.apps[i]['Name']] = {'Launchs': 0, 'App': self.apps[i]}

    def rescan(self, *args, **kwargs):
        self.apps = []
        for folder in self.parser['DesktopFolders']:
            self.scanFolder(folder)
        self.exportApps(self.parser['AppCacheFileLocation'])

    def scanFolder(self, path):
        files = os.listdir(path=path)
        for i in files:
            if i.split('.')[::-1][0] == 'desktop':
                self.apps.append(self.scanApp(path + '/' + i))

    def getIconPath(self, icon):
        if not icon.find('/') == -1:
            return icon
        for folder in self.parser['IconFolders']:
            for theme in self.parser['IconThemes']:
                for res in self.parser['IconResolutions']:
                    for ext in self.parser['IconFormats']:
                        if os.path.isfile(folder + '/' + theme + '/' + res + '/apps/' + icon + '.' + ext):
                            return folder + '/' + theme + '/' + res + '/apps/' + icon + '.' + ext

    def scanApp(self, path):
        conf = configparser.ConfigParser(interpolation=None)
        conf.read(path)
        res = {'Name': None, 'Exec': None, 'Icon': None, 'IconPath': None}
        if 'Name' in conf['Desktop Entry']:
            res['Name'] = conf['Desktop Entry']['Name']
        if 'Exec' in conf['Desktop Entry']:
            res['Exec'] = conf['Desktop Entry']['Exec']
        if 'Icon' in conf['Desktop Entry']:
            res['Icon'] = conf['Desktop Entry']['Icon']
            res['IconPath'] = self.getIconPath(res['Icon'])
        return res

config = Config()

class AppButton(ttk.Frame):
    def __init__(self, parent, text="", f_style=None, height=None, width=None, img_width=config.parser['ButtonImageSize'], compound='top', image_path=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, height=height, width=width, style=f_style)
        if not image_path == None:
            try:
                img_raw = Pil_image.open(image_path).resize((img_width, img_width), Pil_image.ANTIALIAS)
            except BaseException:
                self._photo = None
            else:
                self._photo = Pil_imageTk.PhotoImage(img_raw)
        else:
            self._photo = None
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, image=self._photo, compound=compound, *args, **kwargs)
        self._btn.pack(fill=tk.BOTH, expand=1, padx=config.parser['ButtonFramePaddingX'], pady=config.parser['ButtonFramePaddingY'])
        self.exec_path = None
        def exec_launch():
            self.launch()
        self._btn.exec_launch = exec_launch
        self._btn.text = text

    def focus_on_btn(self):
        self.focus_set()
        self._btn.focus_set()

    def set_style(self, style):
        self._btn.configure(style=style)

    def configure_btn(self):
        pass

    def launch(self):
        if not self.exec_path == None:
            # Export metadata
            config.app_meta[self._btn.text]['Launchs'] += 1
            config.exportMeta(config.parser['AppMetaFileLocation'])
            os.system("./launcher.sh " + self.exec_path + " 2>&1")

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

    def create_entries(self, focus_func, unfocus_func, click_func):
        self.focus_func = focus_func
        self.unfocus_func = unfocus_func
        self.click_func = click_func
        self.buttons_list = []
        self.entries_amount = (config.height - config.top_panel_height)//config.parser['DropdownButtonHeight']
        self.process_elems = sorted(config.apps, key=lambda x: x['Name'])
        self.sorted_elems = self.process_elems
        self.list_pos = 0
        self.actual_entries_amount = self.entries_amount
        if self.entries_amount + (self.list_pos//self.entries_amount)*self.entries_amount > len(self.sorted_elems):
            self.actual_entries_amount = len(self.sorted_elems) - (self.list_pos//self.entries_amount)*self.entries_amount
        self.search_elems = self.sorted_elems[(self.list_pos//self.entries_amount)*self.entries_amount:(self.list_pos//self.entries_amount)*self.entries_amount + self.actual_entries_amount]
        for i in range(self.entries_amount):
            if i >= len(self.search_elems):
                continue
            btn = AppButton(self, self.search_elems[i]['Name'], f_style='L.TFrame', width=config.width, height=config.parser['DropdownButtonHeight'], img_width=config.parser['DropdownButtonIconSize'], compound='left', style='W.TButton', image_path=self.search_elems[i]['IconPath'])
            btn.exec_path = self.search_elems[i]['Exec']
            btn.place(x=0, y=config.top_panel_height+i*config.parser['DropdownButtonHeight'])
            btn.bind("<FocusIn>", focus_func)
            btn.bind("<FocusOut>", unfocus_func)
            btn._btn.bind("<Button-1>", click_func)
            self.buttons_list.append(btn)

    def search(self, phrase):
        res = process.extract(phrase, self.process_elems, limit=len(self.process_elems))
        self.sorted_elems = [i[0] for i in res]
        self.list_pos = 0
        self.redraw_entries(True)

    def redraw_entries(self, update=False):
        if update:
            self.destroy_entries()
            self.buttons_list = []
        self.actual_entries_amount = self.entries_amount
        if self.entries_amount + (self.list_pos//self.entries_amount)*self.entries_amount > len(self.sorted_elems):
            self.actual_entries_amount = len(self.sorted_elems) - (self.list_pos//self.entries_amount)*self.entries_amount
        self.search_elems = self.sorted_elems[(self.list_pos//self.entries_amount)*self.entries_amount:(self.list_pos//self.entries_amount)*self.entries_amount + self.actual_entries_amount]
        if not update:
            return
        for i in range(self.entries_amount):
            if i >= len(self.search_elems):
                continue
            btn = AppButton(self, self.search_elems[i]['Name'], f_style='L.TFrame', width=config.width, height=config.parser['DropdownButtonHeight'], img_width=config.parser['DropdownButtonIconSize'], compound='left', style='W.TButton', image_path=self.search_elems[i]['IconPath'])
            btn.exec_path = self.search_elems[i]['Exec']
            btn.place(x=0, y=config.top_panel_height+i*config.parser['DropdownButtonHeight'])
            btn.bind("<FocusIn>", self.focus_func)
            btn.bind("<FocusOut>", self.unfocus_func)
            btn._btn.bind("<Button-1>", self.click_func)
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
    window.title('nero')
    #window.iconphoto(False, tk.PhotoImage(file='./logo_white.png'))
    # window.tk.call('wm', 'iconphoto', window._w, tk.PhotoImage(file='./logo_white.ico'))

    style = ttk.Style()
    style.configure('W.TButton', font=(config.parser['DefaultFont'], config.parser['ButtonFontSize']), foreground=config.parser['ButtonForegroundColor'], background=config.parser['ButtonBackgroundColor'], relief='flat', highlightthickness=0)
    style.map('W.TButton', background=[('pressed', config.parser['ButtonPressedBackgroundColor']), ('active', config.parser['ButtonActiveBackgroundColor'])])
    style.configure('WF.TButton', font=(config.parser['DefaultFont'], config.parser['ButtonFontSize']), foreground=config.parser['FocusedButtonForegroundColor'], background=config.parser['FocusedButtonBackgroundColor'], relief='flat', highlightthickness=0)
    style.map('WF.TButton', background=[('pressed', config.parser['FocusedButtonPressedForegroundColor']), ('active', config.parser['FocusedButtonActiveForegroundColor'])])
    style.configure('L.TFrame', background=config.parser['ButtonFrameBorderColor'])
    style.configure('G.TLabel', foreground=config.parser['SearchLabelForegroundColor'], font=(config.parser['DefaultFont'], config.parser['SearchLabelFontSize']))

    def set_focus_color(event):
        event.widget.set_style('WF.TButton')
    
    def unset_focus_color(event):
        event.widget.set_style('W.TButton')

    def launch_app(event):
        event.widget.exec_launch()
        window.destroy()

    window.grid_rowconfigure(0, minsize=config.top_panel_height)
    buttons = []
    popular_apps_dict = {key: value for key, value in sorted(config.app_meta.items(), key=lambda item: item[1]['Launchs'], reverse=True)}
    popular_apps = []
    for _, (k, v) in enumerate(popular_apps_dict.items()):
        popular_apps.append((k, v))
    for i in range(config.parser['ButtonsAmountY']):
        buttons.append([])
        for j in range(config.parser['ButtonsAmountX']):
            app = {'Name': None, 'IconPath': None, 'Exec': None}
            if not config.parser['Apps'][i][j] == None:
                if len(config.parser['Apps'][i][j]) == 3:
                    app['Name'] = config.parser['Apps'][i][j]['Name']
                    app['IconPath'] = config.parser['Apps'][i][j]['IconPath']
                    app['Exec'] = config.parser['Apps'][i][j]['Exec']
                elif len(config.parser['Apps'][i][j]) == 1:
                    app = config.scanApp(config.parser['Apps'][i][j]['Desktop'])
            else:
                try:
                    app = popular_apps[i*config.parser['ButtonsAmountX'] + j][1]['App']
                except IndexError:
                    pass
            btn = AppButton(window, app['Name'], f_style='L.TFrame', width=config.parser['ButtonWidth'], height=config.parser['ButtonHeight'], image_path=app['IconPath'], style='W.TButton')
            btn.exec_path = app['Exec']
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
    
    canvas.create_entries(set_focus_color, unset_focus_color, launch_app)

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
            canvas.search(search_label.labeltext)
            if len(canvas.sorted_elems) > 0:
                canvas.buttons_list[0].focus_on_btn()
            fMgr.cur_drop_focus_pos = 0
            canvas.move_to_non_recursive(window, config.width, config.height, 1, step=1, speed=config.parser['CanvasDropdownSpeed'], frame_skip=config.parser['CanvasDropdownFrameSkip'])
        else:
            canvas.search(search_label.labeltext)
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
        if not search_label.labeltext == "":
            canvas.search(search_label.labeltext)
            if len(canvas.sorted_elems) > 0:
                canvas.buttons_list[0].focus_on_btn()
            fMgr.cur_drop_focus_pos = 0
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
                canvas.list_pos -= 1
                if canvas.list_pos < 0:
                    canvas.list_pos = len(canvas.sorted_elems) - 1
                update = False
                if fMgr.cur_drop_focus_pos - 1 < 0:
                    update = True
                canvas.redraw_entries(update)
                fMgr.cur_drop_focus_pos -= 1
                if fMgr.cur_drop_focus_pos < 0:
                    fMgr.cur_drop_focus_pos = canvas.actual_entries_amount - 1
            elif event.keycode in config.parser['ButtonKeyDown']: # DOWN
                actual_entries = canvas.actual_entries_amount                
                canvas.list_pos += 1
                if canvas.list_pos >= len(canvas.sorted_elems):
                    canvas.list_pos = 0
                update = False
                if fMgr.cur_drop_focus_pos + 1 >= actual_entries:
                    update = True
                canvas.redraw_entries(update)
                fMgr.cur_drop_focus_pos += 1
                if fMgr.cur_drop_focus_pos >= actual_entries:
                    fMgr.cur_drop_focus_pos = 0
            if canvas.actual_entries_amount > 0:
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
    window.bind("<Control-r>", lambda event:[config.rescan(), config.updateMeta()])
    window.mainloop()

if __name__ == "__main__":
    main()

