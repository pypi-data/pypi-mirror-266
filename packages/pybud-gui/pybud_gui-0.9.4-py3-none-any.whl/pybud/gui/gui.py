
import time
from threading import Thread
from typing import List

try:
    from readchar import key as Key
    from readchar import readkey
except ModuleNotFoundError:
    print("Unable to find dependency module named 'readchar', install using 'pip install readchar'")
    exit(1)

import pybud.ansi as ansi
from pybud.drawer import ColoredString as CStr
from pybud.drawer import ColorType, Drawer
from .widgets import Widget
from .utils import DEFAULT_BACKGROUND_COLOR

LAST_SHOWN_DRAWABLE = None

class Drawable():
    def __init__(self, ctype: ColorType = None):
        self.ctype = ctype
        self.width = None
        self.height = None
        self.background_color = DEFAULT_BACKGROUND_COLOR
        self.is_disabled = False
        self.closed = True
        self.drawing = False
        #self.last_update = 0
        
        self.tickupdate_started = False
    
    def onClose(self):
        self.close()

    def close(self):
        self.closed = True
        while self.tickupdate_thread.is_alive():
            time.sleep(1/20)
        self.tickupdate_started = False
        ansi.go_up(self.height)
        ansi.write(("\n" + " " * self.width) * (self.height))
        ansi.write(f"\033M" * self.height)
        ansi.write(f"\r" + " " * self.width)
        ansi.write(f"\033M\n")
        

    def update(self, key: str):
        # fix a race condition that breaks refreshing the drawable
        
        if key == Key.CTRL_C:
            self.onClose()
        if key == Key.ESC:
            self.onClose()
        return key

    def doTickUpdates(self):
        t = time.time()
        while not self.closed:
            time.sleep(max(0, 1/20 - (time.time() - t)))
            self.update("UPDATE")
            t = time.time() 
            
    
    def doKeyUpdates(self):
        while not self.closed:
            try:
                key = readkey()
            except KeyboardInterrupt:
                key = Key.CTRL_C
            self.update(key)
            

    def show(self):
        global LAST_SHOWN_DRAWABLE
        LAST_SHOWN_DRAWABLE = self
        self.closed = False

        ansi.write("\n" * self.height)
        self.draw()
        
        if not self.tickupdate_started:
            self.tickupdate_thread = Thread(target=self.doTickUpdates)
            self.tickupdate_thread.start()
            self.tickupdate_started = True
        self.doKeyUpdates()

    def get_drawer(self):
        self.drawing = True
        return Drawer(size=(self.width, self.height), background_color=self.background_color)

    def draw(self):
        if not self.closed:
            self.drawer = self.get_drawer()

class AutoDialouge(Drawable):
    def __init__(self, width: int, ctype: ColorType = None, mode:str = "v"):
        super().__init__(ctype)
        self.width = width
        self.height = 3
        self.widgets: List[Widget] = []
        self.set_active_widget(0)
        self.result = None
        self.tick = 0
        self.mode = mode

    def update_height(self):
        max_height = 0
        for w in self.widgets:
            widget_height = w.pos.getY() + w.size.getHeight()
            if widget_height > max_height:
                max_height = widget_height

        # set the height to one line more than the end of most buttom added dialouge
        self.height = max_height + 1

    def add_widget(self, w: Widget):
        w.parent = self
        self.widgets.append(w)
        # self.height += w.size.getHeight()
        self.update_height()
        

    def get_total_selectable_widgets(self):
        i = 0
        for w in self.widgets:
            if w.selectable:
                i += 1
        return i

    def get_active_widget(self, return_i: bool = False):
        i = 0
        for w in self.widgets:
            if not w.selectable:
                continue
            if w.is_disabled:
                i += 1
                continue
            if return_i:
                return w, i
            else:
                return w

        return None, 0

    def set_active_widget(self, __i: int):
        i = 0
        for w in self.widgets:
            if not w.selectable:
                continue

            if i == __i:
                w.is_disabled = False
            else:
                w.is_disabled = True
            i += 1

    def on_enter(self):
        return self.run_callbacks()

    def run_callbacks(self):
        w, active_i = self.get_active_widget(True)
        if w is not None:
            self.result = w.run_callbacks()

    def update(self, key):
        key = super().update(key)
        if key == Key.ENTER:
            self.on_enter()
            return

        w, i = self.get_active_widget(True)
        if w is not None:
            key = w.update(key)

        if key == Key.TAB:
            self.set_active_widget(
                (i + 1) % self.get_total_selectable_widgets())

        if self.mode.lower() == "v":
            if key == Key.UP:
                self.set_active_widget(
                    (i - 1) % self.get_total_selectable_widgets())
            elif key == Key.DOWN:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
        
        if self.mode.lower() == "iv":
            if key == Key.DOWN:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
            elif key == Key.UP:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())

        if self.mode.lower() == "h":
            if key == Key.LEFT:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
            elif key == Key.RIGHT:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
        
        if self.mode.lower() == "ih":
            if key == Key.RIGHT:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
            elif key == Key.LEFT:
                self.set_active_widget(
                    (i + 1) % self.get_total_selectable_widgets())
        
        if key == "UPDATE":
            self.tick += 1
        
        self.draw()

    def draw(self):
        if self.closed or self.drawing:
            return
        super().draw()
        animation = "▁▂▃▄▅▆▆▅▄▃▂▁▂ "
        def getadmination(tick, n = 3):
            rt = tick
            return animation[rt % (len(animation)-n):rt % (len(animation)-n)+n]
        self.drawer.place(CStr(getadmination(self.tick)), pos = (1, 0))
        w, active_i = self.get_active_widget(True)
        ansi.go_up(self.height)
        i = 0
        for w in self.widgets:
            border = w.selectable and i == active_i
            if w.selectable:
                i += 1
            self.drawer.place_drawer(
                w.get_render(), (w.pos.getX(), w.pos.getY()), borderless=not border)
        ansi.write(self.drawer.tostring(self.ctype) + "\n")
        ansi.flush()
        #time.sleep(0.01)
        self.drawing = False

    def show(self):
        super().show()
        return self.result
