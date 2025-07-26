from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_suface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -target_pos[0] + WINDOW_WIDTH / 2
        self.offset.y = -target_pos[1] + WINDOW_HEIGHT / 2
        
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground') and not hasattr(sprite, 'always_top')]
        top_sprites = [sprite for sprite in self if hasattr(sprite,'always_top')]

        for layer in [ground_sprites, object_sprites, top_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_suface.blit(sprite.image, sprite.rect.topleft + self.offset)