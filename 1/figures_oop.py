import math
from abc import ABC, abstractmethod

class Shape(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        pass

    @property
    @abstractmethod
    def perimeter(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    @property
    def area(self) -> float:
        return math.pi * (self.radius ** 2)

    @property
    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)

class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c

    @property
    def perimeter(self) -> float:
        return self.a + self.b + self.c

    @property
    def area(self) -> float:
        p = self.perimeter / 2
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))