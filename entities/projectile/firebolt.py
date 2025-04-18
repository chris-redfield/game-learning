import pygame
from entities.projectile.projectile import Projectile
from entities.player.particles import ParticleSystem

class Firebolt(Projectile):
    def __init__(self, player, particle_system, speed=6, damage=3, lifespan=2000):
        super().__init__(player, particle_system, speed, damage, lifespan)

    def update(self, current_time, enemies):
        super().update(current_time, enemies)
        self.particle_system.create_fire_trail(self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 100, 0), (int(self.x), int(self.y)), 5)

    def on_hit(self, enemy):
        super().on_hit(enemy)
        self.particle_system.create_fire_explosion(self.x, self.y)
        #self.particle_system.create_smoke_cloud(self.x, self.y)