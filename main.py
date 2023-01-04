from tkinter import Tk, BOTH, Canvas
import time

def main():
    win = Window(800, 600)
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
    num_cols = 12
    num_rows = 10
    m1 = Maze(Point(10,10), num_rows, num_cols, 40, 40, win)
    m1.break_entrance_and_exit()
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
    def __init__(self, point1: Point, point2: Point) -> None:
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.point1 = point1
        self.point2 = point2
        self.visited = False
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

class Maze:
    def __init__(self, point: Point, num_rows: int, num_cols: int, cell_size_x: int, cell_size_y: int, win: Window, seed :int) -> None:
        self.point = point
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        
        self._cells = []
        self._create_cells()
        self.break_entrance_and_exit()
        self._draw_cell()
    def _create_cells(self):
        current = self.point
        for i in range(self.num_cols):
            cell_row = []
            for rows in range(self.num_rows):
                cell_row.append(Cell(current, Point(current.x + self.cell_size_x, current.y + self.cell_size_y)))
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
        time.sleep(0.2)
    def break_entrance_and_exit(self):
        self._cells[0][0].has_left_wall = False
        self._cells[-1][-1].has_right_wall = False

main()