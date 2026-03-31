# Prompt 90

import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import Toplevel
from PIL import Image, ImageDraw
import svgwrite

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing App")
        
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.setup_menu()
        self.setup_toolbar()
        
        self.shapes = []
        self.current_shape = None
        self.current_color = "black"
        self.current_tool = "select"
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_drawing)
        filemenu.add_command(label="Open", command=self.open_drawing)
        filemenu.add_command(label="Save", command=self.save_drawing)
        filemenu.add_command(label="Export as SVG", command=self.export_svg)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.redo)
        menubar.add_cascade(label="Edit", menu=editmenu)
        
        self.root.config(menu=menubar)
    
    def setup_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.select_button = tk.Button(toolbar, text="Select", command=lambda: self.set_tool("select"))
        self.select_button.pack(side=tk.LEFT)
        
        self.rectangle_button = tk.Button(toolbar, text="Rectangle", command=lambda: self.set_tool("rectangle"))
        self.rectangle_button.pack(side=tk.LEFT)
        
        self.ellipse_button = tk.Button(toolbar, text="Ellipse", command=lambda: self.set_tool("ellipse"))
        self.ellipse_button.pack(side=tk.LEFT)
        
        self.color_button = tk.Button(toolbar, text="Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT)
        
        self.rotate_button = tk.Button(toolbar, text="Rotate", command=self.rotate_shape)
        self.rotate_button.pack(side=tk.LEFT)
        
        self.scale_button = tk.Button(toolbar, text="Scale", command=self.scale_shape)
        self.scale_button.pack(side=tk.LEFT)
        
        self.translate_button = tk.Button(toolbar, text="Translate", command=self.translate_shape)
        self.translate_button.pack(side=tk.LEFT)
    
    def set_tool(self, tool):
        self.current_tool = tool
    
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color
    
    def on_button_press(self, event):
        if self.current_tool == "select":
            self.select_shape(event.x, event.y)
        elif self.current_tool == "rectangle":
            self.current_shape = {"type": "rectangle", "start": (event.x, event.y), "end": (event.x, event.y)}
        elif self.current_tool == "ellipse":
            self.current_shape = {"type": "ellipse", "start": (event.x, event.y), "end": (event.x, event.y)}
    
    def on_move_press(self, event):
        if self.current_shape:
            self.current_shape["end"] = (event.x, event.y)
            self.redraw()
    
    def on_button_release(self, event):
        if self.current_shape:
            self.shapes.append(self.current_shape)
            self.current_shape = None
            self.redraw()
    
    def redraw(self):
        self.canvas.delete(tk.ALL)
        for shape in self.shapes:
            if shape["type"] == "rectangle":
                self.canvas.create_rectangle(shape["start"][0], shape["start"][1], shape["end"][0], shape["end"][1], outline=self.current_color)
            elif shape["type"] == "ellipse":
                self.canvas.create_oval(shape["start"][0], shape["start"][1], shape["end"][0], shape["end"][1], outline=self.current_color)
    
    def select_shape(self, x, y):
        for shape in self.shapes:
            if shape["type"] == "rectangle":
                if shape["start"][0] <= x <= shape["end"][0] and shape["start"][1] <= y <= shape["end"][1]:
                    self.current_shape = shape
                    break
            elif shape["type"] == "ellipse":
                if shape["start"][0] <= x <= shape["end"][0] and shape["start"][1] <= y <= shape["end"][1]:
                    self.current_shape = shape
                    break
    
    def rotate_shape(self):
        if self.current_shape:
            angle = simpledialog.askfloat("Rotate", "Enter rotation angle:")
            if angle:
                self.current_shape["angle"] = angle
                self.redraw()
    
    def scale_shape(self):
        if self.current_shape:
            scale = simpledialog.askfloat("Scale", "Enter scale factor:")
            if scale:
                self.current_shape["scale"] = scale
                self.redraw()
    
    def translate_shape(self):
        if self.current_shape:
            dx = simpledialog.askfloat("Translate", "Enter horizontal translation:")
            dy = simpledialog.askfloat("Translate", "Enter vertical translation:")
            if dx and dy:
                self.current_shape["dx"] = dx
                self.current_shape["dy"] = dy
                self.redraw()
    
    def new_drawing(self):
        self.shapes = []
        self.redraw()
    
    def open_drawing(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.shapes = load_drawing(file_path)
            self.redraw()
    
    def save_drawing(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".draw")
        if file_path:
            save_drawing(self.shapes, file_path)
    
    def export_svg(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".svg")
        if file_path:
            export_to_svg(self.shapes, file_path)
    
    def undo(self):
        if self.shapes:
            self.shapes.pop()
            self.redraw()
    
    def redo(self):
        pass

def load_drawing(file_path):
    # Implement loading drawing from file
    pass

def save_drawing(shapes, file_path):
    # Implement saving drawing to file
    pass

def export_to_svg(shapes, file_path):
    dwg = svgwrite.Drawing(file_path, profile='tiny')
    for shape in shapes:
        if shape["type"] == "rectangle":
            dwg.add(dwg.rect(insert=shape["start"], size=(shape["end"][0] - shape["start"][0], shape["end"][1] - shape["start"][1]), stroke=shape.get("color", "black"), fill="none"))
        elif shape["type"] == "ellipse":
            dwg.add(dwg.circle(center=(shape["start"][0] + (shape["end"][0] - shape["start"][0]) / 2, shape["start"][1] + (shape["end"][1] - shape["start"][1]) / 2), r=(shape["end"][0] - shape["start"][0]) / 2, stroke=shape.get("color", "black"), fill="none"))
    dwg.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()