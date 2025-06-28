import pygame
import random
import math
import threading
from entities.npc.npc import NPC
from entities.npc.dialog_balloon import dialog_balloon_system

try:
    from entities.npc.llm import get_dialogue_for_npc, add_player_dialogue
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LLM module not found - Link will use pre-defined dialogues")

class Link(NPC):
    def __init__(self, x, y, use_llm=False):
        self.character_name = "Link"
        # self.character_type = "link"
        self.character_type = "warrior"

        # LLM integration
        self.use_llm = use_llm and LLM_AVAILABLE

        # Call parent constructor with hardcoded character name
        super().__init__(x, y, character_name=self.character_name)

        # Link-specific properties
        self.speed = 3  # Same as player's starting speed
        self.base_speed = 3

        # Link-specific AI behavior settings
        self.movement_pause = random.randint(90, 240)  # Pause duration between movements
        self.movement_duration = random.randint(80, 200)

        # Link is more interactive
        self.interaction_range = 100  # Larger interaction range
        self.is_friendly = True

        # Link-specific dialogue states
        self.dialogue_options = [
            "Hey! Listen!",
            "It's dangerous to go alone!",
            "I'm looking for Princess Zelda.",
            "Have you seen any rupees around?",
            "This reminds me of Hyrule."
        ]

        self.dialog_cooldown = 0
        self.dialog_cooldown_duration = 3000  # 3 seconds between dialogues

        # Combat preferences - Link is more aggressive
        self.combat_ready = True
        self.attack_nearby_enemies = True
        self.enemy_detection_range = 120

        # Link-specific animation speed (slightly more energetic)
        self.animation_speed = 0.18
        
        # Store player reference for LLM usage
        self._last_known_player = None
        
        # Async LLM handling
        self.llm_thinking = False  # Flag to prevent multiple concurrent LLM requests

        print(f"Link NPC created at ({x}, {y}) - LLM mode: {'enabled' if self.use_llm else 'disabled'}")

    def get_player_data(self, player):
        """Extract player data for LLM context"""
        if not player:
            return {}
        
        player_data = {
            'level': player.attributes.level if hasattr(player, 'attributes') else 1,
            'health': player.attributes.current_health if hasattr(player, 'attributes') else 100,
            'max_health': player.attributes.max_health if hasattr(player, 'attributes') else 100,
            'stats': {
                'str': player.attributes.str if hasattr(player, 'attributes') else 1,
                'con': player.attributes.con if hasattr(player, 'attributes') else 1,
                'dex': player.attributes.dex if hasattr(player, 'attributes') else 1,
                'int': player.attributes.int if hasattr(player, 'attributes') else 1,
            },
            'skills': [],
            'location': "the game world"  # Could be enhanced with actual location data
        }
        
        # Extract unlocked skills
        if hasattr(player, 'skill_tree'):
            for skill_id, skill in player.skill_tree.skills.items():
                if skill.unlocked:
                    player_data['skills'].append(skill.name)
        
        return player_data

    def _llm_dialogue_thread(self, player_data, context):
        """Thread function to generate LLM dialogue without blocking"""
        try:
            llm_dialogue = get_dialogue_for_npc(
                npc_name=self.character_name, 
                player_data=player_data, 
                context=context,
                character_type=self.character_type
            )
            if llm_dialogue:
                # Update the dialogue balloon from the thread
                dialog_balloon_system.add_dialog(
                    llm_dialogue,
                    self.x, self.y, self.width, self.height
                )
            else:
                # Fallback if LLM returns nothing
                self._show_fallback_dialogue()
        except Exception as e:
            print(f"LLM dialogue generation failed: {e}")
            # Fallback on error
            self._show_fallback_dialogue()
        finally:
            self.llm_thinking = False
    
    def _show_fallback_dialogue(self):
        """Show a random pre-defined dialogue as fallback"""
        dialogue = random.choice(self.dialogue_options)
        dialog_balloon_system.add_dialog(
            dialogue,
            self.x, self.y, self.width, self.height
        )

    def say_random_dialogue(self):
        """Make Link say something using dialogue balloon"""
        if self.dialog_cooldown == 0:
            # Set cooldown immediately to prevent multiple calls
            current_time = pygame.time.get_ticks()
            self.dialog_cooldown = current_time + self.dialog_cooldown_duration
            
            # Try to use LLM if enabled and we have a player reference
            if self.use_llm and self._last_known_player and not self.llm_thinking:
                # Show thinking indicator immediately
                dialog_balloon_system.add_dialog(
                    "...",
                    self.x, self.y, self.width, self.height
                )
                
                # Mark as thinking
                self.llm_thinking = True
                
                try:
                    player_data = self.get_player_data(self._last_known_player)
                    context = "The player is standing near you."
                    
                    # Add context based on player state
                    if player_data['health'] < player_data['max_health'] * 0.3:
                        context = "The player is badly injured and needs help!"
                    elif player_data['level'] < 3:
                        context = "The player is still a beginner adventurer."
                    elif player_data['level'] > 10:
                        context = "The player is an experienced adventurer."
                    
                    # Start LLM thread
                    llm_thread = threading.Thread(
                        target=self._llm_dialogue_thread,
                        args=(player_data, context),
                        daemon=True  # Daemon thread will close with the main program
                    )
                    llm_thread.start()
                    
                except Exception as e:
                    print(f"Failed to start LLM thread: {e}")
                    self.llm_thinking = False
                    self._show_fallback_dialogue()
            else:
                # Use pre-made dialogue if LLM is disabled, unavailable, or already thinking
                self._show_fallback_dialogue()

    def on_player_nearby(self, player):
        """Called when player is in interaction range"""
        # Link might say something when player is nearby
        if self.dialog_cooldown == 0 and random.random() < 0.02:  # 2% chance per frame
            self.interact_with_player(player)

    def interact_with_player(self, player):
        """Handle interaction with player"""
        if self.dialog_cooldown == 0:
            # 80% chance to say something
            if random.random() < 0.8:
                self.say_random_dialogue()
            # 20% chance to offer help
            else:
                self.offer_help(player)

    def offer_help(self, player):
        """Link offers help to the player"""
        help_options = [
            "take_some_rupees",
            "share_wisdom",
            "heal_player",
            "give_item"
        ]

        help_type = random.choice(help_options)

        if help_type == "take_some_rupees":
            # Give player some XP (representing rupees)
            xp_amount = random.randint(5, 15)
            player.gain_xp(xp_amount)
            dialog_balloon_system.add_dialog(
                f"Here, take these {xp_amount} rupees!",
                self.x, self.y, self.width, self.height
            )

        elif help_type == "share_wisdom":
            wisdom_quotes = [
                "The Master Sword sleeps in the forest...",
                "Courage need not be remembered, for it is never forgotten!",
                "Sometimes you need to take a step back to move forward."
            ]
            dialog_balloon_system.add_dialog(
                random.choice(wisdom_quotes),
                self.x, self.y, self.width, self.height
            )

        elif help_type == "heal_player":
            if player.attributes.current_health < player.attributes.max_health:
                heal_amount = random.randint(10, 25)
                player.heal(heal_amount)
                dialog_balloon_system.add_dialog(
                    f"My fairy healed you for {heal_amount} HP!",
                    self.x, self.y, self.width, self.height
                )
            else:
                dialog_balloon_system.add_dialog(
                    "You're already at full health!",
                    self.x, self.y, self.width, self.height
                )

        elif help_type == "give_item":
            dialog_balloon_system.add_dialog(
                "I'd give you something, but my pockets are empty!",
                self.x, self.y, self.width, self.height
            )

    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        """Link-specific damage handling"""
        # Call parent damage handling
        result = super().take_damage(amount, attacker_x, attacker_y)

        # Link becomes more aggressive when hurt
        if result:
            self.combat_ready = True
            self.attack_nearby_enemies = True
            # Temporarily increase detection range when hurt
            self.enemy_detection_range = min(200, self.enemy_detection_range * 1.5)

            # Link says something when hurt
            pain_quotes = ["Ow!", "That hurt!", "You'll pay for that!", "I won't give up!"]
            dialog_balloon_system.add_dialog(
                random.choice(pain_quotes),
                self.x, self.y, self.width, self.height
            )

        return result

    def engage_enemy(self, enemy, current_time):
        """Move towards and attack an enemy"""
        link_center = (self.x + self.width/2, self.y + self.height/2)
        enemy_center = (enemy.x + enemy.width/2, enemy.y + enemy.height/2)

        dx = enemy_center[0] - link_center[0]
        dy = enemy_center[1] - link_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        # If close enough to attack
        if distance <= 40 and not self.swinging:
            # Face the enemy
            if abs(dx) > abs(dy):
                self.facing = 'right' if dx > 0 else 'left'
            else:
                self.facing = 'down' if dy > 0 else 'up'

            # Attack!
            self.start_swing()
            self.state = "attacking"

            # Battle cry!
            battle_cries = ["Hyah!", "Take this!", "For Hyrule!"]
            if random.random() < 0.3:  # 30% chance to shout
                dialog_balloon_system.add_dialog(
                    random.choice(battle_cries),
                    self.x, self.y, self.width, self.height
                )

        elif distance > 40:
            # Move towards the enemy at normal speed
            if distance > 0:
                self.dx = (dx / distance) * self.speed
                self.dy = (dy / distance) * self.speed

                # Update facing direction
                if abs(dx) > abs(dy):
                    self.facing = 'right' if dx > 0 else 'left'
                else:
                    self.facing = 'down' if dy > 0 else 'up'

                self.state = "moving"
                self.moving = True

    def update(self, current_time=None, obstacles=None, player=None):
        """Link-specific update with enhanced AI behavior - Fixed to avoid double movement"""
        
        # Store player reference for LLM usage
        if player:
            self._last_known_player = player

        # Handle movement animation (from parent)
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

        # Handle sword swing animation (from parent)
        if self.swinging:
            self.swing_animation_counter += self.swing_animation_speed

            if self.swing_animation_counter >= self.swing_frames_total:
                self.swinging = False
                self.swing_animation_counter = 0
                # Reset state after swing completes
                if self.state == "attacking":
                    self.state = "idle"
                    self.moving = False
                if hasattr(self, 'hit_enemies'):
                    self.hit_enemies.clear()

            self.swing_frame = int(self.swing_animation_counter)

        if current_time:
            # Track time delta for animations (from parent)
            time_delta = current_time - (getattr(self, 'last_update_time', current_time))

            # Handle damage animation and knockback (from parent)
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

            # Handle invulnerability and flashing effect (from parent)
            if self.invulnerable:
                self.invulnerability_timer += time_delta

                if (self.invulnerability_timer // self.flash_interval) % 2 == 0:
                    self.visible = True
                else:
                    self.visible = False

                if self.invulnerability_timer >= self.invulnerability_duration:
                    self.invulnerable = False
                    self.visible = True

            # Update particles (from parent)
            self.particles.update(current_time, obstacles)

            # Store current time for next update (from parent)
            self.last_update_time = current_time

        # Check for player interaction (from parent)
        if player and self.is_interactable:
            self.check_player_interaction(player)
       
        # Update dialogue cooldown
        if current_time and self.dialog_cooldown > 0:
            if current_time > self.dialog_cooldown:
                self.dialog_cooldown = 0

        # Link-specific AI behaviors (ONLY THESE, no parent AI)
        if not self.is_taking_damage and obstacles is not None:
            # Check for nearby enemies to fight
            if self.combat_ready and self.attack_nearby_enemies:
                self.check_for_enemies(obstacles, current_time)

            # Enhanced movement AI - Link's own AI system (replaces parent AI)
            self.update_link_ai(obstacles)

        # Check sword collisions when Link is swinging
        if self.swinging and obstacles is not None:
            hit_something = self.check_sword_collisions(obstacles)
            if hit_something:
                print(f"Link's sword hit an enemy!")

    def check_for_enemies(self, obstacles, current_time):
        """Check for nearby enemies and engage in combat"""
        if self.swinging or self.state == "attacking":
            return

        from entities.enemy.enemy import Enemy

        link_center = (self.x + self.width/2, self.y + self.height/2)

        closest_enemy = None
        closest_distance = float('inf')

        # Find the closest enemy within detection range
        for obstacle in obstacles:
            if isinstance(obstacle, Enemy) and obstacle.state != "dying":
                enemy_center = (obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2)

                dx = enemy_center[0] - link_center[0]
                dy = enemy_center[1] - link_center[1]
                distance = math.sqrt(dx**2 + dy**2)

                if distance <= self.enemy_detection_range and distance < closest_distance:
                    closest_enemy = obstacle
                    closest_distance = distance

        # If enemy found, move towards it and attack
        if closest_enemy:
            self.engage_enemy(closest_enemy, current_time)

    def update_link_ai(self, obstacles):
        """Enhanced AI movement for Link - more exploratory behavior"""
        if self.state == "attacking":
            return

        # If not currently pursuing an enemy, use enhanced movement AI
        if self.state == "idle":
            self.movement_timer += 1
            if self.movement_timer >= self.movement_pause:
                self.movement_timer = 0
                # Link has a 30% chance to move (70% idling)
                if random.random() < 0.30:
                    self.start_enhanced_movement()
                else:
                    self.movement_pause = random.randint(90, 240)

        elif self.state == "moving":
            self.movement_timer += 1
            if self.movement_timer >= self.movement_duration:
                self.movement_timer = 0
                self.stop_moving()
                self.movement_pause = random.randint(90, 240)
            else:
                # Apply AI movement
                self.ai_move(self.dx, self.dy, obstacles)

    def start_enhanced_movement(self):
        """Enhanced movement patterns for Link"""
        self.state = "moving"
        self.moving = True

        # Link has more varied movement patterns
        movement_type = random.choice(['random', 'directional', 'circular'])

        if movement_type == 'random':
            # Standard random movement
            angle = random.uniform(0, 2 * math.pi)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed

        elif movement_type == 'directional':
            # Move in cardinal directions (more purposeful)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            dir_x, dir_y = random.choice(directions)
            self.dx = dir_x * self.speed
            self.dy = dir_y * self.speed

        elif movement_type == 'circular':
            # Slightly curved movement
            base_angle = random.uniform(0, 2 * math.pi)
            curve_factor = random.uniform(-0.3, 0.3)
            self.dx = math.cos(base_angle + curve_factor) * self.speed
            self.dy = math.sin(base_angle + curve_factor) * self.speed

        # Set facing direction based on movement
        if abs(self.dx) > abs(self.dy):
            self.facing = 'right' if self.dx > 0 else 'left'
        else:
            self.facing = 'down' if self.dy > 0 else 'up'

    def draw(self, surface):
        """Draw Link with any special effects"""
        # Call parent draw method
        super().draw(surface)

        # Could add special visual effects for Link here
        # For example, a small triforce symbol above his head when player is nearby
        pass

    def render_debug_info(self, surface, font, x, y):
        """Display Link's debug information"""
        if hasattr(self, 'attributes'):
            # Add Link-specific state information
            state_text = f"State: {self.state}"
            if self.combat_ready:
                state_text += " (combat ready)"
            if self.dialog_cooldown > 0:
                state_text += " (thinking)"
            if self.llm_thinking:
                state_text += " (🤔 LLM)"

            info_text = (f"Link: {self.attributes.get_info_text()} | {state_text} | "
                        f"Range: {self.enemy_detection_range}")
            debug_text = font.render(info_text, True, (0, 255, 0))  # Green for Link
            surface.blit(debug_text, (x, y))
        else:
            debug_text = font.render(f"Link: No attributes", True, (0, 255, 0))
            surface.blit(debug_text, (x, y))

    def respond_to_player_message(self, player, player_message):
        """Handle when the player says something to Link"""
        if self.use_llm and LLM_AVAILABLE:
            add_player_dialogue("Link", player_message)
            self._last_known_player = player
            self.say_random_dialogue()
        else:
            self.interact_with_player(player)