import pygame
import json
import uuid

WIDTH = 750
HEIGH = 650

white = (255,255,255)
green = (0,255,0)
red   = (255,0,0)

f = open("data/go_to_from_with_angle.config", "r")
j = json.loads(f.read())
obstacles = j["red_team_positions"]
obstacles = []
f.close()

def f(x,y):
    x += 75
    x *= WIDTH/150.0
    y -= 65
    y = -y
    y *= HEIGH/130.0
    return int(x),int(y)

def g(r):
    return 5*r


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGH))
screen.fill(white)

file = open("data.txt", "r")
for line in file.readlines():
    pos = json.loads(line)
    pygame.draw.circle(screen, green, f(pos["x"], pos["y"]), 4, 0)
file.close()

for obstacle in obstacles:
    pygame.draw.circle(screen, red, f(obstacle[0], obstacle[1]), g(15), 5)
pygame.display.update()
pygame.image.save(screen, str(uuid.uuid1())+".jpg")
while True:
    pass