import turtle
import tkinter as tk
import math
import time

root = tk.Tk()
root.title("Ball Simulation Controls")

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

screen = turtle.TurtleScreen(canvas)
screen.tracer(0, 0)
functionsUsed = 0
t = turtle.RawTurtle(screen)
t.hideturtle()
t.speed(0)

#World parameters
size = 300
fps = 100
airResistance = 0.99
gravity = 10
friction = 0.89
simSpeed = 10

#Ball parameters
xpos = 0
ypos = 0
xspeed = 100
yspeed = 0
angle = 0
speed = 0

#Ball definition
ballSize = 10
elasticity = 0.8

#Sliders
gravitySlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Gravity")
gravitySlider.set(10)
gravitySlider.pack()

massSlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Ball size")
massSlider.set(20)
massSlider.pack()

frictionSlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", label="Friction")
frictionSlider.set(0.9)
frictionSlider.pack()

elasticitySlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", label="Elasticity")
elasticitySlider.set(0.8)
elasticitySlider.pack()

airResistanceSlider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", label="Air Resistance")
airResistanceSlider.set(0.99)
airResistanceSlider.pack()

#Counters
speedCounter = tk.Label(root, text="Speed: 0")
speedCounter.pack()

angleCounter = tk.Label(root, text="Angle: 0")
angleCounter.pack()

#Visibility of momentum
showForce = False
def toggleForceVis():
    global showForce
    showForce = not showForce

showForceButton = tk.Checkbutton(root, text="Show momentum", command=toggleForceVis)
showForceButton.pack()

#Apply force
angleSlider = tk.Scale(root, from_=0, to=360, resolution=15, orient="horizontal", label="Angle of force")
angleSlider.set(45)
angleSlider.pack(pady=(20, 0))

ForceButton = tk.Button(root, text="Apply Force", command=lambda: applyForce(100, angleSlider.get()))
ForceButton.pack()

def updateFrame():
    global xpos, ypos, fps, ballSize, angle, speed, showForce, simSpeed
    t.clear()

    #Drawing border
    t.penup()
    t.goto(-size, size)
    t.pendown()
    t.goto(size, size)
    t.goto(size, -size)
    t.goto(-size, -size)
    t.goto(-size, size)
    t.penup()

    #Drawing ball
    t.goto(xpos, ypos)
    t.dot(ballSize, "black")

    #Drawing momentum line
    if showForce == True:
        t.goto(xpos, ypos)
        t.setheading(angle)
        t.pencolor("red")
        t.pensize(max(5, ballSize / 10))
        t.pendown()
        t.forward(speed + ballSize / 4)
        t.penup()
        t.pencolor("black")
        t.pensize(1)

    deltaT = simSpeed / fps
    calculateFizix(deltaT)

    screen.update()
    root.after(round(1000 / fps) , updateFrame)

def calculateFizix(deltaT):
    global xpos, ypos, xspeed, yspeed, ballSize, fps, airResistance, angle, speed, gravity, friction, elasticity

    airResistance = airResistanceSlider.get()
    friction = frictionSlider.get()
    elasticity = elasticitySlider.get()
    gravity = gravitySlider.get()
    ballSize = massSlider.get() 
    
    #Gravity
    if ypos - ballSize / 2 >= -size:
        yspeed -= gravity * deltaT

    #Air resistance
    xspeed *= airResistance ** deltaT
    yspeed *= airResistance ** deltaT

    #Momentum
    xpos += xspeed * deltaT
    ypos += yspeed * deltaT

    #Bounce and boudary
    if xpos + ballSize / 2 >= size:
        xpos = size - ballSize / 2
        xspeed = -xspeed * elasticity
        xspeed *= friction
    elif xpos - ballSize / 2 <= -size:
        xpos = -size + ballSize / 2
        xspeed = -xspeed * elasticity
        xspeed *= friction

    if ypos + ballSize / 2 >= size:
        ypos = size - ballSize / 2
        yspeed = -yspeed * elasticity
        yspeed *= friction
    elif ypos - ballSize / 2 <= -size:
        ypos = -size + ballSize / 2
        yspeed = -yspeed * elasticity
        yspeed *= friction

    #Ground friction
    if ypos - ballSize / 2 <= -size + 0.1:
        xspeed *= friction

    #Zero speed
    if abs(xspeed) < 0.1:
        xspeed = 0
    if abs(yspeed) < 0.1:
        yspeed = 0

    #Calculate angle
    speed = math.sqrt(xspeed ** 2 + yspeed ** 2)
    if speed != 0:
        angle = math.degrees(math.atan2(yspeed, xspeed))
    else: 
        angle = 0

    angleCounter.config(text=f"Angle: {angle:.0f}")
    speedCounter.config(text=f"Speed: {speed:.0f}")

def applyForce(force, angle):
    global xspeed, yspeed
    angle = math.radians(angle)
    xspeed += math.cos(angle) * force
    yspeed += math.sin(angle) * force

updateFrame()
root.mainloop()
