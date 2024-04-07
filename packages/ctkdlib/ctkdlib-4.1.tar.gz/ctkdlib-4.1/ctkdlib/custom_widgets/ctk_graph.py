import customtkinter as ctk
import tkinter as tk

class CTkGraph(ctk.CTkFrame):
    """
    Widget to display list of integers as a graph. You can customize almost everything, except for the corner radius
    of the canvas that draws the graph.

    You can also set a custom title, if you don't do is the Labeled won't be rendered.

    Graph axis vars are responsible for the arrows of the graph, graph line is responsible for the outline of the
    graph polygon (the graph is represented with a polygon)
    """
    def __init__(self, master,
                 values: list = [],
                 fg_color=None,
                 width=200,
                 height=200,
                 graph_color=None,
                 axis_width=3,
                 line_width=2,
                 axis_color=None,
                 line_color=None,
                 **kwargs):

        super().__init__(master=master, width=width, height=height, **kwargs)

        # data
        self.data_values = values

        self.graph_fg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        self.graph_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if graph_color is None else graph_color
        self.main_canvas = None
        
        if self.graph_fg_color=="transparent":
            self.graph_fg_color = self.cget("bg_color")
            
        # graph data
        self.width = width
        self.height = height
        self.graph_axis_width = axis_width
        self.graph_line_width = line_width
        
        self.graph_axis_color = ctk.ThemeManager.theme["CTkSlider"]["progress_color"] if axis_color is None else axis_color
        self.graph_line_color = ctk.ThemeManager.theme["CTkSlider"]["progress_color"] if line_color is None else line_color

        # setting up
        self.setup_stat()
    
    def setup_stat(self):

        self.main_canvas = ctk.CTkCanvas(self, bd=0, highlightthickness=0,
                                         relief="flat", width=self.width, height=self.height)

        self.main_canvas.bind("<Configure>", lambda event: self.draw_stats(event.width, event.height))
        
        self.draw_stats(self.width, self.height)

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self.height = self._apply_widget_scaling(self.height)
        self.width = self._apply_widget_scaling(self.width)
        self.draw_stats(self.width, self.height)

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        self.draw_stats(self.width, self.height)
        
    def draw_stats(self, width, height):
        # drawing graph lines
        self.main_canvas.delete("all")
        
        # axis for the graph
        self.main_canvas.create_line(width * 0.05, height * 0.95, width * 0.05, height * 0.05, fill=self._apply_appearance_mode(self.graph_axis_color),
                                     width=self.graph_axis_width, arrow="last")
        self.main_canvas.create_line(width * 0.05, height * 0.95, width * 0.95, height * 0.95, fill=self._apply_appearance_mode(self.graph_axis_color),
                                     width=self.graph_axis_width, arrow="last")

        values = []
        for i in self.data_values:
            if isinstance(i, str):
                i = i.replace(" ","")
                if i.isdigit():
                    values.append(int(i))
            else:
                values.append(i)
                
        self.data_values = values
        
        if len(self.data_values)==0:
           self.data_values = [0]
           
        data_len = len(self.data_values)
        max_value = max(self.data_values)
        if max_value==0:
            max_value = 1
        gap = (width - 15) // data_len
        coordinates = [(width * 0.05, height * 0.945)]
        
        for i in range(data_len):
            h = height * 0.8 * self.data_values[i] / max_value
            coordinates.append((width * 0.05 + gap * i, height * 0.945 - h))

        else:
            coordinates.append((width * 0.05 + gap * data_len - gap, height * 0.945))

        self.main_canvas.create_polygon(coordinates, width=self.graph_line_width, fill=self._apply_appearance_mode(self.graph_color),
                                        outline=self._apply_appearance_mode(self.graph_line_color))
        
        self.main_canvas.pack(expand=True, fill="both", padx=self._corner_radius//2 +self._border_width,
                              pady=self._corner_radius//2 +self._border_width)
        self.main_canvas.config(width=self.width, height=self.height, background=self._apply_appearance_mode(self.graph_fg_color))

    def cget(self, param):
        if param=="line_color":
            return self.graph_line_color
        if param=="axis_color":
            return self.graph_axis_color
        if param=="axis_width":
            return self.graph_axis_width
        if param=="line_width":
            return self.graph_line_width
        if param=="graph_color":
            return self.graph_color
        if param=="values":
            return self.data_values

        return super().cget(param)
        
    def configure(self, **kwargs):
        if "line_color" in kwargs:
            self.graph_line_color = kwargs.pop("line_color")
        if "axis_color" in kwargs:
            self.graph_axis_color = kwargs.pop("axis_color")
        if "axis_width" in kwargs:
            self.graph_axis_width = kwargs.pop("axis_width")
        if "line_width" in kwargs:
            self.graph_line_width = kwargs.pop("line_width")
            
        if "graph_color" in kwargs:
            self.graph_color = kwargs.pop("graph_color")
            
        if "fg_color" in kwargs:
            self.graph_fg_color = kwargs.pop("fg_color")
            super().configure(fg_color=self.graph_fg_color)

            if self.graph_fg_color=="transparent":
                self.graph_fg_color = self.cget("bg_color")
            
        if "values" in kwargs:
            self.data_values = kwargs.pop("values")
            
        if "width" in kwargs:
            self.width = kwargs["width"]
            
        if "height" in kwargs:
            self.height = kwargs["height"]
            
        super().configure(**kwargs)
        self.draw_stats(self.width, self.height)

    def bind(self, sequence=None, command=None, add="+"):
        super().bind(sequence, command, add)
        self.main_canvas.bind(sequence, command, add)
        
    def unbind(self, sequence=None):
        super().unbind(sequence)
        self.main_canvas.unbind(sequence)
