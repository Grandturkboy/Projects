import turtle
import tkinter as tk
import math
import random

# Setting up turtle and UI
root = tk.Tk()
root.title("Shape intersection Controls")

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0

t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

worldSize = 300
points = []
lines = []
intersections = []
closePoints = []
xpos = 0
ypos = 0
angle = 0

oneClosest = False

pointsSlider = tk.Scale(root, from_=3, to=100, resolution=1, orient="horizontal", label="Points")
pointsSlider.set(1)
pointsSlider.pack()

radiusSlider = tk.Scale(root, from_=50, to=worldSize, resolution=1, orient="horizontal", label="Radius")
radiusSlider.set(100)
radiusSlider.pack()

jitterSlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", label="Jitter")
jitterSlider.set(0)
jitterSlider.pack()

redrawButton = tk.Button(root, text="Redraw", command=lambda: getPoints())
redrawButton.pack()

xPosSlider = tk.Scale(root, from_=-worldSize, to=worldSize, resolution=1, orient="horizontal", label="X Position")
xPosSlider.set(0)
xPosSlider.pack()

yPosSlider = tk.Scale(root, from_=-worldSize, to=worldSize, resolution=1, orient="horizontal", label="Y Position")
yPosSlider.set(0)
yPosSlider.pack()

angleSlider = tk.Scale(root, from_=0, to=360, resolution=1, orient="horizontal", label="Angle")
angleSlider.set(0)
angleSlider.pack()

def toggleClosest():
    global oneClosest
    oneClosest = not oneClosest

closestButton = tk.Checkbutton(root, text="Closest", command=toggleClosest)
closestButton.pack()

def getPoints():
    global points, lines, prevPoint, prevRadius, prevJitter
    points = []
    lines = []
    angles = []
    jitter = jitterSlider.get()

    for i in range(pointsSlider.get()):
        angles.append(random.random() * 2 * math.pi)
    angles.sort()
    
    for angle in angles:
        radius = radiusSlider.get() * (1 + random.uniform(-jitter, jitter))
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    
    for i in range(len(points)):
        lines.append((points[i % len(points)], points[(i + 1) % len(points)]))

    prevRadius = radiusSlider.get()
    prevPoint = pointsSlider.get()
    prevJitter = jitterSlider.get()


def drawFrame():
    global endPosX, endPosY
    t.clear()
    
    t.up()
    t.goto(worldSize, worldSize)
    t.color("black")
    t.pensize(5)
    t.down()
    t.goto(worldSize, -worldSize)
    t.goto(-worldSize, -worldSize)
    t.goto(-worldSize, worldSize)
    t.up()
    t.pensize(1)

    t.goto(xPosSlider.get(), yPosSlider.get())
    t.dot(10, "red")
    t.setheading(angleSlider.get())
    t.color("blue")
    t.down()
    t.forward(1000)
    endPosX = t.xcor()
    endPosY = t.ycor()
    t.up()

    t.color("black")
    t.goto(points[0][0], points[0][1])
    t.down()
    for p in range(len(points)):
        t.goto(points[p][0], points[p][1])
    t.goto(points[0][0], points[0][1])
    t.up()

    findIntersections()
    
    for i in intersections:
        t.goto(i)
        t.dot(10, "green")
    
    t.goto(0,0)
    inside = False
    if len(intersections) % 2 == 1:
        inside = True
    t.write(f"Inside: {inside}", align="center", font=("Arial", 12, "normal"))
    
    findClosestPoints()
    
    for i in closePoints:
        t.goto(i)
        t.dot(10, "blue")
        t.color("orange")
        t.down()
        t.goto(xPosSlider.get(), yPosSlider.get())
        t.up()
        t.color("black")

    angleSlider.set(angleSlider.get() + 5)
    if angleSlider.get() >= 360:
        angleSlider.set(0)

    checkSliders()
    screen.update()
    root.after(10, drawFrame)

def findIntersections():
    intersections.clear()
    x1 = xPosSlider.get()
    y1 = yPosSlider.get()
    x2 = endPosX
    y2 = endPosY
    for l in lines:
        x3 = l[0][0]
        y3 = l[0][1]
        x4 = l[1][0]
        y4 = l[1][1]

        d1x = x2 - x1
        d1y = y2 - y1
        d2x = x4 - x3
        d2y = y4 - y3

        denom = d1x * d2y - d1y * d2x

        if denom == 0:
            continue
        
        iScalar1 = ((x3 - x1) * d2y - (y3 - y1) * d2x) / denom
        iScalar2 = ((x3 - x1) * d1y - (y3 - y1) * d1x) / denom

        if iScalar1 >= 0 and iScalar1 <= 1 and iScalar2 >= 0 and iScalar2 <= 1:
            ix = x1 + d1x * iScalar1
            iy = y1 + d1y * iScalar1
            intersections.append((ix, iy))

def findClosestPoints():
    closePoints.clear()
    x1 = xPosSlider.get()
    y1 = yPosSlider.get()
    
    for l in lines:
        x2 = l[0][0]
        y2 = l[0][1]
        x3 = l[1][0]
        y3 = l[1][1]

        edgeX = x3 - x2
        edgeY = y3 - y2

        pointX = x1 - x2
        pointY = y1 - y2

        dot = pointX * edgeX + pointY * edgeY
        sqLen = edgeX * edgeX + edgeY * edgeY

        t = dot / sqLen

        if oneClosest:
            if t > 1:
                t = 1
            elif t < 0:
                t = 0
            closestX = x2 + t * edgeX
            closestY = y2 + t * edgeY
            closePoints.append((closestX, closestY))
        elif t > 0 and t < 1:
                closestX = x2 + t * edgeX
                closestY = y2 + t * edgeY
                closePoints.append((closestX, closestY))

        if oneClosest:
            if len(closePoints) > 1:
                smallestDepth = 1000
                for p in closePoints:
                    xp = p[0]
                    yp = p[1]
                    depth = math.sqrt((x1 - xp) ** 2 + (y1 - yp) ** 2)
                    if depth < smallestDepth:
                        smallestDepth = depth
                        closestX = xp
                        closestY = yp

                closePoints.clear()
                closePoints.append((closestX, closestY))

def checkSliders():
    if pointsSlider.get() != prevPoint or radiusSlider.get() != prevRadius or jitterSlider.get() != prevJitter:
        getPoints()

getPoints()
drawFrame()
root.mainloop()

