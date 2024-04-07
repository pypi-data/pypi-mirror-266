import customtkinter as ctk
import tkinter as tk

class CTkChart(ctk.CTkFrame):
    """
    This is widget to create a chart representation of a dict[str, int]. It takes str of the dict as a key and a title
    for certain bar and int or float for that matter as the value and draws it on the canvas. There are also
    indicators like average and max value.

    You can also set title, if you do not define it, it wont be rendered.

    There are two values with tuple[bool, bool] format:
    * bar_info_show: first bool is responsible for drawing the value in the bar, second for drawing title
    * show_indicators: first bool is responsible for max value, second for average.
    """
    
    def __init__(self, master,
                 data=None,
                 width=250,
                 height=200,
                 fg_color=None,
                 axis_width=4,
                 axis_color=None,
                 bar_color=None,
                 font=None,
                 bar_text_color=None,
                 bar_width=20,
                 text_color=None,
                 **kwargs):
        
        super().__init__(master=master, width=width, height=height, **kwargs)

        # data
        self.height = height
        self.width = width
        self.data = {} if data is None else data
        self.data_max = self.format_data()

        self.chart_fg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        # data about chart axis
        self.chart_axis_width = axis_width
        self.chart_axis_color = ctk.ThemeManager.theme["CTkSlider"]["progress_color"] if axis_color is None else axis_color

        # data about bars
        self.bar_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if bar_color is None else bar_color
        self.bar_width = bar_width
        self.bar_text_color = ctk.ThemeManager.theme["CTkButton"]["text_color"] if bar_text_color is None else bar_text_color
        self.text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        
        if not font:
            self.font = ctk.CTkFont(ctk.ThemeManager.theme["CTkFont"]["family"],ctk.ThemeManager.theme["CTkFont"]["size"])
        else:
            if isinstance(font, ctk.CTkFont):
                self.font = font
            else:
                self.font = ctk.CTkFont(*font)
                
        self.main_canvas = ctk.CTkCanvas(self,
                                         background=self._apply_appearance_mode(self.chart_fg_color), bd=0, highlightthickness=0, relief="flat",
                                         width=width, height=height)
        self.main_canvas.pack(expand=True, fill="both", padx=self._corner_radius//1.5, pady=self._corner_radius//1.5)
        self.main_canvas.bind("<Configure>", lambda event: self.draw_bars())

    def format_data(self):
        m = 0.01
        s, count = 0, 0.01

        for value in self.data.values():
            s += value
            count += 1
            m = max(m, value)

        return m

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)
        self.draw_bars()

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        self.draw_bars()
        
    def draw_bars(self):
        # updating canvas and canvas info
        self.main_canvas.delete("all")
        canvas_height = self._apply_widget_scaling(self.main_canvas.winfo_height())
        canvas_width = self._apply_widget_scaling(self.main_canvas.winfo_width())

        # drawing graph axis
        self.main_canvas.create_line(0+self.chart_axis_width, canvas_height -30,
                                     canvas_width, canvas_height-30,
                                     capstyle="round", width=self.chart_axis_width, fill=self._apply_appearance_mode(self.chart_axis_color))
        self.main_canvas.create_line(0 + self.chart_axis_width, canvas_height-30,
                                     0 + self.chart_axis_width, 0,
                                     capstyle="round", width=self.chart_axis_width, fill=self._apply_appearance_mode(self.chart_axis_color))

        for index, key in enumerate(self.data.keys()):
            self.draw_bar_day(canvas_width*0.01, canvas_height * 0.1, canvas_width * 0.9, canvas_height -45,
                               index, key)

        self.main_canvas.pack(expand=True, fill="both", padx=self._corner_radius//2 +self._border_width,
                              pady=self._corner_radius//2 +self._border_width)
        self.main_canvas.config(width=self.width, height=self.height, background=self._apply_appearance_mode(self.chart_fg_color))
        
    def draw_bar_day(self, graph_x_offset, graph_y_offset, graph_width, graph_height, index, key):
        day_width = graph_width//len(self.data.keys())
        day_offset = day_width*0.6

        value = self.data[key]
        day_bar_height = value / self.data_max * graph_height
        canvas_height = self._apply_widget_scaling(self.main_canvas.winfo_height())
        if (graph_y_offset + graph_height - day_bar_height)> graph_height:
            graph_y_offset = 0
        self.main_canvas.create_line(graph_x_offset + day_width * index + day_offset,
                                     graph_height,
                                     graph_x_offset + day_width * index + day_offset,
                                     graph_y_offset + graph_height - day_bar_height,
                                     capstyle="round", fill=self._apply_appearance_mode(self.bar_color),
                                     width=self.bar_width)

        self.main_canvas.create_text(graph_x_offset + day_width * index + day_offset,
                                     graph_height,
                                     text=value, fill=self._apply_appearance_mode(self.bar_text_color),
                                     font=self.font)

        self.main_canvas.create_text(graph_x_offset + day_width * index + day_offset,
                                     canvas_height - 15,
                                     text=key, fill=self._apply_appearance_mode(self.text_color),
                                     font=self.font)

    def cget(self, param):
        
        if param=="axis_color":
            return self.chart_axis_color
        if param=="axis_width":
            return self.chart_axis_width
        if param=="bar_color":
            return self.bar_color
        if param=="data":
            return self.data
        if param=="text_color":
            return self.text_color
        if param=="bar_text_color":
            return self.bar_text_color
        if param=="bar_width":
            return self.bar_width
        if param=="font":
            return self.font
        
        return super().cget(param)
        
    def configure(self, **kwargs):

        if "axis_color" in kwargs:
            self.chart_axis_color = kwargs.pop("axis_color")
        if "axis_width" in kwargs:
            self.chart_axis_width = kwargs.pop("axis_width")
            
        if "fg_color" in kwargs:
            self.chart_fg_color = kwargs.pop("fg_color")
            super().configure(fg_color=self.chart_fg_color)

            if self.chart_fg_color=="transparent":
                self.chart_fg_color = self.cget("bg_color")
        if "bar_color" in kwargs:
            self.bar_color = kwargs.pop("bar_color")
            
        if "bar_width" in kwargs:
            self.bar_width = kwargs.pop("bar_width")
            
        if "data" in kwargs:
            self.data = kwargs.pop("data")
            self.data_max = self.format_data()
            
        if "width" in kwargs:
            self.width = kwargs["width"]
            
        if "height" in kwargs:
            self.height = kwargs["height"]

        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")

        if "bar_text_color" in kwargs:
            self.bar_text_color = kwargs.pop("bar_text_color")
            
        super().configure(**kwargs)
        self.draw_bars()

    def bind(self, sequence=None, command=None, add="+"):
        super().bind(sequence, command, add)
        self.main_canvas.bind(sequence, command, add)
        
    def unbind(self, sequence=None):
        super().unbind(sequence)
        self.main_canvas.unbind(sequence)
