import pygame
import math


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 35  # Increased by ~10% from 32
        self.height = 41  # Increased by ~10% from 37
        self.speed = 3
        
        # Starting attributes
        self.str = 1  # Strength
        self.con = 1  # Constitution
        self.dex = 1  # Dexterity
        self.int = 1  # Intelligence

        self.max_health = 10 + (self.con * 2)  # Base health + CON bonus
        self.current_health = self.max_health
        self.max_mana = 1 + self.int  # Base mana + INT bonus
        self.current_mana = self.max_mana
        self.stat_points = 0  # Available points to spend

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
        
        # Damage animation properties
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_animation_duration = 500  # milliseconds
        self.damage_knockback_distance = 20   # pixels
        self.knockback_direction = None
        self.invulnerable = False
        self.invulnerability_duration = 1000  # milliseconds
        self.invulnerability_timer = 0
        self.flash_interval = 100  # milliseconds
        self.visible = True       # For damage flash effect

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
    
    def increase_stat(self, stat_name):
        """Increase a stat if stat points are available"""
        if self.stat_points <= 0:
            return False
            
        if stat_name == "str":
            self.str += 1
            # Strength increases attack power
            self.stat_points -= 1
            return True
        elif stat_name == "con":
            self.con += 1
            # Constitution increases health
            old_max_health = self.max_health
            self.max_health = 10 + (self.con * 2)
            # Increase current health by the difference
            self.current_health += (self.max_health - old_max_health)
            self.stat_points -= 1
            return True
        elif stat_name == "dex":
            self.dex += 1
            # Dexterity increases movement speed slightly
            self.base_speed = 3 + (self.dex * 0.05)
            self.speed = self.base_speed  # Update current speed
            self.stat_points -= 1
            return True
        elif stat_name == "int":
            self.int += 1
            # Intelligence increases mana
            old_max_mana = self.max_mana
            self.max_mana = 1 + self.int
            # Increase current mana by the difference
            self.current_mana += (self.max_mana - old_max_mana)
            self.stat_points -= 1
            return True
            
        return False

    def level_up(self):
        """Increase player level and unlock abilities"""
        if self.level < self.max_level:
            self.level += 1
            self.stat_points += 1  # Gain a stat point on level up
            print(f"Level up! Player is now level {self.level} and gained a stat point!")
            
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
            
            return True
        else:
            print(f"Already at max level ({self.max_level})! No more levels available.")
            return False
            
    def get_attack_power(self):
        """Calculate attack power based on strength"""
        return 1 + int(self.str * 0.5)  # Base attack + STR bonus
        
    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        """Handle player taking damage with animation and knockback
        
        Args:
            amount: Amount of damage to take
            attacker_x: X position of the damage source (if available)
            attacker_y: Y position of the damage source (if available)
        """
        # Skip if already taking damage or invulnerable
        if self.is_taking_damage or self.invulnerable:
            return False
        
        # Calculate damage reduction based on constitution (defense)
        defense_factor = 1.0 - (self.con * 0.05)  # 5% reduction per CON point
        final_damage = max(1, int(amount * defense_factor))  # Minimum 1 damage
        
        # Apply damage
        self.current_health -= final_damage
        if self.current_health < 0:
            self.current_health = 0
            # Handle player death
            
        # Calculate knockback direction
        if attacker_x is not None and attacker_y is not None:
            # Calculate direction vector from attacker to player
            dir_x = self.x + (self.width / 2) - attacker_x
            dir_y = self.y + (self.height / 2) - attacker_y
            
            # Normalize the direction vector
            length = max(0.1, (dir_x**2 + dir_y**2)**0.5)
            dir_x /= length
            dir_y /= length
        else:
            # Default knockback direction based on facing (opposite to facing)
            dir_x, dir_y = 0, 0
            if self.facing == 'right':
                dir_x = -1
            elif self.facing == 'left':
                dir_x = 1
            elif self.facing == 'down':
                dir_y = -1
            elif self.facing == 'up':
                dir_y = 1
        
        # Store knockback direction
        self.knockback_direction = (dir_x, dir_y)
        
        # Start damage animation
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        
        # Make player invulnerable
        self.invulnerable = True
        self.invulnerability_timer = 0
        
        # Calculate knockback strength based on constitution
        # Higher CON means less knockback
        knockback_reduction = min(0.8, self.con * 0.1)  # Up to 80% reduction
        self.current_knockback = self.damage_knockback_distance * (1 - knockback_reduction)
        
        print(f"Player took {final_damage} damage! Knockback direction: ({dir_x:.2f}, {dir_y:.2f})")
        return True

    def heal(self, amount):
        """Heal the player"""
        self.current_health = min(self.current_health + amount, self.max_health)
        
    def use_mana(self, amount):
        """Use mana if available"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
        
    def restore_mana(self, amount):
        """Restore mana"""
        self.current_mana = min(self.current_mana + amount, self.max_mana)
    
    def update(self, current_time=None, obstacles=None):
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
            # Track time delta for animations
            time_delta = current_time - (getattr(self, 'last_update_time', current_time))
            
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
                
            # Handle damage animation and knockback
            if self.is_taking_damage and obstacles is not None:
                # Update timer
                self.damage_animation_timer += time_delta
                
                # Apply knockback - using a larger factor for more noticeable effect
                if self.damage_animation_timer < self.damage_animation_duration:
                    # Calculate knockback movement for this frame
                    progress = self.damage_animation_timer / self.damage_animation_duration
                    knockback_factor = 1 - progress  # Gradually reduce knockback
                    
                    # Apply knockback movement - increased multiplier for stronger effect
                    dir_x, dir_y = self.knockback_direction
                    move_x = dir_x * self.current_knockback * knockback_factor * 0.5
                    move_y = dir_y * self.current_knockback * knockback_factor * 0.5
                    
                    # Create test rectangles for collision detection during knockback
                    test_rect_x = pygame.Rect(self.x + move_x, self.y, self.width, self.height)
                    test_rect_y = pygame.Rect(self.x, self.y + move_y, self.width, self.height)
                    
                    # Check for collisions on each axis separately
                    x_collision = False
                    for obstacle in obstacles:
                        # Skip self-collision
                        if obstacle is self:
                            continue
                        if test_rect_x.colliderect(obstacle.get_rect()):
                            x_collision = True
                            break
                    
                    # Only apply X movement if no collision
                    if not x_collision:
                        self.x += move_x
                    
                    # Check Y collision
                    y_collision = False
                    for obstacle in obstacles:
                        # Skip self-collision
                        if obstacle is self:
                            continue
                        if test_rect_y.colliderect(obstacle.get_rect()):
                            y_collision = True
                            break
                    
                    # Only apply Y movement if no collision
                    if not y_collision:
                        self.y += move_y
                    
                    # If we hit an obstacle on both axes, end the knockback animation early
                    if x_collision and y_collision:
                        self.is_taking_damage = False
                else:
                    # End damage animation
                    self.is_taking_damage = False
                    
            # Handle invulnerability and flashing effect
            if self.invulnerable:
                self.invulnerability_timer += time_delta
                
                # Toggle visibility for flashing effect
                if (self.invulnerability_timer // self.flash_interval) % 2 == 0:
                    self.visible = True
                else:
                    self.visible = False
                    
                # End invulnerability after duration
                if self.invulnerability_timer >= self.invulnerability_duration:
                    self.invulnerable = False
                    self.visible = True
            
            # Store current time for next update
            self.last_update_time = current_time

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
            collided_with_enemy = False
            
            for obstacle in obstacles:
                obstacle_rect = obstacle.get_rect()
                if test_rect.colliderect(obstacle_rect):
                    collision = True
                    
                    # Check if the obstacle is an enemy
                    from entities.enemy import Enemy  # Import here to avoid circular imports
                    if isinstance(obstacle, Enemy):
                        collided_with_enemy = True
                        # Let the enemy handle the collision
                        obstacle.handle_player_collision(self)
                    
                    break
            
            # Only move if there's no collision or if collided with an enemy
            # (we still want to move if hitting an enemy, just take damage)
            if not collision or collided_with_enemy:
                # Update position
                self.x += dx
                self.y += dy
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
        # Don't draw if not visible (flashing during invulnerability)
        if not self.visible:
            # Still draw the sword if swinging, even when player is flashing
            if self.swinging:
                self.draw_sword(surface)
            return
        
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
        
        # Tint the sprite red if taking damage
        if self.is_taking_damage:
            # Create a copy of the sprite to modify
            tinted_sprite = sprite.copy()
            
            # Add a transparent red overlay
            overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 100))  # Red with alpha
            tinted_sprite.blit(overlay, (0, 0))
            
            # Draw the tinted player character
            surface.blit(tinted_sprite, (self.x, self.y))
        else:
            # Draw the normal player character
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