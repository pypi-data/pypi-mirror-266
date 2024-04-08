import customtkinter
import tkinter as tk
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

class CTkDraw(customtkinter.CTkLabel):
    def __init__(self,
                 master: any,
                 path=None,
                 width=200,
                 height=200,
                 fg_color="grey",
                 corner_radius=0,
                 brightness=10,
                 contrast=10,
                 saturation=10,
                 blur=0,
                 sharpness=10,
                 draw=False,
                 text_color="black",
                 pen_size=5,
                 **kwargs):

        super().__init__(master, text="", width=width, height=height, **kwargs)

        self.image_path = path
        if self.image_path:
            self.image = Image.open(self.image_path).resize((self.winfo_reqwidth(),self.winfo_reqheight())).convert('RGB')
        else:
            self.image = Image.new(mode="RGB", size=(self.winfo_reqwidth(),
                                                     self.winfo_reqheight()),
                                   color=fg_color)
        self.fg = fg_color
        self.draw = ImageDraw.Draw(self.image)
        self.text_color = text_color
        self.br = brightness
        self.con = contrast
        self.sat = saturation
        self.shrp = sharpness
        self.blr = blur
        self.size = pen_size
        self.dr = draw
        self.corner = corner_radius
         
        self.ctk_image = customtkinter.CTkImage(self.image, size=(self.winfo_reqwidth(),self.winfo_reqheight()))

        self.bind('<B1-Motion>', self.paint, add="+")
        
        self.old_x = None
        self.old_y = None
        self.update()
        
        super().configure(image=self.ctk_image)
    
    def round_corners(self, img, radius):
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
    
        draw.ellipse((0, 0, radius * 2 , radius * 2 ), fill=255)
        alpha = Image.new('L', (200,200), 255)
        w, h = (200,200)
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        alpha = alpha.resize(img.size, resample=3).filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.SMOOTH_MORE)
        img.putalpha(alpha)
        
        return img
    
    def brightness(self, img, value):
        value = value/10
        return ImageEnhance.Brightness(img).enhance(value)
        
    def contrast(self, img, value):
        value = value/10
        return ImageEnhance.Contrast(img).enhance(value)
        
    def sharpness(self, img, value):
        value = value/10
        return ImageEnhance.Sharpness(img).enhance(value)
        
    def saturation(self, img, value):
        value = value/10
        return ImageEnhance.Color(img).enhance(value)
        
    def blur(self, img, value):
        return img.filter(ImageFilter.GaussianBlur(value))
        
    def update(self):
  
        image = self.image

        # Post Processing
        
        image = self.saturation(image, self.sat)
        image = self.sharpness(image, self.shrp)
        image = self.brightness(image, self.br)
        image = self.contrast(image, self.con)
        image = self.blur(image, self.blr)
        
        image = self.round_corners(image, self.corner)
   
        self.ctk_image.configure(dark_image=image, light_image=image,
                                 size=(self.winfo_reqwidth(),self.winfo_reqheight()))

        image = None
        
    def paint(self, event):
        if not self.dr: return
        if self.old_x and self.old_y:
            self.draw.line((self.old_x, self.old_y, event.x, event.y), self.text_color, self.size)
        self.update()                         
   
        self.old_x = event.x
        self.old_y = event.y
        
    def reload(self):
        del self.image
        if self.image_path:
            self.image = Image.open(self.image_path).resize((self.winfo_reqwidth(),self.winfo_reqheight())).convert('RGB')
        else:
            self.image = Image.new(mode="RGB", size=(self.winfo_reqwidth(),
                                                     self.winfo_reqheight()),
                                   color=self.fg)
    def clear(self):
        del self.draw
        self.draw = ImageDraw.Draw(self.image)
        self.update()
        
    def paste(self, path, width, height, x=0, y=0):
        new_image = Image.open(path).resize((width, height), resample=0)
        self.image.paste(new_image, (x,y))
        self.update()
        
    def save(self, file_path, **kwargs):
        self.ctk_image._light_image.save(file_path, **kwargs)
        
    def configure(self, **kwargs):
        require_redraw = False
        if "brightness" in kwargs:
            self.br = kwargs.pop("brightness")
        if "contrast" in kwargs:
            self.con = kwargs.pop("contrast")
        if "sharpness" in kwargs:
            self.shrp = kwargs.pop("sharpness")
        if "saturation" in kwargs:
            self.sat = kwargs.pop("saturation")
        if "blur" in kwargs:
            self.blr = kwargs.pop("blur")
        if "pen_size" in kwargs:
            self.size = kwargs.pop("pen_size")
        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")
        if "draw" in kwargs:
            self.dr = kwargs.pop("draw")
            require_redraw = True
            self.clear()
        if "path" in kwargs:
            self.image_path = kwargs.pop("path")
            require_redraw = True
            self.after(100, self.clear)
        if "corner_radius" in kwargs:
            self.corner = kwargs.pop("corner_radius")
            require_redraw = True
        if "fg_color" in kwargs:
            self.fg = kwargs.pop("fg_color")
            require_redraw = True
            self.after(100, self.clear)
        if "height" in kwargs:
            require_redraw = True
        if "width" in kwargs:
            require_redraw = True
        
        super().configure(**kwargs)
        if require_redraw:
            self.reload()
        self.update()
        
        
    def cget(self, param):
        if param=="brightness":
            return self.br
        if param=="contrast":
            return self.con
        if param=="sharpness":
            return self.shrp
        if param=="saturation":
            return self.sat
        if param=="blur":
            return self.blr
        if param=="pen_size":
            return self.size
        if param=="text_color":
            return self.text_color
        if param=="draw":
            return self.dr
        if param=="path":
            return self.image_path
        if param=="corner_radius":
            return self.corner
        if param=="fg_color":
            return self.fg
        if param=="text":
            raise ValueError("Invalid Parameter")
        if param=="font":
            raise ValueError("Invalid Parameter")
        if param=="image":
            raise ValueError("Invalid Parameter, use path parameter")
        if param=="text_color_disabled":
            raise ValueError("Invalid Parameter")
        if param=="justify":
            raise ValueError("Invalid Parameter")
        if param=="padx":
            raise ValueError("Invalid Parameter")
        if param=="pady":
            raise ValueError("Invalid Parameter")
        return super().cget(param)
    
