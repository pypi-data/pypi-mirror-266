import time
import tkinter as tk
import customtkinter as ctk

class CTkTooltip(tk.Message):

    def __init__(
        self,
        master: any,
        text: str=None,
        delay: float = 1.5,
        fg_color=None,
        text_color=None,
        state="normal",
        **kwargs,
         ):

        self.widget = master
        self.msg = text
        self.delay = delay
        self.state = state
        self.msgVar = tk.StringVar()
        self.fg_color = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"] if fg_color is None else fg_color
        self.text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        
        self.msgVar.set(self.msg)
        
        self.status = "outside"
        
        super().__init__(master.winfo_toplevel(), textvariable=self.msgVar, aspect=1000,
                         bg=self.widget._apply_appearance_mode(self.fg_color),
                         fg=self.widget._apply_appearance_mode(self.text_color),
                         **kwargs)

        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<ButtonPress>", self.on_leave, add="+")
        self.widget.bind("<Destroy>", lambda e: self.destroy(), add="+")
        
    def on_enter(self, event) -> None:
        if self.state=="disabled":
            self.place_forget()
            return
        
        self.last_moved = time.time()

        if self.status == "outside":
            self.status = "inside"

        root_width = self.widget.winfo_toplevel().winfo_width()
        
        widget_x = event.x_root
        
        space_on_right = root_width - widget_x
        
        text_width = self.winfo_reqwidth()

        self.x_offset = 0
        
        if space_on_right < text_width + 20:  
            self.x_offset = -text_width - 20  
        
        self.after(int(self.delay * 1000), self._show)
        
    def _set_appearance_mode(self, mode_string):
        self.config(bg=self.widget._apply_appearance_mode(self.fg_color),
                    fg=self.widget._apply_appearance_mode(self.text_color))
        
    def on_leave(self, event=None) -> None:
        self.status = "outside"
        self.place_forget()
        
    def configure(self, **kwargs) -> None:
        if "text" in kwargs:
            self.msg = kwargs.pop("text")
        if "delay" in kwargs:
            self.delay = kwargs.pop("delay")
        if "fg_color" in kwargs:
            self.fg_color = kwargs.pop("fg_color")
            self.config(bg=self.widget._apply_appearance_mode(self.fg_color))
        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")
            self.config(fg=self.widget._apply_appearance_mode(self.text_color))
        if "state" in kwargs:
            self.state = kwargs.pop("state")
            
        super().config(**kwargs)
        
    def _show(self):
        if self.status=="outside":
            return
        self.x = self.widget.winfo_x() + self.widget.winfo_pointerx() - self.widget.winfo_rootx() + 10 + self.x_offset
        self.y = self.widget.winfo_y() + self.widget.winfo_pointery() - self.widget.winfo_rooty() + 10
        self.place(x=self.x, y=self.y)
        self.lift()
    
