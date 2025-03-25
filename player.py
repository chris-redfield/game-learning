import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 35  # Increased by ~10% from 32
        self.height = 41  # Increased by ~10% from 37
        self.speed = 3
        
        # Direction states
        self.facing = 'down'  # 'up', 'down', 'left', 'right'
        self.moving = False
        self.frame = 0
        self.animation_speed = 0.2
        self.animation_counter = 0
        
        # Load spritesheet
        try:
            self.spritesheet = pygame.image.load('assets/sprites.png').convert_alpha()
            
            # Define sprite locations for Link (x, y, width, height)
            self.sprites = {
                'down_idle': [(1, 3, 16, 24)],
                'down_walk': [(1, 3, 16, 24), (19, 3, 16, 24), (36, 3, 16, 24), (53, 3, 16, 24)],
                'up_idle': [(2, 110, 16, 24)],
                'up_walk': [(2, 110, 16, 24), (19, 110, 16, 24), (36, 110, 16, 24), (53, 110, 16, 24)],
                'right_idle': [(2, 56, 16, 24)],
                'right_walk': [(2, 56, 16, 24), (19, 56, 16, 24), (36, 56, 16, 24), (53, 56, 16, 24)]
                # We'll use flipped right sprites for left-facing animations
            }
            
            # Convert sprite locations into actual sprite surfaces
            for key in self.sprites:
                self.sprites[key] = [self.get_sprite(x, y, w, h) for x, y, w, h in self.sprites[key]]
                
        except Exception as e:
            print(f"Error loading sprites: {e}")
            # Create colored rectangle placeholders
            self.sprites = {
                'down_idle': [pygame.Surface((16, 24))],
                'down_walk': [pygame.Surface((16, 24)) for _ in range(4)],
                'up_idle': [pygame.Surface((16, 24))],
                'up_walk': [pygame.Surface((16, 24)) for _ in range(4)],
                'right_idle': [pygame.Surface((16, 24))],
                'right_walk': [pygame.Surface((16, 24)) for _ in range(4)],
                'left_idle': [pygame.Surface((16, 24))],
                'left_walk': [pygame.Surface((16, 24)) for _ in range(4)]
            }
            # Fill placeholders with colors
            for key in self.sprites:
                for sprite in self.sprites[key]:
                    sprite.fill((50, 50, 150))
    
    def get_sprite(self, x, y, width, height):
        """Extract a sprite from the spritesheet"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return pygame.transform.scale(sprite, (self.width, self.height))
    
    def load_specific_sprite(self, sprite_x, sprite_y):
        """For debugging - load a specific sprite from coordinates"""
        self.debug_sprite = self.get_sprite(sprite_x, sprite_y, 16, 24)
        print(f"Loaded sprite at ({sprite_x}, {sprite_y})")
    
    def update(self):
        """Update animation frame"""
        if self.moving:
            self.animation_counter += self.animation_speed
            
            # For left direction, use right animation frame count
            if self.facing == 'left':
                if self.animation_counter >= len(self.sprites['right_walk']):
                    self.animation_counter = 0
            else:
                if self.animation_counter >= len(self.sprites[f'{self.facing}_walk']):
                    self.animation_counter = 0
                    
            self.frame = int(self.animation_counter)
        else:
            self.frame = 0
    
    def move(self, dx, dy, obstacles):
        """Move player and update animation state with collision detection"""
        if dx != 0 or dy != 0:
            self.moving = True
            
            # Set facing direction
            if dx > 0:
                self.facing = 'right'
            elif dx < 0:
                self.facing = 'left'
            elif dy > 0:
                self.facing = 'down'
            elif dy < 0:
                self.facing = 'up'
            
            # Create a test rect for collision detection
            test_rect = pygame.Rect(self.x + dx, self.y + dy, self.width, self.height)
            
            # Check for collisions with obstacles
            collision = False
            for obstacle in obstacles:
                if test_rect.colliderect(obstacle.get_rect()):
                    collision = True
                    break
            
            # Only move if there's no collision
            if not collision:
                # Update position
                self.x += dx
                self.y += dy
                
                # Keep player on screen
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
                self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        else:
            self.moving = False
            
    def get_rect(self):
        """Return player collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        """Draw the player with appropriate animation frame"""
        # If in debug mode and a debug sprite is loaded, draw that instead
        if hasattr(self, 'debug_sprite'):
            surface.blit(self.debug_sprite, (self.x, self.y))
            return
        
        # For left-facing, use the right sprites but flip them horizontally
        if self.facing == 'left':
            if self.moving:
                # Get right sprite and flip it
                right_sprite = self.sprites['right_walk'][self.frame]
                sprite = pygame.transform.flip(right_sprite, True, False)  # Flip horizontally
            else:
                # Get right idle sprite and flip it
                right_sprite = self.sprites['right_idle'][0]
                sprite = pygame.transform.flip(right_sprite, True, False)  # Flip horizontally
        else:
            # Normal sprite handling for other directions
            if self.moving:
                sprite = self.sprites[f'{self.facing}_walk'][self.frame]
            else:
                sprite = self.sprites[f'{self.facing}_idle'][0]
        
        surface.blit(sprite, (self.x, self.y))