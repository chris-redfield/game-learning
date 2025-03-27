import pygame
from entities.enemy import Enemy

class Skeleton(Enemy):
    def __init__(self, x, y):
        # Define skeleton-specific dimensions
        width = 48  # Increased width to better match the sprite proportions
        height = 52  # Increased height to better match the sprite proportions
        
        # Call parent constructor
        super().__init__(x, y, width, height, speed=1)
        
        # Skeleton-specific properties
        self.health = 3  # Override default health if needed
        
        # Load skeleton sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load skeleton-specific sprites from sprite sheets"""
        self.sprites = {
            'idle_right': [],
            'moving_right': []
        }
        
        try:
            # Load idle animation frames
            idle_img = pygame.image.load('assets/Skeleton_02_White_Idle.png').convert_alpha()
            
            # Manually define the frame positions based on careful examination of the sprite sheet
            # These are the x-coordinates of each frame
            idle_frame_positions = [
                0,     # Frame 1 start x-position
                95,    # Frame 2 start x-position
                191,   # Frame 3 start x-position
                287,   # Frame 4 start x-position
                383,   # Frame 5 start x-position
                479,   # Frame 6 start x-position
                575,   # Frame 7 start x-position
            ]
            
            frame_width = 42   # Approximate width of each frame
            frame_height = idle_img.get_height()
            
            # Load each idle frame using manual positions
            for i, x_pos in enumerate(idle_frame_positions):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(idle_img, (0, 0), (x_pos, 0, frame_width, frame_height))
                # Scale to desired size
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                self.sprites['idle_right'].append(scaled_frame)
            
            # Load walking animation frames with manually defined positions
            walk_img = pygame.image.load('assets/Skeleton_02_White_Walk.png').convert_alpha()
            
            # Manually define the walking frame positions based on sprite sheet examination
            walking_frame_positions = [
                0,     # Frame 1 start x-position
                95,    # Frame 2 start x-position
                191,   # Frame 3 start x-position
                287,   # Frame 4 start x-position
                383,   # Frame 5 start x-position
                479,   # Frame 6 start x-position
                575,   # Frame 7 start x-position
                671,   # Frame 8 start x-position
                767    # Frame 9 start x-position
            ]
            
            frame_width = 42   # Approximate width of each frame
            frame_height = walk_img.get_height()
            
            # Load each walking frame using manual positions
            for i, x_pos in enumerate(walking_frame_positions):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(walk_img, (0, 0), (x_pos, 0, frame_width, frame_height))
                # Scale to desired size
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                self.sprites['moving_right'].append(scaled_frame)
                
        except Exception as e:
            print(f"Error loading skeleton sprites: {e}")
            # Create colored rectangle placeholders
            for _ in range(7):  # Only 7 idle frames
                idle_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                idle_placeholder.fill((200, 200, 200))
                self.sprites['idle_right'].append(idle_placeholder)
            
            for _ in range(9):  # 9 walking frames
                move_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                move_placeholder.fill((180, 180, 180))
                self.sprites['moving_right'].append(move_placeholder)
    
    def get_animation_frames(self):
        """Override to always use right-facing animations and let draw() handle flipping"""
        # For skeleton, we only have "_right" animations, so always use those
        # regardless of the actual direction (the draw method will flip them if needed)
        animation_key = f"{self.state}_right"
        
        if animation_key in self.sprites and len(self.sprites[animation_key]) > 0:
            return self.sprites[animation_key]
        
        # If the current state doesn't have animations (e.g., "attacking" isn't implemented),
        # fallback to idle_right as a safe default
        if 'idle_right' in self.sprites and len(self.sprites['idle_right']) > 0:
            return self.sprites['idle_right']
            
        # Return an empty list only if all else fails
        return []
    
    def handle_player_collision(self, player):
        """Override to implement skeleton-specific player collision behavior"""
        super().handle_player_collision(player)
        # You can add skeleton-specific collision behavior here
        # For example, if the skeleton should attack on contact:
        # self.attack(player)
    
    def attack(self, player):
        """Skeleton-specific attack behavior"""
        super().attack(player)
        # Add skeleton-specific attack logic here
        # For example, skeletons might have a specific attack animation or pattern
    
    def die(self):
        """Skeleton-specific death behavior"""
        super().die()
        # Add skeleton-specific death animations or effects here