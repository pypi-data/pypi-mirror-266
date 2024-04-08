import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk

class CTkMeter(ctk.CTkLabel):
    """
    A custom Tkinter widget that displays a circular progress meter.
    """
    
    def __init__(self,
                 master,
                 command=None,
                 value=50,
                 **kwargs):

        self.arc = None
        self.im = Image.new('RGBA', (1000, 1000))
        
        self.min_value = kwargs.get('from_') or 0
        self.max_value = kwargs.get('to_') or 100
        self.steps = kwargs.get('number_of_steps') or 1

        if self.min_value>=self.max_value:
            raise ValueError("min value is larger than max value!")
        
        self.size = kwargs.get('size') or 150
        self.scroll = kwargs.get('scroll') or True
        
        self.background = kwargs.get('bg_color') or master.cget("fg_color")
        self.foreground = kwargs.get('fg_color') or ctk.ThemeManager.theme["CTkSlider"]["fg_color"]
        self.border_width = kwargs.get('border_width') or 0
        self.border_color = kwargs.get('border_color') or ctk.ThemeManager.theme["CTkButton"]["border_color"]
        self.width = kwargs.get('line_width') or 10
        self.progresscolor = kwargs.get('progress_color') or ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.arcvariable = tk.IntVar(value='text')
        self.arcvariable.trace_add('write', self.update_arcvariable)
        self.textvariable = tk.StringVar()
        self.widget = master
        self.value = value
        self.command = command
        self.bg = master.cget("fg_color")
        
        if self.foreground=="transparent":
            self.foreground = self.background
        
        super().__init__(master, image=self.arc, fg_color=self.background, compound='center',
                         textvariable=self.textvariable)
        self.set(self.value)
        
        if self.scroll==True:
            super().bind('<MouseWheel>', self.scroll_command)
            super().bind("<Button-4>", lambda e: self.scroll_command(-1))
            super().bind("<Button-5>", lambda e: self.scroll_command(1))

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self.size = int(self._apply_widget_scaling(self.size))
        self.width = int(self._apply_widget_scaling(self.width))
        self.border_width = int(self._apply_widget_scaling(self.border_width))
        self.set(self.value)
        
    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        self.set(self.value)
        
    def scroll_command(self, event):
        """
        This function is used to change the value of the dial with mouse scroll
        """
        if type(event) is int:
            event_delta = event
        else:
            event_delta = event.delta
            
        if event_delta > 0:
            if self.value < self.max_value:
                self.set(self.value+self.steps)
            if self.value > self.max_value-1:
                self.set(self.max_value-1)
        else:
            if self.value > self.min_value:
                self.set(self.value-self.steps)
            if self.value < self.min_value:
                self.set(self.min_value)
        
    def update_arcvariable(self, *args):
        """Redraw the arc image based on variable settings"""

        width = self.width *10
        angle = int(float(self.arcvariable.get())) + 90
        self.im = Image.new('RGBA', (1000, 1000))
        draw = ImageDraw.Draw(self.im)
        draw.arc((0,0, 990, 990), 0, 360, self.widget._apply_appearance_mode(self.border_color), self.border_width)
        draw.arc((self.border_width, self.border_width, 990-self.border_width, 990-self.border_width), 0, 360, self.widget._apply_appearance_mode(self.foreground), width)
        draw.arc((self.border_width, self.border_width, 990-self.border_width, 990-self.border_width), 90, angle, self.widget._apply_appearance_mode(self.progresscolor), width)
        draw.arc((width+self.border_width, width+self.border_width, 990-width-self.border_width, 990-width-self.border_width), 0, 360,
                 self.widget._apply_appearance_mode(self.border_color), self.border_width)
        self.arc = ctk.CTkImage(self.im.resize((self.size, self.size), Image.LANCZOS), size=(self.size, self.size))
        super().configure(image=self.arc)
        
    def set(self, value):
        """Set the value of arcvariable and call loading_hover_effect if refresh_value is True"""
        angle = float(-(360/(self.min_value - self.max_value))*(value - self.max_value))
        self.value = value
        self.arcvariable.set(angle)
        if self.command:
            self.command(value)
            
    def cget(self, param):

        if param=="fg_color":
            return self.foreground
        if param=="bg_color":
            return self.background
        if param=="border_color":
            return self.border_color
        if param=="border_width":
            return self.border_width
        if param=="progress_color":
            return self.progresscolor
        if param=="line_width":
            return self.width
        if param=="size":
            return self.size
        if param=="width":
            return super().winfo_width()
        if param=="height":
            return super().winfo_height()
        if param=="value":
            return self.value
        if param=="from_":
            return self.min_value
        if param=="to":
            return self.max_value
        if param=="number_of_steps":
            return self.steps
        if param=="scroll":
            return self.scroll
        if param=="text":
            raise ValueError(f"No such parameter: {param}")
        if param=="justify":
            raise ValueError(f"No such parameter: {param}")
        if param=="text_color":
            raise ValueError(f"No such parameter: {param}")
        if param=="text_color_disabled":
            raise ValueError(f"No such parameter: {param}")
        if param=="corner_radius":
            raise ValueError(f"No such parameter: {param}")
        if param=="font":
            raise ValueError(f"No such parameter: {param}")
        if param=="image":
            raise ValueError(f"No such parameter: {param}")
        return super().cget(param)

    def configure(self, **kwargs):
        
        if "fg_color" in kwargs:
            self.foreground = kwargs.pop("fg_color")
            if self.foreground=="transparent":
                self.foreground = self.bg
        if "bg_color" in kwargs:
            self.background = kwargs["bg_color"]
            kwargs.update({"fg_color": self.background})
        if "border_color" in kwargs:
            self.border_color = kwargs.pop("border_color")
        if "border_width" in kwargs:
            self.border_width = kwargs.pop("border_width")
        if "progress_color" in kwargs:
            self.progresscolor = kwargs.pop("progress_color")
        if "size" in kwargs:
            self.size = kwargs.pop("size")
        if "line_width" in kwargs:
            self.width = kwargs.pop("line_width")
        if "from_" in kwargs:
            self.min_value = kwargs.pop("from_")
        if "to" in kwargs:
            self.max_value = kwargs.pop("to")
        if "state" in kwargs:
            if kwargs.pop("state")=="disabled":
                kwargs.update({"scroll":False})
            else:
                kwargs.update({"scroll":True})
            
        if "number_of_steps" in kwargs:
            self.steps = kwargs.pop("number_of_steps")
        if "scroll" in kwargs:
            self.scroll = kwargs.pop("scroll")
            
            if self.scroll==True:
                super().bind('<MouseWheel>', self.scroll_command)
                super().bind("<Button-4>", lambda e: self.scroll_command(-1))
                super().bind("<Button-5>", lambda e: self.scroll_command(1))
            else:
                super().unbind('<MouseWheel>')
                super().unbind("<Button-4>")
                super().unbind("<Button-5>")
            
        self.set(self.value)
        
        super().configure(**kwargs)

    def get(self):
        return self.value
