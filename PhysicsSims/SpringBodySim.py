import turtle
import tkinter as tk
import math
import random

#Setting up turtle and UI
root = tk.Tk()
root.title("Spring Simulation Controls")

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0
t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

#World parameters
gravity = 10
fps = 100
deltaT = 1 / fps
airResistance = 0.99

#Ball parameters
balls = [{"xpos": -50, "ypos": 50, "xspeed": 0, "yspeed": 0, "ballSize": 25},
         {"xpos": 50, "ypos": -50, "xspeed": 0, "yspeed": 0, "ballSize": 25},
         {"xpos": 50, "ypos": 50, "xspeed": 0, "yspeed": 0, "ballSize": 25},
         {"xpos": -50, "ypos": -50, "xspeed": 0, "yspeed": 0, "ballSize": 25}
         ]
balls.sort(key=lambda ball: ball["ypos"], reverse=True)
#Spring parameters
initLen = 50
length = initLen
springConstant = 0.4

#Controls
gravitySlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Gravity")
gravitySlider.set(10)
gravitySlider.pack()

airResSlider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient="horizontal", label="Air Resistance")
airResSlider.set(0.8)
airResSlider.pack()

dampenSlider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient="horizontal", label="Damping")
dampenSlider.set(0.1)
dampenSlider.pack()

springConstantSlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Spring Constant")
springConstantSlider.set(1)
springConstantSlider.pack()

def toggleColor():
    global colorIt
    colorIt = not colorIt

colorIt = False
colorButton = tk.Checkbutton(root, text="Toggle Color", command=toggleColor)
colorButton.pack()

def toggleStretch():
    global stretchIt
    stretchIt = not stretchIt

stretchIt = False
stretchButton = tk.Checkbutton(root, text="Toggle Stretch", command=toggleStretch)
stretchButton.pack()

def kickIt():
    balls[-1]["xspeed"] += random.randint(-300, 300)
    balls[-1]["yspeed"] += random.randint(-300, 300)

kickButton = tk.Button(root, text="Kick", command=kickIt)
kickButton.pack()

def Jump():
    balls.sort(key=lambda ball: ball["ypos"], reverse=True)
    balls[0]["yspeed"] -= 75
    balls[1]["yspeed"] -= 75

jumpButton = tk.Button(root, text="Jump", command=Jump)
jumpButton.pack()

lengthLabel = tk.Label(root, text="Length: " + str(length))
lengthLabel.pack()

connections = []
def getInitLen():
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            startDistance = math.hypot(balls[i]["xpos"] - balls[j]["xpos"], balls[i]["ypos"] - balls[j]["ypos"])
            connections.append([i, j, startDistance])

def drawFrame():
    t.clear()
    t.penup()

    #Drawing connections
    for a in range(len(connections)):
        ballIndex1 = connections[a][0]
        ballIndex2 = connections[a][1]
        initLen = connections[a][2] + 0.001
        distance = math.hypot(balls[ballIndex1]["xpos"] - balls[ballIndex2]["xpos"], balls[ballIndex1]["ypos"] - balls[ballIndex2]["ypos"])
        diff = distance - initLen
        stretch = abs(diff)
        stress = min(1, stretch / 100)

        if colorIt:
            red = int(255 * stress)
            green = int(255 * (1 - stress))
            t.pencolor(f"#{red:02x}{green:02x}00")
        else: 
            t.pencolor("brown")

        if stretchIt:
            t.pensize(min(10, max(2, (-diff + 20) / 5)))
        else:
            t.pensize(10)

        t.goto(balls[ballIndex1]["xpos"], balls[ballIndex1]["ypos"])
        t.pendown()
        t.goto(balls[ballIndex2]["xpos"], balls[ballIndex2]["ypos"])
        t.penup()
    
    #Drawing points
    for i in range(len(balls)):
        t.goto(balls[i]["xpos"], balls[i]["ypos"])
        t.dot(max(min(balls[i]["ballSize"], 120), 30), "black")

    #Drawing ground
    t.goto(-300, -200)
    t.pencolor("black")
    t.pensize(2)
    t.pendown()
    t.goto(300, -200)
    t.penup()

    calcSprings()
    calcFizix()

    screen.update()
    root.after(round(deltaT), drawFrame)

def calcFizix():

    gravity = gravitySlider.get()
    airResistance = (airResSlider.get() + 99) / 100

    #Applying forces exept springs
    for i in range(len(balls)):
        xpos = balls[i]["xpos"]
        ypos = balls[i]["ypos"]
        xspeed = balls[i]["xspeed"]
        yspeed = balls[i]["yspeed"]
        ballSize = balls[i]["ballSize"]

        #Gravity
        yspeed -= gravity * deltaT

        #Air resistance
        xspeed *= airResistance
        yspeed *= airResistance

        #Momentum
        xpos += xspeed * deltaT
        ypos += yspeed * deltaT

        #Boundaries
        if ypos - (ballSize / 2) <= -200:
            ypos = -200 + balls[i]["ballSize"] / 2
            yspeed *= -0.5

        if xpos - (ballSize / 2) <= -300:
            xpos = -300 + balls[i]["ballSize"] / 2
            xspeed *= -0.5

        if xpos + (ballSize / 2) >= 300:
            xpos = 300 - balls[i]["ballSize"] / 2
            xspeed *= -0.5

        balls[i]["xspeed"] = xspeed
        balls[i]["yspeed"] = yspeed
        balls[i]["xpos"] = xpos
        balls[i]["ypos"] = ypos

def calcSprings():
    springConstant = springConstantSlider.get()

    for a in range(len(connections)):

        #Getting info
        ballIndex1 = connections[a][0]
        ballIndex2 = connections[a][1]
        initLen = connections[a][2] + 0.001
        distance = math.hypot(balls[ballIndex1]["xpos"] - balls[ballIndex2]["xpos"], balls[ballIndex1]["ypos"] - balls[ballIndex2]["ypos"])
        
        #Getting ball1 variables
        xpos1 = balls[ballIndex1]["xpos"]
        ypos1 = balls[ballIndex1]["ypos"]
        xspeed1 = balls[ballIndex1]["xspeed"]
        yspeed1 = balls[ballIndex1]["yspeed"]
        ballSize1 = balls[ballIndex1]["ballSize"]
        mass1 = ballSize1 / 25

        #Getting ball2 variables
        xpos2 = balls[ballIndex2]["xpos"]
        ypos2 = balls[ballIndex2]["ypos"]
        xspeed2 = balls[ballIndex2]["xspeed"]
        yspeed2 = balls[ballIndex2]["yspeed"]
        ballSize2 = balls[ballIndex2]["ballSize"]
        mass2 = ballSize2 / 25

        #Calculating force
        angle = math.atan2(ypos1 - ypos2, xpos1 - xpos2)
        force = -(distance - initLen) * springConstant - dampenSlider.get() * ((xspeed1 - xspeed2) * math.cos(angle) + (yspeed1 - yspeed2) * math.sin(angle))

        #Applying spring force
        xspeed1 += math.cos(angle) * force / mass1 * deltaT
        yspeed1 += math.sin(angle) * force / mass1 * deltaT

        xspeed2 -= math.cos(angle) * force / mass2 * deltaT
        yspeed2 -= math.sin(angle) * force / mass2 * deltaT

        balls[ballIndex1]["xspeed"] = xspeed1
        balls[ballIndex1]["yspeed"] = yspeed1
        balls[ballIndex2]["xspeed"] = xspeed2
        balls[ballIndex2]["yspeed"] = yspeed2

getInitLen()
drawFrame()
root.mainloop()
