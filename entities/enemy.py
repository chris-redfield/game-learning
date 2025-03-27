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
        self.hit = False
        self.hit_timer = 0
        self.hit_duration = 200  # milliseconds
        
        self.defense = 0  # Base enemies have no defense
        self.blood_particles = []
    
    def update(self, player=None, obstacles=None):
        """Update enemy state and animation - basic behavior"""
        # Keep existing update code
        
        # Update animation frame
        self.animation_counter += self.animation_speed
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0:
            if self.animation_counter >= len(animation_frames):
                self.animation_counter = 0
            
            self.frame = int(self.animation_counter)
        
        # Check for collision with player first (for combat), regardless of state
        if player and self.rect.colliderect(player.get_rect()):
            self.handle_player_collision(player)
        
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
        
        # Update collision rect position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # NEW: Update hit effect timer
        if self.hit:
            self.hit_timer += 16.67  # Approximate time between frames at 60 FPS
            if self.hit_timer >= self.hit_duration:
                self.hit = False
                self.hit_timer = 0
        
        # NEW: Update blood particles
        if obstacles is not None:
            self.update_blood_particles(obstacles)


    def update_blood_particles(self, obstacles):
        """Update blood particles for the enemy"""
        # Skip if no particles or no blood_particles attribute
        if not hasattr(self, 'blood_particles') or not self.blood_particles:
            return
            
        # Update each particle
        for particle in self.blood_particles[:]:  # Use a copy of the list for safe iteration
            if particle:  # Make sure particle is not None
                particle.update(obstacles)
                
                # Remove inactive particles
                if not particle.active:
                    self.blood_particles.remove(particle)
                
                # Handle stuck particles - for now, just keep them 
                # (in a real game you might want to transfer them to world)
                if particle.stuck:
                    # Just keep stuck particles for now
                    pass


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
        
        # Damage player and pass enemy position for knockback direction
        enemy_center_x = self.x + (self.width / 2)
        enemy_center_y = self.y + (self.height / 2)
        player.take_damage(self.attack_power, enemy_center_x, enemy_center_y)
    
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
        # Apply damage, accounting for defense
        defense_factor = 1.0 - (self.defense * 0.1)  # 10% reduction per defense point
        final_damage = max(1, int(damage * defense_factor))  # At least 1 damage
        
        self.health -= final_damage
        
        # Set hit flag for visual feedback
        self.hit = True
        self.hit_timer = 0
        
        print(f"Enemy {self.__class__.__name__} at ({self.x}, {self.y}) took {final_damage} damage!")
        
        if self.health <= 0:
            print(f"Enemy {self.__class__.__name__} died!")
            self.die()
            return True  # Enemy died
        else:
            # Damage reaction
            print(f"{self.__class__.__name__} has {self.health} health remaining")
            return False  # Enemy still alive
    
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
            
            # NEW: Apply hit effect - alternate between showing and hiding for GIFs
            # or apply red tint for regular sprites
            if self.hit:
                # For GIF-based enemies (like slimes), use flashing instead of tint
                from entities.slime import Slime
                if isinstance(self, Slime):
                    # Flash by only drawing every other frame during hit animation
                    if (self.hit_timer // 50) % 2 == 0:  # Toggle visibility every 50ms
                        surface.blit(sprite, (self.x, self.y))
                else:
                    # For regular sprites (like skeletons), use red tint
                    surface.blit(sprite, (self.x, self.y))
            else:
                # Normal drawing (no hit effect)
                surface.blit(sprite, (self.x, self.y))
            
            # NEW IMPROVED: Draw blood particles
            for particle in self.blood_particles:
                particle.draw(surface)
            
    def load_sprites(self):
        """
        Load sprites for the enemy - this is a placeholder method
        that should be overridden by subclasses
        """
        pass