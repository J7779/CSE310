import pygame
import random
import math
from constants import *
from bullet import Bullet

class Enemy:
    def __init__(self, x, y, enemy_type=0, asset_manager=None):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, ENEMY_SIZE[0], ENEMY_SIZE[1])
        self.colors = [GREEN, CYAN, YELLOW, ORANGE, PURPLE]
        self.color = self.colors[enemy_type % len(self.colors)]
        self.hp = enemy_type // 5 + 1 
        self.max_hp = self.hp
        self.frozen = False
        self.freeze_end = 0
        self.asset_manager = asset_manager
        self.sprite = None
        self.animation_frame = 0
        self.animation_timer = 0
        
        if asset_manager:
      
            sprite_type = (enemy_type % 3) + 1
            self.sprite = asset_manager.get_sprite(f'enemy{sprite_type}')
        
    def update(self, dx, dy, current_time):
        if self.frozen and current_time < self.freeze_end:
            return
        self.frozen = False
            
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Animate sprite
        self.animation_timer += 1
        if self.animation_timer > 30:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
        
    def draw(self, screen):
        if self.sprite:
            # Draw sprite with effects
            sprite_to_draw = self.sprite.copy()
            
            if self.frozen:
                # Apply ice effect
                ice_overlay = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
                ice_overlay.fill((150, 200, 255, 128))
                sprite_to_draw.blit(ice_overlay, (0, 0))
                
            # Damage effect - darken sprite based on HP
            if self.hp < self.max_hp:
                damage_alpha = int(255 * (self.hp / self.max_hp))
                sprite_to_draw.set_alpha(damage_alpha)
            
            # Wobble animation
            offset_y = math.sin(self.animation_timer * 0.1) * 2
            sprite_rect = sprite_to_draw.get_rect(center=(self.rect.centerx, 
                                                         self.rect.centery + offset_y))
            screen.blit(sprite_to_draw, sprite_rect)
            
            # Draw HP bar if damaged
            if self.hp < self.max_hp and self.hp > 0:
                bar_width = 30
                bar_height = 4
                bar_x = self.rect.centerx - bar_width // 2
                bar_y = self.rect.bottom + 2
                
                # Background
                pygame.draw.rect(screen, (100, 0, 0), 
                               (bar_x, bar_y, bar_width, bar_height))
                # Health
                health_width = int(bar_width * (self.hp / self.max_hp))
                pygame.draw.rect(screen, (0, 255, 0), 
                               (bar_x, bar_y, health_width, bar_height))
                
        else:
      
            if self.frozen:
                # Draw ice effect
                pygame.draw.rect(screen, CYAN, self.rect)
                pygame.draw.rect(screen, WHITE, self.rect, 2)
            else:
                # Draw enemy ship shape
                points = [
                    (self.rect.centerx, self.rect.top),
                    (self.rect.left, self.rect.bottom),
                    (self.rect.left + self.rect.width//4, self.rect.centery),
                    (self.rect.right - self.rect.width//4, self.rect.centery),
                    (self.rect.right, self.rect.bottom)
                ]
                pygame.draw.polygon(screen, self.color, points)
                
                # Draw HP indicator
                if self.hp > 1:
                    for i in range(self.hp - 1):
                        pygame.draw.circle(screen, RED, 
                                         (self.rect.centerx - 5 + i * 10, self.rect.centery), 2)
                    
    def shoot(self):
        if random.random() < 0.001: 
            return Bullet(self.rect.centerx, self.rect.bottom, 1, RED, 
                         asset_manager=self.asset_manager)
        return None
        
    def freeze(self, duration, current_time):
        self.frozen = True
        self.freeze_end = current_time + duration
        
    def take_damage(self, damage=1):
        self.hp -= damage
        return self.hp <= 0

class EnemyWave:
    def __init__(self, level=1, asset_manager=None):
        self.enemies = []
        self.direction = 1
        self.drop_timer = 0
        self.level = level
        self.speed_multiplier = 1.0
        self.asset_manager = asset_manager
        self.create_wave(level)
        
    def create_wave(self, level):
        # Calculate enemies based on level
        rows = min(3 + level // 3, 8) 
        cols = min(8 + level // 2, 12) 
        
        start_x = (SCREEN_WIDTH - (cols * (ENEMY_SIZE[0] + 10))) // 2
        start_y = 50
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (ENEMY_SIZE[0] + 10)
                y = start_y + row * (ENEMY_SIZE[1] + 10)
                enemy_type = (level - 1) + row
                self.enemies.append(Enemy(x, y, enemy_type, self.asset_manager))
                
    def update(self, current_time, slow_time=False):
        if not self.enemies:
            return
            
        speed = ENEMY_SPEED * self.speed_multiplier
        if slow_time:
            speed *= 0.3
            
       
        hit_edge = False
        for enemy in self.enemies:
            if (enemy.rect.left <= 0 and self.direction < 0) or \
               (enemy.rect.right >= SCREEN_WIDTH and self.direction > 0):
                hit_edge = True
                break
                
        if hit_edge:
            self.direction *= -1
            for enemy in self.enemies:
                enemy.update(0, ENEMY_DROP_DISTANCE, current_time)
            self.speed_multiplier += 0.1 
        else:
            for enemy in self.enemies:
                enemy.update(self.direction * speed, 0, current_time)
                
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
            
    def get_bullets(self):
        bullets = []
        for enemy in self.enemies:
            bullet = enemy.shoot()
            if bullet:
                bullets.append(bullet)
        return bullets
        
    def freeze_all(self, duration, current_time):
        for enemy in self.enemies:
            enemy.freeze(duration, current_time)