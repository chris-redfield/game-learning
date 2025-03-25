import pygame

class Grass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32  # Size of the grass tile
        self.height = 32
        
        # Load spritesheet
        try:
            self.spritesheet = pygame.image.load('assets/world-tiles-1.png').convert_alpha()
            self.sprite = self.get_sprite(759, 50, 16, 16)  # Coordinates from the sprite sheet
        except Exception as e:
            print(f"Error loading grass sprites: {e}")
            # Create placeholder
            self.sprite = pygame.Surface((16, 16))
            self.sprite.fill((60, 140, 60))
            
    def get_sprite(self, x, y, width, height):
        """Extract a sprite from the spritesheet"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return pygame.transform.scale(sprite, (self.width, self.height))
        
    def draw(self, surface):
        """Draw the grass"""
        surface.blit(self.sprite, (self.x, self.y))