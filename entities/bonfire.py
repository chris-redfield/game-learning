import pygame
import math

class Bonfire:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48  # Size of the bonfire
        self.height = 48
        
        # Create collision rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Animation variables
        self.frame_index = 0
        self.animation_timer = 0
        self.state = "burning"  # Current animation state
        
        # Healing effect variables
        self.heal_particles_active = False
        self.heal_particles_timer = 0
        
        # Save/load functionality
        self.block_x = 0  # Will be set when placed in a block
        self.block_y = 0  # Will be set when placed in a block
        self.save_load_callback = None  # Will be set by main.py
        
        # Print debug info
        print(f"DEBUG: Bonfire created at ({x}, {y}) with rect {self.rect}")
        
        # Load sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load bonfire-specific sprites from sprite sheet"""
        self.sprites = {
            'burning': []  # Only one animation state for the bonfire
        }
        
        try:
            # Load the spritesheet
            bonfire_img = pygame.image.load('assets/bonfire-sprites.png').convert_alpha()
            
            # Define the frame positions based on the sprite sheet
            # These are the x-coordinates of each frame
            frame_positions = [
                0,    # Frame 1 start x-position
                32,   # Frame 2 start x-position
                64,   # Frame 3 start x-position
                96    # Frame 4 start x-position
            ]
            
            frame_width = 32   # Width of each frame
            frame_height = 32  # Height of each frame
            
            # Load each frame using defined positions
            for x_pos in frame_positions:
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(bonfire_img, (0, 0), (x_pos, 0, frame_width, frame_height))
                # Scale to desired size
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                self.sprites['burning'].append(scaled_frame)
                
        except Exception as e:
            print(f"Error loading bonfire sprites: {e}")
            # Create placeholder
            placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            placeholder.fill((200, 100, 0))
            self.sprites['burning'].append(placeholder)
    
    def get_rect(self):
        """Return the collision rectangle"""
        return self.rect
    
    def set_block_coordinates(self, x, y):
        """Set the block coordinates where this bonfire is located"""
        self.block_x = x
        self.block_y = y
    
    def is_origin_bonfire(self):
        """Check if this bonfire is at the origin (0,0) block"""
        return self.block_x == 0 and self.block_y == 0
    
    def update(self, dt=None, current_time=None):
        """Update the bonfire animation"""
        # Track animation time
        self.animation_timer += 1
        
        # Update animation frame when timer exceeds threshold
        if self.animation_timer >= 10:  # Adjust this value to control animation speed
            self.frame_index = (self.frame_index + 1) % len(self.sprites[self.state])
            self.animation_timer = 0
                
        # Update heal particles effect if active
        if self.heal_particles_active:
            self.heal_particles_timer += 1
            if self.heal_particles_timer > 60:  # Show particles for about 1 second
                self.heal_particles_active = False
                self.heal_particles_timer = 0
    
    def get_current_frame(self):
        """Get the current animation frame"""
        if self.state not in self.sprites or len(self.sprites[self.state]) == 0:
            print(f"WARNING: Missing animation state '{self.state}' for bonfire")
            # Return first frame of burning animation if available, or None
            return self.sprites['burning'][0] if 'burning' in self.sprites and self.sprites['burning'] else None
        
        # Make sure frame_index is within bounds
        if self.frame_index >= len(self.sprites[self.state]):
            self.frame_index = 0
        
        return self.sprites[self.state][self.frame_index]
    
    def interact(self, player, current_time=None):
        """Heal the player when they interact with the bonfire"""
        print("DEBUG: Bonfire interact method called!")
        
        # Calculate how much to heal (full health)
        heal_amount = player.attributes.max_health - player.attributes.current_health
        
        print(f"DEBUG: Player health before: {player.attributes.current_health}/{player.attributes.max_health}")
        print(f"DEBUG: Will try to heal for {heal_amount} HP")
        
        # Heal the player if needed
        healed = False
        if heal_amount > 0:
            # Heal the player to full health
            player.heal(heal_amount)
            
            # Activate heal particles effect
            self.heal_particles_active = True
            self.heal_particles_timer = 0
            
            print(f"Bonfire healed player for {heal_amount} HP")
            print(f"DEBUG: Player health after: {player.attributes.current_health}/{player.attributes.max_health}")
            healed = True
        else:
            print("Player already at full health")
        
        # If this is the origin bonfire, also show save/load dialog
        if self.is_origin_bonfire() and self.save_load_callback is not None:
            print("DEBUG: Origin bonfire - showing save/load dialog")
            self.save_load_callback()
        
        return healed or self.is_origin_bonfire()
    
    def draw(self, surface):
        """Draw the bonfire with current animation frame"""
        # Get the current animation frame
        current_frame = self.get_current_frame()
        
        if current_frame is None:
            # Draw a placeholder if frame is missing
            pygame.draw.rect(surface, (255, 100, 0), (self.x, self.y, self.width, self.height))
            return
        
        # Draw the bonfire
        surface.blit(current_frame, (self.x, self.y))
        
        # Draw heal particles if active
        if self.heal_particles_active:
            # Draw some simple particle effects (green healing particles)
            for i in range(8):
                particle_size = 3 + (self.heal_particles_timer % 3)
                particle_x = self.x + self.width//2 + math.cos(i * math.pi/4) * (20 + self.heal_particles_timer//5)
                particle_y = self.y + self.height//2 + math.sin(i * math.pi/4) * (20 + self.heal_particles_timer//5) - self.heal_particles_timer//3
                
                # Draw green healing particle
                pygame.draw.circle(surface, (100, 255, 100), (int(particle_x), int(particle_y)), particle_size)