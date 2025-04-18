import pygame
from entities.enemy.enemy import Enemy

class Projectile:
    def __init__(self, player, particle_system, speed=5, damage=1, lifespan=2000):
        direction = player.facing
        offset = 20

        if direction == 'up':
            self.x = player.x + player.width // 2
            self.y = player.y - offset
            self.vx, self.vy = 0, -speed
        elif direction == 'down':
            self.x = player.x + player.width // 2
            self.y = player.y + player.height + offset
            self.vx, self.vy = 0, speed
        elif direction == 'left':
            self.x = player.x - offset
            self.y = player.y + player.height // 2
            self.vx, self.vy = -speed, 0
        elif direction == 'right':
            self.x = player.x + player.width + offset
            self.y = player.y + player.height // 2
            self.vx, self.vy = speed, 0

        self.damage = damage
        self.lifespan = lifespan
        self.creation_time = pygame.time.get_ticks()
        self.alive = True
        self.particle_system = particle_system

        self.width = 8
        self.height = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, current_time, entities):
        if current_time - self.creation_time > self.lifespan:
            self.alive = False
            return

        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)

        for entity in entities:
            if isinstance(entity, Enemy):
                enemy = entity
                if self.rect.colliderect(enemy.get_rect()):
                    enemy.take_damage(
                        self.damage,
                        attacker_x=self.x,
                        attacker_y=self.y,
                        player_x=self.x,
                        player_y=self.y
                    )
                    self.on_hit(enemy)
                    break
            elif self.rect.colliderect(entity.get_rect()):
                self.on_hit(entity)
                break
                    

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)

    def on_hit(self, enemy):
        self.alive = False