import math
import tkinter as tk
import turtle

# ── Root window ───────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("IK Solver")
root.state('zoomed')
root.configure(bg="#1a1a2e")

# ── Sidebar ───────────────────────────────────────────────────────────────────
SIDEBAR_BG = "#16213e"
SECTION_BG = "#0f3460"
ACCENT     = "#e94560"
TEXT_FG    = "#eaeaea"
MUTED_FG   = "#8892a4"
TROUGH_CLR = "#4a5568"   # visible trough so slider thumb is never lost
BACKGROUND = "#2D3444"

sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=250)
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)

header = tk.Frame(sidebar, bg=ACCENT, pady=12)
header.pack(fill=tk.X)
tk.Label(header, text="⚙  IK SOLVER", font=("Courier", 13, "bold"),
         bg=ACCENT, fg="white").pack()

def make_section(parent, title):
    wrapper = tk.Frame(parent, bg=SIDEBAR_BG, pady=4)
    wrapper.pack(fill=tk.X, padx=10)
    tk.Label(wrapper, text=title.upper(), font=("Courier", 8, "bold"),
             bg=SIDEBAR_BG, fg=MUTED_FG).pack(anchor="w")
    card = tk.Frame(wrapper, bg=SECTION_BG, padx=10, pady=8)
    card.pack(fill=tk.X)
    return card

def make_slider(parent, label, from_, to, default):
    row = tk.Frame(parent, bg=SECTION_BG)
    row.pack(fill=tk.X, pady=2)
    tk.Label(row, text=label, font=("Courier", 9), bg=SECTION_BG,
             fg=TEXT_FG, width=14, anchor="w").pack(side=tk.LEFT)
    val_var = tk.StringVar(value=str(default))
    tk.Label(row, textvariable=val_var, font=("Courier", 9, "bold"),
             bg=SECTION_BG, fg=ACCENT, width=4, anchor="e").pack(side=tk.RIGHT)
    scale = tk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                     bg=SECTION_BG, fg=TEXT_FG,
                     troughcolor=TROUGH_CLR,
                     activebackground=ACCENT,
                     highlightthickness=0, bd=0, sliderrelief="raised",
                     showvalue=False,
                     command=lambda v: val_var.set(v))
    scale.set(default)
    scale.pack(fill=tk.X, pady=(0, 4))
    return scale

arm_card    = make_section(sidebar, "Arm Segments")
l1_slider   = make_slider(arm_card, "Upper  (L1)", 50, 1000, 250)
l2_slider   = make_slider(arm_card, "Lower  (L2)", 50, 1000, 200)

motion_card   = make_section(sidebar, "Motion")
smooth_slider = make_slider(motion_card, "Smoothing", 1, 200, 30)

angle_card    = make_section(sidebar, "Angle Clamp")
angle_slider  = make_slider(angle_card, "Min  (°)", 1, 180, 30)
angle2_slider = make_slider(angle_card, "Max  (°)", 1, 180, 150)

toggle_card = make_section(sidebar, "Display")

showCircles_var = tk.BooleanVar(value=False)
monoLeg_var     = tk.BooleanVar(value=False)
otherLeg_var    = tk.BooleanVar(value=False)
stretch_var     = tk.BooleanVar(value=False)
showArea_var    = tk.BooleanVar(value=False)

def make_toggle(parent, label, var):
    cb = tk.Checkbutton(parent, text=label, variable=var,
                        font=("Courier", 9), bg=SECTION_BG,
                        fg=MUTED_FG, selectcolor=SECTION_BG,
                        activebackground=SECTION_BG, activeforeground=TEXT_FG,
                        relief="flat", anchor="w", padx=6, pady=3)
    cb.pack(fill=tk.X)
    return cb

make_toggle(toggle_card, "  Show Radius Circles", showCircles_var)
make_toggle(toggle_card, "  One Leg Only",         monoLeg_var)
make_toggle(toggle_card, "  Switch Active Leg",    otherLeg_var)
make_toggle(toggle_card, "  Stretch Mode",         stretch_var)
make_toggle(toggle_card, "  Show Reach Area",      showArea_var)

tk.Frame(sidebar, bg=SIDEBAR_BG, height=1).pack(fill=tk.X, pady=8, padx=10)
tk.Label(sidebar, text="Move mouse over canvas", font=("Courier", 8),
         bg=SIDEBAR_BG, fg=MUTED_FG).pack()
tk.Label(sidebar, text="to control the IK arm", font=("Courier", 8),
         bg=SIDEBAR_BG, fg=MUTED_FG).pack()

# ── Turtle canvas ─────────────────────────────────────────────────────────────
canvas = tk.Canvas(root, bg=BACKGROUND)
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

screen = turtle.TurtleScreen(canvas)
screen.bgcolor(BACKGROUND)
t = turtle.RawTurtle(screen)
t.hideturtle()
t.pencolor("gray")
t.pensize(10)
screen.tracer(0)
t.penup()

# ── Original IK globals ───────────────────────────────────────────────────────
xleg, yleg    = 450, -50
a, b          = 0, 0
anew, bnew    = 0, 0
minAngleclamp = 0
maxAngleclamp = 180

# expose as simple booleans so the original logic below is unchanged
def showCircles(): return showCircles_var.get()
def monoLeg():     return monoLeg_var.get()
def otherLeg():    return otherLeg_var.get()
def stretch():     return stretch_var.get()
def showArea():    return showArea_var.get()

# ── Mouse: coords relative to TurtleScreen centre ────────────────────────────
def on_motion(event):
    global anew, bnew
    # canvasx/canvasy account for the scroll region offset that TurtleScreen sets up,
    # matching exactly how turtle's own mouse handlers convert coordinates (see turtle.py:605)
    anew =  canvas.canvasx(event.x) / screen.xscale
    bnew = -canvas.canvasy(event.y) / screen.yscale

# ── Original helper functions (untouched) ─────────────────────────────────────
def getIKpoints(a, b, l1, l2):
    dx = a - xleg
    dy = b - yleg
    d = math.hypot(dx, dy)
    mid_len = (l1**2 - l2**2 + d**2) / (2 * d)
    h = math.sqrt(max(0, l1**2 - mid_len**2))
    mx = xleg + mid_len * (dx / d)
    my = yleg + mid_len * (dy / d)
    x1 = mx + h * (-dy / d)
    y1 = my + h * (dx / d)
    x2 = mx - h * (-dy / d)
    y2 = my - h * (dx / d)
    return x1, y1, x2, y2

def getAngle(l1, l2, dist):
    if dist > l1 + l2:
        dist = l1 + l2
    try:
        alfa = math.acos((l1**2 + l2**2 - dist**2) / (2 * l1 * l2))
    except:
        alfa = 0
    return alfa

# ── Original draw logic (untouched except t. instead of turtle.) ──────────────
def draw():
    global l1, l2, anew, bnew, a, b, minAngleclamp, maxAngleclamp

    l1 = l1_slider.get()
    l2 = l2_slider.get()

    smoothing = smooth_slider.get() / 100
    a += (anew - a) * smoothing
    b += (bnew - b) * smoothing

    dist = math.hypot(a - xleg, b - yleg)

    if dist > l1 + l2:
        l = l1 + l2
        dx = a - xleg
        dy = b - yleg
        a = xleg + dx * l / dist
        b = yleg + dy * l / dist
        x1 = x2 = xleg + (a - xleg) * (l1 / l)
        y1 = y2 = yleg + (b - yleg) * (l1 / l)
    else:
        x1, y1, x2, y2 = getIKpoints(a, b, l1, l2)

    alfa = getAngle(l1, l2, dist)
    minAngleclamp = math.radians(angle_slider.get())
    maxAngleclamp = math.radians(angle2_slider.get())
    minDist = math.sqrt(l1**2 + l2**2 - 2 * l1 * l2 * math.cos(minAngleclamp)) * 2
    maxDist = math.sqrt(l1**2 + l2**2 - 2 * l1 * l2 * math.cos(maxAngleclamp)) * 2
    distnew = math.hypot(xleg - a, yleg - b)

    if alfa < minAngleclamp or alfa > maxAngleclamp:
        if alfa < minAngleclamp:
            disttemp = math.sqrt(l1**2 + l2**2 - 2 * l1 * l2 * math.cos(minAngleclamp))
            state = 0.3
        elif alfa > maxAngleclamp:
            disttemp = math.sqrt(l1**2 + l2**2 - 2 * l1 * l2 * math.cos(maxAngleclamp))
            state = 0.05
        dx = a - xleg
        dy = b - yleg
        a = xleg + dx / distnew * disttemp
        b = yleg + dy / distnew * disttemp
        x1, y1, x2, y2 = getIKpoints(a, b, l1, l2)
    else:
        state = 0

    if stretch():
        a += (anew - a) * state
        b += (bnew - b) * state
        x1, y1, x2, y2 = getIKpoints(a, b, l1, l2)


    t.clear()

    if showArea():
        t.goto(xleg, yleg)
        t.dot(maxDist, TROUGH_CLR)
        t.dot(minDist, BACKGROUND)

    if showCircles():
        t.pencolor("yellow")
        t.pensize(5)
        t.goto(xleg, yleg - l1)
        t.pendown()
        t.circle(l1)
        t.penup()
        t.goto(a, b - l2)
        t.pendown()
        t.circle(l2)
        t.penup()

    t.pencolor("gray")
    t.pensize(10)

    if monoLeg() and not otherLeg() or not monoLeg():
        t.goto(xleg, yleg)
        t.pendown()
        t.goto(x1, y1)
        t.goto(a, b)
        t.penup()
        t.goto(x1, y1)
        t.dot(20, "red")
        t.pencolor("black")
        t.write(f"{math.degrees(getAngle(l1, l2, math.hypot(a - xleg, b - yleg))):.2f}", font=("Comic Sans", 12, "normal"))
        t.pencolor("gray")
    if monoLeg() and otherLeg() or not monoLeg():
        t.goto(xleg, yleg)
        t.pendown()
        t.goto(x2, y2)
        t.goto(a, b)
        t.penup()
        t.goto(x2, y2)
        t.dot(20, "green")
        t.pencolor("black")
        t.write(f"{math.degrees(getAngle(l1, l2, math.hypot(a - xleg, b - yleg))):.2f}", font=("Comic Sans", 12, "normal"))
        t.pencolor("gray")

    t.goto(xleg, yleg)
    t.dot(30, "black")
    t.goto(a, b)
    t.dot(20, "blue")

    screen.update()

def game_loop():
    draw()
    root.after(16, game_loop)

canvas.bind("<Motion>", on_motion)
game_loop()
root.mainloop()
