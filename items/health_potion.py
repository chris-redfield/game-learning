import pygame
from items.item import Item

class HealthPotion(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Health Potion"
        self.description = "Restores health when consumed"
        self.heal_amount = 15  # Amount of health to restore
        self.stackable = True  # Health potions can stack in inventory
        
        # Rotation properties
        self.rotation_angle = -45  # 45 degrees counter-clockwise
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
    
    def draw(self, surface):
        """Draw the rotated potion with bobbing animation"""
        if not self.collected:
            # Get the size difference due to rotation
            offset_x = (self.sprite.get_width() - self.width) // 2
            offset_y = (self.sprite.get_height() - self.height) // 2
            
            # Draw with bobbing animation effect and adjusted position for rotation
            surface.blit(self.sprite, (self.x - offset_x, self.y + self.bob_offset - offset_y))
    
    def get_icon(self):
        """Get a display icon for inventory"""
        # For potions, use the non-rotated version as the icon
        icon_size = 40
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Scale the original (non-rotated) sprite
        if self.original_sprite:
            temp = pygame.transform.scale(self.original_sprite, (icon_size - 8, icon_size - 8))
            # Center the sprite in the icon
            icon.blit(temp, (4, 4))
        else:
            # Fallback if somehow original sprite is missing
            icon.fill((220, 50, 50))
        
        return icon
        
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
        
    def get_rect(self):
        """Return the collision rectangle for the rotated potion"""
        # For rotated potions, we need to account for the rotation when checking collisions
        # Create a slightly larger collision rect to be more forgiving
        rotated_width = int(self.sprite.get_width() * 0.9)  # 90% of the rotated sprite width
        rotated_height = int(self.sprite.get_height() * 0.9)  # 90% of the rotated sprite height
        
        # Calculate the offset to center the collision rect on the visible sprite
        offset_x = (self.sprite.get_width() - self.width) // 2
        offset_y = (self.sprite.get_height() - self.height) // 2
        
        # Update the pickup rect to match the visible part of the rotated sprite
        self.pickup_rect.x = self.x - offset_x + (self.sprite.get_width() - rotated_width) // 2
        self.pickup_rect.y = self.y + self.bob_offset - offset_y + (self.sprite.get_height() - rotated_height) // 2
        self.pickup_rect.width = rotated_width
        self.pickup_rect.height = rotated_height
        
        return self.pickup_rect
    
    def update(self, player=None):
        """Update potion animation and check for collection"""
        # Update bobbing animation using parent logic
        super().update(None)  # Call parent but don't pass player yet
        
        # Custom collision detection for rotated potion
        if player and not self.collected:
            # Get player rect
            player_rect = player.get_rect()
            # Get our updated pickup rect
            potion_rect = self.get_rect()
            
            # Check collision with slightly expanded player rect for better pickup
            expanded_player_rect = player_rect.inflate(8, 8)  # Make player collision area larger
            if potion_rect.colliderect(expanded_player_rect):
                return self.collect(player)
        
        return False