import pygame
import math
from items.item import Item

class AncientScroll(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Ancient Scroll"
        self.description = "A weathered scroll with arcane knowledge that enhances your learning (Effect applied on pickup)"
        self.one_time_use = False  # Can't be used from inventory, effect already applied on pickup
        self.stackable = False     # Cannot stack in inventory
        
        # Custom size for the scroll - slightly larger than default
        self.width = 40
        self.height = 40
        
        # Adjust pickup rect to match new dimensions
        self.pickup_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Different bobbing properties for the scroll
        self.bob_height = 3      # Slightly less bobbing than other items
        self.bob_speed = 0.025   # Slower bobbing animation
        
        # Glow effect parameters
        self.glow_counter = 0
        self.glow_speed = 0.02
        self.glow_intensity = 0
        
        # Try to load the scroll sprite
        try:
            self.sprite = pygame.image.load('assets/ancient_scroll.png').convert_alpha()
            # Scale the sprite to match the desired dimensions
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
            print("Ancient scroll sprite loaded successfully")
        except Exception as e:
            print(f"Error loading ancient scroll sprite: {e}")
            # Create a scroll placeholder
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw a scroll shape
            scroll_color = (220, 190, 120)  # Parchment color
            pygame.draw.rect(self.sprite, scroll_color, (5, 5, 30, 30), border_radius=2)
            
            # Draw scroll edges
            edge_color = (180, 140, 80)  # Darker edge color
            pygame.draw.rect(self.sprite, edge_color, (3, 3, 34, 34), 2, border_radius=3)
            
            # Draw some text lines
            line_color = (60, 40, 20)  # Dark text color
            for i in range(5):
                pygame.draw.line(self.sprite, line_color, (10, 10 + i*5), (30, 10 + i*5), 1)
    
    def update(self, player=None):
        """Update scroll animation and check for collection"""
        # Update bobbing animation using parent logic
        super().update(None)  # Call parent but don't pass player yet
        
        # Update glow effect (not part of parent update)
        if not self.collected:
            self.glow_counter += self.glow_speed
            self.glow_intensity = abs(math.sin(self.glow_counter)) * 0.5  # Pulse between 0 and 0.5
            
            # Custom collision detection for scroll
            if player and not self.collected:
                # Get player rect
                player_rect = player.get_rect()
                # Get our updated pickup rect
                scroll_rect = self.get_rect()
                
                # Check collision with slightly expanded player rect for better pickup
                expanded_player_rect = player_rect.inflate(8, 8)  # Make player collision area larger
                if scroll_rect.colliderect(expanded_player_rect):
                    return self.collect(player)
        
        return False
    
    def draw(self, surface):
        """Draw the scroll with bobbing animation and glow effect"""
        if not self.collected:
            # First draw a glow effect (if sprite loaded successfully)
            if hasattr(self, 'sprite') and self.sprite.get_width() > 1:
                # Create a slightly larger surface for the glow
                glow_size = 6
                glow_surface = pygame.Surface((self.width + glow_size*2, self.height + glow_size*2), pygame.SRCALPHA)
                
                # Set glow color (golden)
                glow_color = (255, 220, 100, int(100 * self.glow_intensity))
                
                # Draw multiple circles for soft glow effect
                center = (glow_surface.get_width()//2, glow_surface.get_height()//2)
                for radius in range(glow_size, 0, -1):
                    alpha = int(150 * self.glow_intensity * (radius/glow_size))
                    temp_color = (glow_color[0], glow_color[1], glow_color[2], alpha)
                    pygame.draw.circle(glow_surface, temp_color, center, radius + self.width//2)
                
                # Draw the glow surface
                glow_pos = (self.x - glow_size, self.y + self.bob_offset - glow_size)
                surface.blit(glow_surface, glow_pos)
            
            # Then draw the scroll on top
            surface.blit(self.sprite, (self.x, self.y + self.bob_offset))
    
    def get_icon(self):
        """Get a display icon for inventory"""
        icon_size = 40
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Scale the sprite to fit the icon
        temp = pygame.transform.scale(self.sprite, (icon_size - 4, icon_size - 4))
        # Center the sprite in the icon
        icon.blit(temp, (2, 2))
        
        return icon
    
    def collect(self, player):
        """Collect the scroll and immediately activate its effect"""
        if not self.collected:
            # Activate the scroll effect when collected
            if hasattr(player, 'attributes') and hasattr(player.attributes, 'find_ancient_scroll'):
                # Apply the XP table change
                result = player.attributes.find_ancient_scroll()
                
                if result:
                    # Create visual effect (if player has a particle system)
                    if hasattr(player, 'particles') and hasattr(player.particles, 'create_xp_particles'):
                        player.particles.create_xp_particles(50)
                    
                    # Add to inventory if there's space
                    added_to_inventory = False
                    if hasattr(player, 'inventory'):
                        added_to_inventory = player.inventory.add_item(self)
                    
                    # Mark as collected regardless of inventory status
                    self.collected = True
                    
                    # Provide feedback message
                    if added_to_inventory:
                        print(f"Obtained the {self.name}! Your mind expands with ancient knowledge.")
                        print("XP requirements are now reduced! (Using 1.3x progression)")
                    else:
                        print(f"You discovered the {self.name} but couldn't carry it.")
                        print("The knowledge still flows into your mind, reducing XP requirements.")
                        
                    return True
                else:
                    print("You already possess this knowledge.")
                    return False
            else:
                # Just mark as collected if the player doesn't have the attributes system
                # Add to inventory if there's space
                if hasattr(player, 'inventory'):
                    player.inventory.add_item(self)
                
                # Mark as collected regardless of inventory status
                self.collected = True
                print(f"Collected {self.name}, but nothing happened!")
                return True
        return False
        
    def use(self, player):
        """Using the scroll from inventory does nothing as its effect is applied on pickup"""
        # Instead of printing, return a message
        return f"The {self.name} has already imparted its knowledge to you."
    
    def get_rect(self):
        """Return the collision rectangle for pickup"""
        # Only return a valid rect if not collected
        if self.collected:
            # Return an empty rect that won't collide with anything
            return pygame.Rect(0, 0, 0, 0)
            
        # Update pickup rect to current position with bobbing
        self.pickup_rect.x = self.x
        self.pickup_rect.y = self.y + self.bob_offset
        return self.pickup_rect