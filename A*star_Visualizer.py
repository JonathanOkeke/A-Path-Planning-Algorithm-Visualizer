import pygame, sys
from queue import PriorityQueue
from pygame.locals import *

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("A Star Path Finding Visualiser")

# Main Menu Screen
screen = pygame.display.set_mode((800, 800), 0, 32)
font1 = pygame.font.SysFont(None, 80, True)
font2 = pygame.font.SysFont(None, 40, True)
font3 = pygame.font.SysFont(None, 30, True)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


click = False


# Handling Main Menu
def main_menu():
    while True:

        screen.fill((0, 0, 0))

        # Drawing all the main menu text assets
        draw_text('WELCOME!', font1, (255, 255, 255), screen, 200, 50)
        draw_text('1. Click on "START" to begin visualization.', font2, (255, 255, 255), screen, 75, 150)
        draw_text('2. Hit the "ESCAPE" key to quit at any time.', font2, (255, 255, 255), screen, 75, 250)
        draw_text('By Jonathan Okeke', font2, (255, 255, 255), screen, 480, 750)

        # Drawing buttons and handling button clicks
        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(150, 400, 500, 100)
        # Calling the visualizer to begin
        if button_1.collidepoint((mx, my)):
            if click:
                start()
        pygame.draw.rect(screen, (255, 0, 0), button_1)
        screen.blit(font1.render("START", True, (255, 255, 255)), (300, 420))

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)


def start():
    # Setting up pygame display
    WIDTH = 800
    WIN = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("A Star Path Finding Visualiser")

    # Defining the colour codes of the visualization
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 255, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165, 0)
    GREY = (128, 128, 128)
    TURQUOISE = (64, 224, 208)

    # Defining the 50x50 node grid visualization tool
    # A class called 'node' or 'node' that generates the cube nodes and keeps track of the node's position (row and column) , size information, its  neighbour nodes etc, barriers etc

    class Node:

        def __init__(self, row, col, width, total_rows):
            self.row = row
            self.col = col
            self.x = row * width  # X position of particular node relative to start node
            self.y = col * width  # Y position of particular node relative to start node
            self.color = WHITE  # sets default node color to white for all nodes
            self.neighbors = []  # holds info on neighbour nodes
            self.width = width
            self.total_rows = total_rows

        # Methods that retrieve info about nodes

        def get_pos(self):  # Deals with finding the index position of the particular node
            return self.row, self.col

        def is_closed(self):  # Check if node has already been traversed by checking if the node color is red
            return self.color == RED

        def is_open(self):  # Checks if node is in the open set for searching by checking if the node color is green
            return self.color == GREEN

        def is_barrier(self):  # Checks if node is a barrier/obstacle node by checking if the node color is black
            return self.color == BLACK

        def is_start(self):  # Checks if node is the current start node by checking if the node color is orange
            return self.color == ORANGE

        def is_end(self):  # Checks if node is the end/goal node by checking if the node color is turquoise
            return self.color == TURQUOISE

        # Methods that do something to a node

        def reset(self):  # Resets a node to white in case a mistake is made
            self.color = WHITE

        def make_start(self):  # Turns chosen start node orange
            self.color = ORANGE

        def make_closed(self):  # Turns node traversed by the algorithm to red color
            self.color = RED

        def make_open(self):  # Turns node IN THE OPEN SEARCH SET NOT YET traversed by the algorithm to green color
            self.color = GREEN

        def make_barrier(self):
            self.color = BLACK

        def make_end(self):
            self.color = TURQUOISE

        def make_path(self):  # Turning active search path to purple
            self.color = PURPLE

        def draw(self, win):  # Starting to draw out the node grid. Pygame starts at the top left of the screen (0,0) up until the bottom right to (800, 800)
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

        def update_neighbors(self, grid):  # We must only include the neighbours are not barriers and that are actually useful since if they are surrounded or obscured by barriers those neighbours are useless to the search
            self.neighbors = []
            # Checking for available neighbours below start node
            if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
                self.neighbors.append(grid[self.row + 1][self.col])

            # Checking for available neighbours above start node
            if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
                self.neighbors.append(grid[self.row - 1][self.col])

            # Checking for available neighbours to the left of start node
            if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
                self.neighbors.append(grid[self.row][self.col - 1])

            # Checking for available neighbours to the right of start node
            if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
                self.neighbors.append(grid[self.row][self.col + 1])

        def __lt__(self, other):  # less_than method. Compares to nodes and in this case will be used to defines what is the previous node
            return False

    # Algorithm Methods

    # H function - guesses distance between two nodes using the "Manhattan Distance" - "L-Distance" - "Quickest L distance between nodes" since we cannot use the diagonal in this case
    def h(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(came_from, current, draw):
        while current in came_from:
            current = came_from[current]
            current.make_path()
            draw()

    # A* Algorithm
    def algorithm(draw, grid, start_node, end_node):
        count = 0
        open_set = PriorityQueue()  # Defining the open set and will remove the smallest f_score value after each case is checked

        # Begin algorithm with start node info
        open_set.put((0, count, start_node))
        came_from = {}  # Keeps track of the node that the current node came from.

        # Assigning an initial infinity G-score to the nodes prior to search commencement in to a dictionary
        g_score = {node: float("inf") for row in grid for node in row}
        g_score[start_node] = 0  # G_score for start node will always be zero

        # Assigning an initial infinity F-score to the nodes prior to search commencement in to a dictionary
        f_score = {node: float("inf") for row in grid for node in row}
        # F_score is based on the distance/heuristic calculation by the h() function defined above
        f_score[start_node] = h(start_node.get_pos(), end_node.get_pos())

        # Let's us query which values are and not in the open_set
        # Is essentially a hash
        open_set_hash = {start_node}

        while not open_set.empty():  # If open set is empty it means that the algorithm has searched through all the possible nodes and no solution was found
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            # Finding node will lowest f_score and removing it from the open set
            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end_node:  # We've found the shortest path
                reconstruct_path(came_from, end_node, draw)
                end_node.make_end()
                return True

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1  # Add one to shortest known distance to get new g_score since we assume that the cost/distance between neighbor nodes is always one

                # If the temp_g_score of the current neighbor node is less than the g_score of the previous neighbour then we update the trajectory
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end_node.get_pos())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()
            draw()

            if current != start_node:
                current.make_closed()

        return False

    # Data structure that will hold all the grid information
    def make_grid(rows, width):
        grid = []
        gap = width // rows  # Defines the actual thickness of each node cube |->|. The width is the width of the pygame screen and rows is the number of node we want
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                node = Node(i, j, gap, rows)
                grid[i].append(node)

        return grid

    def draw_grid(win, rows, width):
        gap = width // rows
        for i in range(rows):
            # Horizontal lines
            pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
            # Vertical lines
            for j in range(rows):
                pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

    def draw(win, grid, rows, width):
        win.fill(WHITE)  # Clears pygame screen in white each time we iterate before we draw out visualization after each update in the search

        for row in grid:
            for node in row:
                node.draw(win)

        draw_grid(win, rows, width)
        pygame.display.update()

    def get_clicked_pos(pos, rows, width):  # Finding the position of which node the user has clicked on
        gap = width // rows
        y, x = pos

        row = y // gap
        col = x // gap
        return row, col

    def visualizer(win, width):
        ROWS = 50
        grid = make_grid(ROWS, width)

        start_node = None  # Will hold the start node. We initialize it with no value
        end_node = None  # Will hold the end node We initialize it with no value

        run = True  # Control for the while loop
        started = False  # Control for beginning the search or not

        while run:
            # Start drawing the grid
            draw(win, grid, ROWS, width)

            # Begin checking for events (clicks)  in this case
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_q:
                        run = False

                if pygame.mouse.get_pressed()[0]:  # Checks if left_click on mouse is pressed
                    # Getting the pixel location (u,v) of the click on the grid from the pygame.mouse.get_pos()  and sending it to the get_clicked_pos() function to get the index of the node in terms of (row, column) so that we can track it and assign it to either the start, end or barrier nodes
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    node = grid[row][col]  # Now we have an indexed position of a node in terms of its row and column.

                    # First click - Assigning the indexed node first clicked on the grid to the start_node

                    if not start_node and node != end_node:  # Assigning a value to the start_node if it still has no value assigned (None) AND if the initial node value is not assigned to the end_node variable.
                        start_node = node
                        start_node.make_start()

                    # Second click - Assigning the indexed node second clicked on the grid to the start_node

                    elif not end_node and node != start_node:  # Assigning a value to the end_node if it still has no value assigned (None) AND if the current node value does not match the start_node value so that your start and end nodes are not the same.
                        end_node = node
                        end_node.make_end()

                    # Remainder click and drags will be  assigned to the barrier nodes
                    elif node != end_node and node != start_node:
                        node.make_barrier()

                # Resetting a mis-placed node position
                elif pygame.mouse.get_pressed()[2]:  # Checks if left_click on mouse is pressed
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    node = grid[row][col]
                    node.reset()  # We reset the node so that we can reassign it again
                    if node == start_node:
                        start_node = None
                    elif node == end_node:
                        end_node = None

                # Updating all possible neighbours
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and start_node and end_node:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)  # Iterating through all nodes and checking neighbours

                        # Beginning A-star search
                        algorithm(lambda: draw(win, grid, ROWS, width), grid, start_node, end_node)

                    if event.key == pygame.K_c:
                        start_node = None
                        end_node = None
                        grid = make_grid(ROWS, width)

        # Returning to Main Menu
        main_menu()

    # Executing the visualizer
    visualizer(WIN, WIDTH)

main_menu()
