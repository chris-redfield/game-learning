import pygame
import random
from PIL import Image, ImageSequence
from entities.enemy import Enemy

class Slime(Enemy):
    def __init__(self, x, y):
        # Define slime-specific dimensions
        width = 32
        height = 24
        
        # Call parent constructor with SLOWER speed (skeletons use 1.0)
        super().__init__(x, y, width, height, speed=0.5)
        
        # Slime-specific properties
        self.health = 2  # Slimes have less health than skeletons
        self.attack_power = 1
        
        # SLOWER animation speed (reduced from the default 0.1)
        self.animation_speed = 0.03  # Half the default animation speed
        
        # Load slime sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load slime sprites from GIF files"""
        self.sprites = {
            'idle': [],
            'moving': []
        }
        
        try:
            # Load idle animation from GIF
            self.load_animation_from_gif('assets/slime_idle.gif', 'idle')
            
            # Load moving animation from GIF
            self.load_animation_from_gif('assets/slime_move.gif', 'moving')
                
        except Exception as e:
            print(f"Error loading slime sprites: {e}")
            # Create colored rectangle placeholders
            for _ in range(4):
                idle_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                idle_placeholder.fill((0, 200, 0))  # Green for slime
                self.sprites['idle'].append(idle_placeholder)
            
            for _ in range(6):
                move_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                move_placeholder.fill((0, 180, 0))  # Slightly darker green
                self.sprites['moving'].append(move_placeholder)
    
    def load_animation_from_gif(self, gif_path, animation_key):
        """Load frames from a GIF file and add them to sprites dictionary"""
        try:
            # Open the GIF file using PIL
            gif = Image.open(gif_path)
            
            # Process each frame in the GIF
            frames = []
            for frame in ImageSequence.Iterator(gif):
                # Convert PIL image to pygame surface
                frame_rgba = frame.convert("RGBA")
                frame_data = frame_rgba.tobytes()
                size = frame_rgba.size
                mode = frame_rgba.mode
                
                # Create pygame surface from the frame data
                py_frame = pygame.image.fromstring(frame_data, size, mode)
                
                # Scale the frame to match the slime's dimensions
                scaled_frame = pygame.transform.scale(py_frame, (self.width, self.height))
                frames.append(scaled_frame)
            
            # Add the frames to the sprites dictionary
            self.sprites[animation_key] = frames
            
        except Exception as e:
            print(f"Error loading animation from {gif_path}: {e}")
            raise
    
    def get_animation_frames(self):
        """Get animation frames based on state - stick to simplest approach"""
        if self.state == "moving" and len(self.sprites["moving"]) > 0:
            return self.sprites["moving"]
        elif self.state == "idle" and len(self.sprites["idle"]) > 0:
            return self.sprites["idle"]
        
        # Fallback to any available animation
        for key in self.sprites:
            if len(self.sprites[key]) > 0:
                return self.sprites[key]
        
        # Default to empty list if no suitable animation found
        return []
    
    def handle_player_collision(self, player):
        """Slimes attack on contact but don't stop moving"""
        # Don't call super() here as it would stop movement
        
        # Attack the player but keep moving
        # Pass position for knockback calculation
        enemy_center_x = self.x + (self.width / 2)
        enemy_center_y = self.y + (self.height / 2)
        player.take_damage(self.attack_power, enemy_center_x, enemy_center_y)
    
    def draw(self, surface):
        """Draw the slime with the current animation frame"""
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0 and self.frame < len(animation_frames):
            sprite = animation_frames[self.frame]
            surface.blit(sprite, (self.x, self.y))
            
            # Uncomment to debug collision boxes
            # pygame.draw.rect(surface, (0, 255, 0), self.get_rect(), 1)