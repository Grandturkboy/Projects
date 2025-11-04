import turtle
import tkinter as tk
import math

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
deltaT = 1000 / fps

#Ball parameters
ballSize = 10
xpos = 0
ypos = 0
xspeed = 100
yspeed = 0

#Spring parameters
length = math.hypot(xpos, ypos - anchory) #Probably/hopefully 100 at start
initLen = 50

def drawFrame():
    t.clear
    t.penup()

    #Drawing anchor, spring and ball
    t.goto(0, anchory)
    t.dot(5, "orange")
    t.pencolor("brown")
    t.pensize(length ** -1)
    t.pendown()
    t.goto(xpos, ypos)
    t.penup
    t.dot(ballSize, "black")

    calcFizix()
    screen.update()
    root.after(round(deltaT), drawFrame)

def calcFizix():
    
    #Gravity
    yspeed -= gravity * deltaT

    #Momentum
    xpos += xspeed * deltaT
    ypos += yspeed * deltaT

    #Finding angle to apply force

    #Finding applied force x and y

    #Applying the force to the speeds
