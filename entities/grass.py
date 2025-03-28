import pygame

class Grass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32  # Size of the grass tile
        self.height = 32
        
        # Create collision rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Load direct bush image instead of spritesheet
        try:
            self.sprite = pygame.image.load('assets/bush.png').convert_alpha()
            # Scale the sprite to match the desired dimensions
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except Exception as e:
            print(f"Error loading bush sprite: {e}")
            # Create placeholder
            self.sprite = pygame.Surface((self.width, self.height))
            self.sprite.fill((60, 140, 60))
    
    def get_rect(self):
        """Return the collision rectangle"""
        return self.rect
        
    def draw(self, surface):
        """Draw the grass"""
        surface.blit(self.sprite, (self.x, self.y))