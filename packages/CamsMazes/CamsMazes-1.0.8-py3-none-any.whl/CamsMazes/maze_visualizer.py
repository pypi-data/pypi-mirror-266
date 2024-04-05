from tkinter import *
import time
from maze import Maze

class MazeVisualizer:
    class CellVisualizer:
        def __init__(self, canvas, cell_size):
            self.canvas = canvas
            self.cell_size = cell_size
            self.visited = False
           
        def draw(self, cell, start = False, end = False, solution = False):
            cellColour = "red" if solution else "white"
            if (start): cellColour = "green" 
            elif (end): cellColour = "yellow"
            self.canvas.create_rectangle(self._get_canvas_coords(cell), fill = cellColour, outline="")

        # Converts cell to canvas coordinates
        def _get_canvas_coords(self, cell):
            row, col = cell
            cell_size = self.cell_size
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            return [x1, y1, x2, y2]
        
    def __init__(self, maze, delay_ms=5, cell_size = 10):
        if (not isinstance(maze, Maze)): raise TypeError("maze is not instance of Maze")
        self.maze = maze
        self.num_rows = self.maze.num_rows
        self.num_cols = self.maze.num_cols
        self.start_cell = self.maze.start_grid_cell
        self.end_cell = self.maze.end_grid_cell
        self.cell_size = cell_size
        self.delay_seconds = delay_ms / 1000
        self.solved = False
        self._init_GUI()
        
    def _init_GUI(self):
        self.window = Tk()
        window = self.window
        window.title("Maze Generator and Solver")

        # Creating GUI Buttons
        generate_maze_button = Button(window, text="Generate Maze", command=self._generate_maze)
        generate_maze_button.pack()
        
        show_solution_button = Button(window, text="Show Solution", command=self._show_solution)
        show_solution_button.pack()

        close_window_button = Button(window, text="Close", command=self.window.destroy)
        close_window_button.pack()
        
        cell_size = self.cell_size
        canvas_height = self.maze.grid_rows * cell_size
        canvas_width = self.maze.grid_cols * cell_size

        self.canvas = Canvas(window, bg="#222", height=canvas_height, width=canvas_width)
        self.canvas.pack()
        self.window.update()

        self.CellVisualizer = self.CellVisualizer(self.canvas, self.cell_size)
        self._draw_maze()
        self.window.mainloop()
    
    ## Update Maze GUI
    def _update_GUI(self):
        self.canvas.update()
        time.sleep(self.delay_seconds)

    # Clear Canvas and Generate New Maze
    def _generate_maze(self):
        self.canvas.delete("all")
        self.maze.generate_maze()
        self.solved = False
        self._draw_maze()
    
    # Updates cells in solution path from white to red
    def _show_solution(self):
        if (self.generating and not self.solved): return 
        for cell in self.maze.solution:
            self.CellVisualizer.draw(cell, start = (cell == self.start_cell), end = (cell == self.end_cell), solution=True)
        self.solved = True
    
    # Draws the maze
    def _draw_maze(self):
        self.generating = True
        cell_visualizer = self.CellVisualizer
        for cell in self.maze.generation_path:
            cell_visualizer.draw(cell, start = (cell == self.start_cell), end = (cell == self.end_cell))
            self._update_GUI()
        self.generating = False