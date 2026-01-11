import pygame
import random
import math
from entities.enemy.enemy_attribute import EnemyAttributes

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
        
        # Add enemy type for attribute system
        self.enemy_type = "normal"
        # Whether the enemy uses magic
        self.has_magic = False
        
        # Initialize the attribute system with default level 1
        self.attributes = EnemyAttributes(self, level=1, enemy_type=self.enemy_type)
        
        # Health and combat properties (from attributes)
        self.health = self.attributes.max_health
        self.attack_power = self.attributes.get_attack_power()
        self.attack_range = 50
        self.detection_range = 150
        self.defense = self.attributes.defense
        
        # Hit effect properties
        self.hit = False
        self.hit_timer = 0
        self.hit_duration = 200  # milliseconds
        
        # Death properties
        self.death_timer = 0
        self.death_duration = 500  # ms before removing entity
        self.should_remove = False
        self.will_drop_soul = False
        
        # Blood particles list
        self.blood_particles = []
        
        # Death particles list
        self.death_particles = []
        
        # Sprite dictionary - to be populated by subclasses
        self.sprites = {}
        
        # Knockback properties
        self.is_being_knocked_back = False
        self.knockback_timer = 0
        self.knockback_duration = 300  # milliseconds
        self.knockback_direction = (0, 0)
        self.current_knockback = 0
        
        # Recovery state properties - NEW
        self.should_recover = False  # Flag to indicate recovery should start after knockback
        self.is_recovering = False   # Flag indicating enemy is recovering from being hit
        self.recovery_timer = 0      # Timer for recovery state
        self.recovery_duration = 1000  # Default 1-second recovery duration
        
        # Debug visualization
        self.show_detection_radius = False
    
    def set_level(self, level, difficulty_factor=1.0):
        """Set the enemy level and apply difficulty scaling"""
        self.attributes = EnemyAttributes(self, level, self.enemy_type)
        
        # Apply area difficulty scaling if specified
        if difficulty_factor > 1.0:
            self.attributes.scale_by_difficulty(difficulty_factor)
        
        # Update enemy stats from attributes
        self.health = self.attributes.max_health
        self.attack_power = self.attributes.get_attack_power()
        self.defense = self.attributes.defense
    
    def update(self, player=None, obstacles=None):
        """Update enemy state and animation with death handling"""
        # If in dying state, update death animation
        # Safety check - if health is <= 0 but not in dying state, trigger death
        if self.health <= 0 and self.state != "dying":
            print(f"Caught zombie skeleton with {self.health} health!")
            self.die()
            return

        if self.state == "dying":
            self.death_timer += 16.67  # Approximate milliseconds per frame at 60 FPS
            
            # Update death particles
            if hasattr(self, 'death_particles') and self.death_particles:
                self.update_death_particles()
            
            # Check if it's time to remove the entity
            if self.death_timer >= self.death_duration:
                self.should_remove = True
                
                # If we should drop a soul, prepare it
                if not hasattr(self, 'will_drop_soul'):
                    self.will_drop_soul = True
            
            return  # Skip regular updates when dying
        
        # Check if recovering from being hit - NEW
        if self.is_recovering:
            # Update recovery timer
            self.recovery_timer += 16.67  # ~60 FPS
            
            # Check if recovery time is over
            if self.recovery_timer >= self.recovery_duration:
                self.is_recovering = False
                self.recovery_timer = 0
                print(f"{self.__class__.__name__} recovery complete, resuming activity")
                
            # Update basic animation during recovery
            self.animation_counter += self.animation_speed
            animation_frames = self.get_animation_frames()
            
            if len(animation_frames) > 0:
                if self.animation_counter >= len(animation_frames):
                    self.animation_counter = 0
                
                self.frame = int(self.animation_counter)
                
            # Update collision rect position
            self.rect.x = self.x
            self.rect.y = self.y
            
            # Update hit effect timer
            if self.hit:
                self.hit_timer += 16.67
                if self.hit_timer >= self.hit_duration:
                    self.hit = False
                    self.hit_timer = 0
            
            # Update blood particles
            if obstacles is not None and hasattr(self, 'blood_particles'):
                self.update_blood_particles(obstacles)
                
            return  # Skip the rest of the update while recovering
        
        # Handle knockback if active
        if self.is_being_knocked_back and obstacles is not None:
            # Update knockback timer
            self.knockback_timer += 16.67  # Approx ms per frame at 60fps
            
            # Apply knockback with diminishing effect
            if self.knockback_timer < self.knockback_duration:
                # Gradually decrease knockback effect
                progress = self.knockback_timer / self.knockback_duration
                knockback_factor = 1 - progress
                
                # Calculate movement for this frame
                dir_x, dir_y = self.knockback_direction
                move_x = dir_x * self.current_knockback * knockback_factor * 0.5
                move_y = dir_y * self.current_knockback * knockback_factor * 0.5
                
                # Move with collision detection
                self.move(move_x, move_y, obstacles)
            else:
                # End knockback
                self.is_being_knocked_back = False
                
                # Check if we should transition to recovery state - NEW
                if hasattr(self, 'should_recover') and self.should_recover:
                    self.state = "idle"  # Set idle state during recovery
                    self.is_recovering = True
                    self.recovery_timer = 0
                    self.should_recover = False  # Reset flag
                    print(f"{self.__class__.__name__} starting recovery after knockback")
        
        # Skip regular movement updates if being knocked back
        if self.is_being_knocked_back:
            # Update collision rect position
            self.rect.x = self.x
            self.rect.y = self.y
            
            # Update hit effect timer
            if self.hit:
                self.hit_timer += 16.67  # Approximate time between frames at 60 FPS
                if self.hit_timer >= self.hit_duration:
                    self.hit = False
                    self.hit_timer = 0
            
            # Update blood particles
            if obstacles is not None and hasattr(self, 'blood_particles'):
                self.update_blood_particles(obstacles)
                
            return
        
        # Regular update code
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
        
        # Update hit effect timer
        if self.hit:
            self.hit_timer += 16.67  # Approximate time between frames at 60 FPS
            if self.hit_timer >= self.hit_duration:
                self.hit = False
                self.hit_timer = 0
        
        # Update blood particles
        if obstacles is not None and hasattr(self, 'blood_particles'):
            self.update_blood_particles(obstacles)

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
        # Skip if recovering - NEW
        if self.is_recovering:
            return
            
        self.stop_moving()
        
        # Get attack power from attributes
        attack_power = self.attributes.get_attack_power()
        
        # Damage player and pass enemy position for knockback direction
        enemy_center_x = self.x + (self.width / 2)
        enemy_center_y = self.y + (self.height / 2)
        player.take_damage(attack_power, enemy_center_x, enemy_center_y)
    
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
        """Move with collision detection and screen boundary checks"""
        if dx == 0 and dy == 0:
            return False
            
        from constants import SCREEN_WIDTH, SCREEN_HEIGHT
            
        # Create test rectangles for movement along each axis separately
        test_rect_x = pygame.Rect(self.x + dx, self.y, self.width, self.height)
        test_rect_y = pygame.Rect(self.x, self.y + dy, self.width, self.height)
        
        # Define how much of the enemy can go outside the screen (as a percentage of their size)
        # Adjust these values to control how far enemies can go off-screen
        margin_x = self.width * 0.75  # Allow 75% of width to go outside
        margin_y = self.height * 0.75  # Allow 75% of height to go outside
        
        # Check if the move would take the enemy too far outside screen boundaries
        x_boundary_violation = (test_rect_x.left < -margin_x or 
                            test_rect_x.right > SCREEN_WIDTH + margin_x)
        
        y_boundary_violation = (test_rect_y.top < -margin_y or 
                            test_rect_y.bottom > SCREEN_HEIGHT + margin_y)
        
        # Check horizontal movement
        x_collision = x_boundary_violation  # Start with boundary check
        if not x_collision:  # Only check obstacles if boundary check passed
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
        y_collision = y_boundary_violation  # Start with boundary check
        if not y_collision:  # Only check obstacles if boundary check passed
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
            
        # If we hit an obstacle or boundary, consider changing direction
        if x_collision or y_collision:
            # Higher chance to change direction when hitting a boundary (75% vs 25% for obstacles)
            chance = 0.75 if (x_boundary_violation or y_boundary_violation) else 0.25
            if random.random() < chance:
                self.start_moving()
            return False
            
        # Successfully moved
        return True

    def attack(self, player):
        """Start attack animation and deal damage - may be overridden by subclasses"""
        # Skip if recovering - NEW
        if self.is_recovering:
            return
            
        self.state = "attacking"
        self.animation_counter = 0
        
        # Get attack power from attributes
        attack_power = self.attributes.get_attack_power()
        
        # Basic attack logic - subclasses can override for specific behavior
        print(f"{self.__class__.__name__} attacks for {attack_power} damage!")
    
    def take_damage(self, damage, attacker_x=None, attacker_y=None, player_x=None, player_y=None):
        """Take damage with defense calculation and trigger knockback
        
        Parameters:
        - damage: Amount of damage before defense reduction
        - attacker_x, attacker_y: Position of the attack (e.g., sword hitbox)
        - player_x, player_y: Position of the player's center (for knockback direction)
        """
        # Skip if already dying
        if self.state == "dying":
            return False
        
        # Store current hit state - NEW
        was_hit = self.hit
            
        # Apply damage through attribute system
        final_damage = self.attributes.take_damage(damage)
        self.health = self.attributes.current_health
        
        # Set hit flag for visual feedback
        self.hit = True
        self.hit_timer = 0
        
        print(f"Enemy {self.__class__.__name__} took {final_damage} damage, {self.health} health remaining")
        
        # If this is a new hit (not already in hit state), set recovery flag - NEW
        if not was_hit:
            self.should_recover = True
        
        # Start knockback effect - use player position for direction if provided
        self.start_knockback(damage, player_x, player_y)
                # Cancel recovery if hit again
        self.is_recovering = False
        self.recovery_timer = 0

        if self.health <= 0:
            print(f"Enemy {self.__class__.__name__} died!")
            self.die()
            return True  # Enemy died
        else:
            return False  # Enemy still alive

    def start_knockback(self, damage_amount, player_x=None, player_y=None):
        """Start or refresh knockback animation when taking damage"""
        if self.state == "dying":
            return False

        # Calculate knockback resistance from attributes
        knockback_resistance = self.attributes.get_knockback_factor()

        # Calculate knockback amount
        knockback_factor = min(1.0, damage_amount / self.attributes.max_health * 2)
        base_knockback = 40
        actual_knockback = base_knockback * knockback_factor * (1 - knockback_resistance)

        if actual_knockback < 3:
            return False

        # Calculate knockback direction
        if player_x is not None and player_y is not None:
            enemy_center_x = self.x + (self.width / 2)
            enemy_center_y = self.y + (self.height / 2)

            dir_x = enemy_center_x - player_x
            dir_y = enemy_center_y - player_y

            length = max(0.1, math.sqrt(dir_x**2 + dir_y**2))
            dir_x /= length
            dir_y /= length
        else:
            # Fallback direction
            dir_x = 1.0 if self.direction == "right" else -1.0
            dir_y = 0.0

        # ✅ Always restart knockback
        self.knockback_direction = (dir_x, dir_y)
        self.current_knockback = actual_knockback
        self.knockback_timer = 0
        self.is_being_knocked_back = True

        return True

    def die(self):
        """Start death animation and prepare to drop a soul"""
        # Set dying state to trigger death animation
        self.state = "dying"
        self.animation_counter = 0
        
        # Create death particles
        self.create_death_particles()
        
        # Set a timer for removing the entity
        self.death_timer = 0
        self.should_remove = False  # Will be set to True when death animation completes
        
        # Prepare to drop a soul
        self.will_drop_soul = True
        
        # Add this line to clear the collision rectangle immediately when dying
        self.rect = pygame.Rect(0, 0, 0, 0)
        
        print(f"{self.__class__.__name__} is dying!")
    
    def create_death_particles(self):
        """Create particles for death animation"""
        self.death_particles = []
        
        # Create 15-20 particles for death effect
        particle_count = random.randint(15, 20)
        
        # Enemy center coordinates
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        for _ in range(particle_count):
            # Random angle for 360-degree spread
            angle = random.uniform(0, 2 * math.pi)
            
            # Direction vector from angle
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            # Random distance from center
            distance = random.uniform(0, self.width / 3)
            
            # Starting position with some randomness
            start_x = center_x + dir_x * distance
            start_y = center_y + dir_y * distance
            
            # Random size, larger than blood particles
            size = random.randint(5, 12)
            
            # Random color (white to gray to black smoke effect)
            gray = random.randint(150, 250)
            color = (gray, gray, gray)
            
            # Create particle
            self.death_particles.append({
                'x': start_x,
                'y': start_y,
                'vel_x': dir_x * random.uniform(0.5, 2.0),
                'vel_y': dir_y * random.uniform(0.5, 2.0),
                'size': size,
                'color': color,
                'life': random.randint(15, 30),
                'max_life': 30
            })
    
    def update_death_particles(self):
        """Update death particles"""
        # Update each particle
        for particle in self.death_particles[:]:
            # Move particle
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Apply "float upward" effect
            particle['vel_y'] -= 0.05  # Slight upward acceleration
            
            # Apply friction
            particle['vel_x'] *= 0.95
            particle['vel_y'] *= 0.95
            
            # Decrease life
            particle['life'] -= 1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.death_particles.remove(particle)

    def update_blood_particles(self, obstacles):
        """Update blood particles for the enemy"""
        # Skip if no particles
        if not self.blood_particles:
            return
            
        # Update each particle
        for particle in self.blood_particles[:]:  # Use a copy of the list for safe iteration
            if particle:  # Make sure particle is not None
                particle.update(obstacles)
                
                # Remove inactive particles
                if not particle.active:
                    self.blood_particles.remove(particle)
    
    def get_rect(self):
        """Return collision rectangle"""
        if self.state == "dying":
            return pygame.Rect(0, 0, 0, 0)
        return self.rect
    
    def draw(self, surface):
        """Draw the enemy with appropriate animation frame and death effects"""
        # Draw detection radius if enabled - NEW
        if hasattr(self, 'show_detection_radius') and self.show_detection_radius:
            self.draw_detection_radius(surface)
        
        # If dying, only draw death particles
        if self.state == "dying":
            self.draw_death_particles(surface)
            return
        
        # Regular drawing for other states
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0 and self.frame < len(animation_frames):
            sprite = animation_frames[self.frame]
            
            # If we're using the right-facing sprites but need to face left,
            # and we don't have dedicated left sprites, then flip the sprite
            animation_key = f"{self.state}_right"
            if self.direction == "left" and animation_key in self.sprites:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # For hit effects, we'll only apply flashing to slimes
            from entities.enemy.slime import Slime
            
            if self.hit and isinstance(self, Slime):
                # Flash only for slimes
                if (self.hit_timer // 40) % 2 == 0:
                    surface.blit(sprite, (self.x, self.y))
            else:
                # Normal drawing for all other cases
                surface.blit(sprite, (self.x, self.y))
            
            # Draw blood particles
            if hasattr(self, 'blood_particles'):
                for particle in self.blood_particles:
                    if particle:
                        particle.draw(surface)
    
    def draw_detection_radius(self, surface):
        """Draw the detection radius as a circle for debugging - NEW"""
        # Get center of the enemy
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw detection range (light blue, semi-transparent)
        detection_surface = pygame.Surface((self.detection_range * 2, self.detection_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(detection_surface, (0, 150, 255, 40), (self.detection_range, self.detection_range), self.detection_range)
        surface.blit(detection_surface, (center_x - self.detection_range, center_y - self.detection_range))
        
        # Draw attack range (red, semi-transparent)
        attack_surface = pygame.Surface((self.attack_range * 2, self.attack_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(attack_surface, (255, 0, 0, 40), (self.attack_range, self.attack_range), self.attack_range)
        surface.blit(attack_surface, (center_x - self.attack_range, center_y - self.attack_range))
    
    def draw_death_particles(self, surface):
        """Draw death particles"""
        if not hasattr(self, 'death_particles'):
            return
            
        for particle in self.death_particles:
            # Calculate fade-out based on life
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            # Create surface for particle
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            
            # Set color with transparency
            color_with_alpha = (*particle['color'], alpha)
            
            # Draw smoke-like particle (circle with blur effect)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                             (particle['size']//2, particle['size']//2), 
                             particle['size']//2)
            
            # Draw the particle
            surface.blit(particle_surface, 
                       (particle['x'] - particle['size']//2, 
                        particle['y'] - particle['size']//2))
    
    def drop_soul(self):
        """Drop a soul when enemy dies"""
        # Import here to avoid circular imports
        from entities.soul import Soul
        
        # Enemy center coordinates
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        # Create a soul at the enemy's position
        soul = Soul(center_x - 10, center_y - 10, self.attributes.level)  # Offset for centering
        
        # Return the soul so it can be added to the world
        return soul
        
    def load_sprites(self):
        """
        Load sprites for the enemy - this is a placeholder method
        that should be overridden by subclasses
        """
        pass
        
    def render_debug_info(self, surface, font, x, y):
        """Display enemy attribute information for debugging"""
        if hasattr(self, 'attributes'):
            # Add state information to debug display - NEW
            state_text = f"State: {self.state}"
            if self.is_recovering:
                state_text += " (recovering)"
            elif self.is_being_knocked_back:
                state_text += " (knockback)"
                
            info_text = self.attributes.get_info_text() + " | " + state_text
            debug_text = font.render(info_text, True, (255, 0, 0))
            surface.blit(debug_text, (x, y))
        else:
            debug_text = font.render(f"No attributes", True, (255, 0, 0))
            surface.blit(debug_text, (x, y))