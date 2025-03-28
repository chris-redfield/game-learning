import pygame
import random
import math

class Soul:
    """Experience orb that can be collected by the player"""
    def __init__(self, x, y, value=1):
        # Position
        self.x = x
        self.y = y
        # Visual size (30% of original)
        self.width = 6
        self.height = 6
        
        # Value (XP amount)
        self.value = value
        
        # Attraction properties
        self.attraction_radius = 100  # Distance at which soul starts getting attracted to player
        self.collection_radius = 10   # Distance at which soul is collected
        self.max_attraction_speed = 3.0  # Maximum speed when close to player
        
        # Animation properties
        self.bob_offset = 0
        self.bob_speed = 0.05
        self.bob_direction = 1
        self.bob_max = 1.5
        self.rotation = 0
        self.rotation_speed = 1
        
        # Particle effects
        self.particles = []
        self.particle_timer = 0
        self.particle_interval = 5  # Frames between particle creation
        
        # Glow effect
        self.glow_size = 9
        self.glow_alpha = 160
        self.pulse_counter = 0
        self.pulse_speed = 0.02
        
        # Debug flag
        self.debug_show_radius = False
        
        # Load or create sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load or create soul sprites"""
        try:
            # Create a small blue/green soul orb
            self.soul_image = pygame.Surface((6, 6), pygame.SRCALPHA)
            
            # Create a blue/green soul orb
            pygame.draw.circle(self.soul_image, (100, 200, 255), (3, 3), 2)  # Inner core
            pygame.draw.circle(self.soul_image, (150, 230, 255, 180), (3, 3), 3)  # Outer glow
            
            # Add a highlight
            pygame.draw.circle(self.soul_image, (220, 240, 255, 200), (2, 2), 1)
            
            print("Created soul orb graphic")
        except Exception as e:
            print(f"Error creating soul sprites: {e}")
            # Fallback to a simple colored circle
            self.soul_image = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(self.soul_image, (0, 200, 255), (3, 3), 2)
    
    def update(self, player):
        """Update soul animation and check for collection"""
        # Bobbing motion
        self.bob_offset += self.bob_speed * self.bob_direction
        if abs(self.bob_offset) >= self.bob_max:
            self.bob_direction *= -1
        
        # Rotation
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Update glow effect
        self.pulse_counter += self.pulse_speed
        self.glow_alpha = 120 + int(40 * math.sin(self.pulse_counter))
        
        # Create particles occasionally
        self.particle_timer += 1
        if self.particle_timer >= self.particle_interval:
            self.particle_timer = 0
            self.create_particle()
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Check for player proximity and handle attraction/collection
        if player:
            # Get player center coordinates
            player_rect = player.get_rect()
            player_center_x = player_rect.x + player_rect.width // 2
            player_center_y = player_rect.y + player_rect.height // 2
            
            # Get soul center coordinates
            soul_center_x = self.x + self.width // 2
            soul_center_y = self.y + self.height // 2
            
            # Calculate distance to player
            dx = player_center_x - soul_center_x
            dy = player_center_y - soul_center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If within attraction radius, move toward player
            if distance < self.attraction_radius:
                # Calculate normalized direction vector
                if distance > 0:  # Avoid division by zero
                    dx /= distance
                    dy /= distance
                
                # Speed increases as soul gets closer to player
                attraction_factor = 1.0 - (distance / self.attraction_radius)
                speed = self.max_attraction_speed * attraction_factor
                
                # Move soul toward player
                self.x += dx * speed
                self.y += dy * speed
                
                # Create extra particles when being attracted
                if random.random() < 0.3:
                    self.create_particle()
            
            # If very close to player, collect immediately
            if distance < self.collection_radius:
                # Immediately add particles to player's XP effect
                if hasattr(player, 'add_xp_particles'):
                    for _ in range(8):  # Create some extra particles
                        player_center_x = player_rect.x + player_rect.width // 2
                        player_center_y = player_rect.y + player_rect.height // 2
                        
                        # Create particle at player's position
                        particle = {
                            'x': player_center_x + random.uniform(-15, 15),
                            'y': player_center_y + random.uniform(-15, 15),
                            'size': random.randint(1, 3),
                            'color': (255, 215, 0),  # Gold color
                            'life': random.randint(10, 20)
                        }
                        
                        # Add to player's XP particles if available
                        if hasattr(player, 'xp_particles'):
                            player.xp_particles.append(particle)
                
                # No need to transfer existing particles - just collect the soul
                self.collect(player)
                return True  # Return True if collected
        
        return False  # Not collected
    
    def create_particle(self):
        """Create a small particle for the soul's trail effect"""
        # Random position around the soul
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(1.5, 2.5)
        
        pos_x = self.x + 3 + math.cos(angle) * distance
        pos_y = self.y + 3 + math.sin(angle) * distance
        
        # Random size and color
        size = random.randint(1, 2)
        
        # Blue-white color for soul particles
        blue = random.randint(150, 230)
        self.particles.append({
            'x': pos_x,
            'y': pos_y,
            'size': size,
            'color': (180, 220, blue),
            'life': random.randint(10, 20)
        })
    
    def collect(self, player):
        """Give XP to the player when collected"""
        # Add XP to player
        player.gain_xp(self.value)
        
        # Clear all particles to prevent lingering
        self.particles.clear()
        
        print(f"Soul collected! Player gained {self.value} XP")
    
    def get_rect(self):
        """Return a small rectangle for debugging"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        """Draw the soul with effects"""
        # Draw glow
        glow_surface = pygame.Surface((self.glow_size, self.glow_size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (100, 200, 255, self.glow_alpha), 
                          (self.glow_size//2, self.glow_size//2), 
                          self.glow_size//2)
        
        glow_x = self.x + 3 - self.glow_size//2
        glow_y = self.y + 3 - self.glow_size//2 + self.bob_offset
        surface.blit(glow_surface, (glow_x, glow_y))
        
        # Draw particles behind the soul
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Draw soul
        # Apply bobbing and rotation
        rotated_soul = pygame.transform.rotate(self.soul_image, self.rotation)
        soul_rect = rotated_soul.get_rect(center=(self.x + 3, self.y + 3 + self.bob_offset))
        surface.blit(rotated_soul, soul_rect.topleft)
        
        # Debug: Draw attraction radius if enabled
        if hasattr(self, 'debug_show_radius') and self.debug_show_radius:
            # Draw attraction radius
            pygame.draw.circle(surface, (0, 255, 0), 
                              (int(self.x + self.width//2), int(self.y + self.height//2)), 
                              self.attraction_radius, 1)
            
            # Draw collection radius
            pygame.draw.circle(surface, (255, 0, 0), 
                              (int(self.x + self.width//2), int(self.y + self.height//2)), 
                              self.collection_radius, 1)