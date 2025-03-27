import pygame
import random
import math

class BloodParticle:
    """A class representing a blood particle for damage effects"""
    def __init__(self, x, y, direction_x, direction_y, size=None):
        # Position
        self.x = x
        self.y = y
        
        # Size (randomized if not provided)
        self.size = size if size else random.randint(4, 8)
        
        # Velocity
        speed = random.uniform(0.5, 3.0)
        self.vel_x = direction_x * speed
        self.vel_y = direction_y * speed
        
        # Physics properties
        self.gravity = 0.15
        self.friction = 0.92
        
        # Life properties
        self.life = random.randint(15, 30)  # How long the particle lives
        self.fade_start = self.life // 2     # When to start fading
        self.current_life = self.life
        
        # State
        self.active = True
        self.stuck = False
        self.stuck_offset_x = 0
        self.stuck_offset_y = 0
        
        # Color (randomize between dark and bright red)
        r = random.randint(120, 220)
        self.color = (r, random.randint(0, 30), random.randint(0, 30))
        
    def update(self, obstacles=None):
        """Update particle position and state"""
        # Skip if already stuck to a surface
        if self.stuck:
            self.current_life -= 1
            if self.current_life <= 0:
                self.active = False
            return
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Calculate new position
        new_x = self.x + self.vel_x
        new_y = self.y + self.vel_y
        
        # Check for collisions with obstacles
        if obstacles:
            particle_rect = pygame.Rect(new_x - self.size//2, new_y - self.size//2, 
                                       self.size, self.size)
            
            for obstacle in obstacles:
                obstacle_rect = obstacle.get_rect()
                if particle_rect.colliderect(obstacle_rect):
                    # Particle hit an obstacle, stick to it
                    self.stuck = True
                    
                    # Calculate offset to the obstacle for rendering
                    self.stuck_offset_x = self.x - obstacle.x
                    self.stuck_offset_y = self.y - obstacle.y
                    break
        
        # If not stuck, update position
        if not self.stuck:
            self.x = new_x
            self.y = new_y
            
            # Reduce life
            self.current_life -= 1
            if self.current_life <= 0:
                self.active = False
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        """Draw the particle with optional camera offset"""
        if not self.active:
            return
            
        # Calculate opacity based on remaining life
        if self.current_life < self.fade_start:
            opacity = int(255 * (self.current_life / self.fade_start))
        else:
            opacity = 255
            
        # Create a surface with alpha for the particle
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Set the color with opacity
        color_with_alpha = (*self.color, opacity)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                         (self.size//2, self.size//2), self.size//2)
        
        # Draw the particle
        if self.stuck:
            # The particle is stuck to an obstacle, don't apply camera offset
            surface.blit(particle_surface, (self.x - self.size//2, self.y - self.size//2))
        else:
            # Apply camera offset for free-floating particles
            surface.blit(particle_surface, 
                       (self.x - self.size//2 - camera_offset_x, 
                        self.y - self.size//2 - camera_offset_y))