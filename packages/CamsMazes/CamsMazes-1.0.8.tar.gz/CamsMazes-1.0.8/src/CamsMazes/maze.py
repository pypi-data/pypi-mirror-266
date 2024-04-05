import random
from random import randint
import json
import copy
from PIL import Image, ImageDraw
from io import BytesIO
import base64

class Maze:
    class Cell:
        def __init__(self, row, col):
            self.col = col
            self.row = row
            self.walls = {"top": 1, "right": 1, "bottom": 1, "left": 1}
            self.visited = False
            self.grid_row =  (self.row * 2) + 1
            self.grid_col =  (self.col * 2) + 1
            self.grid_cell = (self.grid_row, self.grid_col)
            
        def update_walls(self, neighbour_wall_pos):
            self.walls[neighbour_wall_pos] = 0
        
        def get_neighbours(self, grid=False):
            row = self.grid_row if grid else self.row
            col = self.grid_col if grid else self.col
            neighbours = {
                "top": (row-1, col),
                "right": (row, col+1),
                "bottom": (row+1, col),
                "left": (row, col-1)
            }
            return neighbours
        
        def get_wall(self, wall_pos):
            neighbours = self.get_neighbours(grid=True)
            return neighbours[wall_pos]

    def __init__(self, num_rows, num_cols, start_row = 0, start_col = 0, end_row = None, end_col = None, seed = None):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row if end_row else num_rows - 1
        self.end_col = end_col if end_col else num_cols - 1
        self.seed = seed
        self.generate_maze()
    
    # Initalized ungeneranted Maze
    def _init_maze(self):
        ungenerated_maze = []
        for row in range(self.num_rows):
            row_of_cells = []
            for col in range (self.num_cols):
                cell = self.Cell(row, col)
                row_of_cells.append(cell)
            ungenerated_maze.append(row_of_cells)
        self.maze = ungenerated_maze
        self.generated = False
        self.solved = False

    # Generates maze using Depth First Search
    def generate_maze(self):
        self._init_maze()
        if (self.seed is not None): random.seed(self.seed)
        start_cell = self.maze[self.start_row][self.start_col]
        start_cell.visited = True
        stack = []
        stack.append(start_cell)  
        generation_path = []
        generation_path.append(start_cell.grid_cell)
        
        # Returns true if neighbour is in Maze and not visited
        def check_neighbour(row, col):
            return ((row >= 0 and col >= 0) and (row < self.num_rows and col < self.num_cols) and not self.maze[row][col].visited)

        # Generate Maze using DFS
        while (len(stack) > 0):
            cell = stack.pop()
            neighbours = []
            # Filtering out any "bad" neighbours
            neighbours_map = cell.get_neighbours()
            for neighbour_pos in neighbours_map.keys():
                neighbour = neighbours_map[neighbour_pos]
                row, col = neighbour
                if (check_neighbour(row, col)): neighbours.append((self.maze[row][col], neighbour_pos))
                
            if (len(neighbours) > 0):                              
                stack.append(cell)

                # Choosing random neighbour to visit
                random_pos = randint(0, len(neighbours) - 1)
                neighbourArr = neighbours[random_pos]
                neighbour, neighbour_pos = neighbourArr
                neighbour.visited = True
                stack.append(neighbour)

                # Adding neighbour and wall to generation path
                wall = cell.get_wall(neighbour_pos)
                generation_path.append(wall) # Wall between cell and neighbour
                generation_path.append(neighbour.grid_cell) # Neighbour
                
                # Updating walls for current cell and neighbour
                cell.update_walls(neighbour_pos)
                cell_wall_map = {"top": "bottom", "right": "left", "bottom": "top", "left": "right"}
                cell_wall_pos = cell_wall_map[neighbour_pos]
                neighbour.update_walls(cell_wall_pos)

        self.generated = True
        self.generation_path = generation_path
        self.to_grid()
        self.solve()
        return self.maze

    # Converts Maze from grid of Cells to grid of numbers representing the cell type
    # 0 = Walkable Cell
    # 1 = Wall
    # 2 = Start
    # 3 = End Cell
    def to_grid(self):
        grid = []
        rows = self.num_rows
        cols = self.num_cols
        for row in range(rows):
            top_arr = []
            middle_arr = []
            bottom_arr = []
            last_row = row == rows - 1
            for col in range(cols):
                last_col = col == cols - 1
                top, right, bottom, left = self.maze[row][col].walls.values()
                top_arr += [1, top, top or right]
                cell_type = 0
                if (row == self.start_row and col == self.start_col): cell_type = 2
                if (row == self.end_row and col == self.end_col): cell_type = 3
                middle_arr += [left, cell_type, right]
                if last_row: bottom_arr += [bottom or left, bottom, bottom or right]
                if not last_col:
                    top_arr.pop()
                    middle_arr.pop()
                    if last_row: bottom_arr.pop()
            grid.append(top_arr)
            grid.append(middle_arr)
            if (last_row): grid.append(bottom_arr)
        self.grid = grid

        self.grid_rows = (self.num_rows * 2) + 1
        self.grid_cols = (self.num_cols * 2) + 1
        def convert_to_grid_cell(row, col):
            return ((row * 2) + 1, (col * 2) + 1)
        self.start_grid_cell =  convert_to_grid_cell(self.start_row, self.start_col)
        self.end_grid_cell = convert_to_grid_cell(self.end_row, self.end_col)
        return grid
    
    # Solves Maze using Depth First Search
    def solve(self):
        grid = copy.deepcopy(self.grid)
        start_cell = self.start_grid_cell
        end_cell = self.end_grid_cell
        stack = []
        visited = []
        visited.append(start_cell)
        stack.append(start_cell)
     
        def get_neighbours(cell):
            row, col = cell
            neighbours = []
            num_rows = self.grid_rows
            num_cols = self.grid_cols
            if (row > 0 and grid[row-1][col] != 1): neighbours.append((row-1,col)) # Top Neighbour
            if (col < num_cols -1 and grid[row][col+1] != 1): neighbours.append((row,col+1)) # Right Neighbour
            if (row < num_rows -1 and grid[row+1][col] != 1): neighbours.append((row+1,col)) # Bottom Neighbour
            if (col > 0 and grid[row][col-1] != 1): neighbours.append((row,col-1)) # Left Neighbour
            return neighbours
        
        previous_cell_map = {}
        previous_cell_map[start_cell] = None
        while (len(stack) > 0):
            cell = stack.pop()
            visited.append(cell)
            neighbours = get_neighbours(cell)
            for neighbour in neighbours:
                if neighbour not in visited and neighbour not in stack:
                    previous_cell_map[neighbour] = cell
                    if (neighbour == end_cell):
                        break
                    stack.append(neighbour)
        
        # Creating solution path
        solution_path = [end_cell]
        neighbour = previous_cell_map[end_cell]
        solution_path.append(neighbour)
        while True:
            cell = previous_cell_map[neighbour]
            if (cell is None): break
            solution_path.append(cell)
            neighbour = cell
            
        solution_path.reverse() # Reversing path so start_cell is at front
        for cell in solution_path:
            row, col = cell
            if (cell != start_cell and cell != end_cell): grid[row][col] = 4

        self.solution = solution_path # Add solution to Maze
        self.solved = True
        self.grid_solution = grid
        return grid

    # Returns JSON representation of Maze
    def to_json(self):
        img_str = self.to_image(save = False)[1]
        maze = {
            "numCols": self.num_cols,
            "numRows": self.num_rows,
            "startCol": self.start_col,
            "startRow": self.start_row,
            "endCol": self.end_col,
            "endRow": self.end_row,
            "seed": self.seed,
            "grid": {
                "rows": self.grid_rows,
                "cols": self.grid_cols,
                "startCell": self.start_grid_cell,
                "endCell": self.end_grid_cell, 
                "maze": self.grid,
                "mazeSolution": self.grid_solution,
                "generationPath": self.generation_path,
                "solutionPath": self.solution
            },
            "img_base64": img_str
        }
        return json.dumps(maze)
    
    # Prints maze
    def print(self, show_solution = False):
        print(self._get_maze_text(show_solution))

    # Creates txt file of maze
    def to_txt(self, txt_name = "maze", show_solution = False):
        f = open(txt_name, "w").close()
        f = open(txt_name, "a")
        grid = self.grid_solution if show_solution else self.grid
        for row in grid:
            row_str = self._get_row_text(row)
            f.write(row_str)
            f.write("\n")
        f.close()

    def _get_row_text(self, row):
        text_map = {
            0: " ", # Walkable
            1: "#", # Wall
            2: "S", # Start
            3: "E", # End
            4: "X"  # Solution path
        }
        row_str = ""
        for cell in row:
            row_str+=text_map[cell]
        return row_str
    
    def _get_maze_text(self, show_solution = False):
        maze_str = ""
        curr_row = 0
        grid = self.grid_solution if show_solution else self.grid
        for row in grid:
            row_str = self._get_row_text(row)
            maze_str+=row_str
            if (not curr_row == self.grid_rows-1): maze_str+="\n"
            curr_row+=1
        return maze_str

    def __str__(self):
        return self._get_maze_text(show_solution=False)

    # Creates image of maze
    def to_image(self, file_name = "maze", file_ext = "png", cell_size=15, save=True, show_solution = False):
        image = Image.new("RGB", self._get_image_size(cell_size), "black")
        draw = ImageDraw.Draw(image)
        img_colour_map = {0: "white", 1: "black", 2: "green", 3: "yellow", 4: "red"}
        grid = self.grid_solution if show_solution else self.grid
        buff = BytesIO()
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_type = grid[row][col]
                cell_colour = img_colour_map[cell_type]
                draw.rectangle(self._convert_to_image_coords(cell_size, row, col), fill=cell_colour)
        if (save): image.save(f"{file_name}.{file_ext}")
        file_ext = "jpeg" if file_ext == "jpg" else file_ext 
        image.save(buff, format=file_ext)
        img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
        return [image, img_str]
    
    # Creates gif of maze generation
    def to_gif(self, file_name="maze", cell_size=10):
        images = []
        image = Image.new("P", self._get_image_size(cell_size), "black") 
        draw = ImageDraw.Draw(image)
        images.append(image)
        for cell in self.generation_path:
            image = copy.deepcopy(images[-1])
            draw = ImageDraw.Draw(image)
            row, col = cell
            cell_colour = "white"
            if (cell == self.start_grid_cell): cell_colour = "green"
            elif (cell == self.end_grid_cell): cell_colour = "yellow"
            x, y, x2, y2 = self._convert_to_image_coords(cell_size, row, col)
            draw.rectangle((x, y, x2, y2), fill=cell_colour)
            images.append(image)
        images[0].save(f"{file_name}.gif", save_all=True, append_images=images[1:])

    def _convert_to_image_coords(self, cell_size, row, col):
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        return [x1, y1, x2, y2]

    def _get_image_size(self, cell_size):
        image_width = self.grid_cols * cell_size
        image_height = self.grid_rows * cell_size
        return (image_width, image_height)