import pygame
import math
from queue import PriorityQueue


WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Warehouse Pathfinder")


RED = (255, 0, 0)
BLUE = (0, 255, 0)
GREEN = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color =  WHITE
        self.neighbour = []
        self.width = width
        self.total_rows = total_rows


    def get_pos(self):
        return self.row, self.col