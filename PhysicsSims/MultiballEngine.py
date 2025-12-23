import turtle
import tkinter as tk
import math
import time
import random

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

tBorder = turtle.RawTurtle(screen)
tBorder.hideturtle()
tBorder.speed(0)

#World parameters
size = 300
fps = 100
airResistance = 0.99
gravity = 10
friction = 0.89
elasticity = 0.8
simSpeed = 10

start = time.perf_counter()
end = start

#Balls
balls = [
    {"xpos": 0, "ypos": 0, "xspeed": 100, "yspeed": 0, "ballSize": 50, "color": "black"},
    ]

#Sliders
gravitySlider = tk.Scale(root, from_=0, to=100, resolution=1, orient="horizontal", label="Gravity")
gravitySlider.set(10)
gravitySlider.pack()

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
ballCounter = tk.Label(root, text="Balls: 0")
ballCounter.pack()

fpsCounter = tk.Label(root, text="FPS: 0")
fpsCounter.pack()

previousTime = time.time()
fpsUpdateTimer = time.time()
displayedFPS = 0

#Spawn ball
def spawBall():
    balls.append({"xpos": random.randint(-size, size), "ypos": random.randint(0, size), "xspeed": random.randint(-100, 100), "yspeed": random.randint(-100, 100), "ballSize": random.randint(40,60), "color": random.choice(("#FF0000","#FF1900","#FF3300","#FF4C00","#FF6600","#FF7F00","#FF9900","#FFB200","#FFCC00","#FFE500","#FFFF00","#E5FF00","#CCFF00","#B2FF00","#99FF00","#7FFF00","#66FF00","#4CFF00","#33FF00","#19FF00","#00FF00","#00FF19","#00FF33","#00FF4C","#00FF66","#00FF7F","#00FF99","#00FFB2","#00FFCC","#00FFE5","#00FFFF","#00E5FF","#00CCFF","#00B2FF","#0099FF","#007FFF","#0066FF","#004CFF","#0033FF","#0019FF","#0000FF","#1900FF","#3300FF","#4C00FF","#6600FF","#7F00FF","#9900FF","#B200FF","#CC00FF","#E500FF","#FF00FF"))})
    ballCounter.config(text="Balls: " + str(len(balls)))

spawBallButton = tk.Button(root, text="Spawn Ball", command=spawBall)
spawBallButton.pack()

#Drawing border
tBorder.penup()
tBorder.goto(-size, size)
tBorder.pendown()
tBorder.goto(size, size)
tBorder.goto(size, -size)
tBorder.goto(-size, -size)
tBorder.goto(-size, size)
tBorder.penup()

def updateFrame():
    global xpos, ypos, fps, ballSize, simSpeed, previousTime, fpsUpdateTimer, start, end
    t.clear()

    end = time.time()
    deltaT = end - start
    start = end

    #Drawing balls
    for ball in balls:
        t.penup()
        t.goto(ball["xpos"], ball["ypos"])
        t.dot(ball["ballSize"], ball["color"])

    # deltaT = simSpeed / fps
    calculateFizix(deltaT)

    #Calculating FPS
    currentTime = time.time()
    if currentTime - previousTime >= 0.01:
        Measuredfps = round(1 / (currentTime - previousTime))
    else:
        Measuredfps = fps
    
    if currentTime - fpsUpdateTimer >= 0.5:
        displayedFPS = round(Measuredfps)
        fpsCounter.config(text=f"FPS: {displayedFPS}")
        fpsUpdateTimer = currentTime

    previousTime = currentTime
    screen.update()
    root.after(10, updateFrame)

def calculateFizix(deltaT):
    global xpos, ypos, xspeed, yspeed, ballSize, fps, airResistance, gravity, friction, elasticity

    airResistance = airResistanceSlider.get()
    friction = frictionSlider.get()
    elasticity = elasticitySlider.get()
    gravity = gravitySlider.get()
    
    for ball in balls:
        xpos = ball["xpos"]
        ypos = ball["ypos"]
        xspeed = ball["xspeed"]
        yspeed = ball["yspeed"]
        ballSize = ball["ballSize"]

        calculateCollisions()

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
            xspeed = -xspeed * elasticity * friction
        elif xpos - ballSize / 2 <= -size:
            xpos = -size + ballSize / 2
            xspeed = -xspeed * elasticity * friction

        if ypos + ballSize / 2 >= size:
            ypos = size - ballSize / 2
            yspeed = -yspeed * elasticity * friction
        elif ypos - ballSize / 2 <= -size:
            ypos = -size + ballSize / 2
            yspeed = -yspeed * elasticity * friction

        #Ground friction
        if ypos - ballSize / 2 <= -size + 0.1:
            xspeed *= friction

        #Zero speed
        if abs(xspeed) < 0.1:
            xspeed = 0
        if abs(yspeed) < 0.1:
            yspeed = 0
        
        ball["xpos"] = xpos
        ball["ypos"] = ypos
        ball["xspeed"] = xspeed
        ball["yspeed"] = yspeed



def calculateCollisions():
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):

            #Finding important variables
            ball1 = balls[i]
            ball2 = balls[j]

            xDiff = ball2["xpos"] - ball1["xpos"]
            yDiff = ball2["ypos"] - ball1["ypos"]

            distance = math.hypot(xDiff, yDiff)
            minDistance = (ball1["ballSize"] + ball2["ballSize"]) / 2

            if distance < minDistance and distance != 0:
                #Getting normals and tangents
                normalX = xDiff / distance
                normalY = yDiff / distance

                tangentX = - normalY
                tangentY = normalX

                #Getting dot products
                DotProductTan1 = ball1["xspeed"] * tangentX + ball1["yspeed"] * tangentY
                DotProductTan2 = ball2["xspeed"] * tangentX + ball2["yspeed"] * tangentY

                DotProductNorm1 = ball1["xspeed"] * normalX + ball1["yspeed"] * normalY
                DotProductNorm2 = ball2["xspeed"] * normalX + ball2["yspeed"] * normalY

                #Including mass and elasticity
                Mass1 = ball1["ballSize"]
                Mass2 = ball2["ballSize"]
                e = elasticitySlider.get()
                NewDotProductNorm1 = (DotProductNorm1 * (Mass1 - Mass2 * e) + DotProductNorm2 * Mass2 * (1 + e)) / (Mass1 + Mass2)
                NewDotProductNorm2 = (DotProductNorm2 * (Mass2 - Mass1 * e) + DotProductNorm1 * Mass1 * (1 + e)) / (Mass1 + Mass2)

                #Applying the forces to the balls
                ball1["xspeed"] = NewDotProductNorm1 * normalX + DotProductTan1 * tangentX
                ball1["yspeed"] = NewDotProductNorm1 * normalY + DotProductTan1 * tangentY

                ball2["xspeed"] = NewDotProductNorm2 * normalX + DotProductTan2 * tangentX
                ball2["yspeed"] = NewDotProductNorm2 * normalY + DotProductTan2 * tangentY

                #Negating the overlap
                overlap = minDistance - distance

                ball1["xpos"] -= normalX * overlap / 2
                ball1["ypos"] -= normalY * overlap / 2

                ball2["xpos"] += normalX * overlap / 2
                ball2["ypos"] += normalY * overlap / 2

updateFrame()
root.mainloop()
