from PIL import Image
import customtkinter as ctk

class CTkGif(ctk.CTkLabel):

    def __init__(self,
                 master: any,
                 width: int=100,
                 height: int=100,
                 path: str=None,
                 loop: bool=True,
                 speed: int=1,
                 repeat: int=1,
                 **kwargs):
        
        super().__init__(master, **kwargs)
        if speed <= 0:
            speed = 1
        
        self.master = master  
        self.repeat = repeat  
        super().configure(text='', fg_color="black", width=width, height=height, corner_radius=0)
        
        self.path = path
        self.speed = speed
        if self.speed>50:
            self.speed = 50
        if self.path:
            super().configure(fg_color="transparent")
            self.gif = Image.open(path)
            self.n_frame = self.gif.n_frames  
            self.frame_duration = self.gif.info['duration'] * 1/self.speed
            self.after(500, lambda: self.start())
        else:
            self.gif = None
            
        self.count = 0  
        self.loop = loop  
        self.index = 0  
        self.is_playing = False  
        self.force_stop = False

    def update(self): 
        if self.index < self.n_frame:  
            if not self.force_stop:  
                self.gif.seek(self.index)  
                self.configure(image=ctk.CTkImage(self.gif, size=(self.winfo_width(), self.winfo_height())))  
                self.index += 1  
                self.after(int(self.frame_duration), self.update)  
            else:
                self.force_stop = False  
        else:  
            self.index = 0  
            self.count += 1  
            if self.is_playing and (self.count < self.repeat or self.loop): 
                self.after(int(self.frame_duration), self.update)  
            else:
                self.is_playing = False

    def start(self):
        if not self.path:
            return
        if not self.is_playing:
            self.count = 0
            self.is_playing = True
            self.after(int(self.frame_duration), self.update)

    def stop(self, forced=False):
        if self.is_playing:
            self.is_playing = False
            self.force_stop = forced

    def toggle(self, forced=False):
        if self.is_playing:
            self.stop(forced=forced)
        else:
            self.start()

    def configure(self, **kwargs):
        if "repeat" in kwargs:
            self.repeat = kwargs.pop("repeat")
        if "loop" in kwargs:
            self.loop = kwargs.pop("loop")
        if "path" in kwargs:
            self.path = kwargs.pop("path")
            self.gif = Image.open(self.path)
            super().configure(fg_color="transparent")
            self.n_frame = self.gif.n_frames  
            self.frame_duration = self.gif.info['duration'] * 1/self.speed
        if "speed" in kwargs:
            self.speed = kwargs.pop("speed")
            if self.speed>50:
                self.speed = 50
            self.frame_duration = self.gif.info['duration'] * 1/self.speed
            if self.speed==0:
                self.speed = 1
        
        super().configure(**kwargs)

    def cget(self, param):
        if param=="repeat":
            return self.repeat
        if param=="loop":
            return self.loop
        if param=="path":
            return self.path
        if param=="speed":
            return self.speed
        if param=="text":
            raise ValueError("Invalid Parameter")
        if param=="font":
            raise ValueError("Invalid Parameter")
        if param=="image":
            raise ValueError("Invalid Parameter, use path parameter for gif")
        if param=="text_color":
            raise ValueError("Invalid Parameter")
        if param=="text_color_disabled":
            raise ValueError("Invalid Parameter")
        if param=="corner_radius":
            raise ValueError("Invalid Parameter")
        if param=="justify":
            raise ValueError("Invalid Parameter")
        if param=="padx":
            raise ValueError("Invalid Parameter")
        if param=="pady":
            raise ValueError("Invalid Parameter")
        
        return super().cget(param)
