from tkinter import Tk, BOTH, Canvas
import time
import random

WINDOW_HEIGHT = 800
WINDOW_WIDHT = 800
NUM_COLUMNS = 15
NUM_ROWS = 15
CELL_SIZE = 40
SEARCHPATTERN = {
    "N":(-1, 0),
    "S":(1, 0),
    "W":(0, -1),
    "O":(0, 1)
}

def main():
    win = Window(WINDOW_HEIGHT, WINDOW_WIDHT)
    m1 = Maze(Point(10,10), NUM_ROWS, NUM_COLUMNS, CELL_SIZE, CELL_SIZE)
    m1.run(win)
    win.wait_for_close()

class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Line:
    def __init__(self, point1: Point, point2: Point) -> None:
        self.point1 = point1
        self.point2 = point2

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(self.point1.x, self.point1.y, self.point2.x, self.point2.y, fill=fill_color, width=2)
        canvas.pack()

class Window:
    def __init__(self, width, height) -> None:
        self.win = Tk()
        self.win.geometry(str(width) + "x" + str(height))
        self.win.title("MainWindow")
        self.canvas = Canvas(self.win, width=width, height=height)
        self.canvas.pack()
        self.run = False
        self.win.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self) -> None:
        if self.run:
            self.win.update_idletasks()
            self.win.update()   

    def draw_line(self, line: Line, fill_color: str):
        line.draw(self.canvas, fill_color)

    def wait_for_close(self) -> bool:
        self.run = True
        while self.run:
            self.redraw()

    def close(self) -> None:
        self.run = False

class Cell:
    def __init__(self, point1: Point, point2: Point, maze_x:int, maze_y:int) -> None:
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.point1 = point1
        self.point2 = point2
        self.visited = False
        self.maze_x = maze_x
        self.maze_y = maze_y

    def get_center_point(self) -> Point:
        point = Point(self.point1.x + abs(self.point1.x - self.point2.x)/2,self.point1.y + abs(self.point1.y - self.point2.y) /2)
        return point

    def draw(self, window: Window, color: str) -> None:
        if self.has_top_wall:
            window.draw_line(Line(self.point1, Point(self.point2.x, self.point1.y)), color)
        if self.has_right_wall:
            window.draw_line(Line(Point(self.point2.x, self.point1.y), self.point2), color)
        if self.has_bottom_wall:
            window.draw_line(Line(self.point2, Point(self.point1.x, self.point2.y)), color)
        if self.has_left_wall:
            window.draw_line(Line(Point(self.point1.x, self.point2.y), self.point1), color)

    def draw_move(self,window:Window, to_cell, undo=False) -> None:
        color = "red"
        if undo:
            color = "gray"
        window.draw_line(Line(self.get_center_point(), to_cell.get_center_point()), color)

    def remove_wall_to_cell(self, cell) -> None:
        delta_x, delta_y =  cell.maze_x - self.maze_x, cell.maze_y - self.maze_y
        direction = None
        for key, value in SEARCHPATTERN.items():
            if value == (delta_y, delta_x):
                direction = key
        if direction == "N":
            self.has_top_wall = False
            cell.has_bottom_wall = False
        elif direction == "S":
            self.has_bottom_wall = False
            cell.has_top_wall = False
        elif direction == "W":
            self.has_left_wall = False
            cell.has_right_wall = False
        elif direction == "O":
            self.has_right_wall = False
            cell.has_left_wall = False

class Maze:
    def __init__(self, point: Point, num_rows: int, num_cols: int, cell_size_x: int, cell_size_y: int) -> None:
        self.point = point
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self._cells = []

    def run(self, win: Window)  -> None:
        win.run = True
        self.create_cells()
        self.break_entrance_and_exit()
        self.create_labyrinth()
        self.draw_cell(win)
        self.reset_cell_visited()
        self.solve(win)

    def create_cells(self)  -> None:
        current = self.point
        for i in range(self.num_cols):
            cell_row = []
            for rows in range(self.num_rows):
                cell_row.append(Cell(current, Point(current.x + self.cell_size_x, current.y + self.cell_size_y), rows, i))
                current = Point(current.x + self.cell_size_x,current.y)
            self._cells.append(cell_row)
            current = Point(self.point.x, self.point.y + (self.cell_size_y * (i+1))) 

    def draw_cell(self, win: Window) -> None:
        for row in self._cells:
            for cell in row:
                cell.draw(win, "black")
                win.redraw()

    def break_entrance_and_exit(self) -> None:
        self._cells[0][0].has_left_wall = False
        self._cells[-1][-1].has_right_wall = False

    def find_cell_neighbour(self, column:int , row:int) -> list:
        neighbours = []
        for value in SEARCHPATTERN.values():
            y = column + value[0]
            x = row + value[1]
            if x < 0 or y < 0 or y > (self.num_cols-1) or x > (self.num_rows-1):
                continue
            if self._cells[y][x].visited == False:
                neighbours.append(self._cells[y][x])
        return neighbours

    def create_labyrinth(self) -> None:
        self._cells[0][0].visited = True
        cell_stack = []
        cell_stack.append(self._cells[0][0])
        current = None
        while len(cell_stack) > 0:
            current = cell_stack.pop()
            neighbours = self.find_cell_neighbour(current.maze_y, current.maze_x)
            if len(neighbours) > 0:
                cell_stack.append(current)
                chosen = random.choice(neighbours)
                chosen.visited = True
                current.remove_wall_to_cell(chosen)               
                cell_stack.append(chosen)

    def reset_cell_visited(self) -> None:
        for row in self._cells:
            for cell in row:
                cell.visited = False

    def solve(self, win:Window) -> bool:
        self._cells[0][0].visited = True
        cell_stack = []
        cell_stack.append(self._cells[0][0])
        last = None
        current = None
        while len(cell_stack) > 0:
            current = cell_stack.pop()
            neighbours = self.find_path_neighbour(current.maze_y, current.maze_x)
            if len(neighbours) > 0:
                cell_stack.append(current)
                chosen = random.choice(neighbours)
                win.draw_line(Line(current.get_center_point(), chosen.get_center_point()), "red")
                win.redraw()
                if last not in cell_stack and last and self._cells[0][0] != last:
                    win.draw_line(Line(current.get_center_point(), last.get_center_point()), "ghost white")
                if chosen == self._cells[-1][-1]:
                    return True      
                time.sleep(0.1)
                chosen.visited = True  
                cell_stack.append(chosen)
                last = current 
            else:
                win.draw_line(Line(current.get_center_point(), last.get_center_point()), "ghost white")
                win.redraw()
                last = current
        return False

    def find_path_neighbour(self, column:int, row:int) -> list:
        neighbours = []
        for key, value in SEARCHPATTERN.items():
            next_column = column + value[0]
            next_row = row + value[1]
            if next_row < 0 or next_column < 0 or next_column > (self.num_cols-1) or next_row > (self.num_rows-1):
                continue
            ok = False
            if key == "N" and not self._cells[column][row].has_top_wall:
                if not self._cells[next_column][next_row].visited:
                    ok = True
            elif key == "S" and not self._cells[column][row].has_bottom_wall:
                if not self._cells[next_column][next_row].visited:
                    ok = True
            elif key == "W" and not self._cells[column][row].has_left_wall:
                if not self._cells[next_column][next_row].visited:
                    ok = True
            elif key == "O" and not self._cells[column][row].has_right_wall:
                if not self._cells[next_column][next_row].visited:
                    ok = True
            if ok:
                neighbours.append(self._cells[next_column][next_row])
        return neighbours

main()
