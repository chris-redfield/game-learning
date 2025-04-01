import pygame
import math


class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32  # Default size for items
        self.height = 32
        self.name = "Generic Item"
        self.description = "An item in the game world"
        self.collected = False
        
        # Animation properties
        self.bob_height = 4  # How high the item floats up and down
        self.bob_speed = 0.03  # Speed of the floating animation
        self.bob_offset = 0  # Current offset from original position
        self.bob_counter = 0  # Counter for the bobbing animation
        
        # Create collision/pickup rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # The base Item class doesn't load an image
        # Subclasses should implement their own sprites
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill((200, 200, 200))  # Default gray placeholder
        
    def get_rect(self):
        """Return the collision rectangle"""
        return self.rect
    
    def update(self, player=None):
        """Update item state and check for collection
        
        Args:
            player: Optional player entity to check for collection
            
        Returns:
            bool: True if item was collected, False otherwise
        """
        # Update bobbing animation
        self.bob_counter += self.bob_speed
        self.bob_offset = int(self.bob_height * (math.sin(self.bob_counter)))
        
        # Update the rect position for collision detection
        self.rect.y = self.y + self.bob_offset
        
        # Check for collection if player is provided
        if player and not self.collected:
            if self.rect.colliderect(player.get_rect()):
                return self.collect(player)
        return False
        
    def draw(self, surface):
        """Draw the item if not collected"""
        if not self.collected:
            # Draw with bobbing animation effect
            surface.blit(self.sprite, (self.x, self.y + self.bob_offset))
    
    def collect(self, player):
        """Base collect method - to be implemented by subclasses"""
        if not self.collected:
            self.collected = True
            print(f"Collected {self.name}")
            return True
        return False
    
    def use(self, player):
        """Base use method - to be implemented by subclasses"""
        pass