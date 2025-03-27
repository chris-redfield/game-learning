import pygame
import math
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
        
        # Sword swing states
        self.swinging = False
        self.swing_frame = 0
        self.swing_animation_counter = 0
        self.swing_animation_speed = 0.31  # Adjusted for 90-degree swing
        self.swing_frames_total = 5  # Frames for a 90-degree swing
        
        # Level system
        self.level = 1
        self.max_level = 4
        
        # Level 2: Dash (temporary speed boost)
        self.can_dash = False  # Level 2 ability
        self.dash_duration = 1500  # 1.5 seconds in milliseconds
        self.dash_cooldown = 3000  # 3 seconds in milliseconds
        self.dash_timer = 0  # For cooldown tracking
        self.dash_end_time = 0  # For duration tracking
        self.dashing = False
        self.base_speed = 3  # Store the base speed
        
        # Level 4: Blink (teleport)
        self.can_blink = False  # Level 4 ability
        self.blink_distance = 80
        self.blink_cooldown = 2000  # in milliseconds
        self.blink_timer = 0
        
        # Default sword length (will be increased at level 3)
        self.sword_length = 24
        self.base_sword_length = 24  # Store the base value for reference
        
        # Load spritesheet
        try:
            self.spritesheet = pygame.image.load('assets/sprites.png').convert_alpha()
            
            # Define sprite locations for Link (x, y, width, height)
            self.sprites = {
                'down_idle': [(1, 3, 16, 24)],
                'down_walk': [(1, 3, 16, 24), (19, 3, 16, 24), (36, 3, 16, 24), (53, 3, 16, 24)],
                'up_idle': [(1, 111, 16, 24)],
                'up_walk': [(1, 111, 16, 24), (19, 111, 16, 24), (36, 111, 16, 24), (53, 111, 16, 24)],
                'right_idle': [(1, 56, 16, 24)],
                'right_walk': [(1, 56, 16, 24), (19, 56, 16, 24), (36, 56, 16, 24), (53, 56, 16, 24)]
                # We'll use flipped right sprites for left-facing animations
            }
            
            # Define sword swing sprites (x, y, width, height)
            # Using only the first sword sprite as requested
            # Adjusted coordinates based on feedback
            self.sword_sprite = self.get_sword_sprite(1, 269, 8, 16)
            
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
        
    def get_sword_sprite(self, x, y, width, height):
        """Extract a sword sprite from the spritesheet with proper dimensions"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # Keep the original aspect ratio for the sword
        return pygame.transform.scale(sprite, (width * 2, height * 2))
    
    def load_specific_sprite(self, sprite_x, sprite_y):
        """For debugging - load a specific sprite from coordinates"""
        self.debug_sprite = self.get_sprite(sprite_x, sprite_y, 16, 24)
        print(f"Loaded sprite at ({sprite_x}, {sprite_y})")
    
    def level_up(self):
        """Increase player level and unlock abilities"""
        if self.level < self.max_level:
            self.level += 1
            print(f"Level up! Player is now level {self.level}")
            
            # Level 2: Unlock dash ability (temporary speed boost)
            if self.level == 2:
                self.can_dash = True
                print("Unlocked dash ability! Press SHIFT for a temporary speed boost.")
            
            # Level 3: Increase sword length by 50%
            elif self.level == 3:
                self.sword_length = int(self.base_sword_length * 1.5)
                print(f"Increased sword length! ({self.base_sword_length} -> {self.sword_length})")
                
            # Level 4: Unlock blink ability (teleport)
            elif self.level == 4:
                self.can_blink = True
                print("Unlocked blink ability! Press B to teleport in the direction you're facing.")
        else:
            print(f"Already at max level ({self.max_level})!")
    
    def update(self, current_time=None):
        """Update animation frame and ability cooldowns"""
        # Handle movement animation
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
            
        # Handle sword swing animation
        if self.swinging:
            self.swing_animation_counter += self.swing_animation_speed
            
            if self.swing_animation_counter >= self.swing_frames_total:
                self.swinging = False
                self.swing_animation_counter = 0
            
            self.swing_frame = int(self.swing_animation_counter)

        if current_time:
            # Update dash status
            if self.dashing and current_time > self.dash_end_time:
                # End the dash effect
                self.dashing = False
                self.speed = self.base_speed
                print("Dash ended")
                
            # Clear dash cooldown
            if self.dash_timer > 0 and current_time > self.dash_timer:
                self.dash_timer = 0
                
            # Clear blink cooldown
            if self.blink_timer > 0 and current_time > self.blink_timer:
                self.blink_timer = 0
    
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
                
                # # Keep player on screen
                # self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
                # self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        else:
            self.moving = False
    
    def dash(self, current_time):
        """Activate a temporary speed boost"""
        if not self.can_dash or self.dashing or current_time < self.dash_timer:
            return False
        
        # Activate dash (speed boost)
        self.dashing = True
        self.speed = self.base_speed * 1.5  # 50% speed increase
        
        # Set timers
        self.dash_end_time = current_time + self.dash_duration
        self.dash_timer = current_time + self.dash_cooldown + self.dash_duration
        
        print("Dash activated! Speed increased by 50% for 1 second")
        return True
        
    def blink(self, obstacles, current_time):
        """Teleport in the current facing direction"""
        if not self.can_blink or current_time < self.blink_timer:
            return False
        
        # Calculate blink direction based on facing
        blink_dx, blink_dy = 0, 0
        if self.facing == 'right':
            blink_dx = self.blink_distance
        elif self.facing == 'left':
            blink_dx = -self.blink_distance
        elif self.facing == 'down':
            blink_dy = self.blink_distance
        elif self.facing == 'up':
            blink_dy = -self.blink_distance
        
        # Try to move in the blink direction
        self.move(blink_dx, blink_dy, obstacles)

        # Set cooldown timer
        self.blink_timer = current_time + self.blink_cooldown
        print("Blink!")
        return True
            
    def get_rect(self):
        """Return player collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def start_swing(self):
        """Start the sword swing animation"""
        if not self.swinging:  # Only start if not already swinging
            self.swinging = True
            self.swing_animation_counter = 0
            self.swing_frame = 0
            
    def is_swinging(self):
        """Check if player is currently swinging the sword"""
        return self.swinging
    
    def draw_sword(self, surface):
        """Draw sword with a 90-degree swing centered on player's facing direction"""
        if not self.swinging:
            return
            
        # Player center point (handle position)
        player_center_x = self.x + self.width / 2
        player_center_y = self.y + self.height / 2
        
        # Apply offset for upward-facing position
        if self.facing == 'up':
            player_center_y -= 9  # Move sword handle up by 9px

        # Base angles for each direction
        base_angles = {
            'right': 0,
            'left': math.pi,
            'up': -math.pi/2,
            'down': math.pi/2
        }
        
        # Get base angle from player's facing direction
        base_angle = base_angles[self.facing]
        
        # Calculate swing angle: swing 90 degrees (-45° to +45° from center direction)
        # Maps swing_animation_counter from 0 to 1 to an angle from -45° to +45°
        angle_offset = (self.swing_animation_counter / self.swing_frames_total) * math.pi/2 - math.pi/4
        
        # Calculate final rotation angle
        rotation_angle = base_angle + angle_offset
        
        # Default sword length (distance from handle to tip)
        # This value is now controlled by the level system
        sword_length = self.sword_length
        
        # Calculate sword position based on rotation angle
        sword_x = player_center_x + math.cos(rotation_angle) * sword_length
        sword_y = player_center_y + math.sin(rotation_angle) * sword_length
        
        # Calculate display rotation angle in degrees for pygame
        display_angle = -math.degrees(rotation_angle) - 90  # -90 to adjust for sword sprite orientation
        
        # Rotate sword sprite
        rotated_sword = pygame.transform.rotate(self.sword_sprite, display_angle)
        
        # Get the new rect for the rotated sword to properly position it
        sword_rect = rotated_sword.get_rect()
        
        # Set the sword position so that the handle (not the center) is at the rotation point
        # We need to offset from the calculated position to account for handle placement
        handle_offset_x = sword_rect.width * 0.5  # Adjust based on where the handle is in your sprite
        handle_offset_y = sword_rect.height * 0.2  # Assume handle is at 20% of the sprite height
        
        # Calculate the offset position for the sprite
        offset_x = sword_x - handle_offset_x
        offset_y = sword_y - handle_offset_y
        
        # Draw the sword
        surface.blit(rotated_sword, (offset_x, offset_y))
    
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
        
        # Draw the player character
        surface.blit(sprite, (self.x, self.y))
        
        # Draw sword if player is swinging
        self.draw_sword(surface)
        
    def render_level_info(self, surface, font, x, y):
        """Display player level information on screen"""
        level_text = font.render(f"Level: {self.level}/{self.max_level}", True, (255, 255, 255))
        surface.blit(level_text, (x, y))
        
        # Display ability info
        abilities_y = y + 25
        
        # Level 2: Dash
        if self.level >= 2:
            if self.dashing:
                dash_status = "ACTIVE"
                color = (0, 255, 0)  # Green when active
            elif self.dash_timer == 0:
                dash_status = "Ready"
                color = (255, 255, 255)  # White when ready
            else:
                dash_status = "Cooling Down"
                color = (255, 165, 0)  # Orange when on cooldown
                
            dash_text = font.render(f"Dash: {dash_status}", True, color)
            surface.blit(dash_text, (x, abilities_y))
            abilities_y += 25
        
        # Level 3: Extended Sword    
        if self.level >= 3:
            sword_text = font.render(f"Extended Sword: Active", True, (255, 255, 255))
            surface.blit(sword_text, (x, abilities_y))
            abilities_y += 25
            
        # Level 4: Blink
        if self.level >= 4:
            blink_status = "Ready" if self.blink_timer == 0 else "Cooling Down"
            blink_color = (255, 255, 255) if self.blink_timer == 0 else (255, 165, 0)
            blink_text = font.render(f"Blink: {blink_status}", True, blink_color)
            surface.blit(blink_text, (x, abilities_y))