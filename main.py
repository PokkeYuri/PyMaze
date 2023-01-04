from tkinter import Tk, BOTH, Canvas
import time
import random

SEARCHPATTERN = {
    "N":(-1, 0),
    "S":(1, 0),
    "W":(0, -1),
    "O":(0, 1)
}

def main():
    win = Window(800, 800)
    #point1 = Point(10, 10)
    #point2 = Point(40, 40)
    #point3 = Point(40, 10)
    #point4 = Point(70, 40)
    #line = Line(point1, point2)
    #win.draw_line(line, "black")
    #cell = Cell(point1, point2)
    #cell2 = Cell(point3, point4)
    
    #cell.draw(win, "black") 
    #cell2.draw(win, "black")

    #cell.draw_move(win, cell2)
    num_cols = 30
    num_rows = 30
    m1 = Maze(Point(10,10), num_rows, num_cols, 20, 20, win)
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
        self.win.update_idletasks()
        self.win.update()   
    def draw_line(self, line: Line, fill_color: str):
        line.draw(self.canvas, fill_color)
    def wait_for_close(self) -> None:
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
    def __get_center_point(self) -> Point:
        point = Point(self.point1.x + abs(self.point1.x - self.point2.x)/2,self.point1.y + abs(self.point1.y - self.point2.y) /2)
        return point
    def draw(self, window: Window, color: str) -> None:
        if self.has_top_wall:
            window.draw_line(Line(point1=self.point1, point2=Point(self.point2.x, self.point1.y)), color)
        if self.has_right_wall:
            window.draw_line(Line(point1=Point(self.point2.x, self.point1.y), point2=self.point2), color)
        if self.has_bottom_wall:
            window.draw_line(Line(point1=self.point2, point2=Point(self.point1.x, self.point2.y)), color)
        if self.has_left_wall:
            window.draw_line(Line(point1=Point(self.point1.x, self.point2.y), point2=self.point1), color)
    def draw_move(self,window:Window, to_cell, undo=False) -> None:
        color = "red"
        if undo:
            color = "gray"
        window.draw_line(Line(self.__get_center_point(), to_cell.__get_center_point()), color)
    def remove_wall_to_cell(self, cell):
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
    def __init__(self, point: Point, num_rows: int, num_cols: int, cell_size_x: int, cell_size_y: int, win: Window, seed :int = None) -> None:
        self.point = point
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        
        self._cells = []
        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls_r()
        self._draw_cell()
    def _create_cells(self):
        current = self.point
        for i in range(self.num_cols):
            cell_row = []
            for rows in range(self.num_rows):
                cell_row.append(Cell(current, Point(current.x + self.cell_size_x, current.y + self.cell_size_y), rows, i))
                current = Point(current.x + self.cell_size_x,current.y)
            self._cells.append(cell_row)
            current = Point(self.point.x, self.point.y + (self.cell_size_y * (i+1))) 
    def _draw_cell(self):
        for row in self._cells:
            for cell in row:
                cell.draw(self.win, "black")
                self._animate()
    def _animate(self):
        self.win.redraw()
        time.sleep(0.05)
    def _break_entrance_and_exit(self):
        self._cells[0][0].has_left_wall = False
        self._cells[-1][-1].has_right_wall = False
    def _find_cell_neighbour(self, column:int , row:int):
        neighbours = []
        for value in SEARCHPATTERN.values():
            y = column + value[0]
            x = row + value[1]
            if x < 0 or y < 0 or y > (self.num_cols-1) or x > (self.num_rows-1):
                continue
            if self._cells[y][x].visited == False:
                neighbours.append(self._cells[y][x])

        return neighbours
    def _break_walls_r(self):
        self._cells[0][0].visited = True
        cell_stack = []
        cell_stack.append(self._cells[0][0])
        #Iterative Implementation of Backtracking (DFS)
        current = None
        while len(cell_stack) > 0:
            current = cell_stack.pop()
            neighbours = self._find_cell_neighbour(current.maze_y, current.maze_x)
            if len(neighbours) > 0:
                cell_stack.append(current)
                chosen = random.choice(neighbours)
                #chosen = neighbours[0]
                chosen.visited = True
                current.remove_wall_to_cell(chosen)               
                cell_stack.append(chosen)


main()
