import pygame
import random

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32  # Size of the rock tile
        self.height = 32
        
        # Create collision rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Load direct rock image instead of spritesheet
        try:
            rock_choice = random.choice(['rock1.png', 'rock2.png', 'rock3.png'])
            self.sprite = pygame.image.load(f'assets/rock/{rock_choice}').convert_alpha()
            # Scale the sprite to match the desired dimensions
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except Exception as e:
            print(f"Error loading rock sprite: {e}")
            # Create placeholder
            self.sprite = pygame.Surface((self.width, self.height))
            self.sprite.fill((120, 120, 120))
    
    def get_rect(self):
        """Return the collision rectangle"""
        return self.rect
        
    def draw(self, surface):
        """Draw the rock"""
        surface.blit(self.sprite, (self.x, self.y))