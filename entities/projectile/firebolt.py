import pygame
from entities.projectile.projectile import Projectile
from entities.player.particles import ParticleSystem
import random

class Firebolt(Projectile):
    def __init__(self, player, particle_system, speed=6, damage=3, lifespan=400, magic_level=1):
        # Store magic level for size and effect scaling
        self.magic_level = magic_level
        
        # Calculate size based on magic level (base size + level bonus)
        self.bolt_size = 4 + min(8, magic_level)  # Caps at size 12 at level 8
        
        # Scale damage with magic level
        scaled_damage = damage + (magic_level - 1)  # +1 damage per level
        
        # Call parent constructor with scaled damage
        super().__init__(player, particle_system, speed, scaled_damage, lifespan)
        
        # Update the collision rectangle to match new size
        self.width = self.bolt_size * 2
        self.height = self.bolt_size * 2
        self.rect = pygame.Rect(
            self.x - self.bolt_size,  # Center horizontally
            self.y - self.bolt_size,  # Center vertically
            self.width, 
            self.height
        )
        
        # Set firebolt-specific properties
        self.inner_color = (255, 255, 0)  # Bright yellow core
        self.outer_color = (255, 100, 0)  # Orange outer
        
        # Scale particle effects with magic level
        self.trail_particles = 1 + magic_level // 2  # More trail particles at higher levels
        self.explosion_scale = 1.0 + (magic_level * 0.2)  # Explosion size scales with level

    def update(self, current_time, enemies):
        super().update(current_time, enemies)
        self.rect.x = self.x - self.bolt_size
        self.rect.y = self.y - self.bolt_size

        # Create fire trail with intensity based on magic level
        for _ in range(self.trail_particles):
            # Add slight offset for wider trails at higher levels
            offset_x = 0
            offset_y = 0
            
            if self.magic_level > 1:
                offset_x = random.uniform(-self.bolt_size/2, self.bolt_size/2)
                offset_y = random.uniform(-self.bolt_size/2, self.bolt_size/2)
                
            self.particle_system.create_fire_trail(self.x + offset_x, self.y + offset_y)

    def draw(self, surface):
        # Draw outer glow
        pygame.draw.circle(
            surface, 
            self.outer_color, 
            (int(self.x), int(self.y)), 
            self.bolt_size
        )
        
        # Draw inner core (smaller, brighter)
        inner_size = max(2, self.bolt_size // 2)
        pygame.draw.circle(
            surface, 
            self.inner_color, 
            (int(self.x), int(self.y)), 
            inner_size
        )

    def on_hit(self, enemy):
        super().on_hit(enemy)
        
        # Create scaled explosion
        self.create_scaled_explosion()
        
        # Add smoke effect for higher level bolts
        #if self.magic_level >= 3:
        #    self.particle_system.create_smoke_cloud(self.x, self.y)
    
    def create_scaled_explosion(self):
        """Create explosion with size and intensity scaled by magic level"""
        # For a bigger explosion with higher magic levels, we'll create 
        # multiple explosion points around the impact
        
        # Always create main explosion at impact point
        self.particle_system.create_fire_explosion(self.x, self.y)
        
        # For higher levels, add additional explosion points
        if self.magic_level >= 2:
            # Distance of secondary explosions scales with level
            explosion_radius = 5 + (self.magic_level * 2)
            
            # Number of secondary explosions based on level
            num_explosions = min(8, self.magic_level * 2)
            
            import random
            import math
            
            # Create secondary explosions in a circle around impact
            for i in range(num_explosions):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, explosion_radius)
                
                # Calculate position
                ex = self.x + math.cos(angle) * distance
                ey = self.y + math.sin(angle) * distance
                
                # Create smaller secondary explosion
                self.particle_system.create_fire_explosion(ex, ey)