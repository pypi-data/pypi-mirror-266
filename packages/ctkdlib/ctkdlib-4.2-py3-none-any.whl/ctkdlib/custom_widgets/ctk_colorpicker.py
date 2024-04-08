# CTk Color Picker widget for customtkinter
# Author: Akash Bora (Akascape)

import tkinter
import customtkinter
from PIL import Image, ImageTk
import sys
import os
import math

PATH = os.path.dirname(os.path.realpath(__file__))

class CTkColorPicker(customtkinter.CTkFrame):
    
    def __init__(self,
                 master: any = None,
                 size: int = 250,
                 initial_color: str = None,
                 fg_color: str = None,
                 corner_radius: int = 24,
                 command = None,
                 **kwargs):
    
        super().__init__(master=master, corner_radius=corner_radius, **kwargs)
        
        self.WIDTH = size if size>101 else 200
        
        self.image_dimension = int(self._apply_widget_scaling(self.WIDTH - 100))
        self.target_dimension = int(self._apply_widget_scaling(20))
        self.lift()

        self.after(10)       
        self.default_hex_color = "#ffffff"  
        self.default_rgb = [255, 255, 255]
        self.rgb_color = self.default_rgb[:]
        
        self.fg_color = self._fg_color if fg_color is None else fg_color
        self.corner_radius = corner_radius
        
        self.command = command
        
        super().configure(fg_color=self.fg_color)
          
        self.canvas = tkinter.Canvas(self, height=self.image_dimension, width=self.image_dimension, highlightthickness=0, bg=self._apply_appearance_mode(self.fg_color))
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag, add="+")

        self.img1 = Image.open(os.path.join(PATH, 'color_wheel.png')).resize((self.image_dimension, self.image_dimension), Image.Resampling.LANCZOS)
        self.img2 = Image.open(os.path.join(PATH, 'target.png')).resize((self.target_dimension, self.target_dimension), Image.Resampling.LANCZOS)

        self.wheel = ImageTk.PhotoImage(self.img1)
        self.target = ImageTk.PhotoImage(self.img2)
        
        self.canvas.create_image(self.image_dimension/2, self.image_dimension/2, image=self.wheel)
        self.set_initial_color(initial_color)
        
        self.canvas.pack(pady=15, padx=15)
        
    def get(self):
        self._color = self.default_hex_color
        return self._color
    
    def destroy(self):
        super().destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target
        
    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self.WIDTH = int(self._apply_widget_scaling(self.WIDTH))
        self.configure(size=self.WIDTH)

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        self.canvas.config(background=self._apply_appearance_mode(self.cget("fg_color")))
        
    def on_mouse_drag(self, event):
        x = event.x
        y = event.y
        self.canvas.delete("all")
        self.canvas.create_image(self.image_dimension/2, self.image_dimension/2, image=self.wheel)
        
        d_from_center = math.sqrt(((self.image_dimension/2)-x)**2 + ((self.image_dimension/2)-y)**2)
        
        if d_from_center < self.image_dimension/2:
            self.target_x, self.target_y = x, y
        else:
            self.target_x, self.target_y = self.projection_on_circle(x, y, self.image_dimension/2, self.image_dimension/2, self.image_dimension/2 -1)

        self.canvas.create_image(self.target_x, self.target_y, image=self.target)
        
        self.get_target_color()
  
    def get_target_color(self):
        try:
            self.rgb_color = self.img1.getpixel((self.target_x, self.target_y))
            
            r = self.rgb_color[0]
            g = self.rgb_color[1]
            b = self.rgb_color[2]    
            self.rgb_color = [r, g, b]
            
        except AttributeError:
            self.rgb_color = self.default_rgb

        self.default_hex_color = "#{:02x}{:02x}{:02x}".format(*self.rgb_color)
        if self.command:
            self.command(self.default_hex_color)
            
    def projection_on_circle(self, point_x, point_y, circle_x, circle_y, radius):
        angle = math.atan2(point_y - circle_y, point_x - circle_x)
        projection_x = circle_x + radius * math.cos(angle)
        projection_y = circle_y + radius * math.sin(angle)

        return projection_x, projection_y
    
    def set_initial_color(self, initial_color):
        # set_initial_color is in beta stage, cannot seek all colors accurately
        
        if initial_color and initial_color.startswith("#"):
            try:
                r,g,b = tuple(int(initial_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                return
            
            self.default_hex_color = initial_color
            
            if not self.set_target_to_matching_color(r, g, b):
                self.set_target_to_center()
        else:
            self.set_target_to_center()

    def set_target_to_matching_color(self, r, g, b):
        for i in range(0, self.image_dimension):
            for j in range(0, self.image_dimension):
                self.rgb_color = self.img1.getpixel((i, j))
                if (self.rgb_color[0], self.rgb_color[1], self.rgb_color[2]) == (r, g, b):
                    self.canvas.create_image(i, j, image=self.target)
                    self.target_x = i
                    self.target_y = j
                    return True
        return False

    def set_target_to_center(self):
        self.canvas.create_image(self.image_dimension / 2, self.image_dimension / 2, image=self.target)

    def configure(self, **kwargs):
        if "size" in kwargs:
            self.WIDTH = kwargs.pop("size")
            if self.WIDTH<101:
                self.WIDTH = 102
            self.image_dimension = int(self._apply_widget_scaling(self.WIDTH - 100))
            self.img1 = Image.open(os.path.join(PATH, 'color_wheel.png')).resize((self.image_dimension, self.image_dimension), Image.Resampling.LANCZOS)
            self.wheel = ImageTk.PhotoImage(self.img1)
            self.canvas.delete("all")
            self.canvas.config(height=self.image_dimension, width=self.image_dimension)
            
            self.canvas.create_image(self.image_dimension/2, self.image_dimension/2, image=self.wheel)
            
        if "fg_color" in kwargs:
            if kwargs["fg_color"]=="transparent":
                kwargs["fg_color"] = self.cget("bg_color")
            self.canvas.config(background=self._apply_appearance_mode(kwargs["fg_color"]))
            
        if "state" in kwargs:
            if kwargs.pop("state")=="disabled":
                self.canvas.unbind("<B1-Motion>")
            else:
                self.canvas.bind("<B1-Motion>", self.on_mouse_drag, add="+")
            
        super().configure(**kwargs)
        
    def bind(self, sequence=None, command=None, add="+"):
        super().bind(sequence, command, add)
        self.canvas.bind(sequence, command, add)
        
    def unbind(self, sequence=None):
        super().unbind(sequence)
        self.canvas.unbind(sequence)

    def cget(self, param):
        if param=="size":
            return self.WIDTH
        if param=="state":
            return self.canvas.cget("state")
        else:
            return super().cget(param)
