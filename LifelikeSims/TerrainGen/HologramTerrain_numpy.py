import pygame, sys, random, math, colorsys, numpy as np
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
prevx, prevy = 0, 0
angle = 0
xOff, yOff = 0, 0
radarCycle = 0
maxDist = 0
heightArray = None
xOffArray = yOffArray = None
distArray = angleArray = None

def getNewGrid():
    global heightArray, xOffArray, yOffArray, distArray, angleArray, maxDist
    gx, gy = gridx.value, gridy.value
    xOff = np.arange(gx) - (gx - 1) / 2
    yOff = np.arange(gy) - (gy - 1) / 2
    xOffArray, yOffArray = np.meshgrid(xOff, yOff, indexing="ij")

    distArray = np.hypot(xOffArray, yOffArray)
    maxDist = max(maxDist, distArray.max())
    angleArray = np.arctan2(yOffArray, xOffArray) + np.pi
    heightArray = np.random.random((gx, gy))

# Averaging the grid in a plus pattern
def crossAverageGrid():
    heightArray[:] = (np.roll(heightArray, 1, 0) + np.roll(heightArray, -1, 0) + np.roll(heightArray, 1, 1) + np.roll(heightArray, -1, 1) + heightArray) / 5

# Average across 3x3 area
def blobAverageGrid():
    t = (np.roll(heightArray, -1, 0) + heightArray + np.roll(heightArray, 1, 0)) / 3
    heightArray[:] = (np.roll(t, -1, 1) + t + np.roll(t, 1, 1)) / 3

# This is just for the sliding terrain effect
# Also zooming the grid by skipping every nth point
def sampleHeight(nx, ny):
    s = skips.value
    ox, oy = round(xOff), round(yOff)
    shifted = np.roll(heightArray, (-ox, -oy), axis=(0, 1))
    return shifted[:nx*s:s, :ny*s:s]

# Simple vector rotation in order to achieve the 3D rotating effect
def transform(angle_deg, nx, ny):
    s = skips.value
    xs = xOffArray[:nx*s:s, :ny*s:s] * math.sqrt(size.value)
    ys = yOffArray[:nx*s:s, :ny*s:s] * math.sqrt(size.value)

    angle = math.radians(angle_deg)
    coss, sinn = math.cos(angle), math.sin(angle)

    X = (xs * coss - ys * sinn) * gridlenx.value / 10 + WIDTH/2 + SIDEBAR/2
    Y = (xs * sinn + ys * coss) * gridleny.value / 10 + HEIGHT/2
    return X, Y

def rgbToHsv(c):
    r, g, b = c
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return (h, s, v)

def hsvToRgb(c):
    h, s, v = c
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r*255), int(g*255), int(b*255))

def circularDiff(pos, value, whole):
    d = np.abs(pos - value)
    return np.minimum(d, whole - d)

def getRadarColors(colors, nx, ny, distances, angles):
    rType, n = radarType.value, radarAmount.value
    if rType == 0 or n == 0:
        return colors

    if rType == 1:
        size, whole = radarSize.value, nx
        value = np.broadcast_to(np.arange(nx)[:, None], (nx, ny))
        poss = [(((radarCycle % gridx.value) + gridx.value / n * (i + 1)) % gridx.value) * (nx / gridx.value) for i in range(n)]
    elif rType == 2:
        size, whole, value = radarSize.value * 2, maxDist, distances
        poss = [((radarCycle % maxDist) + maxDist / n * (i + 1)) % maxDist for i in range(n)]
    elif rType == 3:
        size, whole, value = radarSize.value / 10, math.pi * 2, angles
        poss = [(((radarCycle / 10) % (2 * math.pi) + (2 * math.pi) / n * (i + 1)) % (2 * math.pi)) for i in range(n)]

    diff = np.min([circularDiff(p, value, whole) for p in poss], axis=0)
    rate = np.clip(1 - diff / size, 0, 1)[..., None]
    radarColor = np.array(hsvToRgb((radarHue.value, 1, 1)), dtype=float)
    return colors + (radarColor - colors) * rate

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
    global angle, xOff, yOff, radarCycle
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill(BACKGROUND_COLOR, canvas)

    s = skips.value
    nx, ny = gridx.value // s, gridy.value // s

    X, Y = transform(angle, nx, ny)
    Hs = sampleHeight(nx, ny)

    # Setting color by height
    top = np.array(hsvToRgb((hueTop.value, 1, 1)), dtype=float)
    bot = np.array(hsvToRgb((hueBot.value, 1, 1)), dtype=float)
    low, high = heightArray.min(), heightArray.max()
    t = (Hs - low) / (high - low if high - low != 0 else 1)
    colors = top + (bot - top) * t[..., None]
    heights = (Hs - low) * math.sqrt(size.value) * heightFactor.value**2

    # Applying radar
    distances = distArray[:nx*s:s, :ny*s:s]
    angles = angleArray[:nx*s:s, :ny*s:s]
    colors = getRadarColors(colors, nx, ny, distances, angles)

    # Adding fade
    if cutRad.value != fullRad.value:
        rf = np.clip((distances - fullRad.value) / (cutRad.value - fullRad.value), 0, 1)
    else:
        rf = np.ones_like(distances)

    colors = colors + (np.array(BACKGROUND_COLOR) - colors) * rf[..., None]
    colors = np.clip(colors, 0, 255).astype(np.uint8)

    points = np.stack([X, Y - heights + 100], axis=-1)

    if lines.value:
        c16 = colors.astype(np.uint16)
        parts = [
            (points[:, :-1], points[:, 1:], (c16[:, :-1] + c16[:, 1:]) // 2),
            (points[:-1, :], points[1:, :], (c16[:-1, :] + c16[1:, :]) // 2)
        ]
        for starts, ends, segmentColors in parts:
            for p, q, k in zip(starts.reshape(-1, 2).tolist(),
                               ends.reshape(-1, 2).tolist(),
                               segmentColors.reshape(-1, 3).tolist()):
                pygame.draw.line(WIN, k, p, q, 1)
    else:
        for p, k in zip(points.reshape(-1, 2).tolist(), colors.reshape(-1, 3).tolist()):
            pygame.draw.circle(WIN, k, p, 3)

    angle += 0.1
    xOff += scroll.value / 100
    yOff += scroll.value / 100
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
            gui.handle_event(event)

        logic()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()
        if not running: pygame.quit()

if __name__ == "__main__":
    main() 
