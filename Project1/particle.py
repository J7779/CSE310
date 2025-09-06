import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, size=3, speed=2, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed * random.uniform(0.5, 1.5)
        self.vy = math.sin(angle) * speed * random.uniform(0.5, 1.5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, 
                                          size=random.randint(2, 5),
                                          speed=random.uniform(1, 4)))
    
    def add_trail(self, x, y, color):
        self.particles.append(Particle(x, y, color, size=2, speed=0.5, lifetime=15))
        
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)