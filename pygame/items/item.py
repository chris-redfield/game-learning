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
        self.stackable = True  # Whether this item can stack in inventory
        
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
        
        self.pickup_rect = pygame.Rect(
            self.x,           # Start at the same X as the sprite
            self.y,           # Start at the same Y as the sprite
            self.width,       # Full width of the sprite
            self.height       # Full height of the sprite
        )
   
    def get_rect(self):
        """Return the collision rectangle for pickup"""
        # Update pickup rect to current position with bobbing
        self.pickup_rect.x = self.x
        self.pickup_rect.y = self.y + self.bob_offset
        return self.pickup_rect

    def update(self, player=None):
        # Update bobbing animation
        self.bob_counter += self.bob_speed
        self.bob_offset = int(self.bob_height * (math.sin(self.bob_counter)))
        
        # Update pickup rect to current position with bobbing
        self.pickup_rect.x = self.x
        self.pickup_rect.y = self.y + self.bob_offset
        
        # Check for collection if player is provided
        if player and not self.collected:
            if self.pickup_rect.colliderect(player.get_rect()):
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
            # Try to add item to player inventory
            if hasattr(player, 'inventory'):
                if player.inventory.add_item(self):
                    self.collected = True
                    print(f"Collected {self.name}")
                    return True
                else:
                    print(f"Could not collect {self.name} - inventory full")
                    return False
            else:
                # If player doesn't have inventory, just mark as collected
                self.collected = True
                print(f"Collected {self.name} (no inventory)")
                return True
        return False
    
    def use(self, player):
        """Base use method - to be implemented by subclasses"""
        pass
        
    def get_icon(self):
        """Get a display icon for inventory
        
        Returns:
            Surface: A scaled copy of the sprite to use as an icon
        """
        # Default is to return a copy of the sprite at the correct size
        icon_size = 40
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Create a scaled copy of the sprite
        temp = pygame.transform.scale(self.sprite, (icon_size, icon_size))
        icon.blit(temp, (0, 0))
        
        return icon