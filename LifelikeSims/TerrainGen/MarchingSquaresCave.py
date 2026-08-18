import pygame, sys, os
from pygame._sdl2.video import Window
import random, math

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "Cave generator"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

FPS = 60
SIDEBAR = 240
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

shouldAvr = False

def avrBt():
    global shouldAvr
    shouldAvr = not shouldAvr

controlsCard = gui.add_section("Controls")
fps_label = gui.add_label(controlsCard, "FPS: --")
size_sl = gui.add_slider(controlsCard, "Cell size", 4, 100, 60, 1)
threshold_sl = gui.add_slider(controlsCard, "Threshold", 0, 100, 50, 1)
dynamicThresholdUsage = gui.add_checkbox(controlsCard, "Linear interpolation", False)
fill_tg = gui.add_checkbox(controlsCard, "Fill segments", False)
avr_bt = gui.add_button(controlsCard, "Average grid", callback=avrBt)

isCaveGettingGenerated = False

def generateCave():
    global isCaveGettingGenerated
    isCaveGettingGenerated = True

caveGenCard = gui.add_section("Cave generation")
generateCave_bt = gui.add_button(caveGenCard, "Generate cave", callback=generateCave)
stepAmount_sl = gui.add_slider(caveGenCard, "Step amount", 1, 100, 10, 1)
genThreshold_sl = gui.add_slider(caveGenCard, "Gen threshold", 0, 100, 46, 1)
edgeRadius_sl = gui.add_slider(caveGenCard, "Edge radius", 0, 20, 2, 1)

# Globals
prevSize = 0
prevThreshold = 0
prevLerp  = False
prevFill = False
grid = []
lines = []
shapes = []
shouldRedraw = False

def step(oldGrid, birthConditions, surviveConditions):
    newGrid = [[cell[:] for cell in row] for row in oldGrid]
    cellSize = size_sl.value
    edgeRadius = edgeRadius_sl.value
    width = (WIDTH - SIDEBAR - 100) // cellSize - edgeRadius
    height = (HEIGHT -100) // cellSize - edgeRadius
    threshold = genThreshold_sl.value / 100

    # Iterating through all the cells
    for ri, r in enumerate(oldGrid):
        for ci, c in enumerate(r):
            # Checking and counting neighbors
            count = 0
            for x in range(3):
                for y in range(3):
                    if not (x == 1 and y == 1) and edgeRadius <= ri - 1 + x < width and edgeRadius <= ci - 1 + y < height:
                        if oldGrid[ri - 1 + x][ci - 1 + y][2] > threshold:
                            count += 1

            # Applying the ruleset
            if c[2] > threshold:
                shouldLive = False
                for condition in surviveConditions:
                    if count == condition: shouldLive = True
                
                if not shouldLive: 
                    newGrid[ri][ci][2] = -0.1
            elif c[2] < threshold:
                for condition in birthConditions:
                    if count == condition: 
                        newGrid[ri][ci][2] = 1

    return newGrid

def weightedMidpoint(p1, p2, threshold):
    v1 = p1[2]
    v2 = p2[2]
    denom = v2 - v1
    if abs(denom) > 10e-5:
        t = (threshold - v1) / denom
    else:
        t = 0.5
    return [p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])]

def midPoint(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

def drawLines(lines, color, width):
    for l in lines:
        pygame.draw.line(WIN, color, l[0], l[1], width)

def drawShapes(shapes, color):
    for s in shapes:
        points = []
        for p in s:
            points.append((p[0], p[1]))
        pygame.draw.polygon(WIN, color, points)

def marchThem(p1, p2, p3, p4, threshold, dynamic):
    v1 = 1 if p1[2] > threshold else 0
    v2 = 1 if p2[2] > threshold else 0
    v3 = 1 if p3[2] > threshold else 0
    v4 = 1 if p4[2] > threshold else 0

    if dynamic:
        if v1 and not v2 or v2 and not v1: mid12 = weightedMidpoint(p1, p2, threshold)
        if v2 and not v3 or v3 and not v2: mid23 = weightedMidpoint(p2, p3, threshold)
        if v3 and not v4 or v4 and not v3: mid34 = weightedMidpoint(p3, p4, threshold)
        if v4 and not v1 or v1 and not v4: mid14 = weightedMidpoint(p1, p4, threshold)
    else:
        if v1 and not v2 or v2 and not v1: mid12 = midPoint(p1, p2)
        if v2 and not v3 or v3 and not v2: mid23 = midPoint(p2, p3)
        if v3 and not v4 or v4 and not v3: mid34 = midPoint(p3, p4)
        if v4 and not v1 or v1 and not v4: mid14 = midPoint(p1, p4)

    state = v1 * 8 + v2 * 4 + v3 * 2 + v4 * 1

    # The marching squares algorithm is used to generate lines or polygons
    if not fill_tg.value:
        if state == 0: return
        elif state == 1: return [[mid34, mid14]]
        elif state == 2: return [[mid23, mid34]]
        elif state == 3: return [[mid23, mid14]]
        elif state == 4: return [[mid12, mid23]]
        elif state == 5: return [[mid12, mid23], [mid34, mid14]]
        elif state == 6: return [[mid12, mid34]]
        elif state == 7: return [[mid12, mid14]]
        elif state == 8: return [[mid12, mid14]]
        elif state == 9: return [[mid12, mid34]]
        elif state == 10: return [[mid14, mid12], [mid23, mid34]]
        elif state == 11: return [[mid12, mid23]]
        elif state == 12: return [[mid23, mid14]]
        elif state == 13: return [[mid23, mid34]]
        elif state == 14: return [[mid34, mid14]]
        elif state == 15: return
        else: print("Huh? Something is wrong with this state:", state)
    else:
        if state == 0: return
        elif state == 1: return [[mid34, p4, mid14]]
        elif state == 2: return [[mid23, p3, mid34]]
        elif state == 3: return [[mid23, p3, p4, mid14]]
        elif state == 4: return [[mid12, p2, mid23]]
        elif state == 5: return [[mid12, p2, mid23], [mid34, p4, mid14]]
        elif state == 6: return [[mid12, p2, p3, mid34]]
        elif state == 7: return [[mid12, p2, p3, p4, mid14]]
        elif state == 8: return [[mid14, p1, mid12]]
        elif state == 9: return [[mid12, mid34, p4, p1]]
        elif state == 10: return [[mid14, p1, mid12], [mid23, p3, mid34]]
        elif state == 11: return [[p1, mid12, mid23, p3, p4]]
        elif state == 12: return [[mid14, p1, p2, mid23]]
        elif state == 13: return [[p1, p2, mid23, mid34, p4]]
        elif state == 14: return [[p1, p2, p3, mid34, mid14]]
        elif state == 15: return [[p1, p2, p3, p4]]
        else: print("Huh? Something is wrong with this state:", state)

def smoothGrid(grid):
    # Double buffered averaging based function
    newGrid = [[cell[:] for cell in row] for row in grid]
    cellSize = size_sl.value
    edgeRadius = edgeRadius_sl.value * 0
    width = (WIDTH - SIDEBAR - 100) // cellSize - edgeRadius
    height = (HEIGHT -100) // cellSize - edgeRadius
    for ri, r in enumerate(grid):
        for ci, c in enumerate(r):
            avr = 0
            count = 0
            for x in range(3):
                for y in range(3):
                    if edgeRadius <= ri - 1 + x < width and edgeRadius <= ci - 1 + y < height:
                        avr += grid[ri - 1 + x][ci - 1 + y][2]
                        count += 1
            if count != 0:
                avr /= count
                newGrid[ri][ci][2] = avr
            else:
                newGrid[ri][ci][2] = 1
    return newGrid

def logic():
    global grid, prevSize, prevThreshold, prevLerp, prevFill, lines, shapes, isCaveGettingGenerated, shouldAvr, shouldRedraw

    # Avoid unnecessary redraws 
    if prevLerp != dynamicThresholdUsage.value or prevFill != fill_tg.value or prevThreshold != threshold_sl.value or prevSize != size_sl.value or isCaveGettingGenerated or shouldAvr:
        prevLerp  = dynamicThresholdUsage.value
        prevFill = fill_tg.value
        prevThreshold = threshold_sl.value
        shouldRedraw = True

    # Getting the semi centered grid
    cellSize = size_sl.value
    width = (WIDTH - SIDEBAR - 100) // cellSize
    height = (HEIGHT -100) // cellSize

    widthOff = (cellSize * width) // 2 - cellSize//2
    heighOff = (cellSize * height) // 2 - cellSize//2

    widthStart = WIDTH//2 - widthOff + SIDEBAR//2
    heightStart = HEIGHT//2 - heighOff

    # Generating the grid (xpos, ypos, random)
    if prevSize != cellSize or isCaveGettingGenerated:
        prevSize = cellSize
        threshold_sl.value = 50
        grid = []
        for c in range(width + 1):
            grid.append([])
            for r in range(height + 1):
                grid[c].append([widthStart + c * cellSize - cellSize//2, heightStart + r * cellSize - cellSize//2, random.random()])
    
        if isCaveGettingGenerated:
            for i in range(stepAmount_sl.value):
                grid = step(grid, [5, 6, 7, 8], [4, 5, 6, 7, 8])
            for r in grid:
                for c in r:
                    c[2] = 1 - c[2]
            threshold_sl.value = 100 - genThreshold_sl.value
            isCaveGettingGenerated = False

    if shouldAvr:
        grid = smoothGrid(grid)
        shouldAvr = False

    # Regenerating lines or shapes if needed
    if shouldRedraw:
        lines = []
        shapes = []
        threshold = threshold_sl.value / 100
        dynamic = dynamicThresholdUsage.value
        for ri, r in enumerate(grid):
            for ci, c in enumerate(r):
                if ri == len(grid) - 1 or ci == len(r) - 1:
                    continue
                if not fill_tg.value:
                    lines.append(marchThem(c, grid[ri][ci + 1], grid[ri + 1][ci + 1], grid[ri + 1][ci], threshold, dynamic))
                else:
                    shapes.append(marchThem(c, grid[ri][ci + 1], grid[ri + 1][ci + 1], grid[ri + 1][ci], threshold, dynamic))

def drawWin():
    global grid, lines, shapes
    
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    cellSize = size_sl.value
    width = (WIDTH - SIDEBAR - 100) // cellSize
    height = (HEIGHT -100) // cellSize
    threshold = threshold_sl.value

    # Black grid background
    gridRect = pygame.Rect(WIDTH//2 - ((cellSize * width) // 2 - cellSize//2) + SIDEBAR//2 - cellSize//2, HEIGHT//2 - ((cellSize * height) // 2 - cellSize//2) - cellSize//2, cellSize * width, cellSize * height)
    pygame.draw.rect(WIN, "black", gridRect)

    # Drawing cell dots
    if not fill_tg.value:
        for r in grid:
            for c in r:
                if c[2] > threshold/100:
                    if dynamicThresholdUsage.value:
                        size = cellSize//8 * (c[2] - (threshold/100)) / max(10e-2, (1 - (threshold/100)))
                    else:
                        size = cellSize//8
                    size = max(1, size)
                    cell = pygame.Rect(c[0] - size//2, c[1] - size//2, size, size)
                    color = "white"
                    pygame.draw.rect(WIN, color, cell)
    
    # Shapes or lines
    if not fill_tg.value:
        for l in lines:
            if l == None: continue
            drawLines(l, "white", 1)
    else:
        for s in shapes:
            if s == None: continue
            drawShapes(s, (30, 36, 54))


def main():
    global shouldRedraw
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
        if shouldRedraw:
            drawWin()
            shouldRedraw = False
            print("redraw", random.random())
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
