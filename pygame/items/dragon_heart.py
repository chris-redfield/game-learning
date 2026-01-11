import pygame
import math
import random
from items.item import Item

class DragonHeart(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Dragon Heart"
        self.description = "The still-beating heart of an ancient dragon, pulsing with magical energy (Effect applied on pickup)"
        self.one_time_use = False  # Can't be used from inventory, effect already applied on pickup
        self.stackable = False     # Cannot stack in inventory
        
        # Custom size for the heart - slightly larger than default
        self.width = 36
        self.height = 36
        
        # Adjust pickup rect to match new dimensions
        self.pickup_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Custom bobbing properties - heart beats
        self.bob_height = 2        # Subtle vertical movement
        self.bob_speed = 0.04      # Regular pulse
        
        # Heart beat effect (separate from bobbing)
        self.beat_counter = random.random() * math.pi  # Start at random phase
        self.beat_speed = 0.03     # Heartbeat pulse speed
        self.beat_size = 1.0       # Normal size
        
        # Particles
        self.particles = []
        self.particle_timer = 0
        
        # Try to load the heart sprite
        try:
            self.sprite = pygame.image.load('assets/dragon_heart.png').convert_alpha()
            # Scale the sprite to match the desired dimensions
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
            print("Dragon heart sprite loaded successfully")
        except Exception as e:
            print(f"Error loading dragon heart sprite: {e}")
            # Create a heart placeholder
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw a heart shape
            heart_color = (200, 30, 30)  # Deep red
            
            # Draw two circles for the top of the heart
            pygame.draw.circle(self.sprite, heart_color, (10, 15), 8)
            pygame.draw.circle(self.sprite, heart_color, (26, 15), 8)
            
            # Draw a triangle for the bottom of the heart
            points = [(4, 18), (self.width//2, 32), (self.width-4, 18)]
            pygame.draw.polygon(self.sprite, heart_color, points)
            
            # Add a highlight
            pygame.draw.circle(self.sprite, (250, 100, 100), (12, 12), 3)
    
    def update(self, player=None):
        """Update heart animation, particles and check for collection"""
        # Update bobbing animation using parent logic
        super().update(None)  # Call parent but don't pass player yet
        
        # Update heartbeat effect
        self.beat_counter += self.beat_speed
        self.beat_size = 1.0 + 0.1 * abs(math.sin(self.beat_counter))
        
        # Update particles
        self.update_particles()
        
        # Create new particles (less frequently)
        self.particle_timer += 1
        if self.particle_timer >= 10 and not self.collected:  # Every 10 frames
            self.particle_timer = 0
            self.create_particle()
        
        # Custom collision detection with expanded player rect
        if player and not self.collected:
            # Get player rect
            player_rect = player.get_rect()
            # Get our updated pickup rect
            heart_rect = self.get_rect()
            
            # Check collision with slightly expanded player rect for better pickup
            expanded_player_rect = player_rect.inflate(8, 8)  # Make player collision area larger
            if heart_rect.colliderect(expanded_player_rect):
                return self.collect(player)
        
        return False
    
    def create_particle(self):
        """Create a red particle that floats upward"""
        # Random starting position within the heart
        start_x = self.x + random.randint(8, self.width - 8)
        start_y = self.y + random.randint(8, self.height - 8)
        
        # Random size, speed, and lifespan
        size = random.randint(2, 4)
        speed_x = random.uniform(-0.2, 0.2)
        speed_y = random.uniform(-0.5, -0.2)
        lifespan = random.randint(30, 60)
        
        # Random red color
        r = random.randint(200, 255)
        g = random.randint(20, 80)
        b = random.randint(20, 80)
        alpha = random.randint(150, 220)
        
        # Add to particles list
        self.particles.append({
            'x': start_x,
            'y': start_y,
            'size': size,
            'speed_x': speed_x,
            'speed_y': speed_y,
            'life': lifespan,
            'max_life': lifespan,
            'color': (r, g, b, alpha)
        })
    
    def update_particles(self):
        """Update and remove particles"""
        for particle in self.particles[:]:  # Use a copy to safely remove
            # Move the particle
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Decrease lifespan
            particle['life'] -= 1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw the heart with beat animation and particles"""
        if not self.collected:
            # Draw particles below the heart
            for particle in self.particles:
                # Calculate fade based on remaining life
                alpha = int(particle['color'][3] * (particle['life'] / particle['max_life']))
                color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                
                # Draw circle particle
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
                surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
            
            # Draw the heart with beat effect
            if hasattr(self, 'sprite') and self.sprite.get_width() > 1:
                # Calculate the scaled size based on beat
                scaled_width = int(self.width * self.beat_size)
                scaled_height = int(self.height * self.beat_size)
                
                # Calculate position offset to keep the heart centered
                x_offset = (scaled_width - self.width) // 2
                y_offset = (scaled_height - self.height) // 2
                
                # Scale the sprite
                scaled_sprite = pygame.transform.scale(self.sprite, (scaled_width, scaled_height))
                
                # Draw with bobbing and scaled for heartbeat
                surface.blit(scaled_sprite, (self.x - x_offset, self.y + self.bob_offset - y_offset))
    
    def get_icon(self):
        """Get a display icon for inventory"""
        icon_size = 40
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Scale the sprite to fit the icon
        temp = pygame.transform.scale(self.sprite, (icon_size - 6, icon_size - 6))
        # Center the sprite in the icon
        icon.blit(temp, (3, 3))
        
        return icon
    
    def collect(self, player):
        """Collect the heart and immediately activate its effect"""
        # If already collected, don't do anything
        if self.collected:
            return False
        
        # Try to activate the heart effect if player has attributes system
        effect_applied = False
        if hasattr(player, 'attributes') and hasattr(player.attributes, 'find_dragon_heart'):
            # Apply the heart effect
            effect_applied = player.attributes.find_dragon_heart()
            
            if effect_applied:
                # Create visual effect (if player has a particle system)
                if hasattr(player, 'particles') and hasattr(player.particles, 'create_fire_particles'):
                    player.particles.create_fire_particles(60)
                    
                # Provide success message
                print(f"Obtained the {self.name}! Its power flows through your veins.")
                print("Your magical abilities are enhanced! (Max mana increased)")
                
                # Only add to inventory if effect was successfully applied
                if hasattr(player, 'inventory'):
                    player.inventory.add_item(self)
            else:
                # Effect wasn't applied (already had it)
                print("You cannot absorb any more dragon hearts.")
        
        # Always mark as collected regardless of effect or inventory
        self.collected = True
        
        # Find the current block to remove this entity
        if hasattr(player, 'current_block_x') and hasattr(player, 'current_block_y'):
            # Access game_world via __main__ to avoid circular imports
            import __main__
            if hasattr(__main__, 'game_world'):
                block_key = (player.current_block_x, player.current_block_y)
                if block_key in __main__.game_world.blocks:
                    current_block = __main__.game_world.blocks[block_key]
                    if self in current_block.entities:
                        current_block.remove_entity(self)
                        print(f"Removed {self.name} from block")
        
        # Return True to indicate the item was collected
        return True
        
    def use(self, player):
        """Using the heart from inventory does nothing as its effect is applied on pickup"""
        # Instead of printing, return a message
        return f"The {self.name} has already been absorbed into your being."
    
    def get_rect(self):
        """Return the collision rectangle for pickup"""
        # Only return a valid rect if not collected
        if self.collected:
            # Return an empty rect that won't collide with anything
            return pygame.Rect(0, 0, 0, 0)
            
        # Calculate the actual rect based on the current beat size
        # This makes the collision area pulse with the heart
        scaled_width = int(self.width * self.beat_size)
        scaled_height = int(self.height * self.beat_size)
        
        # Calculate position offset to keep the heart centered
        x_offset = (scaled_width - self.width) // 2
        y_offset = (scaled_height - self.height) // 2
            
        # Update pickup rect to current position with bobbing and size adjustments
        self.pickup_rect.x = self.x - x_offset
        self.pickup_rect.y = self.y + self.bob_offset - y_offset
        self.pickup_rect.width = scaled_width
        self.pickup_rect.height = scaled_height
        
        return self.pickup_rect