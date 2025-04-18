import pygame
import math
import random

# Import the original BloodParticle class instead of reimplementing it
from entities.blood_particle import BloodParticle

class ParticleSystem:
    """Manages XP and blood particles for the player"""
    def __init__(self, player):
        self.player = player
        self.xp_particles = []
        self.blood_particles = []
        self.max_blood_particles = 15
        
        # Map of stuck particles (organized by block coordinates)
        # Format: {(block_x, block_y): [(x, y, size, color, life), ...]}
        self.stuck_particles = {}
        self.current_block = (0, 0)
    
    def create_xp_particles(self, amount):
        """Create particles when XP is gained"""
        # Create 5-10 particles per XP point (capped for performance)
        particle_count = min(20, amount * 5)
        
        # Player center coordinates
        center_x = self.player.x + self.player.width / 2
        center_y = self.player.y + self.player.height / 2
        
        for _ in range(particle_count):
            # Random position around player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 30)
            
            pos_x = center_x + math.cos(angle) * distance
            pos_y = center_y + math.sin(angle) * distance
            
            # Random size
            size = random.randint(2, 4)
            
            # Golden color for XP particles
            self.xp_particles.append({
                'x': pos_x,
                'y': pos_y,
                'size': size,
                'color': (255, 215, 0),  # Gold color
                'life': random.randint(10, 20)
            })
    
    def spawn_blood_particles(self, damage_amount):
        """Create blood particles based on damage amount"""
        # Clear old particles
        self.blood_particles = []
        
        # Calculate particle count based on damage (more damage = more blood)
        particle_count = min(self.max_blood_particles, damage_amount * 3)
        
        # Player center coordinates
        center_x = self.player.x + self.player.width / 2
        center_y = self.player.y + self.player.height / 2
        
        # Create particles in a circular spray
        for _ in range(particle_count):
            # Random angle for particle direction
            angle = random.uniform(0, 2 * math.pi)
            
            # Direction vector from angle
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            # Create particle - use the original BloodParticle class
            particle = BloodParticle(center_x, center_y, dir_x, dir_y)
            self.blood_particles.append(particle)
    
    def spawn_enemy_blood(self, enemy):
        """Spawn blood particles from an enemy when hit with improved positioning"""
        # Player center coordinates (source of the hit)
        player_center_x = self.player.x + self.player.width / 2
        player_center_y = self.player.y + self.player.height / 2
        
        # Enemy center coordinates
        enemy_center_x = enemy.x + enemy.width / 2
        enemy_center_y = enemy.y + enemy.height / 2
        
        # Direction vector from player to enemy
        dir_x = enemy_center_x - player_center_x
        dir_y = enemy_center_y - player_center_y
        
        # Normalize direction
        length = max(0.1, math.sqrt(dir_x**2 + dir_y**2))
        dir_x /= length
        dir_y /= length
        
        # Calculate impact point (on the edge of the enemy facing the player)
        impact_offset = min(enemy.width, enemy.height) * 0.4  # 40% of enemy size
        impact_x = enemy_center_x - dir_x * impact_offset
        impact_y = enemy_center_y - dir_y * impact_offset
        
        # Create particles
        particle_count = random.randint(8, 12)
        
        # Initialize blood_particles list for enemy if needed
        if not hasattr(enemy, 'blood_particles'):
            enemy.blood_particles = []
        
        # Create particles with direction biased away from player
        for _ in range(particle_count):
            # Random angle in a cone facing away from player
            base_angle = math.atan2(dir_y, dir_x)
            angle_variation = random.uniform(-0.7, 0.7)  # +/- 40 degrees
            angle = base_angle + angle_variation
            
            # Final direction vector with some randomness
            particle_dir_x = math.cos(angle) 
            particle_dir_y = math.sin(angle)
            
            # Add a bit of randomness to particle starting position
            rand_offset = 3.0
            start_x = impact_x + random.uniform(-rand_offset, rand_offset)
            start_y = impact_y + random.uniform(-rand_offset, rand_offset)
            
            # Larger particles for enemies - use original BloodParticle
            size = random.randint(4, 8)
            
            # Create particle
            particle = BloodParticle(start_x, start_y, particle_dir_x, particle_dir_y, size)
            
            # Add to enemy's blood particles
            enemy.blood_particles.append(particle)
    
    def update(self, current_time, obstacles=None):
        """Update all particles"""
        # Update XP particles
        for particle in self.xp_particles[:]:
            # Decrease life
            particle['life'] -= 1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.xp_particles.remove(particle)
        
        # Update blood particles
        if obstacles:
            # Update each particle
            for particle in self.blood_particles[:]:
                particle.update(obstacles)
                
                # Remove inactive particles
                if not particle.active:
                    self.blood_particles.remove(particle)
                
                # If particle is stuck, add it to the stuck particles list for current block
                if hasattr(particle, 'stuck') and particle.stuck and particle in self.blood_particles:
                    self.blood_particles.remove(particle)
                    
                    # Make sure the current block has an entry in the dictionary
                    if self.current_block not in self.stuck_particles:
                        self.stuck_particles[self.current_block] = []
                    
                    # Store information about the stuck particle
                    self.stuck_particles[self.current_block].append((
                        particle.x,
                        particle.y,
                        particle.size,
                        particle.color,
                        particle.current_life
                    ))
    
    def draw_active_blood(self, surface):
        """Draw only the active (flying) blood particles"""
        # Draw active particles
        for particle in self.blood_particles:
            particle.draw(surface)

    def draw_stuck_blood(self, surface):
        """Draw only the stuck blood particles (should be called before drawing entities)"""
        # Draw stuck particles for the current block only
        if self.current_block in self.stuck_particles:
            for x, y, size, color, life in self.stuck_particles[self.current_block]:
                # Skip if outside screen (optimization)
                if x < -size or x > pygame.display.get_surface().get_width() + size or \
                y < -size or y > pygame.display.get_surface().get_height() + size:
                    continue
                
                # Calculate opacity based on life
                opacity = min(255, life * 10)  # Fade out based on life
                
                # Create a surface with alpha for the particle
                particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # Set the color with opacity
                color_with_alpha = (*color, opacity)
                pygame.draw.circle(particle_surface, color_with_alpha, 
                                (size//2, size//2), size//2)
                
                # Draw the particle
                surface.blit(particle_surface, (x - size//2, y - size//2))
    
    def draw_xp_particles(self, surface):
        """Draw XP particles"""
        if not self.xp_particles:
            return
            
        for particle in self.xp_particles:
            # Draw gold particle
            pygame.draw.circle(surface, particle['color'], 
                          (int(particle['x']), int(particle['y'])), 
                          particle['size'])
    
    def set_current_block(self, block_x, block_y):
        """Update the player's current block coordinates"""
        self.current_block = (block_x, block_y)
        
        # Initialize empty list for this block if it doesn't exist
        if self.current_block not in self.stuck_particles:
            self.stuck_particles[self.current_block] = []

    def create_fire_trail(self, x, y):
        # Small orange-red particles behind the projectile
        for _ in range(2):
            self.xp_particles.append({
                'x': x,
                'y': y,
                'size': random.randint(2, 4),
                'color': (255, random.randint(50, 150), 0),
                'life': random.randint(5, 15)
            })

    def create_fire_explosion(self, x, y):
        # Brief burst of bright orange particles upon impact
        for _ in range(10):
            self.xp_particles.append({
                'x': x,
                'y': y,
                'size': random.randint(4, 6),
                'color': (255, random.randint(50, 100), 0),
                'life': random.randint(10, 20)
            })

    def create_smoke_cloud(self, x, y):
        # Small black cloud after firebolt hits
        for _ in range(5):
            self.xp_particles.append({
                'x': x,
                'y': y,
                'size': random.randint(4, 8),
                'color': (30, 30, 30),
                'life': random.randint(20, 30)
            })