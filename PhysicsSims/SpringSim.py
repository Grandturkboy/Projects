import turtle
import tkinter as tk
import math
import random

root = tk.Tk()
root.title("Spring Simulation Controls")

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0
t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

#World parameters
gravity = 10
anchory = 100
fps = 100
deltaT = 1 / fps
airResistance = 0.99

#Ball parameters
ballSize = 25
xpos = 0
ypos = 0
xspeed = 100
yspeed = 0
mass = ballSize / 25

#Spring parameters
initLen = 50
length = initLen
springConstant = 0.4

#Controls
sizeSlider = tk.Scale(root, from_=10, to=500, resolution=1, orient="horizontal", label="Size")
sizeSlider.set(40)
sizeSlider.pack()

gravitySlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Gravity")
gravitySlider.set(10)
gravitySlider.pack()

airResSlider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient="horizontal", label="Air Resistance")
airResSlider.set(0.8)
airResSlider.pack()

initLenSlider = tk.Scale(root, from_=0, to=200, resolution=1, orient="horizontal", label="Initial Length")
initLenSlider.set(100)
initLenSlider.pack()

springConstantSlider = tk.Scale(root, from_=0, to=10, resolution=0.1, orient="horizontal", label="Spring Constant")
springConstantSlider.set(1)
springConstantSlider.pack()

def kickIt():
    global xspeed, yspeed
    xspeed += random.randint(-300, 300)
    yspeed += random.randint(-300, 300)

kickButton = tk.Button(root, text="Kick", command=kickIt)
kickButton.pack()

lengthLabel = tk.Label(root, text="Length: " + str(length))
lengthLabel.pack()

def drawFrame():
    global xpos, ypos, xspeed, yspeed, length, initLen
    t.clear()
    t.penup()
    ballSize = sizeSlider.get()
    initLen = initLenSlider.get()

    #Drawing anchor, spring and ball
    t.goto(xpos, ypos)
    t.dot(max(min(ballSize, 120), 30), "black")
    t.pencolor("brown")
    t.pensize(min(10, max(2,((abs(length - initLen) + 0.01) ** -1) * 500)))
    t.pendown()
    t.goto(0, anchory)
    t.dot(20, "orange")
    t.penup()

    calcFizix()
    screen.update()
    root.after(round(deltaT), drawFrame)

def calcFizix():
    global xpos, ypos, xspeed, yspeed, length
    
    ballSize = sizeSlider.get() + 0.01
    gravity = gravitySlider.get()
    airResistance = (airResSlider.get() + 99) / 100
    initLen = initLenSlider.get()
    springConstant = springConstantSlider.get()

    length = math.hypot(xpos, ypos - anchory)
    lengthLabel.config(text="Length: " + str(round(length)))
    mass = ballSize / 25

    #Gravity
    yspeed -= gravity * deltaT

    #Air resistance
    xspeed *= airResistance
    yspeed *= airResistance

    #Finding angle and force
    angle = math.atan2(ypos - anchory, xpos)
    force = -(length - initLen) * springConstant
    
    #Applying the force to the speeds
    xspeed += math.cos(angle) * force / mass * deltaT
    yspeed += math.sin(angle) * force / mass * deltaT

    #Momentum
    xpos += xspeed * deltaT
    ypos += yspeed * deltaT

drawFrame()
root.mainloop()
