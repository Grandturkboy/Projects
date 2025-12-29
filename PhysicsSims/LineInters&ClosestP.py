import turtle
import tkinter as tk
import math
import random
import time

# Setting up turtle and UI
root = tk.Tk()
root.title("Line intersection Controls")

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0

t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

worldSize = 300
lines = []
intersections = []
closePoints = []
xpos = 0
ypos = 0
angle = 0
maxLen = 200
minLen = 75

linesSlider = tk.Scale(root, from_=0, to=10, resolution=1, orient="horizontal", label="Lines")
linesSlider.set(1)
linesSlider.pack()

redrawButton = tk.Button(root, text="Redraw", command=lambda: getLines())
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

def getLines():
    global lines
    lines = []
    while len(lines) < linesSlider.get():
        p1 = (random.randint(-worldSize, worldSize), random.randint(-worldSize, worldSize))
        p2 = (random.randint(-worldSize, worldSize), random.randint(-worldSize, worldSize))
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if length < maxLen and length > minLen:
            lines.append((p1, p2))

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
    for line in lines:
        t.goto(line[0])
        t.down()
        t.goto(line[1])
        t.up()

    findIntersections()
    
    for i in intersections:
        t.goto(i)
        t.dot(10, "green")
    
    t.goto(0,0)
    t.write(f"Intersections: {len(intersections)}", align="center", font=("Arial", 12, "normal"))

    findClosestPoints()

    for p in closePoints:
        t.goto(p)
        t.dot(10, "yellow")
        
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

        if t > 1:
            t = 1
        elif t < 0:
            t = 0

        closestX = x2 + t * edgeX
        closestY = y2 + t * edgeY

        closePoints.append((closestX, closestY))

getLines()
drawFrame()
root.mainloop()
  
