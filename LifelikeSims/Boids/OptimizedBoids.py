import pygame
import random
import math
import colorsys

import sys
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

WIDTH, HEIGHT = 1400, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Boids sim")

SIDEBAR = 200

gui = pygui.GUI(SIDEBAR, "Boids sim")

simCard = gui.add_section("Simulation")
fps_label = gui.add_label(simCard, "FPS: --")
countSl = gui.add_slider(simCard, "Boid count", 10, 2000, 100, step=10)
simSpSl = gui.add_slider(simCard, "Simulation speed", 0.1, 10, 1, step=0.1)
speedSl = gui.add_slider(simCard, "Max Speed", 0.5, 10, 5, step=0.5)
forceSl = gui.add_slider(simCard, "Max Force", 0.05, 1, 0.2, step=0.05)
accuracySl = gui.add_slider(simCard, "Accuracy", 1, 50, 10, step=1)
sizeSl = gui.add_slider(simCard, "Boid size", 2, 50, 10, step=2)

viewCard = gui.add_section("View settings")
setViewSl = gui.add_slider(viewCard, "Set all view radius", 1, 100, 50, step=1)
fovTg = gui.add_checkbox(viewCard, "Use view angle", True)
fovSl = gui.add_slider(viewCard, "View angle", 0, 360, 270, step=1)

separationCard = gui.add_section("Separation")
separationWeightSl = gui.add_slider(separationCard, "Weight", 0, 3, 1.5, step=0.1)
separationViewRadSl = gui.add_slider(separationCard, "View radius", 0, 100, 50, step=1)

alignmentCard = gui.add_section("Alignment")
alignmentWeightSl = gui.add_slider(alignmentCard, "Weight", 0, 3, 1, step=0.1)
alignmentRadSl = gui.add_slider(alignmentCard, "View radius", 0, 100, 50, step=1)

coherenceCard = gui.add_section("Coherence")
coherenceWeightSl = gui.add_slider(coherenceCard, "Weight", 0, 3, 1, step=0.1)
coherenceRadSl = gui.add_slider(coherenceCard, "View radius", 0, 100, 50, step=1)

borderCard = gui.add_section("Border type")
forceBorderTg = gui.add_checkbox(borderCard, "Force border", False)
wrapBorderTg = gui.add_checkbox(borderCard, "Wrap border", True)

FPS = 60
numBoids = 150
BORDER_RAD = 100
BORDER_STRENGTH = 0.2
boids = []
viewRad = 50
mousePos = pygame.Vector2(0, 0)

cellSize = viewRad

class Boid:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.vel = pygame.Vector2(random.randrange(-100, 100) / 100, random.randrange(-100, 100) / 100)
        self.acc = pygame.Vector2(0, 0)

def buildGrid(cellSize):
    grid = {}
    for b in boids:
        cell = (int(b.pos.x // cellSize), int(b.pos.y // cellSize))
        grid.setdefault(cell, []).append(b)
    return grid

def getNeighbors(b, grid, cellSize):
    cx, cy = int(b.pos.x // cellSize), int(b.pos.y // cellSize)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for other in grid.get((cx + dx, cy + dy), []):
                if other != b:
                    yield other

def border():
    if forceBorderTg.value:
        for b in boids:
            if b.pos.x < BORDER_RAD:
                b.acc.x += BORDER_STRENGTH
            elif b.pos.x > WIDTH - BORDER_RAD - SIDEBAR:
                b.acc.x -= BORDER_STRENGTH
            if b.pos.y < BORDER_RAD:
                b.acc.y += BORDER_STRENGTH
            elif b.pos.y > HEIGHT- BORDER_RAD:
                b.acc.y -= BORDER_STRENGTH
    if wrapBorderTg.value:
        for b in boids:
            if b.pos.x < 0:
                b.pos.x = WIDTH - SIDEBAR
            elif b.pos.x > WIDTH - SIDEBAR:
                b.pos.x = 0
            if b.pos.y < 0 :
                b.pos.y = HEIGHT
            elif b.pos.y > HEIGHT:
                b.pos.y = 0

def checkAngle(vel, pos, otherPos, fov):
        heading = vel.normalize()
        try:
            toOther = (otherPos - pos).normalize()
        except ValueError:
            return False
        if fov < heading.dot(toOther):
            return True
        else:
            return False

def flocking(avRad, avWeight, alRad, alWeight, coRad, coWeight, maxSpeed, maxForce, accuracy, grid, cellSize, useFov, fovAngle):
    avRadSq, alRadSq, coRadSq = avRad**2, alRad**2, coRad**2
    for b in boids:
        av, al, co = pygame.Vector2(0, 0), pygame.Vector2(0, 0), pygame.Vector2(0, 0)
        nAv, nAl, nCo = 0, 0, 0
        for other in getNeighbors(b, grid, cellSize):
            diff = b.pos - other.pos
            distSq = diff.x**2 + diff.y**2
            if useFov and not checkAngle(b.vel, b.pos, other.pos, fovAngle):
                continue
            if 0 < distSq < avRadSq and accuracy > nAv:
                dist = distSq**0.5
                av += diff.normalize() * (avRad / dist) ** 2
                nAv += 1
            if 0 < distSq < alRadSq and accuracy > nAl:
                al += other.vel
                nAl += 1
            if 0 < distSq < coRadSq and accuracy > nCo:
                co += other.pos
                nCo += 1
        if nAv > 0:
            avF = av.normalize() * maxSpeed - b.vel
            if avF.length() > maxForce:
                avF.scale_to_length(maxForce)
            b.acc += avF * avWeight
        if nAl > 0:
            al /= nAl
            alF = (al.normalize() * maxSpeed) - b.vel
            if alF.length() > maxForce:
                alF.scale_to_length(maxForce)
            b.acc += alF * alWeight
        if nCo > 0:
            co /= nCo
            coF = (co - b.pos).normalize() * maxSpeed
            if coF.length() > maxForce:
                coF.scale_to_length(maxForce)
            b.acc += coF * coWeight

def mouseForce(type, maxForce=0.2):
    mousePos = pygame.Vector2(pygame.mouse.get_pos())
    if mousePos.x > SIDEBAR:
        mousePos.x -= SIDEBAR
        for b in boids:
            force = mousePos - b.pos
            force.scale_to_length(maxForce) 
            b.acc += force * type

def noise(strength):
    for b in boids:
        force = pygame.Vector2(random.randrange(-100, 100) / 100, random.randrange(-100, 100) / 100)
        if force.length() != 0:
            force.scale_to_length(strength)
        b.acc += force

def stepPhysics(maxSpeed, delta, simSpeed):
    for b in boids:
        b.vel += b.acc
        speed = b.vel.length()
        if speed > maxSpeed:
            b.vel.scale_to_length(maxSpeed)
        b.pos += b.vel * delta * simSpeed
        b.acc *= 0

def getArrow(pos, vel, size):
    vel = vel.normalize()
    p1 = pos + (vel * size)
    p2 = pos + (vel.rotate(150) * size * 2/3)
    p3 = pos + (-vel * size * 1/3)
    p4 = pos + (vel.rotate(-150) * size * 2/3)
    
    p1.x += SIDEBAR
    p2.x += SIDEBAR
    p3.x += SIDEBAR
    p4.x += SIDEBAR

    return p1, p2, p3, p4

def animateBoids(delta):
    sepView = separationViewRadSl.value
    sepWeight = separationWeightSl.value
    alignView = alignmentRadSl.value
    alignWeight = alignmentWeightSl.value
    cohView = coherenceRadSl.value
    cohWeight = coherenceWeightSl.value

    useFov = fovTg.value
    fovAngleSl = fovSl.value
    fovAngle = math.cos(math.radians(fovAngleSl / 2))
    
    simSpeed = simSpSl.value * 50
    maxSpeed = speedSl.value
    maxForce = forceSl.value
    accuracy = accuracySl.value
    cellSize = setViewSl.value
    grid = buildGrid(cellSize)

    flocking(sepView, sepWeight, alignView, alignWeight, cohView, cohWeight, maxSpeed, maxForce, accuracy, grid, cellSize, useFov, fovAngle)
    noise(0.2)

    if pygame.mouse.get_pressed()[0]:
        mouseForce(1)
    if pygame.mouse.get_pressed()[2]:
        mouseForce(-1)

    stepPhysics(maxSpeed, delta, simSpeed)
    border()

def getColor(vel):
    angle = math.degrees(math.atan2(vel.y, vel.x)) % 360
    hue = angle / 360
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return int(r * 255), int(g * 255), int(b * 255)

def drawWin():
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

    fovAngle = fovSl.value
    fovAngle = math.cos(math.radians(fovAngle / 2))
    boidSize = sizeSl.value
    for b in boids:
        p1, p2, p3, p4 = getArrow(b.pos, b.vel, boidSize)
        pygame.draw.polygon(WIN, getColor(b.vel), (p1, p2, p3, p4))

def main():
    clock = pygame.time.Clock()

    numBoids = countSl.value
    
    for i in range(numBoids):
        boid = Boid()
        boids.append(boid)

    prevViewRad = setViewSl.value
    
    run = True
    while run:
        delta = clock.tick(FPS) / 1000 

        fps_label.text = f"FPS: {int(clock.get_fps())}"
        
        newViewRad = setViewSl.value

        if newViewRad != prevViewRad:
            separationViewRadSl.value = newViewRad
            alignmentRadSl.value = newViewRad
            coherenceRadSl.value = newViewRad
            prevViewRad = newViewRad

        if numBoids != countSl.value:
            diff = countSl.value - numBoids
            if diff > 0:
                for i in range(diff):
                    boid = Boid()
                    boids.append(boid)
            else:
                for i in range(-diff):
                    boids.pop()

            numBoids = countSl.value

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            gui.handle_event(event)

        
        animateBoids(delta)
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
