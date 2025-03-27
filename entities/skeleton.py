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
        
        # Create collision rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
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
        self.dx = 0  # Current movement direction (x component)
        self.dy = 0  # Current movement direction (y component)
        
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
    
    def update(self, player=None, obstacles=None):
        """Update skeleton state and animation"""
        # Update animation frame
        self.animation_counter += self.animation_speed
        animation_frames = self.sprites.get(f"{self.state}_right", [])
        
        if len(animation_frames) > 0:
            if self.animation_counter >= len(animation_frames):
                self.animation_counter = 0
            
            self.frame = int(self.animation_counter)
        
        # Handle AI behavior based on current state
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
                    # Move if currently in moving state
                    if obstacles:
                        self.move(self.dx, self.dy, obstacles)
            
            # Check for collision with player (for potential combat)
            if player and self.rect.colliderect(player.get_rect()):
                self.stop_moving()
                # self.attack(player)  # Uncomment to enable attacking
                
        # Update collision rect position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def start_moving(self):
        """Start movement in a random direction"""
        self.state = "moving"
        
        # Choose a random direction vector
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        # Set direction based on horizontal movement
        if self.dx > 0:
            self.direction = "right"
        elif self.dx < 0:
            self.direction = "left"
    
    def stop_moving(self):
        """Stop movement and go idle"""
        self.state = "idle"
        self.dx = 0
        self.dy = 0
    
    def move(self, dx, dy, obstacles):
        """Move with collision detection - similar to player movement logic"""
        if dx == 0 and dy == 0:
            return False
            
        # Create test rectangles for movement along each axis separately
        test_rect_x = pygame.Rect(self.x + dx, self.y, self.width, self.height)
        test_rect_y = pygame.Rect(self.x, self.y + dy, self.width, self.height)
        
        # Check horizontal movement
        x_collision = False
        for obstacle in obstacles:
            # Skip self-collision
            if obstacle is self:
                continue
                
            if test_rect_x.colliderect(obstacle.get_rect()):
                x_collision = True
                break
        
        # Apply horizontal movement if no collision
        if not x_collision:
            self.x += dx
        
        # Check vertical movement
        y_collision = False
        for obstacle in obstacles:
            # Skip self-collision
            if obstacle is self:
                continue
                
            if test_rect_y.colliderect(obstacle.get_rect()):
                y_collision = True
                break
        
        # Apply vertical movement if no collision
        if not y_collision:
            self.y += dy
            
        # If we hit an obstacle, consider changing direction
        if x_collision or y_collision:
            # 25% chance to choose a new direction when hitting an obstacle
            if random.random() < 0.25:
                self.start_moving()
            return False
            
        # Successfully moved
        return True
    
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
        return self.rect
    
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