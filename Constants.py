import pygame
import wave
from cfg import WIDTH, HEIGHT
# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTGREY = (155, 155, 155)


# WINDOW
window = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.font.init()

# SOUND
pygame.mixer.init(frequency=wave.open('Clack.wav').getframerate())
clack_s = pygame.mixer.Sound("Clack.wav")


def clack():
    pygame.mixer.Sound.play(clack_s)


def font(size):
    return pygame.font.SysFont('Verdana', size)
