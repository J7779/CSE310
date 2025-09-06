import pygame
import math
from constants import *
from bullet import Bullet

class Player:
    def __init__(self, asset_manager=None):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.rect = pygame.Rect(self.x - PLAYER_SIZE[0]//2, 
                               self.y - PLAYER_SIZE[1]//2,
                               PLAYER_SIZE[0], PLAYER_SIZE[1])
        self.speed = PLAYER_SPEED
        self.last_shot = 0
        self.shot_cooldown = 250
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_end = 0
        self.shield_active = False
        self.ghost_active = False
        self.asset_manager = asset_manager
        self.sprite = None
        self.shield_sprite = None
        
        if asset_manager:
            self.sprite = asset_manager.get_sprite('player')
            self.shield_sprite = asset_manager.get_sprite('shield')
        
    def update(self, keys, current_time, powerup_manager):
        # Update speed based on powerups
        speed = self.speed
        if powerup_manager.is_active('SPEED_BOOST'):
            speed *= 1.5
            
        # Update invulnerability
        if self.invulnerable and current_time > self.invulnerable_end:
            self.invulnerable = False
            
        # Update shield status
        self.shield_active = powerup_manager.is_active('SHIELD')
        self.ghost_active = powerup_manager.is_active('GHOST')
        
        # Update shot cooldown based on powerups
        if powerup_manager.is_active('RAPID_FIRE'):
            self.shot_cooldown = 100
        else:
            self.shot_cooldown = 250
            
        # Movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.x += speed
            
        self.rect.centerx = self.x
        
    def shoot(self, current_time, powerup_manager, enemies):
        if current_time - self.last_shot < self.shot_cooldown:
            return []
            
        self.last_shot = current_time
        bullets = []
        
        # Determine bullet properties based on powerups
        color = WHITE
        bullet_type = 'normal'
        piercing = powerup_manager.is_active('PIERCING')
        
        if powerup_manager.is_active('LASER'):
            bullet_type = 'laser'
            color = RED
        elif powerup_manager.is_active('EXPLOSIVE'):
            bullet_type = 'explosive'
            color = ORANGE
        elif powerup_manager.is_active('HOMING') and enemies:
            bullet_type = 'homing'
            color = PURPLE
        elif powerup_manager.is_active('CHAIN_LIGHTNING'):
            bullet_type = 'lightning'
            color = YELLOW
            
        # Create bullets based on active powerups
        if powerup_manager.is_active('TRIPLE_SHOT'):
            for offset in [-15, 0, 15]:
                bullet = Bullet(self.rect.centerx + offset, self.rect.top, 
                              color=color, bullet_type=bullet_type, 
                              piercing=piercing, asset_manager=self.asset_manager)
                bullets.append(bullet)
        elif powerup_manager.is_active('SPREAD_SHOT'):
            for angle in [-30, -15, 0, 15, 30]:
                bullet = Bullet(self.rect.centerx, self.rect.top, 
                              color=color, bullet_type=bullet_type, 
                              piercing=piercing, asset_manager=self.asset_manager)
                rad = math.radians(angle)
                bullet.vx = math.sin(rad) * BULLET_SPEED
                bullet.vy = -math.cos(rad) * BULLET_SPEED
                bullets.append(bullet)
        else:
            # Single shot
            target = enemies[0] if bullet_type == 'homing' and enemies else None
            bullet = Bullet(self.rect.centerx, self.rect.top, 
                          color=color, bullet_type=bullet_type, 
                          target=target, piercing=piercing, 
                          asset_manager=self.asset_manager)
            bullets.append(bullet)
                                
        return bullets
        
    def take_damage(self, current_time):
        if self.shield_active:
            return False  # Shield blocks damage
        if self.ghost_active:
            return False  # Ghost mode avoids damage
        if self.invulnerable:
            return False
            
        self.lives -= 1
        self.invulnerable = True
        self.invulnerable_end = current_time + 2000  # 2 seconds of invulnerability could maybe do 4
        return self.lives <= 0
        
    def draw(self, screen):
        # Flash if invulnerable
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
            
        # Draw player ship
        if self.sprite:
            # Use sprite
            sprite_rect = self.sprite.get_rect(center=self.rect.center)
            if self.ghost_active:
                # Ghost effect - semi-transparent
                ghost_surface = self.sprite.copy()
                ghost_surface.set_alpha(128)
                screen.blit(ghost_surface, sprite_rect)
            else:
                screen.blit(self.sprite, sprite_rect)
        else:
            # Fallback to polygon drawing
            if self.ghost_active:
                points = [
                    (self.rect.centerx, self.rect.top),
                    (self.rect.left, self.rect.bottom),
                    (self.rect.centerx - 10, self.rect.centery + 5),
                    (self.rect.centerx + 10, self.rect.centery + 5),
                    (self.rect.right, self.rect.bottom)
                ]
                pygame.draw.polygon(screen, (100, 100, 255), points, 2)
            else:
                points = [
                    (self.rect.centerx, self.rect.top),
                    (self.rect.left, self.rect.bottom),
                    (self.rect.centerx - 10, self.rect.centery + 5),
                    (self.rect.centerx + 10, self.rect.centery + 5),
                    (self.rect.right, self.rect.bottom)
                ]
                pygame.draw.polygon(screen, BLUE, points)
            
        # Draw shield if active
        if self.shield_active:
            if self.shield_sprite:
                shield_rect = self.shield_sprite.get_rect(center=self.rect.center)
                screen.blit(self.shield_sprite, shield_rect)
            else:
                pygame.draw.circle(screen, CYAN, self.rect.center, 35, 2)
            
        # Draw lives with small ship sprites
        for i in range(self.lives):
            x = 10 + i * 35
            y = SCREEN_HEIGHT - 35
            if self.sprite:
                # Draw mini version of ship sprite
                mini_sprite = pygame.transform.scale(self.sprite, (25, 20))
                screen.blit(mini_sprite, (x, y))
            else:
                # Fallback to polygon
                points = [
                    (x + 10, y),
                    (x, y + 15),
                    (x + 5, y + 10),
                    (x + 15, y + 10),
                    (x + 20, y + 15)
                ]
                pygame.draw.polygon(screen, BLUE, points)