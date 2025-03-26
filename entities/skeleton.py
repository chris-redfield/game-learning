import pygame
import random
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Skeleton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48  # Increased width to better match the sprite proportions
        self.height = 52  # Increased height to better match the sprite proportions
        self.speed = 1
        
        # Animation and state properties
        self.state = "idle"  # "idle", "moving", "attacking", "dying"
        self.direction = random.choice(["left", "right"])
        self.frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        
        # Movement AI properties
        self.movement_timer = 0
        self.movement_pause = random.randint(60, 180)  # Frames to wait between movements
        self.movement_duration = random.randint(30, 120)  # Frames to move when active
        self.target_x = None
        self.target_y = None
        self.moving = False
        
        # Health and combat properties
        self.health = 3
        self.attack_power = 1
        self.attack_range = 50
        self.detection_range = 150
        
        # Load sprite images from separate files
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
            
            print(f"DEBUG: Loaded idle sprite image: {idle_img.get_width()}x{frame_height}")
            
            # Load each idle frame using manual positions
            for i, x_pos in enumerate(idle_frame_positions):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(idle_img, (0, 0), (x_pos, 0, frame_width, frame_height))
                # Scale to desired size
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                self.sprites['idle_right'].append(scaled_frame)
                print(f"DEBUG: Added idle frame {i+1} from position ({x_pos}, 0)")
            
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
            
            print(f"DEBUG: Loaded walk sprite image: {walk_img.get_width()}x{frame_height}")
            
            # Load each walking frame using manual positions
            for i, x_pos in enumerate(walking_frame_positions):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(walk_img, (0, 0), (x_pos, 0, frame_width, frame_height))
                # Scale to desired size
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                self.sprites['moving_right'].append(scaled_frame)
                print(f"DEBUG: Added walking frame {i+1} from position ({x_pos}, 0)")
                
            print(f"DEBUG: Skeleton sprites loaded successfully - {len(self.sprites['idle_right'])} idle frames, {len(self.sprites['moving_right'])} walking frames")
                
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
    
    def update(self, player=None):
        """Update skeleton state and animation"""
        # Update animation frame
        self.animation_counter += self.animation_speed
        animation_frames = self.sprites.get(f"{self.state}_right", [])
        
        if len(animation_frames) > 0:
            if self.animation_counter >= len(animation_frames):
                self.animation_counter = 0
            
            self.frame = int(self.animation_counter)
        
        # AI behavior - switch between idle and moving
        if self.state != "dying" and self.state != "attacking":
            self.movement_timer += 1
            
            if self.state == "idle":
                if self.movement_timer >= self.movement_pause:
                    self.movement_timer = 0
                    self.start_moving()
            
            elif self.state == "moving":
                if self.movement_timer >= self.movement_duration:
                    self.movement_timer = 0
                    self.stop_moving()
                else:
                    self.move()
            
            # Player detection would go here for future implementation
    
    def start_moving(self):
        """Start movement in a random direction"""
        self.state = "moving"
        self.direction = random.choice(["left", "right"])
        
        # Choose a random target point within reasonable distance
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(50, 150)
        self.target_x = self.x + math.cos(angle) * distance
        self.target_y = self.y + math.sin(angle) * distance
        
        # Keep target within screen bounds with padding
        padding = 50
        self.target_x = max(padding, min(SCREEN_WIDTH - padding, self.target_x))
        self.target_y = max(padding, min(SCREEN_HEIGHT - padding, self.target_y))
    
    def stop_moving(self):
        """Stop movement and go idle"""
        self.state = "idle"
        
    def move(self):
        """Move toward the target point"""
        if self.target_x is None or self.target_y is None:
            return
            
        # Calculate direction vector
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # Normalize the vector
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx = dx / distance
        dy = dy / distance
        
        # Set direction based on movement
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        
        # Move the skeleton
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Check if we've reached the target (within a small threshold)
        if distance < 5:
            self.stop_moving()
    
    def attack(self, player):
        """Start attack animation and deal damage (placeholder)"""
        self.state = "attacking"
        self.animation_counter = 0
        # Attack logic would be implemented here
        print("Skeleton attacks!")
    
    def take_damage(self, damage):
        """Take damage and check if dead (placeholder)"""
        self.health -= damage
        if self.health <= 0:
            self.die()
        else:
            # Damage reaction animation could go here
            print(f"Skeleton took {damage} damage, {self.health} health remaining")
    
    def die(self):
        """Start death animation (placeholder)"""
        self.state = "dying"
        self.animation_counter = 0
        print("Skeleton is dying!")
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        """Draw the skeleton with appropriate animation frame and direction"""
        # Get the correct animation set based on state
        animation_key = f"{self.state}_right"
        
        if animation_key in self.sprites and len(self.sprites[animation_key]) > 0 and self.frame < len(self.sprites[animation_key]):
            sprite = self.sprites[animation_key][self.frame]
            
            # Flip sprite if facing left
            if self.direction == "left":
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Draw the skeleton
            surface.blit(sprite, (self.x, self.y))
            
            # For debugging collision boxes (uncomment if needed)
            # pygame.draw.rect(surface, (255, 0, 0), self.get_rect(), 1)