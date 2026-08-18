import pygame, sys, os
import math, random

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Getting screen size
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
info = pygame.display.Info()
screen_width,screen_height = info.current_w,info.current_h

# Setting up variables, window and GUI
PROJECT_NAME = "Top view animals"
WIDTH, HEIGHT = screen_width,screen_height - 50
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)

FPS = 60
SIDEBAR = 250
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

segments_card    = gui.add_section("Segments")
fps_label = gui.add_label(segments_card, "FPS: --")
count_slider = gui.add_slider(segments_card, "Number of segments", 2, 100, 10, 2)
length_slider = gui.add_slider(segments_card, "Base length", 50, 3000, 300, 10)
angle_slider = gui.add_slider(segments_card, "Angle constraint", 0, 180, 140, 1)


legs_card = gui.add_section("Legs")
leg_count_slider = gui.add_slider(legs_card, "Number of leg pairs", 0, 8, 0, 1)
leg_length_slider = gui.add_slider(legs_card, "Leg length", 50, 500, 300, 10)
# leg_anchor_x_slider = gui.add_slider(legs_card, "Anchor X offset", -50, 50, 0, 1)
# leg_anchor_y_slider = gui.add_slider(legs_card, "Anchor Y offset", -50, 50, 0, 1)
leg_target_x_slider = gui.add_slider(legs_card, "Target X offset", -100, 100, 0, 1)
leg_target_y_slider = gui.add_slider(legs_card, "Target Y offset", -100, 100, 0, 1)
leg_bend_mode_sl = gui.add_slider(legs_card, "Bend mode:", 1, 3, 1, 1)
leg_step_mode_sl = gui.add_slider(legs_card, "Step mode:", 1, 4, 1, 1)
leg_distrib_slider = gui.add_slider(legs_card, "Leg x distribution", 0, 100, 50, 1)
leg_inbet_slider = gui.add_slider(legs_card, "Dist between legPairs", 0 , 100, 20, 1)
target_tolerance_slider = gui.add_slider(legs_card, "Target tolerance", 0, 200, 100, 1)

thickness_card = gui.add_section("Thickness control")
fill_tg = gui.add_checkbox(thickness_card, "Fill segments", False)
bodyColor_wheel = gui.add_color_picker(thickness_card, "Body color")
thickness_tg = gui.add_checkbox(thickness_card, "Show thickness", False)
thickness_slider = gui.add_slider(thickness_card, "Thickness", 10, 100, 50, 1)
bulgePos_slider = gui.add_slider(thickness_card, "Bulge position", 0, 100, 10, 1)
bulgeStr_slider = gui.add_slider(thickness_card, "Bulge strength", 1, 20, 2, 1)
thSmooth_slider = gui.add_slider(thickness_card, "Smoothing", 1, 20, 3, 1)
decline_tg = gui.add_checkbox(thickness_card, "Decline thickness", False)
dcStr_slider = gui.add_slider(thickness_card, "Decline strength", -10, 10, 2, 1)

isSnake = False
isLizard = False

def snake():
    global isSnake, isLizard, isSpider
    if not isSnake:
        isSnake = True
        count_slider.value = 63
        length_slider.value = 1500
        thickness_slider.value = 30
        bulgePos_slider.value = 4
        bulgeStr_slider.value = 3
        thSmooth_slider.value = 3
        fill_tg.value = True
        bodyColor_wheel.hex = "#26743e"
        decline_tg.value = True
        dcStr_slider.value = 1
        outline_tg.value = True
        rainbow_tg.value = False
        leg_count_slider.value = 0
        isSpider = False
        isLizard = False
    else:
        isSnake = False

def lizard():
    global isLizard, isSnake, isSpider
    if not isLizard:
        isLizard = True
        count_slider.value = 36
        length_slider.value = 440
        thickness_slider.value = 30
        bulgePos_slider.value = 40
        bulgeStr_slider.value = 14
        thSmooth_slider.value = 14
        decline_tg.value = True
        dcStr_slider.value = 3
        fill_tg.value = True
        bodyColor_wheel.hex = "#3A8676"
        outline_tg.value = True
        rainbow_tg.value = False
        leg_count_slider.value = 2
        leg_length_slider.value = 280
        leg_target_x_slider.value = 0
        leg_target_y_slider.value = 100
        leg_bend_mode_sl.value = 3
        leg_step_mode_sl.value = 3
        leg_distrib_slider.value = 40
        leg_inbet_slider.value = 20
        target_tolerance_slider.value = 130
        isSnake = False
        isSpider = False
    else:
        isLizard = False

display_card = gui.add_section("Display")
polygon_tg = gui.add_checkbox(display_card, "Show polygon points", False)
outline_tg = gui.add_checkbox(display_card, "Show outline", False)
legUI_tg = gui.add_checkbox(display_card, "Show leg UI", False)
auto_tg = gui.add_checkbox(display_card, "Auto movement", False)
rainbow_tg = gui.add_checkbox(display_card, "Rainbow colored", False)
feet_tg = gui.add_checkbox(display_card, "Show feet", False)
snake_button = gui.add_button(display_card, "Snake", callback=snake)
lizard_button = gui.add_button(display_card, "Lizard", callback=lizard)

# Globals
mouseX, mouseY = 0, 0
newMouseX, newMouseY = 0, 0
prevSegCount = 4
points = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
goalX, goalY, slideX, slideY = 0, 0, 0, 0

tonguePos = 20
tonguing = False
outTongue = False
outGoal = 70
numOfReturns = 0

legPairs = []
feet = []
prevLegCount = 0

lizardFoot = pygame.image.load(r'Python\Projects\LifelikeSims\Inverse Kinematics\foot.png').convert_alpha()

COLORS = [
    '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', 
    '#00FF00', '#00FF7F', '#00FFFF', '#007FFF', 
    '#0000FF', '#7F00FF', '#FF00FF', '#FF007F'
]

def paletteSwap(surface, oldC, newC):
    imgCopy = surface.copy()
    old = pygame.Color(oldC)
    new = pygame.Color(newC)
    px = pygame.PixelArray(imgCopy)
    px.replace(imgCopy.map_rgb(old.r, old.g, old.b),
               imgCopy.map_rgb(new.r, new.g, new.b))
    del px
    return imgCopy

def drawRotated(surf, img, pos, angle, pivot):
    rotated = pygame.transform.rotate(img, angle)
    pivotV = pygame.Vector2(pivot)
    offset = pygame.Vector2(img.get_rect().center) - pivotV
    rotated_offs = offset.rotate(-angle)

    blitPos = (pos[0] - rotated.get_width()  // 2 + rotated_offs.x,
               pos[1] - rotated.get_height() // 2 + rotated_offs.y)
    
    surf.blit(rotated, blitPos)

def doLenCorrection(a, b, x, y, l):
    dist = math.hypot(a - x, b - y)
    dx = a - x
    dy = b - y
    if dist == 0:
        dist = 1
    x2 = a - dx * l / dist
    y2 = b - dy * l / dist
    return x2, y2

def getNVector(x1, y1, x2, y2):
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        dist = 1
    return (x2 - x1) / dist, (y2 - y1) / dist

def drawLinesFromPointList(surface, points, color, width):
    for pi, p in enumerate(points):
        if pi < len(points) - 1:
            pygame.draw.line(surface, color, (p[0], p[1]), (points[pi + 1][0], points[pi + 1][1]), width)

def getFrontPoints(points, res):
    frontPoints = []
    for i in range(res+1):
        nx, ny = getNVector(points[0][0], points[0][1], points[1][0], points[1][1])
        deg =  - math.pi / res * (i) + math.pi / 2
        nxr = nx * math.cos(deg) - ny * math.sin(deg)
        nyr = nx * math.sin(deg) + ny * math.cos(deg)
        frontPoints.append((points[0][0] - nxr * points[0][2], points[0][1] - nyr * points[0][2]))
    
    return frontPoints

def getBackPoints(points, res):
    backPoints = []
    for i in range(res+1):
        nx, ny = getNVector(points[-2][0], points[-2][1], points[-1][0], points[-1][1])
        deg =  - math.pi / res * (i) + math.pi / 2
        nxr = nx * math.cos(deg) - ny * math.sin(deg)
        nyr = nx * math.sin(deg) + ny * math.cos(deg)
        backPoints.append((points[-1][0] + nxr * points[-1][2], points[-1][1] + nyr * points[-1][2]))

    return backPoints

def getPolygon(points):
    listOfPoints = []

    # get the first points (front)
    frontPoints = getFrontPoints(points, 8)
    for p in frontPoints:
        listOfPoints.append(p)

    # get first side (right)
    for pi, p in enumerate(points):
        if pi == 0:
            nx, ny = getNVector(points[0][0], points[0][1], points[1][0], points[1][1])
            norx, nory = -ny, nx
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))
        elif pi == (len(points) - 1):
            nx, ny = getNVector(points[-2][0], points[-2][1], points[-1][0], points[-1][1])
            norx, nory = -ny, nx
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))
        else:
            nx1, ny1 = getNVector(points[pi - 1][0], points[pi - 1][1], points[pi][0], points[pi][1])
            nx2, ny2 = getNVector(points[pi][0], points[pi][1], points[pi + 1][0], points[pi + 1][1])
            nxa, nya = nx1 + nx2, ny1 + ny2
            dist = math.hypot(nxa, nya)
            if dist == 0:
                dist = 1
            nxa, nya = nxa / dist, nya / dist
            norx, nory = -nya, nxa
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))
    
    # get end points (back)
    backPoints = getBackPoints(points, 8)
    for p in backPoints:
        listOfPoints.append(p)

    # get other side (left)
    for pi, p in enumerate(points[::-1]):
        pi = len(points) - 1 - pi
        if pi == 0:
            nx, ny = getNVector(points[0][0], points[0][1], points[1][0], points[1][1])
            norx, nory = ny, -nx
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))
        elif pi == (len(points) - 1):
            nx, ny = getNVector(points[-2][0], points[-2][1], points[-1][0], points[-1][1])
            norx, nory = ny, -nx
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))
        else:
            nx1, ny1 = getNVector(points[pi - 1][0], points[pi - 1][1], points[pi][0], points[pi][1])
            nx2, ny2 = getNVector(points[pi][0], points[pi][1], points[pi + 1][0], points[pi + 1][1])
            nxa, nya = nx1 + nx2, ny1 + ny2
            dist = math.hypot(nxa, nya)
            if dist == 0:
                dist = 1
            nxa, nya = nxa / dist, nya / dist
            norx, nory = nya, -nxa
            listOfPoints.append((p[0] + norx * p[2], p[1] + nory * p[2]))

    return listOfPoints

def getSegmentPoints(points):
    segmentPoints = []
    for pi, p in enumerate(points):
        if pi == 0:
            nlx, nly = getNVector(points[0][0], points[0][1], points[1][0], points[1][1])
            nzx1, nzy1 = -nly, nlx
            nzx2, nzy2 = nly, -nlx
            segmentPoints.append(((p[0] + nzx1 * p[2], p[1] + nzy1 * p[2]), (p[0] + nzx2 * p[2], p[1] + nzy2 * p[2])))
        elif pi == (len(points) - 1):
            nlx, nly = getNVector(points[-2][0], points[-2][1], points[-1][0], points[-1][1])
            nzx1, nzy1 = -nly, nlx
            nzx2, nzy2 = nly, -nlx
            segmentPoints.append(((p[0] + nzx1 * p[2], p[1] + nzy1 * p[2]), (p[0] + nzx2 * p[2], p[1] + nzy2 * p[2])))
        else:
            nx1, ny1 = getNVector(points[pi - 1][0], points[pi - 1][1], points[pi][0], points[pi][1])
            nx2, ny2 = getNVector(points[pi][0], points[pi][1], points[pi + 1][0], points[pi + 1][1])
            nxa, nya = nx1 + nx2, ny1 + ny2
            dist = math.hypot(nxa, nya)
            if dist == 0:
                dist = 1
            nxa, nya = nxa / dist, nya / dist
            nzx1, nzy1 = -nya, nxa
            nzx2, nzy2 = nya, -nxa
            segmentPoints.append(((p[0] + nzx1 * p[2], p[1] + nzy1 * p[2]), (p[0] + nzx2 * p[2], p[1] + nzy2 * p[2])))

    return segmentPoints

def buildSegments(segmentPoints):
    segments = []
    for pi, p in enumerate(segmentPoints):
        if pi == 0:
            segments.append((p[0], p[1], segmentPoints[1][1], segmentPoints[1][0]))
        elif pi == (len(segmentPoints) - 1):
            pass
        else:
            segments.append((p[0], p[1], segmentPoints[pi + 1][1], segmentPoints[pi + 1][0]))

    return segments

def collectAllSegments(points):
    segmentPoints = getSegmentPoints(points)
    segments = []
    frontSegment = getFrontPoints(points, 8)
    midSegments = buildSegments(segmentPoints)
    backSegment = getBackPoints(points, 8)
    segments.append(frontSegment)

    for s in midSegments:
        segments.append(s)
    segments.append(backSegment)

    return segments

def getOutlines(segments):
    outlines = []
    for s in segments:
        outlines.append([])
    for si, s in enumerate(segments):
        if si == 0 or si == len(segments) - 1:
            for pi, p in enumerate(s):
                if pi != len(s) - 1:
                    outlines[si].append((p, s[pi + 1]))
        else:
            outlines[si].append((s[0], s[-1]))
            outlines[si].append((s[1], s[2]))

    return outlines

def correctAngle(x1, y1, x2, y2, x3, y3, angleConstraint):
    dx1, dy1 = x1 - x2, y1 - y2
    dx2, dy2 = x3 - x2, y3 - y2
    if (dx1 == 0 and dy1 == 0) or (dx2 == 0 and dy2 == 0):
        return x3, y3

    ang1 = math.degrees(math.atan2(dy1, dx1))
    ang2 = math.degrees(math.atan2(dy2, dx2))
    angle = (ang2 - ang1) % 360

    if angle < angleConstraint:
        dAngle = angleConstraint - angle
    elif angle > (360 - angleConstraint):
        dAngle = (360 - angleConstraint) - angle
    else:
        dAngle = 0

    rdx = dx2 * math.cos(math.radians(dAngle)) - dy2 * math.sin(math.radians(dAngle))
    rdy = dx2 * math.sin(math.radians(dAngle)) + dy2 * math.cos(math.radians(dAngle))

    return x2 + rdx, y2 + rdy

def getAccessoryPos(p1, p2, p3, angle, dist, xOff=0, yOff=0):
    if p1 and p2 and p3: # If there are three given points
        D1v = pygame.Vector2(p1[0] - p2[0], p1[1] - p2[1])
        D2v = pygame.Vector2(p3[0] - p2[0], p3[1] - p2[1])
        forvV = D1v - D2v / 2
    elif p1 and p2: # If there are two given points and the first point is used
        forvV = pygame.Vector2(p1[0] - p2[0], p1[1] - p2[1])
    elif p2 and p3: # If there are two points given and the last point is used 
        forvV = pygame.Vector2(p2[0] - p3[0], p2[1] - p3[1])
    else:
        print("Accessory fetch error:", p1, p2, p3)
        return


    forvAngle = math.degrees(math.atan2(forvV.y, forvV.x))
    offV = pygame.Vector2(xOff, yOff).rotate(forvAngle)
    v1 = pygame.Vector2(forvV.rotate(angle))
    v2 = pygame.Vector2(forvV.rotate(-angle))

    try:
        v1.scale_to_length(dist)
        v2.scale_to_length(dist)
    except ValueError:
        return (p2[0], p2[1]), (p2[0], p2[1]), forvAngle
    
    v1 += offV
    v2 += offV
    accPos1 = p2[0] + v1.x, p2[1] + v1.y
    accPos2 = p2[0] + v2.x, p2[1] + v2.y

    return accPos1, accPos2, forvAngle

def getAccessoryPosFromAngle(p, forvAngle, offsetAngle, dist, xOff=0, yOff=0):
    forvV = pygame.Vector2(0,1).rotate(forvAngle)
    offV = pygame.Vector2(xOff, yOff).rotate(forvAngle)
    v1 = pygame.Vector2(forvV.rotate(offsetAngle))

    try:
        v1.scale_to_length(dist)
    except ValueError:
        return p
    
    v1 += offV
    accPos = p[0] + v1.x, p[1] + v1.y

    return accPos

def getAngleFromPoints(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dy, dx))

def getKneePoint(p1, p2, l, pol):
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


def logic():
    global mouseX, mouseY, newMouseX, newMouseY, prevSegCount, prevLegCount, goalX, goalY, slideX, slideY

    # Mouse smoothing
    newMouseX, newMouseY = pygame.mouse.get_pos()
    
    if newMouseX > SIDEBAR:
        smoothing = 0.25
        mouseX += (newMouseX - mouseX) * smoothing
        mouseY += (newMouseY - mouseY) * smoothing

    newSegCount = count_slider.value
    length = length_slider.value / newSegCount
    thickness = thickness_slider.value
    constraint = angle_slider.value
    newLegCount = leg_count_slider.value

    # Add or remove segments
    if newSegCount != prevSegCount:
        diff = newSegCount - prevSegCount
        if diff > 0:
            for i in range(diff):
                points.append([0, 0, thickness])
        else:
            for i in range(-diff):
                points.pop()

        prevSegCount = newSegCount

    # Add or remove legPairs
    if newLegCount != prevLegCount:
        diff = newLegCount - prevLegCount
        if diff > 0:
            for i in range(diff):
                legPairs.append([0, 0, 0, 0, 0])
                feet.append([0,0, False, 0, 0])
                feet.append([0,0, False, 0, 0])
        else:
            for i in range(-diff):
                legPairs.pop()
                feet.pop()
                feet.pop()

        prevLegCount = newLegCount

    # Integrate bulge position and strength
    ratio = min(newSegCount - 1 ,max(0, int(round(bulgePos_slider.value / 100 * newSegCount, 0))))
    for p in points:
        p[2] = thickness
    points[ratio][2] = thickness * bulgeStr_slider.value

    # Smooth the thickness
    for i in range(thSmooth_slider.value):
        for pi, p in enumerate(points):
            if pi == 0:
                p[2] = (p[2] + points[1][2]) / 2
            elif pi == (len(points) - 1):
                p[2] = (p[2] + points[-2][2]) / 2
            else:
                p[2] = (p[2] + points[pi - 1][2] + points[pi + 1][2]) / 3

    # Apply decline
    if decline_tg.value:
        decl = dcStr_slider.value
        rate = 1 - (abs(decl) / 100)
        if decl >= 0:
            for pi, p in enumerate(points):
                p[2] *= rate**pi
        else:
            for pi, p in enumerate(points[::-1]):
                p[2] *= rate**pi

    speed = 15
    if leg_count_slider.value > 0 or isLizard: speed = 5

    # Set end point ( either by auto logic or to mouse pos)
    if auto_tg.value:
        dx = goalX - slideX
        dy = goalY - slideY
        dist = math.hypot(dx, dy)
        if dist < 50:
            goalX = random.randint(0, WIDTH)
            goalY = random.randint(0, HEIGHT)
        else:
            slideX += dx / dist * speed
            slideY += dy / dist * speed
            points[0][0], points[0][1] = slideX, slideY
    else:
        points[0][0], points[0][1] = mouseX, mouseY
    
    # Main snake like movement logic (just len and angle correction)
    for i in range(newSegCount - 1):
        x, y = doLenCorrection(points[i][0], points[i][1], points[i+1][0], points[i+1][1], length)     
        points[i+1][0], points[i+1][1] = x, y

        if i >= 1 and i < (newSegCount - 1):
            points[i+1][0], points[i+1][1] = correctAngle(points[i-1][0], points[i-1][1], points[i][0], points[i][1], points[i+1][0], points[i+1][1], constraint)

    # Leg logic
    legPairCount = leg_count_slider.value

    if legPairCount != 0:
        if legPairCount <= 1:
            distBetween = 0
        else:
            distBetween = round(leg_inbet_slider.value / 100 * (newSegCount - 2) / (legPairCount - 1))

        legXAnchorOff = 0
        legYAnchorOff = 0
        legXTargetOff = leg_target_x_slider.value
        legYTargetOff = leg_target_y_slider.value
        tolerance = target_tolerance_slider.value
        stepMode = leg_step_mode_sl.value

        usableSegSpace = newSegCount - legPairCount - ((legPairCount - 1) * distBetween)

        if usableSegSpace < 0:
            while usableSegSpace < 0:
                distBetween -= 1
                usableSegSpace = newSegCount - legPairCount - ((legPairCount - 1) * distBetween)

        legStartInd = round(usableSegSpace * leg_distrib_slider.value / 100)
        
        # Getting anchor and target positions
        for li, l in enumerate(legPairs):
            l[-1] = legStartInd + li + (li * distBetween)
            if li == 0:
                l[0], l[1], angle = getAccessoryPos(None, points[l[-1]], points[l[-1] + 1], 90, points[l[-1]][-1] / 2 + legXAnchorOff, legYAnchorOff)
                l[2], l[3], angle = getAccessoryPos(None, points[l[-1]], points[l[-1] + 1], 90, points[l[-1]][-1] + 50 + legXTargetOff, legYTargetOff)
            elif li == len(legPairs) - 1:
                l[0], l[1], angle = getAccessoryPos(points[l[-1] - 1], points[l[-1]], None, 90, points[l[-1]][-1] / 2 + legXAnchorOff, legYAnchorOff)
                l[2], l[3], angle = getAccessoryPos(points[l[-1] - 1], points[l[-1]], None, 90, points[l[-1]][-1] + 50 + legXTargetOff, legYTargetOff)
            else:
                l[0], l[1], angle = getAccessoryPos(points[l[-1] - 1], points[l[-1]], points[l[-1] + 1], 90, points[l[-1]][-1] / 2 + legXAnchorOff, legYAnchorOff)
                l[2], l[3], angle = getAccessoryPos(points[l[-1] - 1], points[l[-1]], points[l[-1] + 1], 90, points[l[-1]][-1] + 50 + legXTargetOff, legYTargetOff)

        # Step logic
        for fi, f in enumerate(feet):
            if fi % 2 == 0:
                dx = f[0] - legPairs[fi // 2][2][0]
                dy = f[1] - legPairs[fi // 2][2][1]
                otherStepping = feet[fi + 1][2]
            else:
                dx = f[0] - legPairs[fi // 2][3][0]
                dy = f[1] - legPairs[fi // 2][3][1]
                otherStepping = feet[fi - 1][2]
            dist = math.hypot(dx, dy)

            if stepMode == 3:
                pairStepping = False
                if fi // 2 != len(legPairs) - 1:
                    if fi % 2 == 0:
                        s1 = feet[fi + 2][2]
                        s2 = feet[fi + 3][2]
                    else:
                        s1 = feet[fi + 1][2]
                        s2 = feet[fi + 2][2]
                    if s1 or s2 or otherStepping:
                        pairStepping = True
                else:
                    if legPairCount == 1:
                        pairStepping = otherStepping
                    else:
                        if fi % 2 == 0:
                            s1 = feet[fi - 1][2]
                            s2 = feet[fi - 2][2]
                        else:
                            s1 = feet[fi - 2][2]
                            s2 = feet[fi - 3][2]
                        if s1 or s2 or otherStepping:
                            pairStepping = True
            
            allowStep = True
            if stepMode == 2:
                allowStep = not otherStepping
            elif stepMode == 3:
                allowStep = not pairStepping
            elif stepMode == 4:
                allowStep = not any(foot[2] for foot in feet if foot is not f)

            if f[2] == False and allowStep:
                if dist >= tolerance:
                    f[2] = True
                    print(f)
                    if fi % 2 == 0:
                        f[3] = legPairs[fi // 2][2][0]
                        f[4] = legPairs[fi // 2][2][1]
                    else:
                        f[3] = legPairs[fi // 2][3][0]
                        f[4] = legPairs[fi // 2][3][1]
            else:
                dx2 = f[0] - f[3]
                dy2 = f[1] - f[4]
                dist2 = math.hypot(dx2, dy2)
                f[0] += (f[3] - f[0]) * 0.33333
                f[1] += (f[4] - f[1]) * 0.33333

                if dist2 < 10:
                    f[2] = False

def drawWin():
    global tonguePos, tonguing, outGoal, outTongue, numOfReturns
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    # Tolerance circles
    if legUI_tg.value:
        tolerance = target_tolerance_slider.value
        for l in legPairs:
            pygame.draw.circle(WIN, "blue", l[2], tolerance)
            pygame.draw.circle(WIN, "blue", l[3], tolerance)

    # Goal
    if auto_tg.value:
        pygame.draw.circle(WIN, "white", (goalX, goalY), 15)
        pygame.draw.circle(WIN, "black", (goalX, goalY), 13)

    # Thickness circles
    if thickness_tg.value and not fill_tg.value:
        for p in points:
            pygame.draw.circle(WIN, "white", (p[0], p[1]), p[2], 1)
    elif thickness_tg.value and fill_tg.value:
        thickness_tg.value = False

    # Connection lines and joint points
    if not fill_tg.value:
        drawLinesFromPointList(WIN, points, "gray", 7)
        for p in points:
            pygame.draw.circle(WIN, "black", (p[0], p[1]), 7)
    
    if outline_tg.value or polygon_tg.value:
        polypoints = getPolygon(points) 

    if fill_tg.value or outline_tg.value:
        segments = collectAllSegments(points)
        outlines = getOutlines(segments)

    # Drawing legs

    if leg_count_slider.value > 0:
        for fi, f in enumerate(feet):
            p1 = (f[0], f[1])
            if fi % 2 == 0:
                p2 = legPairs[fi // 2][0]
            else:
                p2 = legPairs[fi // 2][1]

            l = leg_length_slider.value / 5
            legMode = leg_bend_mode_sl.value
            
            if legMode == 1:
                polarity = 1
            elif legMode == 2:
                polarity = -1
            elif legMode == 3:
                if fi > len(feet) // 2 - 1:
                    polarity = 1
                else:
                    polarity = -1

            if fi % 2 == 0:
                p3 = getKneePoint(p1, p2, l, polarity)
            else:
                p3 = getKneePoint(p1, p2, l, -polarity)

            if fill_tg.value:
                if not feet_tg.value:
                    if f[2]:
                        if outline_tg.value: pygame.draw.circle(WIN, "black", (f[0], f[1]), 25)
                        pygame.draw.circle(WIN, bodyColor_wheel.value, (f[0], f[1]), 20)  
                    else:
                        if outline_tg.value: pygame.draw.circle(WIN, "black", (f[0], f[1]), 20)
                        pygame.draw.circle(WIN, bodyColor_wheel.value, (f[0], f[1]), 15)
                if outline_tg.value:
                    outlineWidth = 10
                    pygame.draw.circle(WIN, "black", p3, 5 + (outlineWidth // 2))
                    pygame.draw.line(WIN, "black", p1, p3, 10 + outlineWidth)
                    pygame.draw.line(WIN, "black", p3, p2, 10 + outlineWidth)

                pygame.draw.circle(WIN, bodyColor_wheel.value, p3, 5)
                pygame.draw.line(WIN, bodyColor_wheel.value, p1, p3, 10)
                pygame.draw.line(WIN, bodyColor_wheel.value, p3, p2, 10)
            else:
                if f[2]:
                    pygame.draw.circle(WIN, "blue", (f[0], f[1]), 10)  
                else:
                    pygame.draw.circle(WIN, "blue", (f[0], f[1]), 7)

                pygame.draw.circle(WIN, "black", p3, 2.5)
                pygame.draw.line(WIN, "black", p1, p3, 5)
                pygame.draw.line(WIN, "black", p3, p2, 5)

            if isLizard and feet_tg.value:
                angle = getAngleFromPoints(p3, p1)
                if f[2]:
                    lizardFootUse = pygame.transform.scale(paletteSwap(lizardFoot, "blue", bodyColor_wheel.value), (70, 70))
                else:
                    lizardFootUse = pygame.transform.scale(paletteSwap(lizardFoot, "blue", bodyColor_wheel.value), (50, 50))
                drawRotated(WIN, lizardFootUse, p1, - angle - 90, (lizardFootUse.get_width() // 2, lizardFootUse.get_height() // 2))
    
    # Filling and outline
    if fill_tg.value:
        if rainbow_tg.value:
            for si, s in enumerate(segments[::-1]):
                segmentColor = COLORS[(len(segments) - si - 1) % len(COLORS)]
                pygame.draw.polygon(WIN, segmentColor, s)
                if outline_tg.value:
                    for l in outlines[len(segments) - si - 1]:
                        pygame.draw.line(WIN, COLORS[si % len(COLORS)], l[0], l[1], 5)
        else:
            for si, s in enumerate(segments[::-1]):
                pygame.draw.polygon(WIN, bodyColor_wheel.value, s)
                if outline_tg.value:
                    for l in outlines[len(segments) - si - 1]:
                        pygame.draw.line(WIN, "black", l[0], l[1], 5)
    elif outline_tg.value:
        for pi, p in enumerate(polypoints):
            pygame.draw.line(WIN, "black", p, polypoints[(pi + 1) % len(polypoints)], 5)

    if isSnake or isLizard:
        # Pupils, eye white, eye outline
        eye1Pos, eye2Pos, angle1 = getAccessoryPos(points[1], points[2], points[3], 90, 25)
        pygame.draw.circle(WIN, "black", eye1Pos, 12)
        pygame.draw.circle(WIN, "black", eye2Pos, 12)
        pygame.draw.circle(WIN, "white", eye1Pos, 10)
        pygame.draw.circle(WIN, "white", eye2Pos, 10)
        pupil1Pos = getAccessoryPosFromAngle(eye1Pos, -90, getAngleFromPoints(eye1Pos, (newMouseX, newMouseY)), 5)
        pupil2Pos = getAccessoryPosFromAngle(eye2Pos, -90, getAngleFromPoints(eye2Pos, (newMouseX, newMouseY)), 5)

        # Working eye tracking
        # pygame.draw.circle(WIN, "white", (300, 300), 10)
        # aPos = getAccessoryPosFromAngle((300, 300), 90, getAngleFromPoints((newMouseX, newMouseY), (300, 300)), 10)
        # pygame.draw.circle(WIN, "black", aPos, 5)
        
        pygame.draw.circle(WIN, "black", pupil1Pos, 5)
        pygame.draw.circle(WIN, "black", pupil2Pos, 5)
        # Nose holes
        nose1Pos, nose2Pos, angle2 = getAccessoryPos(None, points[0], points[1], 30, 20)
        if isSnake:
            pygame.draw.circle(WIN, "black", nose1Pos, 5)
            pygame.draw.circle(WIN, "black", nose2Pos, 5)
        elif isLizard:
            pygame.draw.circle(WIN, "black", nose1Pos, 4)
            pygame.draw.circle(WIN, "black", nose2Pos, 4)
    
    if isSnake:
        # Tongue logic
        if not tonguing:
            if random.randint(1, 100) == 10:
                tonguing = True
                outGoal = random.randint(50, 70)
                outTongue = True
        else:
            if outTongue:
                if tonguePos < outGoal:
                    tonguePos += random.randint(5, 20)
                else:
                    outTongue = False
            else:
                if tonguePos > 20:
                    tonguePos -= random.randint(5, 20)
                else:
                    if random.randint(1, 5) == 1 or numOfReturns > 5:
                        tonguing = False
                        numOfReturns = 0
                    else:
                        outTongue = True
                        outGoal = random.randint(50, 70)
                        numOfReturns += 1
            # Tongue drawing
            if tonguePos > 20:
                tongueWidth = (tonguePos + 20) / 70 * 20
                tongue1Pos, tongue2Pos, angle3 = getAccessoryPos(None, points[0], points[1], tongueWidth, 20, 15)
                tongue3Pos, tongue4Pos, angle4 = getAccessoryPos(None, points[0], points[1], tongueWidth, 20, tonguePos)
                tip1Pos, tip2Pos, angle5 = getAccessoryPos(None, points[0], points[1], tongueWidth + 10, 20, tonguePos + 20)
                tipmidPos = ((tongue4Pos[0] + tongue3Pos[0]) / 2, (tongue4Pos[1] + tongue3Pos[1]) / 2)
                tonguePoly = (tongue1Pos, tongue2Pos, tongue4Pos, tip2Pos, tipmidPos, tip1Pos, tongue3Pos, tongue1Pos)
                pygame.draw.polygon(WIN, "red", tonguePoly)
                drawLinesFromPointList(WIN, tonguePoly, "black", 3)

    # Polygon points
    if polygon_tg.value:
        for p in polypoints:
            pygame.draw.circle(WIN, "red", p, 3)
    
    # Leg UI
    if legUI_tg.value:
        for l in legPairs:
            pygame.draw.circle(WIN, "orange", (points[l[-1]][0], points[l[-1]][1]), 5)
            pygame.draw.circle(WIN, "yellow", l[0], 5)
            pygame.draw.circle(WIN, "yellow", l[1], 5)
            pygame.draw.circle(WIN, "red", l[2], 5)
            pygame.draw.circle(WIN, "red", l[3], 5)
    

def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps())}"

        bendMode = leg_bend_mode_sl.value
        stepMode = leg_step_mode_sl.value
        
        if bendMode == 1:
            leg_bend_mode_sl.label = "Bend mode: Backward"
        elif bendMode == 2:
            leg_bend_mode_sl.label = "Bend mode: Forward"
        elif bendMode == 3:
            leg_bend_mode_sl.label = "Bend mode: Both"
        
        if stepMode == 1:
            leg_step_mode_sl.label = "Step mode: No rules"
        elif stepMode == 2:
            leg_step_mode_sl.label = "Step mode: 1 leg/pair"
        elif stepMode == 3:
            leg_step_mode_sl.label = "Step mode: 1 leg/2 pair"
        elif stepMode == 4:
            leg_step_mode_sl.label = "Step mode: Only 1 leg"

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
