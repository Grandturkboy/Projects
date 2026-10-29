import pygame, sys, numpy as np, random
from pygame._sdl2.video import Window

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "1D cellular automata"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

FPS = 60
SIDEBAR = 200
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)
PALETTE = np.array([[0, 0, 0], [150, 150, 150]])

shouldRestart = False
shouldClear = True
shouldRandomize = False

def restart():
    global shouldRestart
    shouldRestart = True

def clear():
    global shouldClear
    shouldClear = True

def randomize():
    global shouldRandomize
    shouldRandomize = True

gridCard = gui.add_section("Controls")
fps_label = gui.add_label(gridCard, "FPS: --")
xratio = gui.add_slider(gridCard, "X ratio", 0.01, 1, 1, 0.01)
yratio = gui.add_slider(gridCard, "Y ratio", 0.01, 1, 1, 0.01)
size = gui.add_slider(gridCard, "Cell size", 1, 10, 1, 1)
padding = gui.add_slider(gridCard, "Padding", 0, 25, 0, 1)

simCard = gui.add_section("Simulation")
speed = gui.add_slider(simCard, "Speed", 0, 100, 0, 1)
showActive = gui.add_checkbox(simCard, "Show active", False)
restartBt = gui.add_button(simCard, "Restart", callback=restart)
clearBt = gui.add_button(simCard, "Clear", callback=clear)
testRule = gui.add_checkbox(simCard, "Test rule", True)

rulesetCard = gui.add_section("Rule controls")
randomizeBt = gui.add_button(rulesetCard, "Randomize", callback=randomize)
case1 = gui.add_checkbox(rulesetCard, "0 0 0", True)
case2 = gui.add_checkbox(rulesetCard, "1 0 0", True)
case3 = gui.add_checkbox(rulesetCard, "0 1 0", True)
case4 = gui.add_checkbox(rulesetCard, "1 1 0", True)
case5 = gui.add_checkbox(rulesetCard, "0 0 1", True)
case6 = gui.add_checkbox(rulesetCard, "1 0 1", True)
case7 = gui.add_checkbox(rulesetCard, "0 1 1", True)
case8 = gui.add_checkbox(rulesetCard, "1 1 1", True)

# Setting up globals
prevx, prevy, prevs, prevp = 0, 0, 0, 0
poss = None
alives = None
nx, ny = 0, 0
prevActive = 0
active = 0
walk = 0
clicked = []
ruleset = []
prevRow = None
runtilend = False

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

    # poss = np.zeros((nx, ny, 2), dtype=int)
    # for i in range(nx):
    #     for j in range(ny):
    #         poss[i, j] = (startx + i * s, starty - j * s)
    
    i = np.arange(nx)[:, None]
    j = np.arange(ny)[None, :]
    poss = np.empty((nx, ny, 2), dtype=int)
    poss[..., 0] = startx + i * s
    poss[..., 1] = starty - j * s

    return poss

# Getting next step
def iterate():
    global alives, poss, prevRow
    selectedRow = alives[:, active]
    octogonal = np.roll(selectedRow, 1, 0) + selectedRow * 2 + np.roll(selectedRow, -1, 0) * 4
    boolian = ruleset[octogonal.astype(int)]
    alives[:,(active - 1) % alives.shape[1]] = boolian

def getGridPosFromMouse():
    mouseX, mouseY = pygame.mouse.get_pos()
    s = size.value
    startX = SIDEBAR + (WIDTH - SIDEBAR) / 2 - (s * nx) / 2

    xIn = mouseX - startX
    xind = int(xIn // s)
    yind = (active - 1) % alives.shape[1]

    if xind < 0 or xind >= nx or yind < 0 or yind >= ny:
        return None, None
    else:
        return xind, yind

def logic():
    global poss, alives, active, prevActive, walk

    global prevx, prevy, prevs, prevp, ruleset, shouldRandomize, runtilend
    if shouldRandomize:
        for i in range(8): 
            choosen = random.choice([True, False])
            exec(f"case{i + 1}.value = {choosen}")
        shouldRandomize = False
        runtilend = True

    ruleset = np.array([case1.value, case2.value, case3.value, case4.value, case5.value, case6.value, case7.value, case8.value])

    if xratio.value != prevx or yratio.value != prevy or size.value != prevs or padding.value != prevp:
        prevx, prevy, prevs, prevp = xratio.value, yratio.value, size.value, padding.value
        poss = getnewGrid()
        alives = np.zeros((poss.shape[0], poss.shape[1]))
        alives[:, -1] = np.random.randint(0, 2, (poss.shape[0]))

    global shouldRestart, shouldClear
    if shouldRestart or shouldClear:
        walk = 0; prevActive = 0; active = 0
        alives = np.zeros((poss.shape[0], poss.shape[1]))
        if shouldRestart: alives[:, -1] = np.random.randint(0, 2, (poss.shape[0]))
        shouldRestart = False
        shouldClear = False
    if runtilend:
        active = -1
        while active >= -alives.shape[1] + 1:
            iterate()
            active -= 1
        walk = 0; prevActive = 0; active = 0
        runtilend = False

    walk -= speed.value
    active = int((walk / 100) % poss.shape[1])
    if active != prevActive:
        prevActive = active
        iterate()

def drawWin():
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    # for ind in np.ndindex(alives.shape):
    #     pos = poss[ind[0], ind[1]]
    #     color = (0, 0, 0) if alives[ind[0], ind[1]] == 0 or alives[ind[0], ind[1]] == False else (255, 255, 255)
    #     pygame.draw.rect(WIN, color, (pos[0], pos[1], size.value, size.value))

    # Optimized rendering: creating a surface using numpy array (so we dont have to draw all the squares individually)
    s = int(size.value)
    img = np.where(alives > 0, 1, 0).astype(np.uint8)
    rgb = PALETTE[img][:, ::-1]
    surf = pygame.surfarray.make_surface(rgb)
    surf = pygame.transform.scale(surf, (nx * s, ny * s))
    WIN.blit(surf, (poss[0, 0, 0], poss[0, ny - 1, 1]))

    if showActive.value:
        s = size.value
        startx, starty = poss[0, (active - 1) % alives.shape[1]]
        pygame.draw.rect(WIN, (255, 0, 0), (startx, starty, s * nx, s), 1)

def main():
    global poss, alives, ruleset, clicked, prevRow, runtilend
    clock = pygame.time.Clock()
    running = True

    poss = getnewGrid()
    alives = np.random.randint(0, 2, (poss.shape[0], poss.shape[1]))
    ruleset = [case1.value, case2.value, case3.value, case4.value, case5.value, case6.value, case7.value, case8.value]
    
    while running:
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps())}"
        
        prevRow = alives[:, (active - 1) % alives.shape[1]].copy()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            gui.handle_event(event)

            if pygame.mouse.get_pressed()[0]:
                r, c = getGridPosFromMouse()
                if (r, c) not in clicked:
                    if c != None and r != None:
                        if alives[r, c] == 1 or alives[r, c] == True:
                            alives[r, c] = False
                        else:
                            alives[r, c] = True
                        clicked.append((r, c))
                else:
                    pass
            else:
                clicked = []

        if not np.array_equal(prevRow, alives[:, (active - 1) % alives.shape[1]]) and testRule.value:
            runtilend = True
            prevRow = alives[:, (active - 1) % alives.shape[1]]

        logic()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()
        if not running: pygame.quit()

if __name__ == "__main__":
    main()
