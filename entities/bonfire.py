import pygame
import math

class Bonfire:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48  # Size of the bonfire
        self.height = 48
        
        # Create collision rect (slightly smaller than visual size for better gameplay)
        self.rect = pygame.Rect(self.x + 10, self.y + 20, self.width - 20, self.height - 20)
        
        # Animation variables
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
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
    
    def update(self, dt=None):
        """Update the bonfire animation"""
        # Track animation time
        self.animation_timer += 1
        
        # Update animation frame when timer exceeds threshold
        if self.animation_timer >= 10:  # Adjust this value to control animation speed
            self.frame_index = (self.frame_index + 1) % len(self.sprites['burning'])
            self.animation_timer = 0
    
    def get_current_frame(self):
        """Get the current animation frame"""
        return self.sprites['burning'][self.frame_index]
    
    def draw(self, surface):
        """Draw the bonfire with current animation frame"""
        # Get the current animation frame
        current_frame = self.get_current_frame()
        
        # Draw the bonfire
        surface.blit(current_frame, (self.x, self.y))