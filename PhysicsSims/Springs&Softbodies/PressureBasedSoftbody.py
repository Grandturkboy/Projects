import turtle
import tkinter as tk
import math
import random

# Setting up turtle and UI
root = tk.Tk()
root.title("Pressure Simulation Controls")

canvas = tk.Canvas(root, width=610, height=610)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0

t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

# Setting up shape
points = []
connections = []
bodyRadius = 75


def getNewShape(n):
    global gasAmount, volume
    points.clear()
    connections.clear()

    t.penup()
    t.setheading(0)
    t.goto(0, bodyRadius)

    n = int(n)
    side = bodyRadius * 2 * math.sin(math.pi / n)

    for i in range(n):
        points.append({"xpos": t.xcor(), "ypos": t.ycor(), "xspeed": 0, "yspeed": 0})
        t.left(360 / n)
        t.forward(side)

    for i in range(n):
        connections.append([
            i, (i + 1) % n, math.hypot(points[i]["xpos"] - points[(i + 1) % n]["xpos"], points[i]["ypos"] - points[(i + 1) % n]["ypos"])])

    gasAmount = calcArea()
    volume = gasAmount


# Shoelace area
def calcArea():
    area = 0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        add = points[i]["xpos"] * points[j]["ypos"]
        rem = points[j]["xpos"] * points[i]["ypos"]
        area += add - rem

    if area < 0:
        points.reverse()
        print("Reversed")
        area *= -1

    return area / 2


# Object parameters
getNewShape(10)
gasAmount = calcArea()
pointMass = 1
springStrength = 1000
pressureCoefficient = 100
volume = gasAmount
maxSpeed = 2000
kickForce = 800
elasticity = 0.2
forceReduction = 0.9

# World parameters
gravity = 400
friction = 0.8
fps = 300
deltaT = 1 / fps
simulationsPerFrame = 10
simCounter = 0
dampening = 1

# Controls
sideSlider = tk.Scale(root, from_=3, to=100, resolution=1, orient=tk.HORIZONTAL, label="Side Amount", command=getNewShape)
sideSlider.set(10)
sideSlider.pack()
getNewShape(sideSlider.get())

gravitySlider = tk.Scale(root, from_=0, to=1000, resolution=10, orient=tk.HORIZONTAL, label="Gravity")
gravitySlider.set(400)
gravitySlider.pack()

elasticitySlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Elasticity")
elasticitySlider.set(0.2)
elasticitySlider.pack()

airResSlider = tk.Scale(root, from_=0.9, to=1, resolution=0.001, orient=tk.HORIZONTAL, label="Air Resistance")
airResSlider.set(0.995)
airResSlider.pack()

forceReductionSlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Force Reduction")
forceReductionSlider.set(0.9)
forceReductionSlider.pack()

pressureCoefficientSlider = tk.Scale(root, from_=0, to=50, resolution=0.1, orient=tk.HORIZONTAL, label="Pressure Coefficient")
pressureCoefficientSlider.set(10)
pressureCoefficientSlider.pack()

springStrengthSlider = tk.Scale(root, from_=0, to=1000, resolution=1, orient=tk.HORIZONTAL, label="Spring Strength")
springStrengthSlider.set(300)
springStrengthSlider.pack()

areaLabel = tk.Label(root, text="Area: " + str(gasAmount), width=20)
areaLabel.pack()

pressureLabel = tk.Label(root, text="Pressure: " + str(pressureCoefficient), width=20)
pressureLabel.pack()

kickAngleSlider = tk.Scale(root, from_=0, to=180, resolution=3, orient=tk.HORIZONTAL, label="Kick Angle")
kickAngleSlider.set(90)
kickAngleSlider.pack()


def kickIt():
    x = kickForce * math.cos(math.radians(kickAngleSlider.get()))
    y = kickForce * math.sin(math.radians(kickAngleSlider.get()))

    for i in range(len(points)):
        points[i]["xspeed"] += x
        points[i]["yspeed"] += y


kickButton = tk.Button(root, text="Kick", command=kickIt)
kickButton.pack()


def forceToggle():
    global showForce
    showForce = not showForce


showForce = False
showForceButton = tk.Checkbutton(root, text="Show momentum", command=forceToggle)
showForceButton.pack()


def toggleStress():
    global showStress
    showStress = not showStress


showStress = False
showStressButton = tk.Checkbutton(root, text="Show stress", command=toggleStress)
showStressButton.pack()


def drawFrame():
    global pressure, volume

    t.clear()
    t.penup()

    # Pressure
    pressureCoefficient = pressureCoefficientSlider.get()
    volume = calcArea()
    area = volume

    if volume > 0:
        pressure = min(1e5, ((gasAmount / max(volume, 1e-2)) ** 0.8) * pressureCoefficient)
        pressure = gasAmount / volume * pressureCoefficient
        pressureLabel.config(text="Pressure: " + str(round(pressure, 1)))
    else:
        print("Volume is 0")
        getNewShape(sideSlider.get())

    # Draw points
    t.penup()
    t.goto(points[0]["xpos"], points[0]["ypos"])
    t.fillcolor("orange")
    t.begin_fill()

    for i in range(len(points)):
        t.goto(points[i]["xpos"], points[i]["ypos"])
        t.dot(pointMass, "black")

    t.goto(points[0]["xpos"], points[0]["ypos"])
    t.end_fill()
    t.penup()

    # Draw edges
    for i in range(len(connections)):
        t.penup()
        t.goto(points[connections[i][0]]["xpos"], points[connections[i][0]]["ypos"])

        if showStress:
            t.pensize(3)
            restLen = connections[i][2]
            distance = math.hypot(
                points[connections[i][0]]["xpos"] - points[connections[i][1]]["xpos"],
                points[connections[i][0]]["ypos"] - points[connections[i][1]]["ypos"])
            stress = min(1, abs(distance - restLen) / 100) * (len(connections) ** 0.5)
            red = min(255, max(0, int(255 * stress)))
            green = min(255, max(0, int(255 * (1 - stress))))
            t.pencolor(f"#{red:02x}{green:02x}00")
        else:
            t.pensize(1)
            t.pencolor("black")

        t.pendown()
        t.goto(points[connections[i][1]]["xpos"], points[connections[i][1]]["ypos"])
        t.penup()

    # Draw border
    t.pensize(1)
    t.pencolor("black")

    t.goto(-300, 300)
    t.pendown()
    t.goto(-300, -200)
    t.goto(300, -200)
    t.goto(300, 300)
    t.goto(-300, 300)
    t.penup()

    # Average pos
    avrX = sum(p["xpos"] for p in points) / len(points)
    avrY = sum(p["ypos"] for p in points) / len(points)

    # Kick angle arrow
    t.penup()
    t.goto(avrX, avrY)
    t.setheading(kickAngleSlider.get())
    t.pendown()
    t.forward(bodyRadius * 2)

    t.left(135)
    t.forward(20)
    t.backward(20)
    t.left(90)
    t.forward(20)
    t.penup()

    areaLabel.config(text="Area: " + str(round(area / 100, 1)))

    # Physics substeps
    for i in range(simulationsPerFrame):
        doFizix()

    screen.update()
    root.after(round(1000 * deltaT), drawFrame)


def doFizix():
    global pressure, simCounter

    showForceCheck = showForce

    if simCounter >= simulationsPerFrame and showForce:
        showForceCheck = True
        simCounter = 1
    else:
        showForceCheck = False
        simCounter += 1

    airResistance = airResSlider.get()
    forceReduction = forceReductionSlider.get()
    elasticity = elasticitySlider.get()
    springStrength = springStrengthSlider.get() * pressureCoefficientSlider.get()
    pressureCoefficient = pressureCoefficientSlider.get()

    # Spring + pressure forces
    for i in range(len(connections)):
        ballIndex1 = connections[i][0]
        ballIndex2 = connections[i][1]

        xpos1 = points[ballIndex1]["xpos"]
        ypos1 = points[ballIndex1]["ypos"]
        xpos2 = points[ballIndex2]["xpos"]
        ypos2 = points[ballIndex2]["ypos"]

        xspeed1 = points[ballIndex1]["xspeed"]
        yspeed1 = points[ballIndex1]["yspeed"]
        xspeed2 = points[ballIndex2]["xspeed"]
        yspeed2 = points[ballIndex2]["yspeed"]

        edgeVectorX = xpos2 - xpos1
        edgeVectorY = ypos2 - ypos1

        perpendicularVectorX = -edgeVectorY
        perpendicularVectorY = edgeVectorX
        pVectorLength = math.hypot(perpendicularVectorX, perpendicularVectorY)

        if pVectorLength > 1e-8:
            perpendicularVectorX /= pVectorLength
            perpendicularVectorY /= pVectorLength
        else:
            perpendicularVectorX = 0.0
            perpendicularVectorY = 0.0
            print("pVectorLength is 0")

        edgeLength = math.hypot(edgeVectorX, edgeVectorY)
        if edgeLength == 0:
            print("Edge length is 0")
            edgeLength = 0.01

        angle = math.atan2(ypos1 - ypos2, xpos1 - xpos2)
        pressureForce = (-pressure * edgeLength * pressureCoefficient) * forceReduction

        if showForce and showForceCheck:
            t.penup()
            t.goto((xpos1 + xpos2) / 2, (ypos1 + ypos2) / 2)
            t.setheading(math.degrees(angle - math.pi / 2))
            t.pencolor("blue")
            t.pendown()
            t.forward(pressureForce / pointMass * deltaT)
            t.penup()

        # Pressure force
        points[ballIndex1]["xspeed"] += perpendicularVectorX * pressureForce * deltaT / 2
        points[ballIndex1]["yspeed"] += perpendicularVectorY * pressureForce * deltaT / 2
        points[ballIndex2]["xspeed"] += perpendicularVectorX * pressureForce * deltaT / 2
        points[ballIndex2]["yspeed"] += perpendicularVectorY * pressureForce * deltaT / 2

        # Spring
        restLength = connections[i][2]
        relSx = xspeed1 - xspeed2
        relSy = yspeed1 - yspeed2

        springDirx = math.cos(angle)
        springDiry = math.sin(angle)

        springVel = relSx * springDirx + relSy * springDiry
        dampenForce = dampening * springVel

        Springforce = (-(edgeLength - restLength) * springStrength - dampenForce) * forceReduction

        if showForce and showForceCheck:
            t.goto((xpos1 + xpos2) / 2, (ypos1 + ypos2) / 2)
            t.setheading(math.degrees(angle + math.pi / 2))
            t.pencolor("red")
            t.pendown()
            t.forward(Springforce / pointMass * deltaT / 10)
            t.penup()

        points[ballIndex1]["xspeed"] += math.cos(angle) * Springforce / pointMass * deltaT
        points[ballIndex1]["yspeed"] += math.sin(angle) * Springforce / pointMass * deltaT
        points[ballIndex2]["xspeed"] -= math.cos(angle) * Springforce / pointMass * deltaT
        points[ballIndex2]["yspeed"] -= math.sin(angle) * Springforce / pointMass * deltaT

    # Forces per point
    for i in range(len(points)):
        gravity = gravitySlider.get()

        xpos = points[i]["xpos"]
        ypos = points[i]["ypos"]
        xspeed = points[i]["xspeed"]
        yspeed = points[i]["yspeed"]

        yspeed -= gravity * deltaT

        xspeed *= airResistance
        yspeed *= airResistance

        if abs(xspeed) > maxSpeed or abs(yspeed) > maxSpeed:
            print("Too fast bitch")
            pressureCoefficientSlider.set(pressureCoefficientSlider.get() - 1)
            springStrengthSlider.set(springStrengthSlider.get() - 1)

            if pressureCoefficientSlider.get() == 0 or springStrengthSlider.get() == 0:
                print("Resetting sliders")
                springStrengthSlider.set(100)
                pressureCoefficientSlider.set(10)
                getNewShape(sideSlider.get())
                break

        xspeed = max(-maxSpeed, min(xspeed, maxSpeed))
        yspeed = max(-maxSpeed, min(yspeed, maxSpeed))

        if abs(xspeed) < 1:
            xspeed = 0
        if abs(yspeed) < 1:
            yspeed = 0

        xpos += xspeed * deltaT
        ypos += yspeed * deltaT

        points[i]["xpos"] = xpos
        points[i]["ypos"] = ypos
        points[i]["xspeed"] = xspeed
        points[i]["yspeed"] = yspeed

    # Boundaries
    for i in range(len(points)):
        xpos = points[i]["xpos"]
        ypos = points[i]["ypos"]
        xspeed = points[i]["xspeed"]
        yspeed = points[i]["yspeed"]

        if ypos - (pointMass / 2) <= -200:
            ypos = -200 + pointMass / 2
            yspeed *= -friction * elasticity
            xspeed *= friction

        if xpos - (pointMass / 2) <= -300:
            xpos = -300 + pointMass / 2
            xspeed *= -friction * elasticity
            yspeed *= friction

        if xpos + (pointMass / 2) >= 300:
            xpos = 300 - pointMass / 2
            xspeed *= -friction * elasticity
            yspeed *= friction

        if ypos + (pointMass / 2) >= 300:
            ypos = 300 - pointMass / 2
            yspeed *= -friction * elasticity
            xspeed *= friction

        points[i]["xpos"] = xpos
        points[i]["ypos"] = ypos
        points[i]["xspeed"] = xspeed
        points[i]["yspeed"] = yspeed


# Start drawing
drawFrame()
root.mainloop()
