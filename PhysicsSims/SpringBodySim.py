import turtle
import tkinter as tk
import math
import random

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

springConstantSlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Spring Constant")
springConstantSlider.set(1)
springConstantSlider.pack()

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

    for a in range(len(connections)):
        ballIndex1 = connections[a][0]
        ballIndex2 = connections[a][1]
        initLen = connections[a][2] + 0.001
        distance = math.hypot(balls[ballIndex1]["xpos"] - balls[ballIndex2]["xpos"], balls[ballIndex1]["ypos"] - balls[ballIndex2]["ypos"])
        
        t.goto(balls[ballIndex1]["xpos"], balls[ballIndex1]["ypos"])
        t.pencolor("brown")
        t.pensize(min(10, max(2,(abs(distance - initLen) ** -1) * 500)))
        t.pendown()
        t.goto(balls[ballIndex2]["xpos"], balls[ballIndex2]["ypos"])
        t.penup()

    for i in range(len(balls)):
        t.goto(balls[i]["xpos"], balls[i]["ypos"])
        t.dot(max(min(balls[i]["ballSize"], 120), 30), "black")

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

    for i in range(len(balls)):
        xpos = balls[i]["xpos"]
        ypos = balls[i]["ypos"]
        xspeed = balls[i]["xspeed"]
        yspeed = balls[i]["yspeed"]
        ballSize = balls[i]["ballSize"]

        yspeed -= gravity * deltaT

        xspeed *= airResistance
        yspeed *= airResistance

        xpos += xspeed * deltaT
        ypos += yspeed * deltaT

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
        ballIndex1 = connections[a][0]
        ballIndex2 = connections[a][1]
        initLen = connections[a][2] + 0.001
        distance = math.hypot(balls[ballIndex1]["xpos"] - balls[ballIndex2]["xpos"], balls[ballIndex1]["ypos"] - balls[ballIndex2]["ypos"])
        
        xpos1 = balls[ballIndex1]["xpos"]
        ypos1 = balls[ballIndex1]["ypos"]
        xspeed1 = balls[ballIndex1]["xspeed"]
        yspeed1 = balls[ballIndex1]["yspeed"]
        ballSize1 = balls[ballIndex1]["ballSize"]
        mass1 = ballSize1 / 25

        xpos2 = balls[ballIndex2]["xpos"]
        ypos2 = balls[ballIndex2]["ypos"]
        xspeed2 = balls[ballIndex2]["xspeed"]
        yspeed2 = balls[ballIndex2]["yspeed"]
        ballSize2 = balls[ballIndex2]["ballSize"]
        mass2 = ballSize2 / 25

        angle = math.atan2(ypos1 - ypos2, xpos1 - xpos2)
        force = -(distance - initLen) * springConstant

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
