import pygame, sys, os
from pygame._sdl2.video import Window
import random, math, time

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Used code:
    # cave generation: from 2d cellular automata
    # linear interpolation and terrain gen: from marching squares
    # collision logic: modified from ballPit engine
    # intersection finding and projection logic: From line intersection
    # legs: from inverse kinematics

# New systems:
    # Linear interpolation
    # Custom movement system
    # Custom camera system
    # Foolproof and fast collision detection
    # Dynamic web wrap and unwrap system

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "Webbed"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

FPS = 60
SIDEBAR = 240
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

displaysCard = gui.add_section("Display controls")
fps_label = gui.add_label(displaysCard, "FPS: --")
size_sl = gui.add_slider(displaysCard, "Cell size", 1, 100, 14, 1)
threshold_sl = gui.add_slider(displaysCard, "Threshold", 0, 100, 50, 0.1)
dynamicThresholdUsage = gui.add_checkbox(displaysCard, "Linear interpolation", True)
fill_tg = gui.add_checkbox(displaysCard, "Fill segments", False)

shouldAvr = True
isCaveGettingGenerated = True

def avrBt():
    global shouldAvr
    shouldAvr = True

def generateCave():
    global isCaveGettingGenerated, shouldAvr
    isCaveGettingGenerated = True
    shouldAvr = True

cameraCard = gui.add_section("Camera")
zoom_sl = gui.add_slider(cameraCard, "Zoom", 0.1, 20, 1, 0.1)
xCamOff_sl = gui.add_slider(cameraCard, "X offset", -10000, 10000, 0, 0.1)
yCamOff_sl = gui.add_slider(cameraCard, "Y offset", -10000, 10000, 0, 0.1)
useCam_cb = gui.add_checkbox(cameraCard, "Use camera", True)

webCard = gui.add_section("Web controls")
webRange_sl = gui.add_slider(webCard, "Web range", 0, 1000, 400, 1)
webForce_sl = gui.add_slider(webCard, "Web force", 0, 10, 5, 0.01)

phyCard = gui.add_section("Physics")
ballSize_sl = gui.add_slider(phyCard, "Ball size", 0.1, 20, 8, 0.1)
elas_sl = gui.add_slider(phyCard, "Elasticity", 0, 1, 0.2, 0.01)
fric_sl = gui.add_slider(phyCard, "Friction", 0, 1, 0.9, 0.01)
steps_sl = gui.add_slider(phyCard, "Num of phy steps", 0, 10, 1, 1)
inside_cb = gui.add_checkbox(phyCard, "Check for inside", True)
dirty_cb = gui.add_checkbox(phyCard, "Check for line crossing", True)

caveGenCard = gui.add_section("Cave generation")
generateCave_bt = gui.add_button(caveGenCard, "Generate cave", callback=generateCave)
avr_bt = gui.add_button(caveGenCard, "Average grid", callback=avrBt)

debugCard = gui.add_section("Debug visuals")
bare_cb = gui.add_checkbox(debugCard, "Show barebones body", False)
webUI_cb = gui.add_checkbox(debugCard, "Show web debug", False)
showState_cb = gui.add_checkbox(debugCard, "Show state", False)
showCollision_cb = gui.add_checkbox(debugCard, "Show collisions", False)
showCam_cb = gui.add_checkbox(debugCard, "Show cam points", False)
showVel_cb = gui.add_checkbox(debugCard, "Show velocity", False)
showLeg_cb = gui.add_checkbox(debugCard, "Show leg UI", False)

# Globals (fuck thats way too much)
prevSize = 0
prevThreshold = 0
prevLerp  = False
prevFill = False
prevZoom = 0
prevXOff = 0
prevYOff = 0
grid = []
lines = []
shapes = []
neighbors = []
projections = []
collisions = []
shouldRedraw = True
widthStart = 0
heightStart = 0
webTiles = []
webCollisions = []
webSegmentsForGrid = []

prevMouse = (0, 0)

class Player():
    def __init__(self):
        self.x = (WIDTH + SIDEBAR) / 2
        self.y = HEIGHT / 2
        self.px = 0
        self.py = 0
        self.sx = 0
        self.sy = 0
        self.xv = 0
        self.yv = 0
        self.acc = 0.2

        self.isGrounded = False
        self.canControl = False
        self.isGoingLorR = False
        self.isJumping = False
        self.stoppedHoldingSpace = True
        self.stoppedHoldingLeft = True

        self.isGrappling = False
        self.isActivelyGrappled = False
        self.grappleX = 0
        self.grappleY = 0
        self.webSegments = []
        self.webExtensionProgress = 0
        self.webExtensionState = 0

        self.legPivots = []
        self.legJoints = []
        self.legGoal = []
        self.legSmoothEnd = []
        self.legStepState = 0
        self.bodyAngleGoal = 0
        self.bodyAngle = 0
        self.homeAnglePatience = 30
        self.lookAngle = 0
        self.lookDist = 0

        for i in range(8):
            self.legJoints.append([0,0])
            self.legSmoothEnd.append([0,0])

    def respawn(self):
        if inside_cb.value:
            self.x = (WIDTH + SIDEBAR) / 2 + random.randint(-400, 400)
            self.y = HEIGHT / 2 + random.randint(-400, 400)
            self.xv = 0
            self.yv = 0

spider = Player()

def worldToScreen(zoom, xOff, yOff, wx, wy):
    sx = (wx - xOff) * zoom + (WIDTH + SIDEBAR) / 2
    sy = (wy - yOff) * zoom + HEIGHT / 2
    return sx, sy

def screenToWorld(zoom, xOff, yOff, sx, sy):
    wx = (sx - (WIDTH + SIDEBAR) / 2) / zoom + xOff
    wy = (sy - HEIGHT / 2) / zoom + yOff
    return wx, wy

def calculateCollision(cp, elas, fric, radius, dist=None):
    if dist == None: dist = max(math.hypot(cp[0] - spider.x, cp[1] - spider.y), 10e-4) # Avoid zero division
    dx = cp[0] - spider.x
    dy = cp[1] - spider.y

    nx = dx / dist # Normalized vector
    ny = dy / dist
    tx = -ny # Tangent vector (normal => perp to n)
    ty = nx

    nv = spider.xv * nx + spider.yv * ny # Normal dot
    tv = spider.xv * tx + spider.yv * ty # Tangent dot
    
    nv *= -elas # Applying physics
    tv *= fric
    
    xv = nv * nx + tv * tx # New velocities
    yv = nv * ny + tv * ty
    
    overlap = radius - dist
    x = min(nx * overlap, radius) # Clamped overlap correction
    y = min(ny * overlap, radius)

    return x, y, xv, yv

def resolveCollisions(elas, fric, radius):
    global collisions # Applying the collision with the closest coll point
    if collisions:
        collisions.sort(key=lambda x: x[1])
        collPoint = collisions[0][0]
        dist = max(collisions[0][1], 10e-4)

        x, y, xv, yv = calculateCollision(collPoint, elas, fric, radius, dist)
        spider.xv = xv
        spider.yv = yv
        spider.x -= x
        spider.y -= y

def findIntersection(l1, l2):
    x1 = l1[0][0]
    y1 = l1[0][1]
    x2 = l1[1][0]
    y2 = l1[1][1]
    x3 = l2[0][0]
    y3 = l2[0][1]
    x4 = l2[1][0]
    y4 = l2[1][1]

    d1x = x2 - x1
    d1y = y2 - y1
    d2x = x4 - x3
    d2y = y4 - y3

    denom = d1x * d2y - d1y * d2x

    if denom == 0: # If the lines are parallel
        return None
    
    iScalar1 = ((x3 - x1) * d2y - (y3 - y1) * d2x) / denom
    iScalar2 = ((x3 - x1) * d1y - (y3 - y1) * d1x) / denom

    if iScalar1 >= 0 and iScalar1 <= 1 and iScalar2 >= 0 and iScalar2 <= 1:
        ix = x1 + d1x * iScalar1
        iy = y1 + d1y * iScalar1
        return ix, iy
    
    return None

def project(p, l):
    x1 = p[0]
    y1 = p[1]
    
    lx1 = l[0][0]
    ly1 = l[0][1]
    lx2 = l[1][0]
    ly2 = l[1][1]

    edgeX = lx2 - lx1
    edgeY = ly2 - ly1

    pointX = x1 - lx1
    pointY = y1 - ly1

    dot = pointX * edgeX + pointY * edgeY
    sqLen = edgeX * edgeX + edgeY * edgeY

    if sqLen == 0: sqLen = 10e-3 
    t = min(1, max(0, dot / sqLen))

    closestX = lx1 + t * edgeX
    closestY = ly1 + t * edgeY

    return closestX, closestY

def step(oldGrid, birthConditions, surviveConditions):
    newGrid = [[cell[:] for cell in row] for row in oldGrid] # Double buffer
    cellSize = size_sl.value
    edgeRadius = 2
    width = (WIDTH - SIDEBAR - 100) // cellSize - edgeRadius
    height = (HEIGHT -100) // cellSize - edgeRadius
    threshold = 46 / 100

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
    return [p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])] # The algorithm of linear interpolation

def midPoint(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

def drawLines(lines, color, width, zoom, xOff, yOff):
    for l in lines:
        sx1, sy1 = worldToScreen(zoom, xOff, yOff, l[0][0], l[0][1])
        sx2, sy2 = worldToScreen(zoom, xOff, yOff, l[1][0], l[1][1])
        pygame.draw.line(WIN, color, [sx1, sy1], [sx2, sy2], width)

def drawShape(shape, color, zoom, xOff, yOff):
    for s in shape:
        points = []
        for p in s:
            px, py = worldToScreen(zoom, xOff, yOff, p[0], p[1])
            points.append((px, py))
        pygame.draw.polygon(WIN, color, points)

def drawLinesFromPoints(points, color, width, zoom, xOff, yOff, extension):
    if extension <= 0: return
    segs = []
    totalLen = 0
    for i in range(len(points) - 1):
        sx1, sy1 = worldToScreen(zoom, xOff, yOff, points[i][0], points[i][1])
        sx2, sy2 = worldToScreen(zoom, xOff, yOff, points[i + 1][0], points[i + 1][1])
        segLen = math.hypot(sx2 - sx1, sy2 - sy1)
        segs.append([[sx1, sy1], [sx2, sy2], segLen])
        totalLen += segLen

    segs = segs[::-1]
    targetLen = totalLen * min(extension,100) / 100
    progress = 0
    for seg in segs:
        if progress + seg[2] <= targetLen:
            pygame.draw.line(WIN, color, seg[0], seg[1], width)
            progress += seg[2]
        else:
            remaining = targetLen - progress
            if remaining <= 0: break
            dv = pygame.Vector2(seg[0][0] - seg[1][0], seg[0][1] - seg[1][1])
            if dv.length() > 0:
                dv.scale_to_length(remaining)
                pygame.draw.line(WIN, color, seg[1], [seg[1][0] + dv.x, seg[1][1] + dv.y], width)
            break
    return totalLen

def marchThem(p1, p2, p3, p4, threshold, dynamic, fill=False):

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
    if not fill:
        if state == 0: return False
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
        elif state == 15: return True
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
    edgeRadius = 0
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

def getGridPos(trueWstart, trueHstart, x, y, cellSize):
    r = round((x - trueWstart) // cellSize)
    c = round((y - trueHstart) // cellSize)

    return r, c

def getNeighbors(totalRange, r, c):
    global lines # Looks though the grid, find all the lines that are within range of the indexes given
    width = len(lines)
    height = len(lines[0])
    neighbors = []
    lookRange = (totalRange-1)//2
    for x in range(totalRange):
        for y in range(totalRange):
            if 0 <= r - lookRange + x < width and 0 <= c - lookRange + y < height:
                try:
                    if lines[r - lookRange + x][c - lookRange + y] == None or lines[r - lookRange + x][c - lookRange + y] == True or lines[r - lookRange + x][c - lookRange + y] == False:
                        continue
                    for l in lines[r - lookRange + x][c - lookRange + y]:
                        neighbors.append(l)
                except IndexError:
                    pass
    
    return neighbors

def intersectionWithTerrain(line, v, cellSize, trueWstart, trueHstart, width, height, grappleRange):
        global lines, webTiles, webSegmentsForGrid, webCollisions
        webTiles = []
        webSegmentsForGrid = []
        lenPoints = round(grappleRange // (cellSize*math.sqrt(2))) * 2

        for i in range(lenPoints): # Distributing points along the view line and finding their distinct indexes
            x = spider.x + v.x * i / lenPoints
            y = spider.y + v.y * i / lenPoints
            webSegmentsForGrid.append([x, y])
            r, c = getGridPos(trueWstart, trueHstart, x, y, cellSize)
            if not [r, c] in webTiles and 0 <= r < width and 0 <= c < height:
                webTiles.append([r, c])

        # Get collision points
        webCollisions = []
        for p in webTiles:
            liness = getNeighbors(3, p[0], p[1])
            if liness == None or liness == True or liness == False or liness == []: continue
            for l in liness:
                cp = findIntersection(l, line)
                if cp != None:
                    dist = math.hypot(cp[0] - spider.x, cp[1] - spider.y)
                    if not [cp, dist] in webCollisions: webCollisions.append([cp, dist])
        return webCollisions

def getJoint(p1, p2, l, pol):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    d = math.hypot(dx, dy)
    if d == 0:
        d = 1
    mid_len = (d**2) / (2 * d)
    h = math.sqrt(max(0, l**2 - mid_len**2))
    mx = p2[0] + mid_len * (dx / d)
    my = p2[1] + mid_len * (dy / d)
    if pol == 1:
        x = mx + h * (-dy / d)
        y = my + h * (dx / d)
    if pol == -1:
        x = mx - h * (-dy / d)
        y = my - h * (dx / d)
    return x, y

def handlePlayer():
    global widthStart, heightStart, lines, neighbors, projections, collisions
    cellSize = size_sl.value
    width = (WIDTH - SIDEBAR - 100) // cellSize
    height = (HEIGHT -100) // cellSize
    trueWstart = widthStart - cellSize/2
    trueHstart = heightStart - cellSize/2
    radius = ballSize_sl.value * cellSize/20
    zoom = zoom_sl.value
    xOff = xCamOff_sl.value
    yOff = yCamOff_sl.value
    spider.px, spider.py = spider.x, spider.y

    # Physics constants
    damping = 0.99
    gravity = 0.2
    elasticity = 0
    friction = 0.9

    # Reading mouse input for webbing
    mouseIn = pygame.mouse.get_pressed()
    if mouseIn[0]:
        spider.isGrappling = True
        spider.y -= gravity
        spider.isJumping = False
    else:
        spider.isGrappling = False
        spider.isActivelyGrappled = False

    # Web swinging detection
    mousePos = pygame.mouse.get_pos()
    grappleRange = webRange_sl.value
    if spider.isGrappling and not spider.isActivelyGrappled:
        # Get mouse position
        worldMousePosX, worldMousePosY = screenToWorld(zoom, xOff, yOff, mousePos[0], mousePos[1])
        # Get web vector and line
        dv = pygame.Vector2(worldMousePosX - spider.x, worldMousePosY - spider.y)
        dv.scale_to_length(grappleRange)
        webLine = [[spider.x, spider.y], [spider.x + dv.x, spider.y + dv.y]]
        
        # Get collisions
        webCollisions = intersectionWithTerrain(webLine, dv, cellSize, trueWstart, trueHstart, width, height, grappleRange)

        # Select closest collision point
        if webCollisions:
            webCollisions.sort(key=lambda x: x[1])
            spider.isActivelyGrappled = True
            spider.grappleX, spider.grappleY = webCollisions[0][0]

    if spider.isActivelyGrappled:
        # Get mouse position
        mousePos = pygame.mouse.get_pos()
        worldMousePosX, worldMousePosY = screenToWorld(zoom, xOff, yOff, mousePos[0], mousePos[1])
        # Get web vector and line
        dv = pygame.Vector2(spider.grappleX - spider.x, spider.grappleY - spider.y)
        webLine = [[spider.x, spider.y], [spider.grappleX, spider.grappleY]]

        # Get collisions
        webCollisions = intersectionWithTerrain(webLine, dv, cellSize, trueWstart, trueHstart, width, height, grappleRange)

        # Select the point farthest from the spider (the one that should create a new pivot since its wrapping around the terrain)
        if webCollisions:
            webCollisions.sort(key=lambda x: x[1])
            if len(webCollisions) > 1:
                spider.webSegments.append([spider.grappleX, spider.grappleY])
            spider.grappleX, spider.grappleY = webCollisions[0][-2]

        # Unwrap logic
        ignorePatience = 10e-2
        if spider.webSegments:
            dv = pygame.Vector2(spider.webSegments[-1][0] - spider.x, spider.webSegments[-1][1] - spider.y)
            secWebLine = [[spider.x, spider.y], [spider.webSegments[-1][0], spider.webSegments[-1][1]]]
            secondaryWebColl = intersectionWithTerrain(secWebLine, dv, cellSize, trueWstart, trueHstart, width, height, grappleRange)
            # Remove glitched collision points (this is needed to avoid getting the web stuck in terrain (also results in being able to ignore smaller bits or terrain))
            if secondaryWebColl:
                for p in secondaryWebColl:
                    dx = p[0][0] - spider.webSegments[-1][0]
                    dy = p[0][1] - spider.webSegments[-1][1]
                    if dx**2 + dy**2 < ignorePatience**2:
                        secondaryWebColl.remove(p)
            # If no secondary collisions, we can unwrap
            if not secondaryWebColl:
                spider.grappleX, spider.grappleY = spider.webSegments[-1]
                spider.webSegments.pop()

    if spider.webExtensionState == 0:
        spider.webSegments = []

    # Handling player input (deceleration faster than acceleration for better movement control)
    decelerationMult = 3
    airControlMult = 0.3
    # Less control while flying
    if spider.canControl:
        activeAcc = spider.acc
    else:
        activeAcc = spider.acc * airControlMult


    spider.isGoingLorR = False
    keys = pygame.key.get_pressed()

    # Manual respawn(needed because the prevPos based collision resolution rarely causes a softlock)
    if keys[pygame.K_r]:
        spider.respawn()

    if keys[pygame.K_a]:
        if spider.x > trueWstart + radius:
            spider.isGoingLorR = True
            if spider.xv > 10e-3:
                spider.xv -= activeAcc * decelerationMult
                spider.xv = max(spider.xv, 0)
            else:
                spider.xv -= activeAcc

    if keys[pygame.K_d]:
        if spider.x < trueWstart + width*cellSize - radius:
            spider.isGoingLorR = True
            if spider.xv < -10e-3:
                spider.xv += activeAcc * decelerationMult
                spider.xv = min(spider.xv, 0)
            else:
                spider.xv += activeAcc

    # Jumping logic (extremely stupid input reading, but has jump buffer and variable jump height)
    if keys[pygame.K_SPACE]:
        if spider.canControl and spider.stoppedHoldingSpace:
            spider.stoppedHoldingSpace = False
            spider.isJumping = True
            spider.y -= gravity + 10e-3
            spider.yv -= 7
    else:
        spider.stoppedHoldingSpace = True
        if spider.isJumping:
            spider.yv *= 0.5
    if spider.isJumping and spider.yv > 0:
        spider.isJumping = False

    # Adding web force
    if spider.webExtensionState == 2:
        force = webForce_sl.value / 10
        dv = pygame.Vector2(spider.grappleX - spider.x, spider.grappleY - spider.y)
        dv = dv.normalize()
        spider.xv += dv.x * force
        spider.yv += dv.y * force

    # Border detection and resolution
    if spider.x < trueWstart + radius and spider.xv < 0:
        spider.x = trueWstart + radius
        spider.xv *= -elasticity
    elif spider.x > trueWstart + width*cellSize - radius and spider.xv > 0:
        spider.x = trueWstart + width*cellSize - radius
        spider.xv *= -elasticity
    if spider.y < trueHstart + radius and spider.yv < 0:
        spider.y = trueHstart + radius - 10e-2
        spider.yv *= -elasticity
        if not spider.isGoingLorR: spider.xv *= friction
    elif spider.y > trueHstart + height*cellSize - radius and spider.yv > 0:
        spider.y = trueHstart + height*cellSize - radius
        spider.yv *= -elasticity
        if not spider.isGoingLorR: spider.xv *= friction
    
    # Inside terrain check (if inside, respawn)
    inside = True
    while inside:
        r, c = getGridPos(trueWstart, trueHstart, spider.x, spider.y, cellSize)
        try:
            if lines[r][c] == True:
                spider.respawn()
                inside = False
            else:
                inside = False
        except IndexError:
            spider.respawn()
            inside = False

    elas = elas_sl.value
    fric = fric_sl.value
    steps = steps_sl.value

    neighbors = getNeighbors(5, r, c)
    for _ in range(steps):
        # Projecting point upon neighbors
        projections.clear()
        for n in neighbors:
            px, py = project([spider.x, spider.y], n)
            projections.append([px, py])
            collisions.clear()

        # Checking whether projection is inside the spider (gives collision points and spider state)
        spider.isGrounded = False
        spider.canControl = False
        groundAcceptance = 0.71
        for p in projections:
            dx = p[0] - spider.x
            dy = p[1] - spider.y
            dist = math.hypot(dx, dy)
            if dist < radius:
                collisions.append([p, dist])
                if dy > 0:
                    spider.canControl = True
                    if abs(dx) < radius * groundAcceptance:
                        spider.isGrounded = True

        # Changing elasticity and friction based on the state
        elas = 1 - ((1-elas) / steps)
        fric = 1 - ((1-fric) / steps)

        if spider.isGrounded and not spider.isGoingLorR:
            elas = 0
            fric = 0.3
        elif spider.isGrounded and spider.isGoingLorR:
            elas = 0
            fric = 1
        
        if spider.isGoingLorR: fric = 1

        resolveCollisions(elas, fric, radius)

    # Euler integration
    maxSpeed = radius / 3 if spider.isGoingLorR and spider.canControl else radius * 10
    spider.yv += gravity * 10e-4 if spider.isGrounded else gravity
    spider.xv *= damping
    spider.yv *= damping

    spider.xv = max(-maxSpeed, min(maxSpeed, spider.xv))
    spider.yv = max(-maxSpeed, min(maxSpeed, spider.yv))

    spider.x += spider.xv # * 60 * delta
    spider.y += spider.yv # * 60 * delta

    # Checking whether the ball has passed through the terrain (we check if the line connecting the previous and current pos intersects the terrain)
    if dirty_cb.value:
        posLine = [[spider.px, spider.py],  [spider.x, spider.y]]
        for l in neighbors:
            cp = findIntersection(posLine, l)
            if cp != None:
                x, y, xv, yv = calculateCollision(cp, elas, fric, radius * 2)
                spider.xv = xv
                spider.yv = yv
                spider.x = spider.px
                spider.y = spider.py
                break

    # Calculating leg and body positions
    worldMouse = screenToWorld(zoom, xOff, yOff, mousePos[0], mousePos[1])
    dx = worldMouse[0] - spider.x
    dy = worldMouse[1] - spider.y
    spider.lookAngle = math.atan2(dy, dx)
    spider.lookDist = math.hypot(dx, dy)

def logic():
    global grid, prevSize, prevThreshold, prevLerp, prevFill, lines, shapes, isCaveGettingGenerated, shouldAvr, shouldRedraw, prevZoom, prevXOff, prevYOff, prevMouse, widthStart, heightStart

    # Setting up cam offset based on mouse and spider pos (smoothed)
    mousePos = pygame.mouse.get_pos()
    newMouseStrength = 0.05
    newPosStrength = 0.1
    prevMouse = ((mousePos[0] * newMouseStrength + prevMouse[0]) / (1 + newMouseStrength), (mousePos[1] * newMouseStrength + prevMouse[1]) / (1 + newMouseStrength))
    spider.sx = (spider.x * newPosStrength + spider.sx) / (1 + newPosStrength)
    spider.sy = (spider.y * newPosStrength + spider.sy) / (1 + newPosStrength)
    xCamOff_sl.value = spider.sx + ((prevMouse[0] - (WIDTH + SIDEBAR) / 2) / zoom_sl.value) / 2
    yCamOff_sl.value = spider.sy + ((prevMouse[1] - HEIGHT / 2) / zoom_sl.value) / 2

    if not useCam_cb.value:
        xCamOff_sl.value = (WIDTH + SIDEBAR) / 2
        yCamOff_sl.value = HEIGHT / 2

    if abs(xCamOff_sl.value) == 10000 or abs(yCamOff_sl.value) == 10000:
        spider.respawn()

    # Avoid unnecessary redraws 
    if (
        prevLerp != dynamicThresholdUsage.value
        or prevFill != fill_tg.value
        or prevThreshold != threshold_sl.value
        or prevSize != size_sl.value
        # or prevZoom != zoom_sl.value
        # or prevXOff != xCamOff_sl.value
        # or prevYOff != yCamOff_sl.value
        or isCaveGettingGenerated or shouldAvr
        ):
        
        prevLerp  = dynamicThresholdUsage.value
        prevFill = fill_tg.value
        prevThreshold = threshold_sl.value
        prevZoom = zoom_sl.value
        prevXOff = xCamOff_sl.value
        prevYOff = yCamOff_sl.value
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
            for i in range(10):
                grid = step(grid, [5, 6, 7, 8], [4, 5, 6, 7, 8])
            for r in grid:
                for c in r:
                    c[2] = 1 - c[2]
            threshold_sl.value = 100 - 46
            isCaveGettingGenerated = False

    if shouldAvr:
        grid = smoothGrid(grid)
        shouldAvr = False

    # Regenerating shapes and lines if needed
    if shouldRedraw:
        lines.clear()
        shapes.clear()
        for ri, r in enumerate(grid):
            lines.append([])
            shapes.append([])
            for ci, c in enumerate(r):
                lines[ri].append([])
                shapes[ri].append([])

        threshold = threshold_sl.value / 100
        dynamic = dynamicThresholdUsage.value
        for ri, r in enumerate(grid):
            for ci, c in enumerate(r):
                if ri == len(grid) - 1 or ci == len(r) - 1:
                    continue
                if not fill_tg.value:
                    lines[ri][ci] = marchThem(c, grid[ri][ci + 1], grid[ri + 1][ci + 1], grid[ri + 1][ci], threshold, dynamic)
                else:
                    shapes[ri][ci] = marchThem(c, grid[ri][ci + 1], grid[ri + 1][ci + 1], grid[ri + 1][ci], threshold, dynamic, True)
                    lines[ri][ci] = marchThem(c, grid[ri][ci + 1], grid[ri + 1][ci + 1], grid[ri + 1][ci], threshold, dynamic)

def drawWin():
    global grid, lines, shapes, prevMouse, neighbors, projections, collisions, webTiles, webCollisions, webSegmentsForGrid, widthStart, heightStart
    
    # Drawing order:
        # Background (clearing)
        # Grid rectangle
        # Cell dots
        # Terrain lines or shapes
        # Neighbors and projections
        # Web reach line and distributed points
        # The web itself
        # Web tiles and collisions
        # Cam debug
        # Spider itself
        # Velocity vector
        # Spider, terrain collisions

    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas) 
    
    cellSize = size_sl.value
    width = (WIDTH - SIDEBAR - 100) // cellSize
    height = (HEIGHT -100) // cellSize
    threshold = threshold_sl.value

    zoom = zoom_sl.value
    xOff = xCamOff_sl.value
    yOff = yCamOff_sl.value

    p1 = screenToWorld(zoom, xOff, yOff, SIDEBAR, 0)
    p2 = screenToWorld(zoom, xOff, yOff, WIDTH, HEIGHT)

    trueWstart = widthStart - cellSize/2
    trueHstart = heightStart - cellSize/2

    minx, miny = getGridPos(trueWstart, trueHstart, p1[0], p1[1], cellSize)
    maxx, maxy = getGridPos(trueWstart, trueHstart, p2[0], p2[1], cellSize)

    minx = min(max(minx - 1, 0), width)
    miny = min(max(miny - 1, 0), height)
    maxx = min(max(maxx + 1, 0), width)
    maxy = min(max(maxy + 1, 0), height)

    # Spider screen pos
    px, py = worldToScreen(zoom, xOff, yOff, (spider.x + spider.px) / 2, (spider.y + spider.py) / 2)

    # Applying cam to background rectangle
    rx, ry = worldToScreen(zoom, xOff, yOff, WIDTH//2 - ((cellSize * width) // 2 - cellSize//2) + SIDEBAR//2 - cellSize//2, HEIGHT//2 - ((cellSize * height) // 2 - cellSize//2) - cellSize//2)
    gridRect = pygame.Rect(rx, ry, cellSize * width * zoom, cellSize * height * zoom)
    pygame.draw.rect(WIN, "#9C9C9C", gridRect)

    # Drawing cell dots
    if not fill_tg.value:
        for ri, r in enumerate(grid):
            for ci , c in enumerate(r):
                if c[2] > threshold/100 and minx <= ri < maxx and miny <= ci < maxy:
                    if dynamicThresholdUsage.value:
                        size = cellSize/8 * (c[2] - (threshold/100)) / max(10e-2, (1 - (threshold/100))) * zoom
                    else:
                        size = cellSize/8 * zoom
                    size = max(1, size)
                    cx, cy = worldToScreen(zoom, xOff, yOff, c[0], c[1])
                    cell = pygame.Rect(cx - size/2, cy - size/2, size, size)
                    color = "#2E2E2E"
                    pygame.draw.rect(WIN, color, cell)

    # Shapes or lines
    if not fill_tg.value:
        for ri, r in enumerate(lines):
            for ci, c in enumerate(r):
                if c == None or c == True or c == False: continue
                if minx <= ri < maxx and miny <= ci < maxy:
                    drawLines(c, "#2E2E2E", max(1, round(zoom * 1)), zoom, xOff, yOff)
    else:
        for ri, r in enumerate(shapes):
            for ci, c in enumerate(r):
                if c == None: continue
                if minx <= ri < maxx and miny <= ci < maxy:
                    drawShape(c, (30, 36, 54), zoom, xOff, yOff)

    if showCollision_cb.value:
        # Neighbors
        for l in neighbors:
            px1, py1 = worldToScreen(zoom, xOff, yOff, l[0][0], l[0][1])
            px2, py2 = worldToScreen(zoom, xOff, yOff, l[1][0], l[1][1])
            pygame.draw.line(WIN, "blue", (px1, py1), (px2, py2), round(2 * zoom))
        
        # Projections
        for p in projections:
            psx, psy = worldToScreen(zoom, xOff, yOff, p[0], p[1])
            pygame.draw.circle(WIN, "yellow", (psx, psy), round(zoom))
    
    # Web projection line and distributed points
    if webUI_cb.value:
        mousePos = pygame.mouse.get_pos()
        worldMousePosX, worldMousePosY = screenToWorld(zoom, xOff, yOff, mousePos[0], mousePos[1])
        # Get web vector and line
        dv = pygame.Vector2(worldMousePosX - spider.x, worldMousePosY - spider.y)
        dv.scale_to_length(webRange_sl.value)
        endX, endY = worldToScreen(zoom, xOff, yOff, spider.x + dv.x, spider.y + dv.y)
        webLine = [[px, py], [endX, endY]]
        pygame.draw.line(WIN, "grey", webLine[0], webLine[1], round(2 * zoom))

        for p in webSegmentsForGrid:
            psx, psy = worldToScreen(zoom, xOff, yOff, p[0], p[1])
            pygame.draw.circle(WIN, "dark grey", (psx, psy), round(zoom))

    # Web itself
    webPoints = []
    if spider.isActivelyGrappled or spider.webExtensionState == 2 or spider.webExtensionState == 3:
        for p in spider.webSegments:
            webPoints.append(p)

        webPoints.append([spider.grappleX, spider.grappleY])
        webPoints.append([spider.x, spider.y])
        drawLinesFromPoints(webPoints, "white", round(1.5 * zoom * cellSize / 14), zoom, xOff, yOff, spider.webExtensionProgress)

    # Web extending state and progress
    totalLen = 0
    for i in range(len(webPoints) - 1):
        totalLen += math.hypot(webPoints[i][0] - webPoints[i+1][0], webPoints[i][1] - webPoints[i+1][1])
    speed = 5000 / totalLen if totalLen > 0 else 0
    if spider.isActivelyGrappled:
        if spider.webExtensionState == 0:
            spider.webExtensionState = 1
            spider.webExtensionProgress = 0
        elif spider.webExtensionState == 1:
            spider.webExtensionProgress +=  speed
            if spider.webExtensionProgress >= 100:
                spider.webExtensionProgress = 100
                spider.webExtensionState = 2
    else:
        if spider.webExtensionState == 1:
            spider.webExtensionState = 3
        elif spider.webExtensionState == 2:
            spider.webExtensionState = 3
            spider.webExtensionProgress = 100

    if spider.webExtensionState == 3:
        spider.webExtensionProgress -= speed
        if spider.webExtensionProgress <= 10:
            spider.webExtensionProgress = 0
            spider.webExtensionState = 0

    # Web tiles and collisions
    if webUI_cb.value:
        for t in webTiles:
            line = lines[t[0]][t[1]]
            if line == None or line == True or line == False or line == []: continue
            l = line[0]
            px1, py1 = worldToScreen(zoom, xOff, yOff, l[0][0], l[0][1])
            px2, py2 = worldToScreen(zoom, xOff, yOff, l[1][0], l[1][1])
            pygame.draw.line(WIN, "blue", (px1, py1), (px2, py2), round(2 * zoom))
        for p in webCollisions:
            psx, psy = worldToScreen(zoom, xOff, yOff, p[0][0], p[0][1])
            pygame.draw.circle(WIN, "yellow", (psx, psy), round(zoom * 3))

    circleSize = ballSize_sl.value * cellSize/20 * zoom
    dependentSize = ballSize_sl.value * cellSize/20
    # Cam debug
    if showCam_cb.value:
        # Mouse pos
        mousePos = pygame.mouse.get_pos()
        pygame.draw.circle(WIN, "red", mousePos, circleSize)
        prevMousePos = prevMouse
        pygame.draw.circle(WIN, "orange", prevMousePos, circleSize)
        
        # Spider world pos
        spiderWorldPos = [spider.x, spider.y]
        pygame.draw.circle(WIN, "green", spiderWorldPos, circleSize)
        prevSpiderWorldPos = [spider.px, spider.py]
        pygame.draw.circle(WIN, "dark green", prevSpiderWorldPos, circleSize)
        
        # Prev spider screen pos
        ppx, ppy = worldToScreen(zoom, xOff, yOff, spider.px, spider.py)
        pygame.draw.circle(WIN, "orange", (ppx, ppy), circleSize)

        # Practically cam pos
        mid = midPoint(prevMouse, (ppx, ppy))
        pygame.draw.circle(WIN, "blue", mid, circleSize)

    # Drawing screen spider
    backColor = "#4E2626"
    midColor = "#885151"
    frontColor = "#A06161"
    dist = min(spider.lookDist / 20, circleSize / 4)
    offSet = dependentSize * (1.4/5.6)
    lookVec = [dist * math.cos(spider.lookAngle), dist * math.sin(spider.lookAngle)]
    if bare_cb.value:
        pygame.draw.circle(WIN, "red", (px - lookVec[0], py - lookVec[1] - offSet), circleSize * 1.2)
        pygame.draw.circle(WIN, "orange", (px, py - offSet), circleSize)
    else:
        pygame.draw.circle(WIN, backColor, (px - lookVec[0], py - lookVec[1] - offSet), circleSize * 1.2)
        pygame.draw.circle(WIN, midColor, (px, py - offSet), circleSize)
    if showState_cb.value:
        if spider.canControl:
            pygame.draw.circle(WIN, "yellow", (px, py), circleSize)
            if spider.isGrounded:
                pygame.draw.circle(WIN, "green", (px, py), circleSize)
            if spider.isGoingLorR:
                pygame.draw.circle(WIN, "blue", (px, py), circleSize)
        else:
            pygame.draw.circle(WIN, "red", (px, py), circleSize)
        
        if spider.isJumping:
            pygame.draw.circle(WIN, "grey", (px, py), circleSize)

    # Getting body angle lerp strength
    if collisions and spider.canControl:
        c = collisions[0][0]
        spider.bodyAngleGoal = math.atan2(c[1] - spider.y, c[0] - spider.x)
        spider.homeAnglePatience = 10
        lerpStrength = 0.4
    elif spider.isActivelyGrappled:
        spider.bodyAngleGoal = math.atan2(spider.grappleY - spider.y, spider.grappleX - spider.x)
        spider.homeAnglePatience = 10
        lerpStrength = 0.4
    elif spider.homeAnglePatience > 0:
        spider.homeAnglePatience -= 1
        lerpStrength = 0
    else:
        spider.bodyAngleGoal = + math.pi/2
        lerpStrength = 0.2

    # Smoothing body angle
    nAngle = [math.cos(spider.bodyAngle), math.sin(spider.bodyAngle)]
    nGoal = [math.cos(spider.bodyAngleGoal), math.sin(spider.bodyAngleGoal)]
    lerpedn = [nAngle[0] * (1 - lerpStrength) + nGoal[0] * lerpStrength, nAngle[1] * (1 - lerpStrength) + nGoal[1] * lerpStrength]
    spider.bodyAngle = math.atan2(lerpedn[1], lerpedn[0])

    # Getting leg pivots
    offSet = dependentSize * (2/5.6)
    bodyRotation = spider.bodyAngle - math.pi/2
    bodyRotVec = [offSet * math.cos(bodyRotation), offSet * math.sin(bodyRotation)]
    spider.legPivots = []
    p01 = [spider.x - bodyRotVec[0], spider.y - bodyRotVec[1] - offSet]
    p02 = [spider.x + bodyRotVec[0], spider.y + bodyRotVec[1] - offSet]
    legRotationPivots = [p01, p02]
    legPivotVec = [lookVec[0] * 0.25, lookVec[1] * 0.2]
    for p in legRotationPivots:
        spider.legPivots.append([p[0] - legPivotVec[0] * 2, p[1] - legPivotVec[1] * 2])
        spider.legPivots.append([p[0] - legPivotVec[0], p[1] - legPivotVec[1]])
        spider.legPivots.append([p[0] + legPivotVec[0] * 2, p[1] + legPivotVec[1] * 2])
        spider.legPivots.append([p[0] + legPivotVec[0], p[1] + legPivotVec[1]])

    # Getting leg check lines
    legCheckLines = []
    startxOff = dependentSize * (10/5.6)
    startyOff = dependentSize * (-10/5.6)
    goalOff = dependentSize * (2/5.6)
    goalHeight = dependentSize * (30/5.6)
    for i in range(3, -1, -1):
        v1 = [-startxOff - i * goalOff, startyOff]
        v2 = [-startxOff - i * goalOff, startyOff + goalHeight]
        vBod1 = [v1[0] * math.cos(bodyRotation) - v1[1] * math.sin(bodyRotation), v1[0] * math.sin(bodyRotation) + v1[1] * math.cos(bodyRotation)]
        vBod2 = [v2[0] * math.cos(bodyRotation) - v2[1] * math.sin(bodyRotation), v2[0] * math.sin(bodyRotation) + v2[1] * math.cos(bodyRotation)]
        legCheckLines.append([[spider.x + vBod1[0], spider.y + vBod1[1]], [spider.x + vBod2[0], spider.y + vBod2[1]]])
    for i in range(0, 4, 1):
        v1 = [startxOff + i * goalOff, startyOff]
        v2 = [startxOff + i * goalOff, startyOff + goalHeight]
        vBod1 = [v1[0] * math.cos(bodyRotation) - v1[1] * math.sin(bodyRotation), v1[0] * math.sin(bodyRotation) + v1[1] * math.cos(bodyRotation)]
        vBod2 = [v2[0] * math.cos(bodyRotation) - v2[1] * math.sin(bodyRotation), v2[0] * math.sin(bodyRotation) + v2[1] * math.cos(bodyRotation)]
        legCheckLines.append([[spider.x + vBod1[0], spider.y + vBod1[1]], [spider.x + vBod2[0], spider.y + vBod2[1]]])

    # Getting leg goals
    spider.legGoal = []
    if not spider.isActivelyGrappled:
        hLength = dependentSize * (5/5.6)
        horizontalVector = [math.cos(bodyRotation) * hLength, math.sin(bodyRotation) * hLength]
        vLength = dependentSize * (-7/5.6)
        verticalVector = [-math.sin(bodyRotation) * vLength, math.cos(bodyRotation) * vLength]
        for li, l in enumerate(legCheckLines):
            intersection = None
            for n in neighbors:
                intersection = findIntersection(l, n)
                if intersection is not None:
                    spider.legGoal.append(intersection)
                    break
            if intersection is None:
                xNum = li if li < 4 else 7 - li
                legPortion = 0.8 + 0.05 * xNum
                if li < 4:
                    spider.legGoal.append([l[0][0] + (l[1][0] - l[0][0]) * legPortion + horizontalVector[0] + verticalVector[0], l[0][1] + (l[1][1] - l[0][1]) * legPortion + horizontalVector[1] + verticalVector[1]])
                else:
                    spider.legGoal.append([l[0][0] + (l[1][0] - l[0][0]) * legPortion - horizontalVector[0] + verticalVector[0], l[0][1] + (l[1][1] - l[0][1]) * legPortion - horizontalVector[1] + verticalVector[1]])
    else:
        grapplingLegDist = min(dependentSize * (20/5.6), math.hypot(spider.x - spider.grappleX, spider.y - spider.grappleY))
        for i in range(8):
            spider.legGoal.append([spider.x + grapplingLegDist * math.cos(bodyRotation + math.pi/2), spider.y + grapplingLegDist * math.sin(bodyRotation + math.pi/2)])

    # Getting smoothed leg goals
    legPatience = dependentSize * (5/5.6)
    legRaiseDist = dependentSize * (2/5.6)
    smoothStrength = 0.3
    for pi, p in enumerate(spider.legGoal):
        num = pi if pi < 4 else 7 - pi
        leglen = dependentSize * (12/5.6) - dependentSize * (0.5/5.6) * num
        smoothP = spider.legSmoothEnd[pi]
        if spider.canControl:
            dist = math.hypot(p[0] - smoothP[0], p[1] - smoothP[1])
            if pi%2 == 0:
                if spider.legStepState == 0:
                    if dist > legPatience:
                        spider.legStepState = 1
                        spider.legSmoothEnd[pi] = [p[0] + (p[0] - smoothP[0]) / 2, p[1] - legRaiseDist]
                elif spider.legStepState == 1:
                    spider.legSmoothEnd[pi] = [p[0] + (p[0] - smoothP[0]) / 2, p[1] - legRaiseDist]
                elif spider.legStepState == 2:
                    spider.legSmoothEnd[pi] = p
            else:
                if spider.legStepState == 0:
                    if dist > legPatience:
                        spider.legStepState = 3
                        spider.legSmoothEnd[pi] = [p[0] + (p[0] - smoothP[0]) / 2, p[1] - legRaiseDist]
                elif spider.legStepState == 3:
                    spider.legSmoothEnd[pi] = [p[0] + (p[0] - smoothP[0]) / 2, p[1] - legRaiseDist]
                elif spider.legStepState == 4:
                    spider.legSmoothEnd[pi] = p
        else:
            spider.legSmoothEnd[pi] = [smoothP[0] * (1 - smoothStrength) + p[0] * smoothStrength, smoothP[1] * (1 - smoothStrength) + p[1] * smoothStrength]
            velCorrectionStrength = 0.5
            spider.legSmoothEnd[pi] = [spider.legSmoothEnd[pi][0] + (spider.xv * velCorrectionStrength), spider.legSmoothEnd[pi][1] + (spider.yv * velCorrectionStrength)]

        if pi < 4:
            spider.legJoints[pi] = getJoint(spider.legSmoothEnd[pi], spider.legPivots[pi], leglen, 1)
        else:
            spider.legJoints[pi] = getJoint(spider.legSmoothEnd[pi], spider.legPivots[pi], leglen, -1)

    if spider.legStepState == 1:
        spider.legStepState = 2
    elif spider.legStepState == 2:
        spider.legStepState = 0
    elif spider.legStepState == 3:
        spider.legStepState = 4
    elif spider.legStepState == 4:
        spider.legStepState = 0

    # Drawing legs
    jointColor = "red" if bare_cb.value or showLeg_cb.value else "#885151"
    legColor = "yellow" if bare_cb.value or showLeg_cb.value else "#885151"
    for pi, p in enumerate(spider.legSmoothEnd):
        pSE = worldToScreen(zoom, xOff, yOff, p[0], p[1])
        pygame.draw.circle(WIN, jointColor, pSE, circleSize * 0.2)
        pJ = worldToScreen(zoom, xOff, yOff, spider.legJoints[pi][0], spider.legJoints[pi][1])
        pygame.draw.circle(WIN, jointColor, pJ, circleSize * 0.2)
        pP = worldToScreen(zoom, xOff, yOff, spider.legPivots[pi][0], spider.legPivots[pi][1])
        pygame.draw.line(WIN, legColor, pJ, pP, round(1.5 * zoom * cellSize / 14))
        pygame.draw.line(WIN, legColor, pSE, pJ, round(1.5 * zoom * cellSize / 14))

    # Extra leg UI
    if showLeg_cb.value:
        for p in spider.legGoal:
            px, py = worldToScreen(zoom, xOff, yOff, p[0], p[1])
            pygame.draw.circle(WIN, "red", (px, py), circleSize * 0.2)
        for l in legCheckLines:
            sx1, sy1 = worldToScreen(zoom, xOff, yOff, l[0][0], l[0][1])
            sx2, sy2 = worldToScreen(zoom, xOff, yOff, l[1][0], l[1][1])
            pygame.draw.line(WIN, "red", [sx1, sy1], [sx2, sy2], round(0.5 * zoom))

        for p in spider.legPivots:
            px, py = worldToScreen(zoom, xOff, yOff, p[0], p[1])
            pygame.draw.circle(WIN, "red", (px, py), circleSize * 0.2)

    if bare_cb.value:
        pygame.draw.circle(WIN, "green", (px + lookVec[0], py + lookVec[1] - offSet), circleSize * 0.8)
    else:
        pygame.draw.circle(WIN, frontColor, (px + lookVec[0], py + lookVec[1] - offSet), circleSize * 0.8)

    # Velocity
    if showVel_cb.value:
        length = 10
        vx, vy = round(px + spider.xv * zoom * length), round(py + spider.yv * zoom * length)
        pygame.draw.line(WIN, "red", (px, py), (vx, vy), round(2 * zoom))

    # Collisions
    if showCollision_cb.value:
        for c in collisions:
            px, py = worldToScreen(zoom, xOff, yOff, c[0][0], c[0][1])
            pygame.draw.circle(WIN, "red", (px, py), cellSize/4 * zoom)

def main():
    global shouldRedraw
    clock = pygame.time.Clock()
    running = True
    start = time.time_ns()
    while running:
        # Builtin pygame fps and custom, more accurate fps
        end = time.time_ns()
        delta2 = (end - start) / 10e8
        start = time.time_ns()
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps()), int(1 / delta2)}"
        
        # Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            gui.handle_event(event)
        
        # Main logic loop
        logic()
        handlePlayer()
        if shouldRedraw or True:
            drawWin()
            shouldRedraw = False
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
