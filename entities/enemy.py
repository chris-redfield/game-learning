import pygame
import random
import math

class Enemy:
    def __init__(self, x, y, width, height, speed=1):
        # Basic properties
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        
        # Create collision rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Animation and state properties
        self.state = "idle"  # Default state
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
        
        # Sprite dictionary - to be populated by subclasses
        self.sprites = {}
    
    def update(self, player=None, obstacles=None):
        """Update enemy state and animation - basic behavior"""
        # Update animation frame
        self.animation_counter += self.animation_speed
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0:
            if self.animation_counter >= len(animation_frames):
                self.animation_counter = 0
            
            self.frame = int(self.animation_counter)
        
        # Base AI behavior - can be overridden by subclasses
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
                self.handle_player_collision(player)
                
        # Update collision rect position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def get_animation_frames(self):
        """Get the correct animation frames based on current state and direction"""
        # This is a base implementation - subclasses should override to provide their specific logic
        direction_suffix = "right" if self.direction == "right" else "left"
        animation_key = f"{self.state}_{direction_suffix}"
        
        # Try to get animation frames with direction-specific key
        if animation_key in self.sprites and len(self.sprites[animation_key]) > 0:
            return self.sprites[animation_key]
            
        # Fallback to direction-agnostic animation if available
        if self.state in self.sprites and len(self.sprites[self.state]) > 0:
            return self.sprites[self.state]
            
        # Default to empty list if no suitable animation found
        return []
    
    def handle_player_collision(self, player):
        """Handle collision with player - override in subclasses for specific behavior"""
        self.stop_moving()
        # Subclasses can override this to implement specific collision behavior
    
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
        """Move with collision detection"""
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
        """Start attack animation and deal damage - may be overridden by subclasses"""
        self.state = "attacking"
        self.animation_counter = 0
        # Basic attack logic - subclasses can override for specific behavior
        print(f"{self.__class__.__name__} attacks!")
    
    def take_damage(self, damage):
        """Take damage and check if dead"""
        self.health -= damage
        if self.health <= 0:
            self.die()
        else:
            # Damage reaction could be implemented by subclasses
            print(f"{self.__class__.__name__} took {damage} damage, {self.health} health remaining")
    
    def die(self):
        """Start death animation"""
        self.state = "dying"
        self.animation_counter = 0
        print(f"{self.__class__.__name__} is dying!")
    
    def get_rect(self):
        """Return collision rectangle"""
        return self.rect
    
    def draw(self, surface):
        """Draw the enemy with appropriate animation frame and direction"""
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0 and self.frame < len(animation_frames):
            sprite = animation_frames[self.frame]
            
            # If we're using the right-facing sprites but need to face left,
            # and we don't have dedicated left sprites, then flip the sprite
            animation_key = f"{self.state}_right"
            if self.direction == "left" and animation_key in self.sprites:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Draw the enemy
            surface.blit(sprite, (self.x, self.y))
            
            # For debugging collision boxes (uncomment if needed)
            # pygame.draw.rect(surface, (255, 0, 0), self.get_rect(), 1)
            
    def load_sprites(self):
        """
        Load sprites for the enemy - this is a placeholder method
        that should be overridden by subclasses
        """
        pass