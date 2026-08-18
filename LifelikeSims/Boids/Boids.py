import pygame
import random
import math
import colorsys

import sys
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

WIDTH, HEIGHT = 1400, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boids sim")

SIDEBAR = 200

gui = pygui.GUI(SIDEBAR, "Boids sim")

simCard = gui.add_section("Simulation")
fps_label = gui.add_label(simCard, "FPS: --")
countSl = gui.add_slider(simCard, "Boid count", 10, 300, 100, step=10)
speedSl = gui.add_slider(simCard, "Max Speed", 0.5, 10, 5, step=0.5)
forceSl = gui.add_slider(simCard, "Max Force", 0.05, 1, 0.2, step=0.05)
accuracySl = gui.add_slider(simCard, "Accuracy", 1, 50, 10, step=1)
fovTg = gui.add_checkbox(simCard, "Use view angle", False)
fovSl = gui.add_slider(simCard, "View angle", 0, 360, 180, step=1)

separationCard = gui.add_section("Separation")
separationWeightSl = gui.add_slider(separationCard, "Weight", 0, 3, 1.5, step=0.1)
separationRadSl = gui.add_slider(separationCard, "View radius", 0, 100, 50, step=1)

alignmentCard = gui.add_section("Alignment")
alignmentWeightSl = gui.add_slider(alignmentCard, "Weight", 0, 3, 1, step=0.1)
alignmentRadSl = gui.add_slider(alignmentCard, "View radius", 0, 100, 50, step=1)

coherenceCard = gui.add_section("Coherence")
coherenceWeightSl = gui.add_slider(coherenceCard, "Weight", 0, 3, 1, step=0.1)
coherenceRadSl = gui.add_slider(coherenceCard, "View radius", 0, 100, 50, step=1)

FPS = 60
numBoids = 150
# maxSpeed = 5
# maxForce = 0.2
BORDER_RAD = 100
BORDER_STRENGTH = 0.2
boids = []
viewRad = 50
mousePos = pygame.Vector2(0, 0)

class Boid:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.vel = pygame.Vector2(random.randrange(-100, 100) / 100, random.randrange(-100, 100) / 100)
        self.acc = pygame.Vector2(0, 0)

def border():
    for b in boids:
        if b.pos.x < BORDER_RAD + SIDEBAR:
            b.acc.x += BORDER_STRENGTH
        elif b.pos.x > WIDTH - BORDER_RAD - SIDEBAR:
            b.acc.x -= BORDER_STRENGTH
        if b.pos.y < BORDER_RAD:
            b.acc.y += BORDER_STRENGTH
        elif b.pos.y > HEIGHT- BORDER_RAD:
            b.acc.y -= BORDER_STRENGTH

def checkAngle(vel, pos, otherPos, fov):
    heading = vel.normalize()
    toOther = (otherPos - pos).normalize()
    if fov < heading.dot(toOther):
        return True
    else:
        return False


def separation(viewRad, weight, maxSpeed, maxForce, accuracy, useFov, fovAngle):
    for b in boids:
        avr = pygame.Vector2(0, 0)
        neighbors = 0
        for bOther in boids:
            dist = bOther.pos.distance_to(b.pos)
            if useFov and bOther != b and not checkAngle(b.vel, b.pos, bOther.pos, fovAngle):
                continue
            if bOther != b and dist < viewRad and dist > 0 and accuracy > neighbors:
                v1 = (b.pos - bOther.pos).normalize()
                avr += v1 * (viewRad / dist)
                neighbors += 1
        if neighbors > 0 and avr.length() > 0:
            force = avr.normalize() * maxSpeed - b.vel
            if force.length() > maxForce:
                force.scale_to_length(maxForce)
            b.acc += force * weight

def alignment(viewRad, weight, maxSpeed, maxForce, accuracy, useFov, fovAngle):
    for b in boids:
        avr = pygame.Vector2(0, 0)
        neighbors = 0
        for bOther in boids:
            dist = bOther.pos.distance_to(b.pos)
            if useFov and bOther != b and not checkAngle(b.vel, b.pos, bOther.pos, fovAngle):
                    continue
            if bOther != b and dist < viewRad and dist > 0 and accuracy > neighbors:
                avr += bOther.vel
                neighbors += 1
        if neighbors > 0 and avr.length() > 0:
            avr /= neighbors
            avr = avr.normalize() * maxSpeed
            force = avr - b.vel
            if force.length() > maxForce:
                force.scale_to_length(maxForce)
            b.acc += force * weight

def coherence(viewRad, weight, maxSpeed, maxForce, accuracy, useFov, fovAngle):
    for b in boids:
        avr = pygame.Vector2(0, 0)
        neighbors = 0
        for bOther in boids:
            dist = bOther.pos.distance_to(b.pos)
            if useFov and bOther != b and not checkAngle(b.vel, b.pos, bOther.pos, fovAngle):
                continue
            if bOther != b and dist < viewRad and dist > 0 and accuracy > neighbors:
                avr += bOther.pos
                neighbors += 1
        if neighbors > 0 and avr.length() > 0:
            avr /= neighbors
            force = (avr - b.pos).normalize() * maxSpeed
            if force.length() > maxForce:
                force.scale_to_length(maxForce)
            b.acc += force * weight

def mouseForce(type, maxForce=0.2):
    mousePos = pygame.Vector2(pygame.mouse.get_pos())
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

def stepPhysics(maxSpeed):
    for b in boids:
        b.vel += b.acc
        speed = b.vel.length()
        if speed > maxSpeed:
            b.vel.scale_to_length(maxSpeed)
        b.pos += b.vel
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

def animateBoids():
    sepView = separationRadSl.value
    sepWeight = separationWeightSl.value
    alignView = alignmentRadSl.value
    alignWeight = alignmentWeightSl.value
    cohView = coherenceRadSl.value
    cohWeight = coherenceWeightSl.value
    useFov = fovTg.value
    fovAngleSl = fovSl.value
    
    fovAngle = math.cos(math.radians(fovAngleSl / 2))

    maxSpeed = speedSl.value
    maxForce = forceSl.value
    accuracy = accuracySl.value

    separation(sepView, sepWeight, maxSpeed, maxForce, accuracy, useFov, fovAngle)
    alignment(alignView, alignWeight, maxSpeed, maxForce, accuracy, useFov, fovAngle)
    coherence(cohView, cohWeight, maxSpeed, maxForce, accuracy, useFov, fovAngle)
    noise(0.2)

    if pygame.mouse.get_pressed()[0]:
        mouseForce(1)
    if pygame.mouse.get_pressed()[2]:
        mouseForce(-1)

    stepPhysics(maxSpeed)
    border()

def getColor(vel):
    angle = math.degrees(math.atan2(vel.y, vel.x)) % 360
    hue = angle / 360
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return int(r * 255), int(g * 255), int(b * 255)

def drawWin():
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)
    for b in boids:
        p1, p2, p3, p4 = getArrow(b.pos, b.vel, 10)
        pygame.draw.polygon(WIN, getColor(b.vel), (p1, p2, p3, p4))

def main():
    clock = pygame.time.Clock()

    numBoids = countSl.value
    
    for i in range(numBoids):
        boid = Boid()
        boids.append(boid)
    
    run = True
    while run:
        clock.tick(FPS)

        fps_label.text = f"FPS: {int(clock.get_fps())}"

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

        
        animateBoids()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
