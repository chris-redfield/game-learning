import pygame

class SpriteSheet:
    """
    A class to handle loading, extracting, and managing sprites from a sprite sheet
    """
    def __init__(self, character_name="link"):
        """
        Initialize the sprite sheet for the specified character
        
        Args:
            character_name (str): Name of the character ("link", "gojou", etc.)
        """
        self.character_name = character_name
        self.spritesheet = None
        
        # Load the appropriate sprite sheet
        self.load_spritesheet()
    
    def load_spritesheet(self):
        """Load the sprite sheet image based on character name"""
        try:
            # For now, we'll use a single sprite sheet, but this could be extended
            # to load different sheets based on character_name
            self.spritesheet = pygame.image.load('assets/sprites.png').convert_alpha()
        except Exception as e:
            print(f"Error loading sprites: {e}")
            self.spritesheet = None
    
    def get_sprite_definitions(self, character_name):
        """Define sprite locations based on character name"""
        if character_name.lower() == "link":
            # Define Link's sprite locations (x, y, width, height)
            sprite_defs = {
                'down_idle': [(1, 3, 16, 24)],
                'down_walk': [(1, 3, 16, 24), (19, 3, 16, 24), (36, 3, 16, 24), 
                             (53, 3, 16, 24), (70, 3, 16, 24), (87, 3, 16, 24), 
                             (104, 3, 16, 24), (121, 3, 16, 24), (138, 3, 16, 24)],
                'up_idle': [(1, 111, 16, 24)],
                'up_walk': [(1, 111, 16, 24), (19, 111, 16, 24), (36, 111, 16, 24), 
                           (53, 111, 16, 24), (70, 111, 16, 24), (87, 111, 16, 24), 
                           (104, 111, 16, 24), (121, 111, 16, 24), (138, 111, 16, 24)],
                'right_idle': [(1, 56, 16, 24)],
                'right_walk': [(1, 56, 16, 24), (19, 56, 16, 24), (36, 56, 16, 24), 
                              (54, 56, 16, 24), (72, 56, 16, 24), (89, 56, 16, 24), 
                              (107, 56, 16, 24), (125, 56, 16, 24), (142, 56, 16, 24)]
                # We'll use flipped right sprites for left-facing animations
            }
            
            # Define sword sprite location
            sword_def = (1, 269, 8, 16)
            
        elif character_name.lower() == "gojou":
            # Example: Define Gojou's sprite locations (placeholders - would need actual coordinates)
            sprite_defs = {
                'down_idle': [(10, 10, 16, 24)],
                'down_walk': [(10, 10, 16, 24), (30, 10, 16, 24), (50, 10, 16, 24), 
                             (70, 10, 16, 24), (90, 10, 16, 24), (110, 10, 16, 24),
                             (130, 10, 16, 24), (150, 10, 16, 24), (170, 10, 16, 24)],
                'up_idle': [(10, 120, 16, 24)],
                'up_walk': [(10, 120, 16, 24), (30, 120, 16, 24), (50, 120, 16, 24),
                           (70, 120, 16, 24), (90, 120, 16, 24), (110, 120, 16, 24),
                           (130, 120, 16, 24), (150, 120, 16, 24), (170, 120, 16, 24)],
                'right_idle': [(10, 60, 16, 24)],
                'right_walk': [(10, 60, 16, 24), (30, 60, 16, 24), (50, 60, 16, 24),
                              (70, 60, 16, 24), (90, 60, 16, 24), (110, 60, 16, 24),
                              (130, 60, 16, 24), (150, 60, 16, 24), (170, 60, 16, 24)]
            }
            
            # Define sword sprite location for Gojou
            sword_def = (10, 280, 8, 16)
            
        else:
            # Default to Link if character not recognized
            print(f"Character '{character_name}' not recognized. Using Link as default.")
            return self.get_sprite_definitions("link")
            
        return sprite_defs, sword_def
    
    def get_sprite(self, x, y, width, height, target_width=None, target_height=None):
        """
        Extract a sprite from the spritesheet
        
        Args:
            x, y: Coordinates in the spritesheet
            width, height: Size in the spritesheet
            target_width, target_height: Size to scale to (optional)
        
        Returns:
            A pygame Surface with the extracted sprite
        """
        if self.spritesheet is None:
            # Create a placeholder if spritesheet failed to load
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.fill((50, 50, 150))
            return sprite
            
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        
        if target_width and target_height:
            return pygame.transform.scale(sprite, (target_width, target_height))
        return sprite
    
    def get_sword_sprite(self, x, y, width, height):
        """Extract a sword sprite from the spritesheet with proper dimensions"""
        sprite = self.get_sprite(x, y, width, height)
        # Keep the original aspect ratio for the sword
        return pygame.transform.scale(sprite, (width * 2, height * 2))
    
    def load_character_sprites(self, character_name, player_width, player_height):
        """
        Load all sprites for the character and scale them to the player size
        
        Args:
            character_name: Name of the character to load
            player_width, player_height: Size to scale sprites to
            
        Returns:
            Dictionary of sprites and sword sprite
        """
        sprites = {}
        
        # Get sprite definitions for this character
        sprite_defs, sword_def = self.get_sprite_definitions(character_name)
        
        # Check if sprite sheet was loaded successfully
        if not self.spritesheet:
            # Create colored rectangle placeholders
            sprites = {
                'down_idle': [pygame.Surface((16, 24))],
                'down_walk': [pygame.Surface((16, 24)) for _ in range(9)],
                'up_idle': [pygame.Surface((16, 24))],
                'up_walk': [pygame.Surface((16, 24)) for _ in range(9)],
                'right_idle': [pygame.Surface((16, 24))],
                'right_walk': [pygame.Surface((16, 24)) for _ in range(9)]
            }
            
            # Fill placeholders with colors
            for key in sprites:
                for sprite in sprites[key]:
                    sprite.fill((50, 50, 150))
                    
            sword_sprite = pygame.Surface((8, 16), pygame.SRCALPHA)
            sword_sprite.fill((200, 200, 200))
            
            return sprites, sword_sprite
        
        # Extract and scale sprites based on definitions
        for key, positions in sprite_defs.items():
            sprites[key] = []
            for (x, y, w, h) in positions:
                sprite = self.get_sprite(x, y, w, h, player_width, player_height)
                sprites[key].append(sprite)
        
        # Extract sword sprite
        x, y, w, h = sword_def
        sword_sprite = self.get_sword_sprite(x, y, w, h)
        
        return sprites, sword_sprite