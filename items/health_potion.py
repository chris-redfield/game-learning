import pygame
from items.item import Item

class HealthPotion(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Health Potion"
        self.description = "Restores health when consumed"
        self.heal_amount = 2  # Amount of health to restore
        
        # Rotation properties
        self.rotation_angle = 45  # 45 degrees counter-clockwise
        self.original_sprite = None
        
        # Try to load the health potion sprite
        try:
            self.original_sprite = pygame.image.load('assets/health-potion.png').convert_alpha()
            # Scale the sprite to match the desired dimensions
            self.original_sprite = pygame.transform.scale(self.original_sprite, (self.width, self.height))
            # Rotate the sprite
            self.sprite = pygame.transform.rotate(self.original_sprite, self.rotation_angle)
            print("Health potion sprite loaded successfully")
        except Exception as e:
            print(f"Error loading health potion sprite: {e}")
            # Create a red potion placeholder
            self.original_sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw a potion bottle shape
            bottle_color = (220, 50, 50)  # Red for health
            pygame.draw.rect(self.original_sprite, bottle_color, (8, 12, 16, 16))  # Bottle body
            pygame.draw.rect(self.original_sprite, bottle_color, (10, 6, 12, 6))   # Bottle neck
            pygame.draw.rect(self.original_sprite, (150, 150, 150), (11, 4, 10, 2)) # Bottle cap
            
            # Add a shine effect
            pygame.draw.circle(self.original_sprite, (250, 200, 200), (12, 15), 2)
            
            # Rotate the placeholder sprite
            self.sprite = pygame.transform.rotate(self.original_sprite, self.rotation_angle)
    
    def update(self, player=None):
        """Update potion animation and check for collection"""
        # Call the parent update method for basic animation and collection logic
        result = super().update(player)
        
        # Return the result from the parent method
        return result
    
    def draw(self, surface):
        """Draw the rotated potion with bobbing animation"""
        if not self.collected:
            # Get the size difference due to rotation
            offset_x = (self.sprite.get_width() - self.width) // 2
            offset_y = (self.sprite.get_height() - self.height) // 2
            
            # Draw with bobbing animation effect and adjusted position for rotation
            surface.blit(self.sprite, (self.x - offset_x, self.y + self.bob_offset - offset_y))
        
    def use(self, player):
        """Use the potion to heal the player"""
        if player.attributes.current_health < player.attributes.max_health:
            # Heal the player
            player.attributes.current_health = min(
                player.attributes.current_health + self.heal_amount,
                player.attributes.max_health
            )
            print(f"Used {self.name}, healed for {self.heal_amount} health!")
            return True
        else:
            print("Health is already full!")
            return False