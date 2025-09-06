import pygame
import random
import math
from constants import *
from player import Player
from enemy import EnemyWave
from bullet import Bullet
from powerup import PowerupManager
from particle import ParticleSystem
from assets import AssetManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Ultimate")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 72)
        
        # Load assets
        self.asset_manager = AssetManager()
        self.background = self.asset_manager.get_sprite('star_field')
        self.explosion_frames = self.asset_manager.get_sprite('explosion_frames')
        
        # Background animation
        self.bg_offset = 0
        self.explosions = []  
        
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(self.asset_manager)
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemy_wave = EnemyWave(1, self.asset_manager)
        self.powerup_manager = PowerupManager()
        self.particle_system = ParticleSystem()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.score_multiplier = 1
        self.explosions = []
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    current_time = pygame.time.get_ticks()
                    bullets = self.player.shoot(current_time, self.powerup_manager, 
                                               self.enemy_wave.enemies)
                    self.player_bullets.extend(bullets)
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
        
    def add_explosion(self, x, y, size='medium'):
        self.explosions.append({
            'x': x,
            'y': y,
            'frame': 0,
            'size': size,
            'timer': 0
        })
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Animate background
        self.bg_offset += 0.5
        if self.bg_offset > SCREEN_HEIGHT:
            self.bg_offset = 0
        
        # Update player
        self.player.update(keys, current_time, self.powerup_manager)
        
        # Check for continuous shooting with space held was a little buggy at first
        if keys[pygame.K_SPACE]:
            bullets = self.player.shoot(current_time, self.powerup_manager, 
                                       self.enemy_wave.enemies)
            self.player_bullets.extend(bullets)
        
        # Update score multiplier
        self.score_multiplier = 2 if self.powerup_manager.is_active('DOUBLE_POINTS') else 1
        
        # Update enemies
        slow_time = self.powerup_manager.is_active('SLOW_TIME')
        self.enemy_wave.update(current_time, slow_time)
        
        # Enemy shooting
        if not self.powerup_manager.is_active('FREEZE'):
            enemy_bullets = self.enemy_wave.get_bullets()
            if slow_time:
                enemy_bullets = [b for b in enemy_bullets if random.random() < 0.3]
            self.enemy_bullets.extend(enemy_bullets)
        
        # Update bullets
        self.player_bullets = [b for b in self.player_bullets if b.update()]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.update()]
        
        # Update powerups
        self.powerup_manager.update(current_time)
        
        # Update particles
        self.particle_system.update()
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion['timer'] += 1
            if explosion['timer'] > 3:
                explosion['timer'] = 0
                explosion['frame'] += 1
                if explosion['frame'] >= len(self.explosion_frames):
                    self.explosions.remove(explosion)
        
        # Check for powerup collection
        collected = self.powerup_manager.check_collection(self.player.rect)
        if collected:
            self.powerup_manager.activate_powerup(collected.type, current_time)
            self.score += POWERUP_POINTS * self.score_multiplier
            self.particle_system.add_explosion(collected.x, collected.y, collected.color, 10)
            
            # Handle special instant powerups
            if collected.type == 'MEGA_BOMB':
                self.mega_bomb()
            elif collected.type == 'FREEZE':
                self.enemy_wave.freeze_all(3000, current_time)
        
        # Check bullet-enemy collisions
        for bullet in self.player_bullets[:]:
            for enemy in self.enemy_wave.enemies[:]:
                if enemy not in self.enemy_wave.enemies:
                    continue  # Skip if already removed
                    
                if bullet.get_rect().colliderect(enemy.rect) and bullet.can_hit_enemy(enemy):
                    # Handle chain lightning
                    if bullet.bullet_type == 'lightning':
                        self.chain_lightning(enemy, self.enemy_wave.enemies)
                    
                    # Handle explosive bullets
                    if bullet.bullet_type == 'explosive':
                        self.explosion_damage(enemy.rect.center, 50, 2)
                        self.add_explosion(enemy.rect.centerx, enemy.rect.centery, 'large')
                    
                    # Damage enemy
                    if enemy.take_damage(bullet.damage):
                        if enemy in self.enemy_wave.enemies:
                            self.enemy_wave.enemies.remove(enemy)
                            self.score += ENEMY_POINTS * self.score_multiplier
                            self.add_explosion(enemy.rect.centerx, enemy.rect.centery)
                            self.particle_system.add_explosion(enemy.rect.centerx, 
                                                              enemy.rect.centery, 
                                                              enemy.color, 15)
                    
                    bullet.mark_enemy_hit(enemy)
                    if not bullet.piercing:
                        if bullet in self.player_bullets:
                            self.player_bullets.remove(bullet)
                        break
        
        # Check enemy bullet-player collisions
        for bullet in self.enemy_bullets[:]:
            if bullet.get_rect().colliderect(self.player.rect):
                if self.player.take_damage(current_time):
                    self.game_over = True
                    self.add_explosion(self.player.rect.centerx, 
                                     self.player.rect.centery, 'large')
                    self.particle_system.add_explosion(self.player.rect.centerx,
                                                      self.player.rect.centery,
                                                      RED, 30)
                else:
                    self.add_explosion(bullet.x, bullet.y, 'small')
                self.enemy_bullets.remove(bullet)
        
        # Check enemy-player collisions
        for enemy in self.enemy_wave.enemies:
            if enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(current_time):
                    self.game_over = True
                    self.add_explosion(self.player.rect.centerx, 
                                     self.player.rect.centery, 'large')
                    self.particle_system.add_explosion(self.player.rect.centerx,
                                                      self.player.rect.centery,
                                                      RED, 30)
        
        # Check if wave is cleared
        if not self.enemy_wave.enemies:
            self.level += 1
            self.enemy_wave = EnemyWave(self.level, self.asset_manager)
            # Bonus points for clearing level
            self.score += 500 * self.level * self.score_multiplier
            # Spawn bonus powerup
            self.powerup_manager.spawn_powerup()
    
    def mega_bomb(self):
        # Destroy all enemies on screen with explosion effect
        for enemy in self.enemy_wave.enemies[:]:
            self.score += ENEMY_POINTS * self.score_multiplier
            self.add_explosion(enemy.rect.centerx, enemy.rect.centery, 'large')
            self.particle_system.add_explosion(enemy.rect.centerx, 
                                              enemy.rect.centery, 
                                              RED, 20)
        self.enemy_wave.enemies.clear()
        # Clear enemy bullets
        self.enemy_bullets.clear()
    
    def chain_lightning(self, hit_enemy, all_enemies):
        # Find nearby enemies
        chain_targets = []
        for enemy in all_enemies:
            if enemy != hit_enemy and enemy in all_enemies:
                dist = math.sqrt((enemy.rect.centerx - hit_enemy.rect.centerx)**2 + 
                               (enemy.rect.centery - hit_enemy.rect.centery)**2)
                if dist < 100:
                    chain_targets.append(enemy)
        
        # Damage up to 3 enemies
        for enemy in chain_targets[:3]:
            if enemy in all_enemies and enemy.take_damage(1):
                all_enemies.remove(enemy)
                self.score += ENEMY_POINTS * self.score_multiplier
                self.add_explosion(enemy.rect.centerx, enemy.rect.centery, 'small')
            if enemy in all_enemies:
                self.particle_system.add_explosion(enemy.rect.centerx, 
                                                  enemy.rect.centery, 
                                                  YELLOW, 10)
    
    def explosion_damage(self, center, radius, damage):
        # Damage all enemies in radius
        enemies_to_remove = []
        for enemy in self.enemy_wave.enemies[:]:
            dist = math.sqrt((enemy.rect.centerx - center[0])**2 + 
                           (enemy.rect.centery - center[1])**2)
            if dist < radius:
                if enemy.take_damage(damage):
                    enemies_to_remove.append(enemy)
                    self.score += ENEMY_POINTS * self.score_multiplier
                    self.particle_system.add_explosion(enemy.rect.centerx, 
                                                      enemy.rect.centery, 
                                                      ORANGE, 10)
        
        # Remove enemies after iteration
        for enemy in enemies_to_remove:
            if enemy in self.enemy_wave.enemies:
                self.enemy_wave.enemies.remove(enemy)
    
    def draw(self):
        # Draw scrolling background
        if self.background:
            # Draw two copies for seamless scrolling
            self.screen.blit(self.background, (0, self.bg_offset))
            self.screen.blit(self.background, (0, self.bg_offset - SCREEN_HEIGHT))
        else:
            self.screen.fill(BLACK)
            # Fallback stars
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Draw game objects
        if not self.game_over:
            self.player.draw(self.screen)
            
        self.enemy_wave.draw(self.screen)
        
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
            
        self.powerup_manager.draw(self.screen)
        self.particle_system.draw(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            if explosion['frame'] < len(self.explosion_frames):
                frame = self.explosion_frames[explosion['frame']]
                
                if explosion['size'] == 'small':
                    frame = pygame.transform.scale(frame, (30, 30))
                elif explosion['size'] == 'large':
                    frame = pygame.transform.scale(frame, (80, 80))
                
                frame_rect = frame.get_rect(center=(explosion['x'], explosion['y']))
                self.screen.blit(frame, frame_rect)

        # Score with glow effect to make it look nicer cause basic sucked
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_shadow = self.font.render(f"Score: {self.score}", True, (100, 100, 100))
        self.screen.blit(score_shadow, (SCREEN_WIDTH - 198, 12))
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 10))
        
        # Level with glow
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        level_shadow = self.font.render(f"Level: {self.level}", True, (100, 100, 100))
        self.screen.blit(level_shadow, (SCREEN_WIDTH - 198, 52))
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, 50))
        
        # Draw active powerups
        self.powerup_manager.draw_active_effects(self.screen)
        
        # Draw game over screen
        if self.game_over:
            # Darken screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text with glow
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            
            # Draw glow
            for i in range(3):
                glow = self.big_font.render("GAME OVER", True, (100, 0, 0))
                glow_rect = glow.get_rect(center=(SCREEN_WIDTH//2 + i, SCREEN_HEIGHT//2 - 50 + i))
                self.screen.blit(glow, glow_rect)
            
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            text_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(restart_text, text_rect)
            
            final_score = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            text_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(final_score, text_rect)
            
            high_level = self.font.render(f"Reached Level: {self.level}", True, CYAN)
            text_rect = high_level.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(high_level, text_rect)
        
        # Draw pause screen
        if self.paused and not self.game_over:
            # Darken screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(64)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.big_font.render("PAUSED", True, YELLOW)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(pause_text, text_rect)
            
            continue_text = self.small_font.render("Press P to continue", True, WHITE)
            text_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(continue_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()