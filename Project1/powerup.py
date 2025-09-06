import pygame
import random
import math
from constants import *

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(list(POWERUP_TYPES.keys()))
        self.color = POWERUP_TYPES[self.type]['color']
        self.symbol = POWERUP_TYPES[self.type]['symbol']
        self.duration = POWERUP_TYPES[self.type]['duration']
        self.rect = pygame.Rect(x - POWERUP_SIZE[0]//2, y - POWERUP_SIZE[1]//2, 
                               POWERUP_SIZE[0], POWERUP_SIZE[1])
        self.pulse = 0
        
    def update(self):
        self.y += POWERUP_FALL_SPEED
        self.rect.y = self.y - POWERUP_SIZE[1]//2
        self.pulse += 0.1
        
        # Remove if off screen
        if self.y > SCREEN_HEIGHT + 50:
            return False
        return True
        
    def draw(self, screen):
        # Pulsing effect
        pulse_size = int(abs(math.sin(self.pulse)) * 3)
        
        # Draw powerup box
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw glowing effect
        glow_rect = self.rect.inflate(pulse_size * 2, pulse_size * 2)
        pygame.draw.rect(screen, self.color, glow_rect, 1)
        
        # Draw symbol
        font = pygame.font.Font(None, 20)
        text = font.render(self.symbol, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class PowerupManager:
    def __init__(self):
        self.powerups = []
        self.active_effects = {}
        self.last_spawn = 0
        self.spawn_interval = 5000 
        
    def update(self, current_time):
        # Spawn new powerups
        if current_time - self.last_spawn > self.spawn_interval:
            if random.random() < 0.3:
                self.spawn_powerup()
                self.last_spawn = current_time
                
        # Update existing powerups
        self.powerups = [p for p in self.powerups if p.update()]
        
        # Update active effects
        expired = []
        for effect, end_time in self.active_effects.items():
            if end_time > 0 and current_time > end_time:
                expired.append(effect)
        for effect in expired:
            del self.active_effects[effect]
            
    def spawn_powerup(self):
        x = random.randint(POWERUP_SIZE[0], SCREEN_WIDTH - POWERUP_SIZE[0])
        self.powerups.append(Powerup(x, -POWERUP_SIZE[1]))
        
    def check_collection(self, player_rect):
        for powerup in self.powerups[:]:
            if powerup.rect.colliderect(player_rect):
                self.powerups.remove(powerup)
                return powerup
        return None
        
    def activate_powerup(self, powerup_type, current_time):
        duration = POWERUP_TYPES[powerup_type]['duration']
        if duration > 0:
            self.active_effects[powerup_type] = current_time + duration
        else:
            # Instant effect powerups
            self.active_effects[powerup_type] = -1
            
    def is_active(self, powerup_type):
        return powerup_type in self.active_effects
        
    def draw(self, screen):
        for powerup in self.powerups:
            powerup.draw(screen)
            
    def draw_active_effects(self, screen):
        y = 10
        font = pygame.font.Font(None, 24)
        for effect in self.active_effects:
            color = POWERUP_TYPES[effect]['color']
            text = font.render(f"{effect}: Active", True, color)
            screen.blit(text, (10, y))
            y += 25