import pygame, sys, numpy as np, random, time
from pygame._sdl2.video import Window

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "Sandbox"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

FPS = 60
SIDEBAR = 200
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)
PALETTE = np.array([(0, 0, 0), (150, 150, 0), (0, 60, 150), (150, 150, 150)], dtype=np.uint8)

shouldClear = False
shouldStep = False

def clear():
    global shouldClear
    shouldClear = True

def stepit():
    global shouldStep
    shouldStep = True

gridCard = gui.add_section("Controls")
fps_label = gui.add_label(gridCard, "FPS: --")
xratio = gui.add_slider(gridCard, "X ratio", 0.01, 1, 1, 0.01)
yratio = gui.add_slider(gridCard, "Y ratio", 0.01, 1, 1, 0.01)
size = gui.add_slider(gridCard, "Cell size", 1, 10, 10, 1)
padding = gui.add_slider(gridCard, "Padding", 0, 25, 2, 1)

simCard = gui.add_section("Simulation")
selectedState = gui.add_slider(simCard, "State", 0, 3, 1, 1)
brushSize = gui.add_slider(simCard, "Brush size", 1, 10, 1, 1)
clearBt = gui.add_button(simCard, "Clear", callback=clear)
stepBt = gui.add_button(simCard, "Step", callback=stepit)
runCb = gui.add_checkbox(simCard, "Run", True)
simSpeed = gui.add_slider(simCard, "Speed", 1, 1000, 100, 1)

prevx, prevy, prevs, prevp = 0, 0, 0, 0
poss = None
states = None
nx, ny = 0, 0
walk = 0

# Dynamic grid generation based on height width ratio, resolution and padding
def getnewGrid():
    global nx, ny
    x = xratio.value
    y = yratio.value
    if x > y:
        y = y / x; x = 1
    elif y > x:
        x = x / y; y = 1
    else:
        x = 1; y = 1
        
    s = size.value
    width = (WIDTH - SIDEBAR) * x
    height = HEIGHT * y
    p = int(padding.value / s * 30)
    nx = max(1, int((width // s) - p))
    ny = max(1, int((height // s) - p))

    startx = SIDEBAR + (WIDTH - SIDEBAR) / 2 - (s * nx) / 2
    starty = HEIGHT / 2 + (s * ny) / 2 - s
    
    i = np.arange(nx)[:, None]
    j = np.arange(ny)[None, :]
    poss = np.empty((nx, ny, 2), dtype=int)
    poss[..., 0] = startx + i * s
    poss[..., 1] = starty - j * s

    return poss

def stepGrid():
    global variation
    newGrid = states.copy()
    # Applying the rules based on cell contents
    for i in range(nx):
        for j in range(ny):
            validLeft = False if i - 1 < 0 else True # These are needed to avoid index errors
            validRight = False if i + 1 > nx - 1 else True
            validDown = False if j - 1 < 0 else True
            target = False
            if newGrid[i, j] == 1: # Sand
                if validDown:
                    if newGrid[i, j - 1] == 0 or newGrid[i, j - 1] == 2:
                        target = [i, j - 1]
                        replace = 2 if newGrid[i, j - 1] == 2 else 0
                if validLeft and not target:
                    if newGrid[i - 1, j - 1] == 0 or newGrid[i - 1, j - 1] == 2:
                        target = [i - 1, j - 1]
                        replace = 2 if newGrid[i - 1, j - 1] == 2 else 0
                if validRight and not target:
                    if newGrid[i + 1, j - 1] == 0 or newGrid[i + 1, j - 1] == 2:
                        target = [i + 1, j - 1]
                        replace = 2 if newGrid[i + 1, j - 1] == 2 else 0
                if not target:
                    target = [i, j]
                    replace = 0
                if 0 <= target[0] <= nx - 1 and 0 <= target[1] <= ny - 1:
                    newGrid[i, j] = replace # Replacing the cell with water if water was replaced (needed so that sand falls though water)
                    newGrid[target[0], target[1]] = 1

                    # Dragging the color variation for consistency
                    ownvar = variation[i, j].copy()
                    repvar = variation[target[0], target[1]].copy()
                    variation[i, j] = repvar
                    variation[target[0],target[1]] = ownvar

            elif newGrid[i, j] == 2: # Water
                if validDown:
                    if newGrid[i, j - 1] == 0:
                        target = [i, j - 1]
                if validLeft and validDown and not target:
                    if newGrid[i - 1, j - 1] == 0:
                        target = [i - 1, j - 1]
                if validRight and validDown and not target:
                    if newGrid[i + 1, j - 1] == 0:
                        target = [i + 1, j - 1]
                if not target:
                    target = [i, j]

                # Also can move sideways
                if target == [i, j] or not validDown:
                    if validLeft and validRight:
                        if newGrid[i + 1, j] == 0 and newGrid[i - 1, j] == 0:
                            dir = random.choice([-1, 1])
                            target = [i + dir, j]
                    if validRight and target == [i, j]:
                        if newGrid[i + 1, j] == 0:
                            target = [i + 1, j]
                    if validLeft and target == [i, j]:
                        if newGrid[i - 1, j] == 0:
                            target = [i - 1, j]

                if 0 <= target[0] <= nx - 1 and 0 <= target[1] <= ny - 1:
                    newGrid[i, j] = 0
                    newGrid[target[0], target[1]] = 2

                    # Dragging the color variation for consistency
                    ownvar = variation[i, j].copy()
                    repvar = variation[target[0], target[1]].copy()
                    variation[i, j] = repvar
                    variation[target[0], target[1]] = ownvar

    return newGrid

def getGridPosFromMouse():
    mouseX, mouseY = pygame.mouse.get_pos()
    s = size.value
    startX = SIDEBAR + (WIDTH - SIDEBAR) / 2 - (s * nx) / 2
    startY = HEIGHT / 2 - (s * ny) / 2

    xIn = mouseX - startX
    yIn = mouseY - startY
    xind = int(xIn // s)
    yind = ny - int(yIn // s) - 1

    if xind < 0 or xind >= nx or yind < 0 or yind >= ny:
        return None, None
    else:
        return xind, yind

def logic():
    global prevx, prevy, prevs, prevp, poss, states, variation, shouldClear, shouldStep, walk

    if xratio.value != prevx or yratio.value != prevy or size.value != prevs or padding.value != prevp:
        prevx, prevy, prevs, prevp = xratio.value, yratio.value, size.value, padding.value
        poss = getnewGrid()
        states = np.zeros((poss.shape[0], poss.shape[1])).astype(np.uint8)
        variation = np.ones((poss.shape[0], poss.shape[1])).astype(np.float16)[..., None]

    if shouldClear:
        states = np.zeros((poss.shape[0], poss.shape[1])).astype(np.uint8)
        shouldClear = False

    if runCb.value:
        walk += simSpeed.value
        if walk >= 100:
            for i in range(walk // 100):
                states = stepGrid()
            walk = 0

    if shouldStep:
        states = stepGrid()
        shouldStep = False

def drawWin():
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    # Optimized rendering: creating a surface using numpy array (so we dont have to draw all the squares individually)
    s = int(size.value)
    rgb = PALETTE[states][:, ::-1]
    rgb = (variation[:, ::-1] * rgb.astype(np.float64)).astype(np.uint8)
    surf = pygame.surfarray.make_surface(rgb)
    surf = pygame.transform.scale(surf, (nx * s, ny * s))
    WIN.blit(surf, (poss[0, 0, 0], poss[0, ny - 1, 1]))

def main():
    global poss, states, variation
    clock = pygame.time.Clock()
    running = True

    poss = getnewGrid()
    states = np.zeros((poss.shape[0], poss.shape[1])).astype(np.uint8)
    variation = np.ones((poss.shape[0], poss.shape[1])).astype(np.float16)[..., None]

    while running:
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps())}"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            gui.handle_event(event)

            if pygame.mouse.get_pressed()[0]:
                r, c = getGridPosFromMouse()
                if r != None and c != None:
                    for i in range(brushSize.value):
                        for j in range(brushSize.value):
                            x = min(nx - 1, max(0, (i - brushSize.value // 2) + r))
                            y = min(ny - 1, max(0, (j - brushSize.value // 2) + c))
                            states[x, y] = selectedState.value
                            variation[x, y] = (random.random() / 5) + 1

        logic()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()
        if not running: pygame.quit()

if __name__ == "__main__":
    main()
