import pygame
import socket
import struct

# Initialize the game engine
pygame.init()
 
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

UDP_IP = ""
UDP_PORT = 7000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)

# Set the height and width of the screen
size = [400, 300]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Test vision data")

done = False
clock = pygame.time.Clock()
array = [0] * 20
 
while not done:
 
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)
     
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop

    try:
        data, addr = sock.recvfrom(1024)
        data = struct.unpack('20f', data)
        array = map(lambda x: int(x), data)
        print('Received:', array)
    except:
        pass


    # Clear the screen and set the screen background
    screen.fill(WHITE)

    for i in range(6):
        if i < 3:
            COLOR = RED
        else:
            COLOR = BLUE
        pygame.draw.circle(screen, COLOR, array[3*i:3*i+2], 3)

    pygame.draw.circle(screen, GREEN, array[18:20], 3)

    pygame.display.flip()

# Be IDLE friendly
pygame.quit()
