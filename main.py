import pygame
import math
from queue import PriorityQueue
from collections import deque


WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Warehouse Pathfinder")


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.is_obj = False


    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE
    
    def is_path(self):
        return self.color == PURPLE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def make_obj(self):
        self.is_obj = True
        self.color = BLUE;

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        if self.is_obj:
            pygame.draw.circle(win, BLUE, (self.x + self.width // 2, self.y + self.width // 2), self.width // 2)

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # left
            self.neighbors.append(grid[self.row][self.col - 1])
    def __lt__(self, other):
        return False
    

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw):
    total_cost = 0
    moving_on_x = None
    if abs(came_from[current].get_pos()[0] - current.get_pos()[0]) != 0:
        moving_on_x = False
    elif abs(came_from[current].get_pos()[1] - current.get_pos()[1]) != 0:
        moving_on_x = True

    while current in came_from:
        total_cost += 2 #account for the step
        if abs(came_from[current].get_pos()[0] - current.get_pos()[0]) != 0: #x coordinate change
            if not moving_on_x:# robot wasn't moving on x
                total_cost += 1 #account for the rotation
                moving_on_x = True #rotate the robot
        elif abs(came_from[current].get_pos()[1] - current.get_pos()[1]) != 0: #y coordinate change
            if  moving_on_x:# robot wasn't moving on y
                total_cost += 1 #account for the rotation
                moving_on_x = False #rotate the robot
        
        current = came_from[current]
        if not current.is_start() or current.is_path():
            current.make_path()
        draw()
    
    print("total_cost: ", total_cost)




def sort_targets(current, targets):
    def custom_sort(obj):
        if obj.is_end():
            return (float('inf'), h(current.get_pos(), obj.get_pos()))
        else:
            return (0, h(current.get_pos(), obj.get_pos()))

    return sorted(targets, key=custom_sort)

def a_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    obj_spots = [spot for row in grid for spot in row if spot.is_obj]

    path_targets = sort_targets(start, obj_spots + [end])

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == path_targets[0]:
            #path_targets[0].make_closed()
            reconstruct_path(came_from, current, draw)
            for row in grid:
                    for spot in row:
                        if not spot.is_obj and not spot.is_end() and not spot.is_start() and not spot.is_path():
                            if spot.is_closed() or spot.is_open():
                                spot.reset()
                                g_score[spot] = float("inf")
            path_targets = sort_targets(current, path_targets[1:])
            if path_targets:
                f_score[current] = h(current.get_pos(), path_targets[0].get_pos())
                open_set = PriorityQueue()
                open_set.put((0, count, current))
                open_set_hash = {current}
                

            else:
                return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), path_targets[0].get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not neighbor.is_end():
                        neighbor.make_open()

        draw()
        if current != start and current != path_targets[0]:
            current.make_closed()

    return False

def dijkstra_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    open_set_hash = {start}

    obj_spots = [spot for row in grid for spot in row if spot.is_obj]

    path_targets = sort_targets(start, obj_spots + [end])

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == path_targets[0]:
            reconstruct_path(came_from, current, draw)
            for row in grid:
                    for spot in row:
                        if not spot.is_obj and not spot.is_end() and not spot.is_start() and not spot.is_path():
                            if spot.is_closed() or spot.is_open():
                                spot.reset()
                                g_score[spot] = float("inf")
            path_targets = sort_targets(current, path_targets[1:])
            g_score[current] = 0
            if path_targets:
                open_set = PriorityQueue()
                open_set.put((0, count, current))
                open_set_hash = {current}
            else:
                return True

        for neighbor in current.neighbors:
            if not neighbor.is_path():    
                temp_g_score = g_score[current] + 1
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((g_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        if not neighbor.is_end():
                            neighbor.make_open()

        draw()
        if current != start and current != path_targets[0]:
            current.make_closed()

    return False


def bfs_algorithm(draw, grid, start, end):
    queue = deque([start])
    came_from = {}
    visited = set([start])

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.popleft()

        if current == end:
            reconstruct_path(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited and not neighbor.is_obj:
                queue.append(neighbor)
                visited.add(neighbor)
                came_from[neighbor] = current
                neighbor.make_open()

        # Check if the current node is an object node
        if current.is_obj:
            reconstruct_path(came_from, current, draw)
            current.make_closed()

        draw()
        if current != start and not current.is_obj:
            current.make_closed()

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def distance_to_obj_heuristic(robot_position, obj_position):
    return abs(robot_position[0] - obj_position[0]) + abs(robot_position[1] - obj_position[1])


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None


    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
            # In the main loop
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    a_star_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                if event.key == pygame.K_o and start and end:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if not spot.is_start() and not spot.is_end():
                        spot.make_obj()

                if event.key == pygame.K_d and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    dijkstra_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_b and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    bfs_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)


    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)
