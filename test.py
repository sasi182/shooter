import pygame
pygame.init()
surf = pygame.Surface((50, 50))
rect = surf.get_frect(center=(100, 100))
print(rect)
