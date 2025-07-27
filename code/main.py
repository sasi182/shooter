from settings import *  # alles aus Settings importieren
from player import Player # Klasse Player aus player importiern
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from weapon_data import weapon_data
from os import walk
from os.path import join

from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()       # pygame initialisieren
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))   # Spielfenster definieren; aus settings.py
        pygame.display.set_caption('Survivor')  #Spielfenster Titel setzen
        self.clock = pygame.time.Clock()    # Erstellt Clock
        self.running = True     # wen False wird spiel Beendet

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0

        # Wapon-list
        self.weapon_types = list(weapon_data.keys())        # Liest die keys aus dem Diconary weapon_data // list wandet dict. ind liste um
        self.weapon_index = 0       # erste Waffe in der Liste
        self.gun_cooldown = weapon_data[self.weapon_types[self.weapon_index]]['cooldown'] # dict[Key[Key['Value'] = z.B. 300


        # enemy timer
        self.enemy_event = pygame.event.custom_type()       # erstelt einen Event
        pygame.time.set_timer(self.enemy_event, 1000)       # 1000ms ein Event in der Queue von pygame
        self.spawn_positions = []                           # erstelt leere Liste

        # audio
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.wav'))
        self.music = pygame.mixer.Sound(join('audio', 'music.mp3'))
        self.music.set_volume(0.3)
        self.music.play(loops=  -1)     # -1 Endlosschleide // 0 einmale abspielen // 1 einmal abspielen und eine Wiederholung 

        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surfs = {}  # erstellt ein leeres Dict.
        for weapon, data in weapon_data.items():    # for key, value in dictionary         
            path = join('images', 'gun', data['bullet_image'])
            self.bullet_surfs[weapon] = pygame.image.load(path).convert_alpha() # Läd alle bullet bilder mit dem Namen der dazugehöringen Waffe
    
        folders = list(walk(join('images', 'enemies')))[0][1]       # Liste aller Namen der Unterordner von enemies
        self.enemy_frames = {}  # leeres Dict.
        for folder in folders:
            self.enemy_frames[folder] = []
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):    # Numerische Sortierung der Bilder    
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)      # append = Element an Ende der Liste hinzufügen

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:    # linke Taste und can_shoot True
            self.shoot_sound.play() # Sound abspielen

            weapon = self.gun.weapon_type
            data = weapon_data[weapon]

            pos = self.gun.rect.center
            base_dir = self.gun.player_direction

            count = data['bullets_per_shot']
            spread = data['spread_angle']
            speed = data['bullet_speed']

            # Kugeln mit Winkelabweichung erzeugen
            for i in range(count):
                # Gleichmäßige Verteilung der Winkel, z.B. -spread/2 bis +spread/2
                if count > 1:
                    angle_offset = -spread/2 + (spread/(count-1)) * i
                else:
                    angle_offset = 0

                # Richtung rotieren
                dir_vector = base_dir.rotate(angle_offset)

                Bullet(self.bullet_surfs[weapon], pos, dir_vector, (self.all_sprites, self.bullet_sprites), speed)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()   # setz jetzigen Zeitpunkt in ms

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown: # wen Zeit jetzt minus Zeit Schuss grösser als cooldown
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world01.tmx'))  # lade ein TMX File für die Tiles 
        for x,y, image in map.get_layer_by_name('ground').tiles():      # X und Y sind nur punkte auf dem Korindatensystem von der map
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)  # X und Y mit anzahl Pixel von Tile multiplizieren

        for obj in map.get_layer_by_name('collisions'):
            if hasattr(obj, "image") and obj.image:  # objekt hat attribut image und image ist nicht None
                CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
            else:  # nur Rechteck
                surf = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
                # Optional: Debugfarbe sichtbar machen
                surf.fill((255, 0, 0, 100))  # rot halbtransparent
                CollisionSprite((obj.x, obj.y), surf, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('entities'):
            if obj.name == 'Player': 
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.weapon_types[self.weapon_index], self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()
   
    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def run(self):
        while self.running:     # Loop solange self.running True ist
            #dt
            dt=self.clock.tick() / 1000      #Zeit seit letztem Frame in Millisekunden /1000 = Sekunden

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # Wen pygmae Event Quit 
                        self.running = False    # self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: # Rechtsklick
                        self.weapon_index = (self.weapon_index + 1) % len(self.weapon_types) # Len berechnet Rest einer Division // 0/3=0 1/3=1 2/3=2 3/3=0
                        self.gun.kill()  # Prite der alten Waffe entfernen
                        self.gun = Gun(self.player, self.weapon_types[self.weapon_index], self.all_sprites)

            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            #draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
            

        pygame.quit()

if __name__== '__main__':
    game = Game()
    game.run()
