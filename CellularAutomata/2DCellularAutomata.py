import pygame, sys, os, random

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Getting screen size
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
info = pygame.display.Info()
screen_width,screen_height = info.current_w,info.current_h

# Setting up variables, window and GUI
PROJECT_NAME = "Conway's game of life"
WIDTH, HEIGHT = screen_width,screen_height - 50
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)

SIDEBAR = 300
FPS = 60
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

gridCard = gui.add_section("Grid controls")
fps_label = gui.add_label(gridCard, "FPS: --")
width_sl = gui.add_slider(gridCard, "Width", 1, 400, 100, 1)
height_sl = gui.add_slider(gridCard, "Height", 1, 400, 75, 1)
size_sl = gui.add_slider(gridCard, "Cell size", 2, 100, 10, 1)

shouldSpawn = False
shouldReverse = False

def spawnButton():
    global shouldSpawn
    shouldSpawn = True

def reverseButton():
    global shouldReverse
    shouldReverse = True

spawnCard = gui.add_section("Spawn controls")
spawnAreaSize_sl = gui.add_slider(spawnCard, "Spawn area size", 10, 200, 10, 1)
spawn_bt = gui.add_button(spawnCard, "Spawn", callback=spawnButton)
reverse_bt = gui.add_button(spawnCard, "Reverse", callback=reverseButton)

rulesetCard = gui.add_section("Ruleset selection")
ruleset_lb = gui.add_label(rulesetCard, "Conway's game of life")
ruleset_sl = gui.add_slider(rulesetCard, "", 1, 16, 1, 1)

shouldStep = False
isSimRunning = False

def stepButton():
    global shouldStep
    shouldStep = True

timeCard = gui.add_section("Time controls")
step_bt = gui.add_button(timeCard, "Step 1", callback=stepButton)
run_tg = gui.add_checkbox(timeCard, "Run sim", False)
maxFps_sl = gui.add_slider(timeCard, "Max sim FPS", 1, 60, 20, 1)

simTimer = 0.0
grid = []
prevWidth = 0
prevHeight = 0

AGE_COLORS = [
    (0, "white"),
    (2, "#ffd381"),
    (4, "orange"),
    (6, "#ffcc00"),
    (8, "yellow"),
    (16, "#acff68"),
    (32, "green"),
    (64, "#33ffee"),
    (96, "#7b7bff"),
    (128, "blue")
]

def getColorFromAge(age):
    color = AGE_COLORS[0][1]
    for threshold, c in AGE_COLORS:
        if age >= threshold:
            color = c
        else:
            break
    return color

def step(oldGrid, birthConditions, surviveConditions):
    newGrid = [[cell[:] for cell in row] for row in oldGrid]
    width = width_sl.value
    height = height_sl.value

    # Iterating through all the cells
    for ri, r in enumerate(oldGrid):
        for ci, c in enumerate(r):
            # Checking and counting neighbors
            count = 0
            for x in range(3):
                for y in range(3):
                    if not (x == 1 and y == 1) and 0 <= ri - 1 + x < width and 0 <= ci - 1 + y < height:
                        if oldGrid[ri - 1 + x][ci - 1 + y][0] == 1:
                            count += 1

            # Applying the ruleset
            if c[0] == 1:
                shouldLive = False
                for condition in surviveConditions:
                    if count == condition: shouldLive = True
                
                if not shouldLive: 
                    newGrid[ri][ci][0] = 0
                    newGrid[ri][ci][1] = 0
                else:
                    newGrid[ri][ci][1] += 1
            elif c[0] == 0:
                for condition in birthConditions:
                    if count == condition: 
                        newGrid[ri][ci][0] = 1
                        newGrid[ri][ci][1] = 1

    return newGrid

def getGridPosFromMouse():
    mouseX, mouseY = pygame.mouse.get_pos()
    cellSize = size_sl.value
    width = width_sl.value
    height = height_sl.value

    startX = WIDTH//2 + SIDEBAR//2 - (cellSize * width)//2
    startY = HEIGHT//2 - (cellSize * height)//2
    gridRect = pygame.Rect(startX, startY, cellSize * width, cellSize * height)
    
    if gridRect.collidepoint(mouseX, mouseY):
        xIn = mouseX - startX
        yIn = mouseY - startY

        return int(xIn // cellSize), int(yIn // cellSize)
    else: 
        return None, None

def logic(delta):
    global prevWidth, prevHeight, shouldStep, isSimRunning, grid, shouldSpawn, simTimer, shouldReverse

    isSimRunning = run_tg.value
    width = width_sl.value
    height = height_sl.value
    
    ruleset = ruleset_sl.value

    if ruleset == 1:
        ruleset_lb.text = "Conway's game of life"
        birthConditions = [3]
        surviveConditions = [2, 3]
    elif ruleset == 2:
        ruleset_lb.text = "Maze"
        birthConditions = [3]
        surviveConditions = [1, 2, 3, 4, 5]
    elif ruleset == 3:
        ruleset_lb.text = "Mazetric"
        birthConditions = [3]
        surviveConditions = [1, 2, 3, 4]
    elif ruleset == 4:
        ruleset_lb.text = "Mazetric with mice"
        birthConditions = [3, 7]
        surviveConditions = [1, 2, 3, 4]
    elif ruleset == 5:
        ruleset_lb.text = "Ant colony"
        birthConditions = [3]
        surviveConditions = [2, 3, 4]
    elif ruleset == 6:
        ruleset_lb.text = "A world on fire"
        birthConditions = [3, 4]
        surviveConditions = [2, 3]
    elif ruleset == 7:
        ruleset_lb.text = "Blinkers"
        birthConditions = [3, 4, 5]
        surviveConditions = [2]
    elif ruleset == 8:
        ruleset_lb.text = "Coral"
        birthConditions = [3]
        surviveConditions = [4, 5, 6, 7, 8]
    elif ruleset == 9:
        ruleset_lb.text = "Life without death"
        birthConditions = [3]
        surviveConditions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    elif ruleset == 10:
        ruleset_lb.text = "Assimilation"
        birthConditions = [3, 4, 5]
        surviveConditions = [4, 5, 6, 7]
    elif ruleset == 11:
        ruleset_lb.text = "Rotten egg"
        birthConditions = [3, 4]
        surviveConditions = [4, 5, 6, 7]
    elif ruleset == 12:
        ruleset_lb.text = "Healthy egg"
        birthConditions = [3, 4]
        surviveConditions = [4, 5, 6, 7, 8]
    elif ruleset == 13:
        ruleset_lb.text = "High Life"
        birthConditions = [3, 6]
        surviveConditions = [2, 3]
    elif ruleset == 14:
        ruleset_lb.text = "Seeds"
        birthConditions = [2]
        surviveConditions = []
    elif ruleset == 15:
        ruleset_lb.text = "Sierpinski's triangle"
        birthConditions = [1]
        surviveConditions = [1, 2]
    elif ruleset == 16:
        ruleset_lb.text = "Seb's cavegen"
        birthConditions = [5, 6, 7, 8]
        surviveConditions = [4, 5, 6, 7, 8]


    ruleset_sl.label = f"B{birthConditions}/S{surviveConditions}"

    
    # Rebuilding grid if needed
    if width_sl.value != prevWidth or height_sl.value != prevHeight:
        grid = []
        for c in range(width):
            grid.append([])
            for r in range(height):
                grid[c].append([0, 0])
        prevWidth = width
        prevHeight = height

    if shouldSpawn:
        shouldSpawn = False
        spawnArea = spawnAreaSize_sl.value
        for ri, r in enumerate(grid):
            for ci, c in enumerate(r):
                grid[ri][ci][0] = 0
                if width//2 - spawnArea//2 < ri < width//2 + spawnArea//2 and height//2 - spawnArea//2 < ci < height//2 + spawnArea//2:
                    grid[ri][ci][0] = random.randint(0,1)

    stepInterval = 1.0 / maxFps_sl.value

    # Stepping when needed
    if shouldStep and not isSimRunning:
        newGrid = step(grid, birthConditions, surviveConditions)
        grid = newGrid.copy()
        shouldStep = False
    elif isSimRunning:
        simTimer += delta
        if simTimer >= stepInterval:
            newGrid = step(grid, birthConditions, surviveConditions)
            grid = newGrid.copy()
            simTimer -= stepInterval
    
    if shouldReverse:
        shouldReverse = False
        for ri, r in enumerate(grid):
            for ci, c in enumerate(r):
                grid[ri][ci][0] = 1 if grid[ri][ci][0] == 0 else 0


def drawWin():
    global grid, isSimRunning
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    cellSize = size_sl.value
    width = width_sl.value
    height = height_sl.value

    widthOff = (cellSize * width) // 2 - cellSize//2
    heighOff = (cellSize * height) // 2 - cellSize//2

    widthStart = WIDTH//2 - widthOff + SIDEBAR//2
    heightStart = HEIGHT//2 - heighOff

    gridRect = pygame.Rect(widthStart - cellSize//2, heightStart - cellSize//2, cellSize * width, cellSize * height)
    pygame.draw.rect(WIN, "black", gridRect)

    for ri, r in enumerate(grid):
        for ci, c in enumerate(r):
            if c[0] == 1:
                cell = pygame.Rect(widthStart + ri * cellSize - cellSize//2, heightStart + ci * cellSize - cellSize//2, cellSize, cellSize)
                color = getColorFromAge(c[1])
                pygame.draw.rect(WIN, color, cell)
    
    if not isSimRunning:
        spawnArea = spawnAreaSize_sl.value
        rect1 = pygame.Rect((widthStart + (width//2 - spawnArea//2) * cellSize - cellSize//2, heightStart + (height//2 - spawnArea//2) * cellSize - cellSize//2), (cellSize, cellSize))
        rect2 = pygame.Rect((widthStart + (width//2 + spawnArea//2) * cellSize - cellSize//2, heightStart + (height//2 + spawnArea//2) * cellSize - cellSize//2), (cellSize, cellSize))
        pygame.draw.rect(WIN, "darkblue", rect1)
        pygame.draw.rect(WIN, "darkblue", rect2)

def main():
    global grid
    clock = pygame.time.Clock()
    running = True
    
    while running:
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps())}"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            gui.handle_event(event)

            if pygame.mouse.get_pressed()[0]:
                r, c = getGridPosFromMouse()
                print(c)
                if c != None and r != None:
                    if grid[r][c][0] == 1:
                        grid[r][c][0] = 0
                    else:
                        grid[r][c][0] = 1
                        grid[r][c][1] = 0

        logic(delta)
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
