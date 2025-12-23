import tkinter as tk

class GraphicObject:
    def __init__(self, shade="black"):
        self.shade = shade

    def paint(self, cv):
        pass

class Dot(GraphicObject):
    def __init__(self, pos, shade="black"):
        super().__init__(shade)
        self.x, self.y = pos

    def paint(self, cv):
        r = 2
        cv.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, 
                       fill=self.shade, outline=self.shade)

class Segment(GraphicObject):
    def __init__(self, start, end, shade="black"):
        super().__init__(shade)
        self.start = start
        self.end = end

    def paint(self, cv):
        cv.create_line(*self.start, *self.end, fill=self.shade, width=2)

class Quad(GraphicObject):
    def __init__(self, coords, shade="blue"):
        super().__init__(shade)
        self.coords = coords

    def paint(self, cv):
        flat_coords = [val for pt in self.coords for val in pt]
        cv.create_polygon(flat_coords, outline=self.shade, fill='', width=2)

class Trigon(GraphicObject):
    def __init__(self, a, b, c, shade="red"):
        super().__init__(shade)
        self.pts = [a, b, c]

    def paint(self, cv):
        flat = [v for p in self.pts for v in p]
        cv.create_polygon(flat, outline=self.shade, fill='', width=2)

class Ring(GraphicObject):
    def __init__(self, center, r, shade="green"):
        super().__init__(shade)
        self.cx, self.cy = center
        self.r = r

    def paint(self, cv):
        cv.create_oval(self.cx - self.r, self.cy - self.r,
                       self.cx + self.r, self.cy + self.r,
                       outline=self.shade, width=2)

def main():
    root = tk.Tk()
    root.title("Geometry Demo")
    
    cv = tk.Canvas(root, width=600, height=400, bg="white")
    cv.pack(padx=15, pady=15)

    scene = [
        Dot((50, 50)),
        Segment((100, 50), (250, 100)),
        Quad([(300, 50), (400, 20), (450, 80), (320, 120)], shade="purple"),
        Trigon((50, 150), (150, 150), (100, 250)),
        Ring((350, 250), 70, shade="orange")
    ]

    for item in scene:
        item.paint(cv)

    root.mainloop()

if __name__ == "__main__":
    main()