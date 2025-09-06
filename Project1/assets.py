import pygame
import math
import random

class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.create_all_sprites()
    
    def create_all_sprites(self):
        self.sprites['player'] = self.create_player_ship()
        self.sprites['enemy1'] = self.create_enemy_ship(1)
        self.sprites['enemy2'] = self.create_enemy_ship(2)
        self.sprites['enemy3'] = self.create_enemy_ship(3)
        self.sprites['missile'] = self.create_missile()
        self.sprites['laser'] = self.create_laser_beam()
        self.sprites['shield'] = None  
        self.sprites['explosion_frames'] = [] 
        self.sprites['star_field'] = None 
        
    def create_player_ship(self):
     
        surface = pygame.Surface((50, 40))
        surface.fill((0, 0, 0))
        surface.set_colorkey((0, 0, 0))
        
        # Simple triangle ship
        pygame.draw.polygon(surface, (0, 100, 255), [
            (25, 5),
            (5, 35),
            (15, 30),
            (25, 35),
            (35, 30),
            (45, 35)
        ])
        
        # Cockpit
        pygame.draw.circle(surface, (0, 200, 255), (25, 20), 4)
        
        return surface
    
    def create_enemy_ship(self, enemy_type):
      
        surface = pygame.Surface((40, 30))
        surface.fill((0, 0, 0))
        surface.set_colorkey((0, 0, 0))
        
        if enemy_type == 1:
            # Simple UFO
            color = (0, 255, 100)
            pygame.draw.ellipse(surface, color, (5, 10, 30, 12))
            pygame.draw.arc(surface, color, (10, 5, 20, 20), 0, math.pi, 3)
            
        elif enemy_type == 2:
            # Diamond enemy
            color = (255, 100, 0)
            pygame.draw.polygon(surface, color, [
                (20, 5),
                (35, 15),
                (20, 25),
                (5, 15)
            ])
            
        else:
            # Box enemy
            color = (200, 0, 255)
            pygame.draw.rect(surface, color, (8, 8, 24, 16))
            pygame.draw.rect(surface, (150, 0, 200), (8, 8, 24, 16), 2)
            
        return surface
    
    def create_missile(self):
    
        surface = pygame.Surface((6, 16))
        surface.fill((0, 0, 0))
        surface.set_colorkey((0, 0, 0))
        
        # Missile body
        pygame.draw.rect(surface, (200, 200, 200), (2, 4, 2, 8))
        
        # Warhead
        pygame.draw.polygon(surface, (255, 100, 100), [(3, 0), (0, 4), (6, 4)])
        
        # Exhaust
        pygame.draw.polygon(surface, (255, 200, 0), [(2, 12), (3, 16), (4, 12)])
        
        return surface
    
    def create_laser_beam(self):
     
        surface = pygame.Surface((4, 20))
        surface.fill((0, 0, 0))
        surface.set_colorkey((0, 0, 0))
        
        # Laser beam
        pygame.draw.rect(surface, (255, 100, 100), (1, 0, 2, 20))
        
        return surface
    
    def get_sprite(self, name):
    
        return self.sprites.get(name, None)