import customtkinter

class CTkPopupMenu(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 width=120,
                 height=25,
                 popup_type=0, # 0 for right click, 1 for bottom side, 2 for left side, 3 for right side, 4 for top
                 text_color=None,
                 hover_color=None,
                 hover: bool=True,
                 border_width: int=1,
                 values: dict={},
                 font=None,
                 corner_radius: int=5,
                 **kwargs):
        
        super().__init__(master.winfo_toplevel(), border_width=border_width, width=width, corner_radius=corner_radius, **kwargs)

        self.text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        self.hover_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"] if hover_color is None else hover_color
        self.corner_radius = corner_radius
        self.hover = hover
        self.values = values
        self.spawn = popup_type
        self.widget = master
        self.height = height
        self.width = width
        
        if not font:
            self.font = customtkinter.CTkFont(customtkinter.ThemeManager.theme["CTkFont"]["family"],
                                              customtkinter.ThemeManager.theme["CTkFont"]["size"])
        else:
            if isinstance(font, customtkinter.CTkFont):
                self.font = font
            else:
                self.font = customtkinter.CTkFont(*font)
                
        for i in self.values:
            self.add_buttons(text=i, command=self.values[i])

        if self.spawn==0:
            self.widget.bind("<Button-3>", lambda event: self.popup(), add="+") # right click mouse bind
        else:
            self.widget.bind("<Button-1>", lambda event: self.popup(), add="+")
            
        self.widget.winfo_toplevel().bind("<Button-1>", lambda event: self.hide(), add="+")
        self.widget.bind("<FocusOut>", lambda event: self.hide(), add="+")
        self.widget.bind("<Configure>", lambda event: self.hide(), add="+")
        self.bind("<Button-1>", lambda event: self.hide())
        self.widget.bind("<Destroy>", lambda event: self.destroy())
        
    def add_buttons(self, text, command, **kwargs):
        button = customtkinter.CTkButton(self, height=self.height, width=self.width, text=text, command=command,
                                         fg_color="transparent", corner_radius=self.corner_radius,
                                         hover=self.hover, hover_color=self.hover_color, border_width=0, anchor="w", font=self.font,
                                         **kwargs)
        button.pack(padx=5, pady=5)
        button.bind("<Button-1>", lambda event: self.hide(), add="+")
        
    def clear_all(self):
        for i in self.winfo_children():
            i.destroy()

    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = kwargs.pop("values")
        
        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")

        if "hover_color" in kwargs:
            self.hover_color = kwargs.pop("hover_color")

        if "hover" in kwargs:
            self.hover = kwargs.pop("hover")

        if "corner_radius" in kwargs:
            self.corner_radius = kwargs["corner_radius"]

        if "font" in kwargs:
            self.font = kwargs.pop("font")

        super().configure(**kwargs)
        
        self.clear_all()
        
        for i in self.values:
            self.add_buttons(text=i, command=self.values[i])

    def cget(self, param):
        if param=="values":
            return self.values
        if param=="text_color":
            return self.text_color
        if param=="hover_color":
            return self.hover_color
        if param=="hover":
            return self.hover
        if param=="font":
            return self.font
        return super().cget(param)

    def destroy(self):
        super().destroy()
        
    def popup(self):
        if self.spawn==0:
            x = self.widget.winfo_x() + self.widget.winfo_pointerx() - self.widget.winfo_rootx() + 10
            y = self.widget.winfo_y() + self.widget.winfo_pointery() - self.widget.winfo_rooty() + 10

        if self.spawn==1:
            x = self.widget.winfo_x()
            y = self.widget.winfo_y() + self.widget.winfo_reqheight() + 5

        if self.spawn==2:
            x = self.widget.winfo_x() + self.widget.winfo_reqwidth() + 5
            y = self.widget.winfo_y() 

        if self.spawn==3:
            x = self.widget.winfo_x() - self.winfo_reqwidth() -5
            y = self.widget.winfo_y()

        if self.spawn==4:
            x = self.widget.winfo_x() - self.winfo_reqwidth() -5
            y = self.widget.winfo_y() - self.winfo_reqheight() -5
            
        self.place(x=x,y=y)
        self.focus()
        self.lift()
        
    def hide(self):
        if self.widget.winfo_exists():
            if self.winfo_ismapped():
                self.place_forget()
        
