import webbrowser
import customtkinter

class CTkHyperlink(customtkinter.CTkLabel):
    """
    Link widget for customtkinter
    Author: Akash Bora (Akascape)
    License: MIT
    """

    def __init__(self,
                 master,
                 url: str = None,
                 text: str = "CTkHyperlink",
                 text_color: tuple or str = ["#004a8c", "#66b4ef"],
                 font: tuple or customtkinter.CTkFont = None,
                 command: callable = None,
                 **kwargs):
        
        super().__init__(master, text=text, text_color=text_color, **kwargs)

        if not font:
            self.font = customtkinter.CTkFont(customtkinter.ThemeManager.theme["CTkFont"]["family"],
                                              customtkinter.ThemeManager.theme["CTkFont"]["size"])
        else:
            if isinstance(font, customtkinter.CTkFont):
                self.font = font
            else:
                self.font = customtkinter.CTkFont(*font)
                
        self.url = url
        self.command = command
        super().configure(font=self.font)
        
        self.bind("<Button-1>", lambda event: self.run_command())
        self.bind("<Enter>", lambda event: self.font.configure(underline=True) or self.configure(cursor="hand2"))
        self.bind("<Leave>", lambda event: self.font.configure(underline=False) or self.configure(cursor="arrow"))
        
    def run_command(self):
        if self.url:
            webbrowser.open_new_tab(self.url)
        if self.command:
            self.command()

    def cget(self, name):
        if name=="url":
            return self.url
        else:
            return super().cget(name)

    def configure(self, **kwargs):
        if "url" in kwargs:
            self.url = kwargs.pop("url")

        if "command" in kwargs:
            self.command = kwargs.pop("command")

        if "font" in kwargs:
            if isinstance(kwargs["font"], customtkinter.CTkFont):
                self.font = kwargs.pop("font")
            else:
                self.font = customtkinter.CTkFont(*kwargs.pop("font"))
            super().configure(font=self.font)
            
        super().configure(**kwargs)
