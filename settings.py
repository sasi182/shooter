import pygame
from os.path import join, dirname, abspath
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 32

# Projektbasisverzeichnis (geht von settings.py aus eine Ebene höher)
BASE_DIR = dirname(dirname(abspath(__file__)))

# Bildpfad-Helfer
def image_path(*parts):
    return join(BASE_DIR, 'images', *parts)
