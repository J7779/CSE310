import pygame
import math
from constants import *

class Bullet:
    def __init__(self, x, y, direction=-1, color=WHITE, bullet_type='normal', 
                 target=None, piercing=False, damage=1, asset_manager=None):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = direction * BULLET_SPEED
        self.color = color
        self.bullet_type = bullet_type
        self.target = target
        self.piercing = piercing
        self.damage = damage
        self.width = 3
        self.height = 10
        self.hit_enemies = set()
        self.asset_manager = asset_manager
        self.sprite = None
        self.angle = 0 
        
        if asset_manager:
            if bullet_type == 'laser':
                self.sprite = asset_manager.get_sprite('laser')
            else:
                self.sprite = asset_manager.get_sprite('missile')
        
        if bullet_type == 'laser':
            self.width = 4
            self.height = 30
            self.vy *= 1.5
        elif bullet_type == 'explosive':
            self.width = 8
            self.height = 8
        elif bullet_type == 'homing' and target:
            self.update_homing_direction()
            
    def update_homing_direction(self):
        if self.target and hasattr(self.target, 'rect'):
            dx = self.target.rect.centerx - self.x
            dy = self.target.rect.centery - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.vx = (dx / dist) * BULLET_SPEED * 0.8
                self.vy = (dy / dist) * BULLET_SPEED * 0.8
           
                self.angle = math.degrees(math.atan2(-self.vx, self.vy))
                
    def update(self, enemies=None):
        if self.bullet_type == 'homing' and self.target:
            self.update_homing_direction()
        else:
            # Calculate angle for regular bullets
            if self.vx != 0 or self.vy != 0:
                self.angle = math.degrees(math.atan2(-self.vx, self.vy))
            
        self.x += self.vx
        self.y += self.vy
        
        # Check if bullet is off screen
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            return False
        if self.x < -20 or self.x > SCREEN_WIDTH + 20:
            return False
        return True
        
    def get_rect(self):
        if self.sprite:
            return pygame.Rect(self.x - self.sprite.get_width()//2, 
                              self.y - self.sprite.get_height()//2, 
                              self.sprite.get_width(), self.sprite.get_height())
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
        
    def draw(self, screen):
        if self.sprite:
            # Draw sprite with rotation
            if self.bullet_type == 'laser':
            
                sprite_rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(self.sprite, sprite_rect)
            else:
                # Rotate missile sprite
                rotated_sprite = pygame.transform.rotate(self.sprite, self.angle)
                sprite_rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(rotated_sprite, sprite_rect)
                
            # Add glow effect for special bullets
            if self.bullet_type == 'explosive':
                pygame.draw.circle(screen, (255, 100, 0, 100), 
                                 (int(self.x), int(self.y)), 12, 2)
            elif self.bullet_type == 'homing':
                pygame.draw.circle(screen, (200, 0, 255, 100), 
                                 (int(self.x), int(self.y)), 10, 1)
        else:
            # Fallback to simple drawing
            if self.bullet_type == 'laser':
                pygame.draw.line(screen, self.color, 
                               (self.x, self.y - self.height//2),
                               (self.x, self.y + self.height//2), 4)
                # Add glow
                pygame.draw.line(screen, (255, 200, 200), 
                               (self.x, self.y - self.height//2),
                               (self.x, self.y + self.height//2), 2)
            elif self.bullet_type == 'explosive':
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                                 self.width//2)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 
                                 self.width//2 - 1, 1)
            else:
                # Regular bullet - draw as missile shape as I dont have time for a fully nice one haha
                missile_points = [
                    (self.x, self.y - self.height//2),  # Tip
                    (self.x - self.width//2, self.y),    # Left
                    (self.x - self.width//2, self.y + self.height//2),  # Left bottom
                    (self.x + self.width//2, self.y + self.height//2),  # Right bottom
                    (self.x + self.width//2, self.y),    # Right
                ]
                pygame.draw.polygon(screen, self.color, missile_points)
       
                pygame.draw.circle(screen, (255, 100, 0), 
                                 (int(self.x), int(self.y + self.height//2)), 2)
            
    def can_hit_enemy(self, enemy):
        if self.piercing:
            return id(enemy) not in self.hit_enemies
        return True
        
    def mark_enemy_hit(self, enemy):
        if self.piercing:
            self.hit_enemies.add(id(enemy))