import pygame
import math
import random
from inventory import Inventory
from .attributes import PlayerAttributes
from .particles import ParticleSystem
from .sprite_sheet import SpriteSheet

class NPC:
    def __init__(self, x, y, character_name="default_npc"):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 41
        self.speed = 2  # Slightly slower than player
        self.base_speed = 2
        
        # Store character name
        self.character_name = character_name
        
        # Create component systems (same as player)
        self.attributes = PlayerAttributes(self)
        self.particles = ParticleSystem(self)
        
        # Import here to avoid circular imports
        from entities.player.skill_tree import SkillTree
        # Initialize skill tree after attributes are created
        self.skill_tree = SkillTree(self)
        
        # Direction states
        self.facing = 'down'  # 'up', 'down', 'left', 'right'
        self.moving = False
        self.frame = 0
        self.animation_speed = 0.15  # Slightly slower animation
        self.animation_counter = 0
        
        # AI Movement states (from Enemy class)
        self.state = "idle"  # "idle", "moving", "interacting"
        self.movement_timer = 0
        self.movement_pause = random.randint(120, 300)  # Longer pauses than enemies
        self.movement_duration = random.randint(60, 180)  # How long to move
        self.dx = 0  # Current movement direction (x component)
        self.dy = 0  # Current movement direction (y component)
        
        # Sword swing states (keeping combat capability)
        self.swinging = False
        self.swing_frame = 0
        self.swing_animation_counter = 0
        self.swing_animation_speed = 0.31
        self.swing_frames_total = 5
        
        # Damage animation properties
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_animation_duration = 500
        self.damage_knockback_distance = 20
        self.knockback_direction = None
        self.invulnerable = False
        self.invulnerability_duration = 1000
        self.invulnerability_timer = 0
        self.flash_interval = 100
        self.visible = True
        
        # Hit enemies tracking (for sword collisions)
        self.hit_enemies = set()
        
        # Debug flag for sword collision visualization
        self.debug_sword_rect = False

        # NPC-specific properties
        self.interaction_range = 80  # Range at which player can interact
        self.is_interactable = True
        self.dialogue_state = "none"  # "none", "talking", "quest_giving"
        
        # Inventory (NPCs can have items)
        self.inventory = Inventory(max_slots=20)
        
        # Load character sprites
        self.load_sprites(character_name)
    
    def load_sprites(self, character_name):
        """Load sprites for the specified character"""
        self.sprite_sheet = SpriteSheet(character_name)
        self.sprites, self.sword_sprite = self.sprite_sheet.load_character_sprites(
            character_name, self.width, self.height
        )

    def gain_xp(self, amount):
        """Add XP to the NPC and check for level up"""
        # Create XP particles for visual feedback
        self.particles.create_xp_particles(amount)
        
        # Update attributes with XP gain
        return self.attributes.gain_xp(amount)
    
    def increase_stat(self, stat_name):
        """Forward to attribute component"""
        return self.attributes.increase_stat(stat_name)
    
    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        """Handle NPC taking damage with animation and knockback"""
        # Skip if already taking damage or invulnerable
        if self.is_taking_damage or self.invulnerable:
            return False
        
        # Calculate damage reduction based on constitution
        final_damage = self.attributes.take_damage(amount)
        
        # Apply damage
        self.attributes.current_health -= final_damage
        if self.attributes.current_health < 0:
            self.attributes.current_health = 0
            # Handle NPC death
            
        # Calculate knockback direction
        if attacker_x is not None and attacker_y is not None:
            # Calculate direction vector from attacker to NPC
            dir_x = self.x + (self.width / 2) - attacker_x
            dir_y = self.y + (self.height / 2) - attacker_y
            
            # Normalize the direction vector
            length = max(0.1, (dir_x**2 + dir_y**2)**0.5)
            dir_x /= length
            dir_y /= length
        else:
            # Default knockback direction based on facing
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
        
        # Make NPC invulnerable
        self.invulnerable = True
        self.invulnerability_timer = 0
        
        # Calculate knockback strength
        knockback_reduction = min(0.8, self.attributes.con * 0.1)
        self.current_knockback = self.damage_knockback_distance * (1 - knockback_reduction)
        
        # Create blood particles
        self.particles.spawn_blood_particles(final_damage)
        
        print(f"NPC {self.character_name} took {final_damage} damage!")
        return True

    def heal(self, amount):
        """Heal the NPC"""
        self.attributes.heal(amount)
        
    def use_mana(self, amount):
        """Use mana if available"""
        return self.attributes.use_mana(amount)
        
    def restore_mana(self, amount):
        """Restore mana"""
        self.attributes.restore_mana(amount)
    
    def start_moving(self):
        """Start movement in a random direction (AI behavior)"""
        self.state = "moving"
        self.moving = True
        
        # Choose a random direction vector
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        # Set facing direction based on movement
        if abs(self.dx) > abs(self.dy):
            self.facing = 'right' if self.dx > 0 else 'left'
        else:
            self.facing = 'down' if self.dy > 0 else 'up'
    
    def stop_moving(self):
        """Stop movement and go idle"""
        self.state = "idle"
        self.moving = False
        self.dx = 0
        self.dy = 0

    def update_ai_movement(self, obstacles):
        """Update AI movement behavior (similar to Enemy class)"""
        if self.state == "idle":
            self.movement_timer += 1
            if self.movement_timer >= self.movement_pause:
                self.movement_timer = 0
                # 70% chance to start moving (NPCs are less active than enemies)
                if random.random() < 0.7:
                    self.start_moving()
                else:
                    # Reset pause timer for another idle period
                    self.movement_pause = random.randint(120, 300)
        
        elif self.state == "moving":
            self.movement_timer += 1
            if self.movement_timer >= self.movement_duration:
                self.movement_timer = 0
                self.stop_moving()
                # Set new pause duration
                self.movement_pause = random.randint(120, 300)
            else:
                # Apply AI movement
                self.ai_move(self.dx, self.dy, obstacles)

    def ai_move(self, dx, dy, obstacles):
        """Move with collision detection for AI (similar to Enemy.move)"""
        if dx == 0 and dy == 0:
            return False
            
        from constants import SCREEN_WIDTH, SCREEN_HEIGHT
            
        # Create test rectangles for movement
        test_rect_x = pygame.Rect(self.x + dx, self.y, self.width, self.height)
        test_rect_y = pygame.Rect(self.x, self.y + dy, self.width, self.height)
        
        # Screen boundary margins
        margin_x = self.width * 0.5
        margin_y = self.height * 0.5
        
        # Check boundaries
        x_boundary_violation = (test_rect_x.left < -margin_x or 
                            test_rect_x.right > SCREEN_WIDTH + margin_x)
        
        y_boundary_violation = (test_rect_y.top < -margin_y or 
                            test_rect_y.bottom > SCREEN_HEIGHT + margin_y)
        
        # Check horizontal movement
        x_collision = x_boundary_violation
        if not x_collision:
            for obstacle in obstacles:
                if obstacle is self:
                    continue
                    
                # Skip collectible entities
                if hasattr(obstacle, 'is_collectible') and obstacle.is_collectible():
                    continue
                    
                if test_rect_x.colliderect(obstacle.get_rect()):
                    x_collision = True
                    break
        
        # Apply horizontal movement if no collision
        if not x_collision:
            self.x += dx
        
        # Check vertical movement
        y_collision = y_boundary_violation
        if not y_collision:
            for obstacle in obstacles:
                if obstacle is self:
                    continue
                    
                # Skip collectible entities
                if hasattr(obstacle, 'is_collectible') and obstacle.is_collectible():
                    continue
                    
                if test_rect_y.colliderect(obstacle.get_rect()):
                    y_collision = True
                    break
        
        # Apply vertical movement if no collision
        if not y_collision:
            self.y += dy
            
        # If we hit an obstacle or boundary, change direction
        if x_collision or y_collision:
            if random.random() < 0.8:  # High chance to change direction
                self.start_moving()
            return False
            
        return True
    
    def update(self, current_time=None, obstacles=None, player=None):
        """Update NPC state, animation, and AI"""
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
                if hasattr(self, 'hit_enemies'):
                    self.hit_enemies.clear()
            
            self.swing_frame = int(self.swing_animation_counter)

        if current_time:
            # Track time delta for animations
            time_delta = current_time - (getattr(self, 'last_update_time', current_time))
            
            # Handle damage animation and knockback (same as player)
            if self.is_taking_damage and obstacles is not None:
                self.damage_animation_timer += time_delta
                
                if self.damage_animation_timer < self.damage_animation_duration:
                    progress = self.damage_animation_timer / self.damage_animation_duration
                    knockback_factor = 1 - progress
                    
                    dir_x, dir_y = self.knockback_direction
                    move_x = dir_x * self.current_knockback * knockback_factor * 0.5
                    move_y = dir_y * self.current_knockback * knockback_factor * 0.5
                    
                    # Move with collision detection
                    test_rect_x = pygame.Rect(self.x + move_x, self.y, self.width, self.height)
                    test_rect_y = pygame.Rect(self.x, self.y + move_y, self.width, self.height)
                    
                    x_collision = False
                    for obstacle in obstacles:
                        if obstacle is self:
                            continue
                        if test_rect_x.colliderect(obstacle.get_rect()):
                            x_collision = True
                            break
                    
                    if not x_collision:
                        self.x += move_x
                    
                    y_collision = False
                    for obstacle in obstacles:
                        if obstacle is self:
                            continue
                        if test_rect_y.colliderect(obstacle.get_rect()):
                            y_collision = True
                            break
                    
                    if not y_collision:
                        self.y += move_y
                    
                    if x_collision and y_collision:
                        self.is_taking_damage = False
                else:
                    self.is_taking_damage = False
                    
            # Handle invulnerability and flashing effect
            if self.invulnerable:
                self.invulnerability_timer += time_delta
                
                if (self.invulnerability_timer // self.flash_interval) % 2 == 0:
                    self.visible = True
                else:
                    self.visible = False
                    
                if self.invulnerability_timer >= self.invulnerability_duration:
                    self.invulnerable = False
                    self.visible = True
            
            # Update particles
            self.particles.update(current_time, obstacles)
            
            # Store current time for next update
            self.last_update_time = current_time

        # Update AI movement if not taking damage
        if not self.is_taking_damage and obstacles is not None:
            self.update_ai_movement(obstacles)
        
        # Check for player interaction
        if player and self.is_interactable:
            self.check_player_interaction(player)

    def check_player_interaction(self, player):
        """Check if player is in interaction range"""
        player_rect = player.get_rect()
        npc_center = (self.x + self.width/2, self.y + self.height/2)
        player_center = (player_rect.x + player_rect.width/2, player_rect.y + player_rect.height/2)
        
        dx = player_center[0] - npc_center[0]
        dy = player_center[1] - npc_center[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.interaction_range:
            # Player is in range - could trigger dialogue or other interactions
            self.on_player_nearby(player)
    
    def on_player_nearby(self, player):
        """Called when player is in interaction range - override in subclasses"""
        pass
    
    def interact_with_player(self, player):
        """Handle interaction with player - override in subclasses"""
        print(f"Player interacts with {self.character_name}")

    def interact(self, player):
        """Wrapper method for compatibility with existing interaction system"""
        self.interact_with_player(player)
        
    def get_rect(self):
        """Return NPC collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def start_swing(self):
        """Start the sword swing animation"""
        if not self.swinging:
            self.swinging = True
            self.swing_animation_counter = 0
            self.swing_frame = 0
            if hasattr(self, 'hit_enemies'):
                self.hit_enemies.clear()
            else:
                self.hit_enemies = set()
            
    def is_swinging(self):
        """Check if NPC is currently swinging the sword"""
        return self.swinging

    def check_sword_collisions(self, obstacles):
        """Check if the sword is colliding with any enemies and apply damage"""
        if not self.swinging:
            return False
            
        sword_rect = self.get_sword_rect()
        if not sword_rect:
            return False
            
        if not hasattr(self, 'hit_enemies'):
            self.hit_enemies = set()
        
        if self.swing_frame == 0:
            self.hit_enemies.clear()
            
        hit_something = False
        
        npc_center_x = self.x + (self.width / 2)
        npc_center_y = self.y + (self.height / 2)
        
        # Check collisions with enemies
        from entities.enemy.enemy import Enemy
        for obstacle in obstacles:
            if (not isinstance(obstacle, Enemy) or 
                obstacle in self.hit_enemies or
                obstacle.state == "dying"):
                continue
                
            if sword_rect.colliderect(obstacle.get_rect()):
                damage = self.attributes.get_attack_power()
                
                obstacle.take_damage(
                    damage,
                    attacker_x=sword_rect.centerx,
                    attacker_y=sword_rect.centery,
                    player_x=npc_center_x,
                    player_y=npc_center_y
                )
                
                self.particles.spawn_enemy_blood(obstacle)
                self.hit_enemies.add(obstacle)
                hit_something = True
                
        return hit_something

    def get_sword_rect(self):
        """Get a sword hitbox that scales with the sword length"""
        if not self.swinging:
            return None
            
        # Same implementation as player
        npc_center_x = self.x + self.width / 2
        npc_center_y = self.y + self.height / 2
        
        if self.facing == 'up':
            npc_center_y -= 9
        
        hitbox_size = 24
        base_distance = 20
        
        length_scale = self.attributes.sword_length / self.attributes.base_sword_length
        scaled_distance = base_distance * length_scale
        
        if length_scale > 1:
            hitbox_size = int(hitbox_size * (1 + (length_scale - 1) * 0.5))
        
        if self.facing == 'right':
            base_dir_x, base_dir_y = 1, 0
        elif self.facing == 'left':
            base_dir_x, base_dir_y = -1, 0
        elif self.facing == 'up':
            base_dir_x, base_dir_y = 0, -1
            scaled_distance *= 1.2
        elif self.facing == 'down':
            base_dir_x, base_dir_y = 0, 1
            scaled_distance *= 1.2
            npc_center_y += 10
        
        swing_progress = min(1.0, self.swing_animation_counter / self.swing_frames_total)
        swing_angle = math.radians(-45 + 90 * swing_progress)
        
        cos_angle = math.cos(swing_angle)
        sin_angle = math.sin(swing_angle)
        
        dir_x = base_dir_x * cos_angle - base_dir_y * sin_angle
        dir_y = base_dir_x * sin_angle + base_dir_y * cos_angle
        
        hitbox_x = npc_center_x + dir_x * scaled_distance - hitbox_size/2
        hitbox_y = npc_center_y + dir_y * scaled_distance - hitbox_size/2
        
        return pygame.Rect(hitbox_x, hitbox_y, hitbox_size, hitbox_size)

    def draw_sword_rect(self, surface):
        """Draw the sword collision rectangle for debugging"""
        if not self.swinging:
            return
            
        sword_rect = self.get_sword_rect()
        if sword_rect:
            pygame.draw.rect(surface, (255, 0, 0), sword_rect, 2)

    def draw_sword(self, surface):
        """Draw sword with a 90-degree swing centered on NPC's facing direction"""
        if not self.swinging:
            return
            
        # Same implementation as player
        npc_center_x = self.x + self.width / 2
        npc_center_y = self.y + self.height / 2
        
        if self.facing == 'up':
            npc_center_y -= 9

        base_angles = {
            'right': 0,
            'left': math.pi,
            'up': -math.pi/2,
            'down': math.pi/2
        }
        
        base_angle = base_angles[self.facing]
        angle_offset = (self.swing_animation_counter / self.swing_frames_total) * math.pi/2 - math.pi/4
        rotation_angle = base_angle + angle_offset
        
        sword_length = self.attributes.sword_length
        
        sword_x = npc_center_x + math.cos(rotation_angle) * sword_length
        sword_y = npc_center_y + math.sin(rotation_angle) * sword_length
        
        display_angle = -math.degrees(rotation_angle) - 90
        
        rotated_sword = pygame.transform.rotate(self.sword_sprite, display_angle)
        sword_rect = rotated_sword.get_rect()
        
        handle_offset_x = sword_rect.width * 0.5
        handle_offset_y = sword_rect.height * 0.2
        
        offset_x = sword_x - handle_offset_x
        offset_y = sword_y - handle_offset_y
        
        surface.blit(rotated_sword, (offset_x, offset_y))
    
    def draw(self, surface):
        """Draw the NPC with appropriate animation frame"""
        # Don't draw if not visible (flashing during invulnerability)
        if not self.visible:
            if self.swinging:
                self.draw_sword(surface)
                if hasattr(self, 'debug_sword_rect') and self.debug_sword_rect:
                    self.draw_sword_rect(surface)
            
            self.particles.draw_active_blood(surface)
            self.particles.draw_xp_particles(surface)
            return
        
        # If in debug mode and a debug sprite is loaded, draw that instead
        if hasattr(self, 'debug_sprite'):
            surface.blit(self.debug_sprite, (self.x, self.y))
            self.particles.draw_active_blood(surface)
            self.particles.draw_xp_particles(surface)
            return
        
        # For left-facing, use the right sprites but flip them horizontally
        if self.facing == 'left':
            if self.moving:
                right_sprite = self.sprites['right_walk'][self.frame]
                sprite = pygame.transform.flip(right_sprite, True, False)
            else:
                right_sprite = self.sprites['right_idle'][0]
                sprite = pygame.transform.flip(right_sprite, True, False)
        else:
            if self.moving:
                sprite = self.sprites[f'{self.facing}_walk'][self.frame]
            else:
                sprite = self.sprites[f'{self.facing}_idle'][0]
        
        # Draw the NPC character
        surface.blit(sprite, (self.x, self.y))
        
        # Draw sword if NPC is swinging
        self.draw_sword(surface)
        
        # Debug: Draw sword collision rectangle if enabled
        if hasattr(self, 'debug_sword_rect') and self.debug_sword_rect:
            self.draw_sword_rect(surface)
        
        # Draw particles
        self.particles.draw_active_blood(surface)
        self.particles.draw_xp_particles(surface)

    def draw_stuck_blood(self, surface):
        """Backward compatibility for draw_stuck_blood"""
        self.particles.draw_stuck_blood(surface)

    def set_current_block(self, block_x, block_y):
        """Forward to particle system"""
        self.particles.set_current_block(block_x, block_y)
        
    def render_level_info(self, surface, font, x, y):
        """Display NPC level information on screen"""
        self.attributes.render_info(surface, font, x, y)

    def use_item(self, item_index):
        """Use an item from the inventory"""
        if 0 <= item_index < len(self.inventory.items):
            item = self.inventory.items[item_index]
            
            if item.use(self):
                self.inventory.remove_item(item_index)
                return True
        
        return False