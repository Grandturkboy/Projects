
# This is a useful file to speed up the setup phase of most projects, since it sets up all needed libraries, basic UI and a barebones event loop.

import pygame, sys, os
from pygame._sdl2.video import Window

# Importing pygui
sys.path.append("C:/Users/User/Documents/Programming/")  # This should be the path to the pygui file in order to import it
import pygui

# Setting up variables, window and GUI
pygame.init()
PROJECT_NAME = "Game Name"
WIN = pygame.display.set_mode((1536, 800), pygame.RESIZABLE)
pygame.display.set_caption(PROJECT_NAME)
win = Window.from_display_module()
win.maximize()
WIDTH, HEIGHT = WIN.get_size()

FPS = 60
SIDEBAR = 200
gui = pygui.GUI(SIDEBAR, PROJECT_NAME)

def pressed():
    print("Button 2 Pressed")

Card = gui.add_section("Controls")
fps_label = gui.add_label(Card, "FPS: --")
Sl = gui.add_slider(Card, "Demo Slider", 2, 10, 5, 1)
btn1 = gui.add_button(Card, "Button", callback=lambda: print("Button 1 Pressed"))
btn2 = gui.add_button(Card, "Another Button", callback=pressed)

def logic():
    pass

def drawWin():
    canvas = pygame.Rect(SIDEBAR, 0, WIDTH - SIDEBAR, HEIGHT)
    WIN.fill((30, 36, 54), canvas)

def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        delta = clock.tick(FPS) / 1000 
        fps_label.text = f"FPS: {int(clock.get_fps())}"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            gui.handle_event(event)
        
        logic()
        drawWin()
        gui.draw(WIN)
        pygame.display.flip()

if __name__ == "__main__":
    main()
