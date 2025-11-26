import turtle
import tkinter as tk
from tkinter import ttk
import math
import random
import time

# Setting up turtle and UI
root = tk.Tk()
root.title("Shape Matching Controls")

canvas = tk.Canvas(root, width=610, height=610)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0

t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

# Setting up shape
objs = []
shapes = []
shapeIndex = 0
newPoints = []
newConnections = []

# Setting up simulation
fps = 100
deltaT = 1 / fps
simPerFrame = 2

# Setting up world
worldSize = 250
gravity = 10
friction = 0.99
elasticity = 0.5
springStrength = 1
airResistance = 0.99

# Controls and UI
label = tk.Label(root, text="Spawn mode")
label.pack(pady=(20, 0))

# Rearranging controls with the corresponding spawn mode
def arrangeControls():
    sideSlider.pack_forget()
    xposSlider.pack_forget()
    yposSlider.pack_forget()
    addPointButton.pack_forget()
    gravitySlider.pack_forget()
    springStrengthSlider.pack_forget()
    airResistanceSlider.pack_forget()
    showShapesCheck.pack_forget()
    if spawningMode.get() == "Custom":
        xposSlider.pack()
        yposSlider.pack()
        addPointButton.pack(pady=(2, 20))
        gravitySlider.pack()
        springStrengthSlider.pack()
        airResistanceSlider.pack()
        showShapesCheck.pack()
    elif spawningMode.get() == "N-gon":
        sideSlider.pack(pady=(0, 5))
        gravitySlider.pack()
        springStrengthSlider.pack()
        airResistanceSlider.pack()
        showShapesCheck.pack()

spawningMode = ttk.Combobox(root, values=["Custom", "N-gon"], width=10, state="readonly")
spawningMode.set("N-gon")
spawningMode.pack()
spawningModeVar = spawningMode.get()

def spawnNewShape():
    global objs, points, shapeIndex, newConnections, newPoints

    points = newPoints.copy()
    connections = newConnections.copy()

    objs.append({"points": points.copy(), "connections": connections.copy()})

    shapes.append({"points": [], "avrX": 0, "avrY": 0, "avrAngle": 0})

    findAvrPoint(shapeIndex)

    avrX = shapes[shapeIndex]["avrX"]
    avrY = shapes[shapeIndex]["avrY"]

    shapes[shapeIndex]["points"] = []
    for i in range(len(objs[shapeIndex]["points"])):
        px = objs[shapeIndex]["points"][i]["xpos"] - avrX
        py = objs[shapeIndex]["points"][i]["ypos"] - avrY
        shapes[shapeIndex]["points"].append({"xpos": px,"ypos": py, "angle": math.degrees(math.atan2(py, px))})

    shapeIndex += 1
    getNewShape(sideSlider.get())

spawnShapeButton = tk.Button(root, text="Spawn Shape", command=spawnNewShape)
spawnShapeButton.pack(pady=(2, 20))

# N-gon shape generator
def getNewShape(n):
    global newPoints, newConnections
    newPoints = []
    newConnections = []

    t.penup()
    t.setheading(0)
    t.goto(0, 75)

    n = int(n)
    side = 75 * 2 * math.sin(math.pi / n)

    for i in range(n):
        newPoints.append({"xpos": t.xcor(), "ypos": t.ycor(), "xspeed": 0, "yspeed": 0})
        t.left(360 / n)
        t.forward(side)
    
    for i in range(len(newPoints)):
        newConnections.append([i, (i + 1) % len(newPoints)])

sideSlider = tk.Scale(root, from_=3, to=20, resolution=1, orient=tk.HORIZONTAL, label="Side Amount", command=getNewShape)
sideSlider.set(10)
sideSlider.pack(pady=(0, 20))

xposSlider = tk.Scale(root, from_=-worldSize, to=worldSize, resolution=1, orient=tk.HORIZONTAL, label="X Position")
xposSlider.set(0)

yposSlider = tk.Scale(root, from_=-worldSize, to=worldSize, resolution=1, orient=tk.HORIZONTAL, label="Y Position")
yposSlider.set(0)

def addPoint():
    print("Add point")

addPointButton = tk.Button(root, text="Add Point", command=lambda: addPoint())

gravitySlider = tk.Scale(root, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, label="Gravity")
gravitySlider.set(10)
gravitySlider.pack()

springStrengthSlider = tk.Scale(root, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, label="Spring Strength")
springStrengthSlider.set(1)
springStrengthSlider.pack()

airResistanceSlider = tk.Scale(root, from_=0.9, to=1, resolution=0.001, orient=tk.HORIZONTAL, label="Air Resistance")
airResistanceSlider.set(0.998)
airResistanceSlider.pack()

showShapes = False
def toggleShapes():
    global showShapes
    showShapes = not showShapes

showShapesCheck = tk.Checkbutton(root, text="Show shapes", command=toggleShapes)
showShapesCheck.pack()

# Emptying temporary lists
def resetSpawning():
    global newPoints, newConnections
    newPoints = []
    newConnections = []

# def spawnShape():
    # global objs, points, shapeIndex, newConnections, newPoints

    # points = []
    # points.clear()
    # points.append({"xpos": -50, "ypos": 50, "xspeed": 0, "yspeed": 0})
    # points.append({"xpos": 0, "ypos": 10, "xspeed": 0, "yspeed": 0})
    # points.append({"xpos": 50, "ypos": 50, "xspeed": 0, "yspeed": 0})
    # points.append({"xpos": 50, "ypos": -50, "xspeed": 0, "yspeed": 0})
    # points.append({"xpos": -50, "ypos": -60, "xspeed": 0, "yspeed": 0})

    # connections = []
    # for i in range(len(points)):
    #     connections.append([i, (i + 1) % len(points)])

    # objs.append({"points": points.copy(), "connections": connections.copy()})

    # shapes.append({"points": []})

    # findAvrPoint(shapeIndex)

    # for i in range(len(objs[shapeIndex]["points"])):
    #     px = objs[shapeIndex]["points"][i]["xpos"] - avrX
    #     py = objs[shapeIndex]["points"][i]["ypos"] - avrY
    #     shapes[shapeIndex]["points"].append({"xpos": px,"ypos": py, "angle": math.degrees(math.atan2(py, px))})

    # findAvrAngle(shapeIndex)
    
    # shapeIndex += 1

def drawFrame():
    global spawningModeVar
    t.clear()
    t.penup()

    for i in range(simPerFrame):
        doFizix()

    # Getting and drawing the "frames" of the shapes
    if showShapes:
        for si in range(len(shapes)):
            findAvrPoint(si)
            findAvrAngle(si)

            avrX = shapes[si]["avrX"]
            avrY = shapes[si]["avrY"]
            avrAngle = shapes[si]["avrAngle"]

            shapePts = shapes[si]["points"]
            for pi in range(len(shapePts)):
                p1x = avrX + shapePts[pi]["xpos"] * math.cos(math.radians(avrAngle)) - shapePts[pi]["ypos"] * math.sin(math.radians(avrAngle))
                p1y = avrY + shapePts[pi]["xpos"] * math.sin(math.radians(avrAngle)) + shapePts[pi]["ypos"] * math.cos(math.radians(avrAngle))
                p2x = avrX + shapePts[(pi + 1) % len(shapePts)]["xpos"] * math.cos(math.radians(avrAngle)) - shapePts[(pi + 1) % len(shapePts)]["ypos"] * math.sin(math.radians(avrAngle))
                p2y = avrY + shapePts[(pi + 1) % len(shapePts)]["xpos"] * math.sin(math.radians(avrAngle)) + shapePts[(pi + 1) % len(shapePts)]["ypos"] * math.cos(math.radians(avrAngle))
                
                t.goto(p1x, p1y)
                t.dot(5, "lightblue")
                t.pencolor("lightblue")
                t.pendown()
                t.goto(p2x, p2y)
                t.penup()

            t.goto(avrX, avrY)
            t.dot(5, "blue")
    else:
        for i in range(len(shapes)):
            findAvrPoint(i)
            findAvrAngle(i)

    # Drawing the objects
    for oi in range(len(objs)):
        for c in objs[oi]["connections"]:
            t.goto(objs[oi]["points"][c[0]]["xpos"], objs[oi]["points"][c[0]]["ypos"])
            t.pencolor("black")
            t.pendown()
            t.goto(objs[oi]["points"][c[1]]["xpos"], objs[oi]["points"][c[1]]["ypos"])
            t.penup()

    # Drawing the border
    t.goto(-worldSize, worldSize)
    t.pencolor("gray")
    t.pendown()
    t.goto(worldSize, worldSize)
    t.goto(worldSize, -worldSize)
    t.goto(-worldSize, -worldSize)
    t.goto(-worldSize, worldSize)
    t.penup()

    # Drawing the new shape
    t.pencolor("lightgray")
    for i in range(len(newConnections)):
        t.penup()
        t.goto(newPoints[newConnections[i][0]]["xpos"], newPoints[newConnections[i][0]]["ypos"])
        t.pendown()
        t.goto(newPoints[newConnections[i][1]]["xpos"], newPoints[newConnections[i][1]]["ypos"])
        t.penup()
    for i in range(len(newPoints)):
        t.goto(newPoints[i]["xpos"], newPoints[i]["ypos"])
        t.dot(5, "lightgray")

    # Rearranging the controls if needed
    if spawningModeVar != spawningMode.get():
        spawningModeVar = spawningMode.get()
        resetSpawning()
        arrangeControls()
        if spawningModeVar == "N-gon":
            getNewShape(sideSlider.get())

    screen.update()
    root.after(round(deltaT * 100), drawFrame)

def doFizix():
    gravity = gravitySlider.get()
    springStrength = springStrengthSlider.get()
    airResistance = airResistanceSlider.get()
    for o in range(len(objs)):
        findAvrPoint(o)
        findAvrAngle(o)

        avrX = shapes[o]["avrX"]
        avrY = shapes[o]["avrY"]
        avrAngle = shapes[o]["avrAngle"]

        for pt in range(len(objs[o]["points"])):
            p = objs[o]["points"][pt]
            s = shapes[o]["points"][pt]
            angleRad = math.radians(avrAngle)
            springX = avrX + s["xpos"] * math.cos(angleRad) - s["ypos"] * math.sin(angleRad)
            springY = avrY + s["xpos"] * math.sin(angleRad) + s["ypos"] * math.cos(angleRad)

            # Gravity
            p["yspeed"] -= gravity * deltaT * airResistance ** -1

            # Air resistance
            p["xspeed"] *= math.sqrt(airResistance)
            p["yspeed"] *= math.sqrt(airResistance)
            
            # Spring forces(F = mű * deltaX)
            xStretch = springX - p["xpos"]
            yStretch = springY - p["ypos"]

            xForce = xStretch * springStrength
            yForce = yStretch * springStrength

            p["xspeed"] += xForce * deltaT
            p["yspeed"] += yForce * deltaT

            # Acceleration (V = V0 + A*t)
            p["xpos"] += p["xspeed"] * deltaT
            p["ypos"] += p["yspeed"] * deltaT

            # Boundaries friction and elasticity
            if p["xpos"] > worldSize:
                p["xpos"] = worldSize
                p["xspeed"] *= -elasticity * friction
                p["yspeed"] *= friction
            elif p["xpos"] < -worldSize:
                p["xpos"] = -worldSize
                p["xspeed"] *= -elasticity * friction
                p["yspeed"] *= friction

            if p["ypos"] > worldSize:
                p["ypos"] = worldSize
                p["yspeed"] *= -elasticity * friction
                p["xspeed"] *= friction
            elif p["ypos"] < -worldSize:
                p["ypos"] = -worldSize
                p["yspeed"] *= -elasticity * friction
                p["xspeed"] *= friction

# Finding average position of a shape
def findAvrPoint(si):
    avrX = 0
    avrY = 0
    for pi in range(len(objs[si]["points"])):
        avrX += objs[si]["points"][pi]["xpos"]
        avrY += objs[si]["points"][pi]["ypos"]
    avrX /= len(objs[si]["points"])
    avrY /= len(objs[si]["points"])

    shapes[si]["avrX"] = avrX
    shapes[si]["avrY"] = avrY

# Finding average angle of a shape
def findAvrAngle(si):
    avrAngle = 0
    sumSin = 0
    sumCos = 0
    pts = objs[si]["points"]

    avrX = shapes[si]["avrX"]
    avrY = shapes[si]["avrY"]

    for pi in range(len(pts)):
        objAngle = math.degrees(math.atan2(pts[pi]["ypos"] - avrY, pts[pi]["xpos"] - avrX))

        # Getting the average difference
        diff = math.radians(objAngle - shapes[si]["points"][pi]["angle"])
        sumSin += math.sin(diff)
        sumCos += math.cos(diff)

    avrAngle = math.degrees(math.atan2(sumSin, sumCos))

    shapes[si]["avrAngle"] = avrAngle

# spawnShape()
drawFrame()
root.mainloop()
