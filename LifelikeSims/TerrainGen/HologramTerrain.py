import pygame, sys, random, math, colorsys
from pygame._sdl2.video import Window

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "Hologram"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

BACKGROUND_COLOR = (30, 36, 54)
FPS = 60
SIDEBAR = 200
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

shouldCross, shouldBlob, shouldReset = False, False, False

def cross():
    global shouldCross
    shouldCross = not shouldCross

def blob():
    global shouldBlob
    shouldBlob = not shouldBlob

def reset():
    global shouldReset
    shouldReset = not shouldReset

gridCard = gui.add_section("Grid controls")
fps_label = gui.add_label(gridCard, "FPS: --")
gridx = gui.add_slider(gridCard, "Lenght", 1, 250, 250, 1)
gridy = gui.add_slider(gridCard, "Width", 1, 250, 250, 1)

displayCard = gui.add_section("Display controls")
size = gui.add_slider(displayCard, "Size", 1, 100, 3, 1)
gridlenx = gui.add_slider(displayCard, "Shear length", 1, 50, 20, 1)
gridleny = gui.add_slider(displayCard, "Shear width", 1, 50, 10, 1)
scroll = gui.add_slider(displayCard, "Scroll speed", -100, 100, 20, 1)
skips = gui.add_slider(displayCard, "Skips", 1, 10, 4, 1)
heightFactor = gui.add_slider(displayCard, "Height factor", 1, 100, 20, 1)
lines = gui.add_checkbox(displayCard, "Show lines", True)

smoothCard = gui.add_section("Smooth controls")
smoothStrength = gui.add_slider(smoothCard, "Strength", 1, 10, 3, 1)
crossBt = gui.add_button(smoothCard, "Cross average", cross)
blobBt = gui.add_button(smoothCard, "Blob average", blob)
resetBt = gui.add_button(smoothCard, "Reset", reset)

colorCard = gui.add_section("Color controls")
hueTop = gui.add_slider(colorCard, "Hue top", 0, 1, 0, 0.01)
# satTop = gui.add_slider(colorCard, "Saturation top", 0, 1, 1, 0.01)
# valTop = gui.add_slider(colorCard, "Value top", 0, 1, 1, 0.01)
hueBot = gui.add_slider(colorCard, "Hue bottom", 0, 1, 0.6, 0.01)
# satBot = gui.add_slider(colorCard, "Saturation bottom", 0, 1, 1, 0.01)
# valBot = gui.add_slider(colorCard, "Value bottom", 0, 1, 1, 0.01)
fullRad = gui.add_slider(colorCard, "Draw radius", 1, 300, 80, 1)
cutRad = gui.add_slider(colorCard, "Cutoff radius", 1, 300, 120, 1)

radarCard = gui.add_section("Radar controls")
radarHue = gui.add_slider(radarCard, "Radar Color", 0, 1, 0.2, 0.01)
radarType = gui.add_slider(radarCard, "Radar type", 0, 3, 1, 1)
radarSpeed = gui.add_slider(radarCard, "Radar speed", -10, 10, 2, 1)
radarSize = gui.add_slider(radarCard, "Radar size", 0.1, 10, 2, 0.1)
radarAmount = gui.add_slider(radarCard, "Radar amount", 0, 10, 1, 1)

# Setting up globals
grid = []
drawnGrid = []
prevx, prevy = 0, 0
angle = 0
xoff, yOff = 0, 0
walk = [0, 0, 0, 0, 0]
radarCycle = 0
maxDist = 0

def getNewGrid():
    global grid, maxDist
    grid = []
    midx, midy = (WIDTH + SIDEBAR) / 2, HEIGHT / 2
    for i in range(gridx.value):
        grid.append([])
        for j in range(gridy.value):
            xOff = i - gridx.value//2 + 0.5 if gridx.value % 2 == 0 else i - gridx.value//2
            yOff = j - gridy.value//2 + 0.5 if gridy.value % 2 == 0 else j - gridy.value//2
            dist = math.hypot(xOff, yOff)
            if dist > maxDist: maxDist = dist
            angle = math.atan2(yOff, xOff) + math.pi
            grid[i].append([midx + xOff, midy + yOff, dist, angle, random.random()])

# Averaging the grid in a plus pattern
def crossAverageGrid():
    global grid
    x = gridx.value
    y = gridy.value
    gridold = grid.copy()
    for i in range(x):
        for j in range(y):
            grid[i][j][-1] = (gridold[(i-1)%x][j][-1] + gridold[(i+1)%x][j][-1] + gridold[i][(j-1)%y][-1] + gridold[i][(j+1)%y][-1]) / 4

# Average across 3x3 area
def blobAverageGrid(): 
    global grid
    x = gridx.value
    y = gridy.value
    oldGrid = grid.copy()
    for i in range(x):
        for j in range(y):
            grid[i][j][-1] = (oldGrid[(i-1)%x][(j-1)%y][-1] + 
                          oldGrid[(i-1)%x][j][-1] + 
                          oldGrid[(i-1)%x][(j+1)%y][-1] +
                          oldGrid[i][(j-1)%y][-1] + 
                          oldGrid[i][j][-1] + 
                          oldGrid[i][(j+1)%y][-1] +
                          oldGrid[(i+1)%x][(j-1)%y][-1] + 
                          oldGrid[(i+1)%x][j][-1] + 
                          oldGrid[(i+1)%x][(j+1)%y][-1]) / 9

# This is just for the sliding terrain effect
def slideGrid(x, y):
    global grid
    newGrid = grid.copy()
    for i in range(gridx.value):
        for j in range(gridy.value):
            if x >= 0:
                newGrid[i][j][-1] = grid[i][j][-1] * (1 - x) + grid[(i+1)%gridx.value][j][-1] * x
            else:
                newGrid[i][j][-1] = grid[i][j][-1] * (-x) + grid[(i-1)%gridx.value][j][-1] * (1 + x)
            if y >= 0:
                newGrid[i][j][-1] = grid[i][j][-1] * (1 - y) + grid[i][(j+1)%gridy.value][-1] * y
            else:
                newGrid[i][j][-1] = grid[i][j][-1] * (-y) + grid[i][(j-1)%gridy.value][-1] * (1 + y)
    grid = newGrid

# Zooming the grid by skipping every nth point
def getZoomed(skips):
    global grid
    newGrid = []
    for i in range(gridx.value//skips):
        newGrid.append([])
        for j in range(gridy.value//skips):
            newGrid[i].append(grid[i*skips][j*skips])
    return newGrid

# Simple vector rotation in order to achieve the 3D rotating effect
def getRotatedPoint(x, y, angle):
    x0 = (x - WIDTH/2 - SIDEBAR/2) * math.sqrt(size.value)
    y0 = (y - HEIGHT/2) * math.sqrt(size.value)
    newx = (x0 * math.cos(angle) - y0 * math.sin(angle)) * gridlenx.value / 10
    newy = (x0 * math.sin(angle) + y0 * math.cos(angle)) * gridleny.value / 10
    return newx + WIDTH/2 + SIDEBAR/2, newy + HEIGHT/2

def rgbToHsv(c):
    r, g, b = c
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return (h, s, v)

def hsvToRgb(c):
    h, s, v = c
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r*255), int(g*255), int(b*255))

def lerpColor(c1, c2, f):
    r = int(max(0, min(255, lerp(c1[0], c2[0], f))))
    g = int(max(0, min(255, lerp(c1[1], c2[1], f))))
    b = int(max(0, min(255, lerp(c1[2], c2[2], f))))
    return r, g, b

def lerp(x1, x2, x):
    return x1 + (x2 - x1) * x

# Wrapping difference finder
def findDiff(pos, width, maxx, minn, value):
    whole = maxx - minn
    diff = whole
    if pos + width > maxx and value <= pos + width - whole:
        diff = min(abs(pos - value - whole), diff)
    if pos - width < minn and value >= whole - pos - width:
        diff = min(abs(pos - value + whole), diff)
    diff = min(abs(pos - value), diff)
    return diff

def logic():
    global prevx, prevy, shouldReset, shouldCross, shouldBlob
    if gridx.value != prevx or gridy.value != prevy or shouldReset:
        getNewGrid()
        for i in range(30): blobAverageGrid()
        prevx, prevy, shouldReset = gridx.value, gridy.value, False
    if shouldCross:
        for i in range(smoothStrength.value): crossAverageGrid()
        shouldCross = False
    if shouldBlob:
        for i in range(smoothStrength.value): blobAverageGrid()
        shouldBlob = False

def drawWin():
    global grid, angle, xoff, yOff, walk, radarCycle, maxDist
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill(BACKGROUND_COLOR, canvas)
    maxHeight = max([max([p[-1] for p in r]) for r in grid])
    minHeight = min([min([p[-1] for p in r]) for r in grid])
    for r in grid:
        for p in r:
            p[-1] -= minHeight

    zoomed = getZoomed(skips.value)
    points = zoomed.copy()
    for ri, r in enumerate(zoomed):
        for pi, p in enumerate(r):
            # Rotating, applying height and coloring based on height
            x, y = getRotatedPoint(p[0], p[1], math.radians(angle))
            h = grid[(ri * skips.value + round(xoff)) % gridx.value][(pi * skips.value + round(yOff)) % gridy.value][-1]
            height = h * math.sqrt(size.value) * heightFactor.value**2
            heightrate = (h - minHeight) / (maxHeight - minHeight)
            oneColor = lerp(0, 1, heightrate)
            rt, gt, bt = hsvToRgb((hueTop.value, 1, 1))
            rb, gb, bb = hsvToRgb((hueBot.value, 1, 1))
            mixedColor = (lerpColor((rt, gt, bt), (rb, gb, bb), oneColor))

            # Applying radar
            radarColor = hsvToRgb((radarHue.value, 1, 1))
            radars = radarAmount.value
            if radarType.value == 1: # Sweep
                localSize = radarSize.value
                diff = len(points)
                for i in range(radars):
                    pos = (((radarCycle % gridx.value) + (gridx.value / radars * (i+1))) % gridx.value) * (len(zoomed) / len(grid))
                    diff = min(diff, findDiff(pos, localSize, len(points), 0, ri))

                if diff <= localSize:
                    rate = 1 - (diff / localSize)
                    mixedColor = (lerpColor(mixedColor, radarColor, rate))
            elif radarType.value == 2: # Expanding circle
                localSize = radarSize.value * 2
                diff = maxDist
                for i in range(radars):
                    pos = ((radarCycle % maxDist) + (maxDist / radars * (i+1))) % maxDist
                    diff = min(diff, findDiff(pos, localSize, maxDist, 0, p[2]))

                if diff <= localSize:
                    rate = (localSize - diff) / localSize
                    mixedColor = (lerpColor(mixedColor, radarColor, rate))  
            elif radarType.value == 3: # Radar circle
                localSize = radarSize.value / 10
                diff = 2*math.pi
                for i in range(radars):
                    pos = (((radarCycle / 10) % (2*math.pi)) + (2*math.pi / radars * (i+1))) % (2*math.pi)
                    diff = min(diff, findDiff(pos, localSize, 2*math.pi, 0, p[3]))

                if diff <= localSize:
                    rate = min(1, (localSize - diff) / localSize)
                    mixedColor = (lerpColor(mixedColor, radarColor, rate))
            elif radarType.value == 0:
                pass

            # Fading out the colors
            if cutRad.value != fullRad.value:
                radiusFactor = min(max(((p[2] - fullRad.value) / (cutRad.value - fullRad.value)), 0), 1)
            else:
                radiusFactor = 1
            color = lerpColor(mixedColor, BACKGROUND_COLOR, radiusFactor)
            if lines.value:
                points[ri][pi] = (x, y - height + 100, color)
            else:
                pygame.draw.circle(WIN, color, (x, y - height + 100), 3)
    if lines.value:
        for ri, r in enumerate(points):
            for pi, p in enumerate(r):
                if ri != len(points)-1 and pi != len(r)-1:
                    pygame.draw.line(WIN, lerpColor(p[2], r[pi + 1][2], 0.5), (p[0], p[1]), (r[pi + 1][0], r[pi + 1][1]), 1)
                    pygame.draw.line(WIN, lerpColor(p[2], points[ri+1][pi][2], 0.5), (p[0], p[1]), (points[ri+1][pi][0], points[ri+1][pi][1]), 1)
                if ri == len(points)-1 and pi != len(r)-1: pygame.draw.line(WIN, lerpColor(p[2], r[pi + 1][2], 0.5), (p[0], p[1]), (r[pi + 1][0], r[pi + 1][1]), 1)
                if pi == len(r)-1 and ri != len(points)-1: pygame.draw.line(WIN, lerpColor(p[2], points[ri + 1][pi][2], 0.5), (p[0], p[1]), (points[ri + 1][pi][0], points[ri + 1][pi][1]), 1)


    angle += 0.1

    # if walk[4] == 0:
    #     walkangle = random.randrange(0, 360)
    #     walk[0] = math.cos(math.radians(walkangle))
    #     walk[1] = math.sin(math.radians(walkangle))
    #     walk[4] = 10
    # else:
    #     walk[4] -= 1
    #     walk[2] = min(walk[2] + walk[0] * 2, walk[0] * 2) if walk[0] > 0 else max(-1 * (walk[2] - walk[0] * 2), -walk[0] * 2)
    #     walk[3] = min(walk[3] + walk[1] * 2, walk[1] * 2) if walk[1] > 0 else max(-1 * (walk[3] - walk[1] * 2), -walk[1] * 2)

    xoff += scroll.value / 100 # * walk[2]
    yOff += scroll.value / 100 # * walk[3]
    radarCycle += radarSpeed.value / 5

def main():
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
        
        logic()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main() 
