import pygame
import random
import math
from entities.enemy.enemy import Enemy
from entities.enemy.enemy_attribute import EnemyAttributes

class Skeleton(Enemy):
    def __init__(self, x, y):
        # Define skeleton-specific dimensions
        width = 48
        height = 52
        
        # Call parent constructor
        super().__init__(x, y, width, height, speed=1)
        
        # Set skeleton-specific type (default to "normal")
        self.enemy_type = "normal"  # Could be "brute" in higher difficulties
        
        # Initialize attributes with skeleton defaults
        self.attributes = EnemyAttributes(self, level=1, enemy_type=self.enemy_type)
        
        # Update properties from attributes 
        self.health = self.attributes.max_health
        self.attack_power = self.attributes.get_attack_power()
        self.defense = self.attributes.defense
        
        # Skeleton animation properties
        self.animation_speed = 0.08
        
        # Attack state tracking
        self.attack_timer = 0
        self.attack_duration = 500  # ms
        self.attack_cooldown = 800  # ms
        self.attack_cooldown_timer = 0
        self.can_attack = True
        
        # Recovery state tracking (1 second break after being hit)
        self.is_recovering = False
        self.recovery_timer = 0
        self.recovery_duration = 1000  # 1 second in milliseconds
        
        # Load skeleton sprites
        self.load_sprites()
        
        # Debug: Verify sprites were loaded
        sprites_count = sum(len(frames) for frames in self.sprites.values())
        print(f"Skeleton created at ({x}, {y}) with {sprites_count} sprite frames")
        
        # Debug visualization
        self.show_detection_radius = False
    
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
            
            print(f"Successfully loaded skeleton sprites: {len(self.sprites['idle_right'])} idle, {len(self.sprites['moving_right'])} moving")
                
        except Exception as e:
            print(f"Error loading skeleton sprites: {e}")
            # Create colored rectangle placeholders
            for _ in range(7):  # Only 7 idle frames
                idle_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                idle_placeholder.fill((200, 200, 200))
                # Add border for better visibility
                pygame.draw.rect(idle_placeholder, (100, 100, 100), 
                               (0, 0, self.width, self.height), 2)
                self.sprites['idle_right'].append(idle_placeholder)
            
            for _ in range(9):  # 9 walking frames
                move_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                move_placeholder.fill((180, 180, 180))
                # Add border for better visibility
                pygame.draw.rect(move_placeholder, (90, 90, 90), 
                               (0, 0, self.width, self.height), 2)
                self.sprites['moving_right'].append(move_placeholder)
            
            print(f"Created placeholder sprites for skeleton: {len(self.sprites['idle_right'])} idle, {len(self.sprites['moving_right'])} moving")
    
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
    
    def update(self, player=None, obstacles=None):
        """Skeleton specific update logic with attack state management"""
        # Store current time for timers
        current_time = pygame.time.get_ticks()
        
        # Check if recovering from being hit
        if self.is_recovering:
            # Update recovery timer
            self.recovery_timer += 16.67  # ~60 FPS
            
            # Check if recovery time is over
            if self.recovery_timer >= self.recovery_duration:
                self.is_recovering = False
                self.recovery_timer = 0
                print("Skeleton recovery complete, resuming activity")
                
            # Skip all other AI behavior while recovering
            # Just update basic animation
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
            
            return  # Skip the rest of the update while recovering
        
        # First check attack timers
        if self.state == "attacking":
            # Update attack timer
            self.attack_timer += 16.67  # ~60 FPS

            # If attack animation finished, transition back to movement
            if self.attack_timer >= self.attack_duration:
                print(f"Skeleton attack completed, returning to movement AI")
                self.attack_timer = 0
                self.state = "idle"  # Reset to idle, the AI will determine if we should move
                self.can_attack = False  # Start cooldown
                self.attack_cooldown_timer = current_time
        
        # Update attack cooldown
        if not self.can_attack:
            if current_time - self.attack_cooldown_timer >= self.attack_cooldown:
                self.can_attack = True
        
        # Call parent update for basic behavior - skip if recovering
        super().update(player, obstacles)
        
        # Skip additional AI if dying or being knocked back
        if self.state == "dying" or self.is_being_knocked_back:
            return
            
        # Add more advanced AI for skeletons when player is nearby
        if player and self.state != "attacking":
            # Calculate distance to player
            player_rect = player.get_rect()
            skeleton_center = (self.x + self.width/2, self.y + self.height/2)
            player_center = (player_rect.x + player_rect.width/2, player_rect.y + player_rect.height/2)
            
            dx = player_center[0] - skeleton_center[0]
            dy = player_center[1] - skeleton_center[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            # If player is within detection range, move toward them
            if distance < self.detection_range and distance > self.attack_range:
                self.state = "moving"
                
                # Calculate direction to player
                if distance > 0:
                    self.dx = (dx / distance) * self.speed
                    self.dy = (dy / distance) * self.speed
                    
                    # Update facing direction
                    if abs(dx) > abs(dy):
                        self.direction = "right" if dx > 0 else "left"
            
            # If player is within attack range and we can attack, attack
            elif distance < self.attack_range and self.can_attack:
                self.attack(player)
    
    def handle_player_collision(self, player):
        """Skeleton-specific player collision behavior using attributes"""
        # Skip if currently attacking, knocked back, or recovering
        if self.state == "attacking" or self.is_being_knocked_back or self.is_recovering:
            return
            
        self.stop_moving()
        
        # Get attack power from attributes
        attack_power = self.attributes.get_attack_power()
        
        # Damage player with position for knockback
        enemy_center_x = self.x + (self.width / 2)
        enemy_center_y = self.y + (self.height / 2)
        player.take_damage(attack_power, enemy_center_x, enemy_center_y)
        
        print(f"Skeleton collided with player, dealing {attack_power} damage")
        
        # Set attacking state to prevent continuous damage
        self.attack(player)
    
    def attack(self, player):
        """Skeleton-specific attack behavior using attributes"""
        # Don't attack if already attacking, in knockback, or on cooldown, or recovering
        if self.state == "attacking" or self.is_being_knocked_back or not self.can_attack or self.is_recovering:
            return
            
        # Start attack animation
        self.state = "attacking"
        self.animation_counter = 0
        self.attack_timer = 0  # Reset attack timer
        
        # Get attack power from attributes
        attack_power = self.attributes.get_attack_power()
        
        # Get skeleton position
        skeleton_center_x = self.x + (self.width / 2)
        skeleton_center_y = self.y + (self.height / 2)
        
        # Apply damage to player
        player.take_damage(attack_power, skeleton_center_x, skeleton_center_y)
        print(f"Skeleton attacks for {attack_power} damage! State: {self.state}")
    
    def take_damage(self, damage, attacker_x=None, attacker_y=None, player_x=None, player_y=None):
        """Take damage with attribute-based defense calculation and knockback"""
        # Store current state before taking damage
        old_state = self.state
        was_hit = self.hit
        
        # Use parent class implementation which now has attributes integrated
        result = super().take_damage(damage, attacker_x, attacker_y, player_x, player_y)
        
        # If this is a new hit (not already in hit state), start recovery timer
        # The recovery period will begin AFTER knockback ends
        if not was_hit and self.hit:
            # We'll start the recovery state when knockback ends (in update)
            # For now, just flag that we should enter recovery when knockback is done
            self.should_recover = True
            
        # Log state change for debugging
        print(f"Skeleton hit: State changed from {old_state} to {self.state}, knockback: {self.is_being_knocked_back}")
        
        return result
    
    def create_death_particles(self):
        """Create particles for skeleton death animation - bone fragments"""
        # Call parent method first
        super().create_death_particles()
        
        # Add some bone-like particles (whiter)
        particle_count = random.randint(10, 15)
        
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
            
            # Random size for bone fragments
            size = random.randint(3, 7)
            
            # Whiter colors for bone particles
            white = random.randint(220, 255)
            color = (white, white, white - random.randint(10, 30))
            
            # Create bone particle
            self.death_particles.append({
                'x': start_x,
                'y': start_y,
                'vel_x': dir_x * random.uniform(0.7, 2.0),
                'vel_y': dir_y * random.uniform(0.7, 2.0),
                'size': size,
                'color': color,
                'life': random.randint(20, 35),
                'max_life': 35
            })
    
    def die(self):
        """Override to add skeleton-specific death behavior"""
        # Call parent implementation
        super().die()
        print(f"Skeleton dying at ({self.x}, {self.y})")
    
    def draw(self, surface):
        """Override draw method to ensure visibility and draw detection radius if enabled"""
        # First draw detection radius if debugging is enabled
        if self.show_detection_radius:
            self.draw_detection_radius(surface)
        
        # If dying, just draw death particles
        if self.state == "dying":
            self.draw_death_particles(surface)
            return
        
        # Get animation frames
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0 and self.frame < len(animation_frames):
            sprite = animation_frames[self.frame]
            
            # Handle left-facing sprites by flipping the right sprites
            if self.direction == "left":
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Handle hit animation
            if self.hit:
                # Only draw on even frames during hit animation for flashing effect
                if (self.hit_timer // 40) % 2 == 0:
                    surface.blit(sprite, (self.x, self.y))
            else:
                # Normal drawing
                surface.blit(sprite, (self.x, self.y))
            
            # Draw blood particles if any
            if hasattr(self, 'blood_particles'):
                for particle in self.blood_particles:
                    if particle:
                        particle.draw(surface)
    
    def draw_detection_radius(self, surface):
        """Draw the detection radius as a circle for debugging"""
        # Get center of the skeleton
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
    
    def render_debug_info(self, surface, font, x, y):
        """Display enemy attribute information for debugging"""
        if hasattr(self, 'attributes'):
            # Add state information to debug display
            state_text = f"State: {self.state}"
            if self.is_recovering:
                state_text += " (recovering)"
            elif self.is_being_knocked_back:
                state_text += " (knockback)"
            elif not self.can_attack:
                state_text += " (cooldown)"
                
            info_text = self.attributes.get_info_text() + " | " + state_text
            debug_text = font.render(info_text, True, (220, 220, 220))  # Light gray for skeletons
            surface.blit(debug_text, (x, y))
        else:
            debug_text = font.render(f"No attributes", True, (220, 220, 220))
            surface.blit(debug_text, (x, y))