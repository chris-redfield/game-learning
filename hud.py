import pygame
from entities.enemy.enemy import Enemy

class HUD:
    def __init__(self, player):
        self.player = player
        
        # Colors
        self.colors = {
            'border': (30, 30, 30),         # Dark border
            'health': (220, 50, 50),        # Red for health (always)
            'mana': (50, 50, 220),          # Blue for mana
            'bg': (60, 60, 60),             # Dark gray background
            'text': (255, 255, 255),        # White text
            'xp': (255, 255, 255)           # White for XP text
        }
        
        # Fonts
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)  # Smaller font for XP text
        
        # Cached positions and measurements
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()
        
        # Bar scaling parameters
        self.health_base_width = 30         # Base width for initial health (6)
        self.health_scaling = 7             # Width increase per health point
        self.mana_base_width = 10           # Base width for initial mana (2)
        self.mana_scaling = 6               # Width increase per mana point

    def draw_status_bars(self, surface):
        """Draw health and mana bars in the main game view"""
        # Measurements
        margin = 10                        # Margin from screen edge
        bar_spacing = 5                    # Space between bars
        bar_height = 15                    # Height of each bar
        icon_size = 40                     # Size of the octagonal icon
        max_bar_width = 300                # Maximum width for any bar
        
        # Draw the octagonal icon (placeholder for character icon)
        icon_x = margin
        icon_y = margin
        pygame.draw.rect(surface, self.colors['border'], (icon_x, icon_y, icon_size, icon_size))
        pygame.draw.rect(surface, (30, 30, 40), (icon_x + 2, icon_y + 2, icon_size - 4, icon_size - 4))
        
        # Calculate health bar width - scales linearly with max health
        health_width = min(max_bar_width, self.health_base_width + (self.player.attributes.max_health - 5) * self.health_scaling)
        
        # Calculate mana bar width - scales linearly with max mana, independent of health
        mana_width = min(max_bar_width, self.mana_base_width + (self.player.attributes.max_mana - 1) * self.mana_scaling)
        
        # Bar positions
        health_x = icon_x + icon_size + 10
        health_y = icon_y
        mana_x = health_x
        mana_y = health_y + bar_height + bar_spacing
        
        # Calculate fill percentages
        health_percent = self.player.attributes.current_health / self.player.attributes.max_health
        health_fill_width = int(health_width * health_percent)
        
        mana_percent = self.player.attributes.current_mana / self.player.attributes.max_mana
        mana_fill_width = int(mana_width * mana_percent)
        
        # Draw health bar
        pygame.draw.rect(surface, self.colors['bg'], (health_x, health_y, health_width, bar_height))
        pygame.draw.rect(surface, self.colors['border'], (health_x, health_y, health_width, bar_height), 1)
        pygame.draw.rect(surface, self.colors['health'], (health_x, health_y, health_fill_width, bar_height))
        
        # Draw mana bar
        pygame.draw.rect(surface, self.colors['bg'], (mana_x, mana_y, mana_width, bar_height))
        pygame.draw.rect(surface, self.colors['border'], (mana_x, mana_y, mana_width, bar_height), 1)
        pygame.draw.rect(surface, self.colors['mana'], (mana_x, mana_y, mana_fill_width, bar_height))
        
        # Display XP text underneath the icon - with fixed alignment
        # Now we access XP through the attributes component
        xp_text = self.font.render(f"XP: {int(self.player.attributes.xp)}/{int(self.player.attributes.xp_needed)}", True, self.colors['xp'])
        text_x = icon_x
        text_y = icon_y + icon_size + 5  # 5px padding below the icon
        surface.blit(xp_text, (text_x, text_y))
        
        # Display values on bars
        health_text = self.font.render(f"{self.player.attributes.current_health}/{self.player.attributes.max_health}", True, self.colors['text'])
        surface.blit(health_text, (health_x + 5, health_y))
        
        mana_text = self.font.render(f"{self.player.attributes.current_mana}/{self.player.attributes.max_mana}", True, self.colors['text'])
        surface.blit(mana_text, (mana_x + 5, mana_y))

    def render_ability_info(self, surface):
        """Display ability status information"""
        # Position below status bars with extra space for XP text
        x = 10
        y = 85  # Increased to make room for XP text under the icon
        
        # Display ability info based on skill tree unlocks
        # Dash ability
        if self.player.skill_tree.is_skill_unlocked("dash"):
            if self.player.attributes.dashing:
                dash_status = "ACTIVE"
                color = (0, 255, 0)  # Green when active
            elif self.player.attributes.dash_timer == 0:
                dash_status = "Ready"
                color = (255, 255, 255)  # White when ready
            else:
                dash_status = "Cooling Down"
                color = (255, 165, 0)  # Orange when on cooldown
                
            dash_text = self.font.render(f"Dash: {dash_status}", True, color)
            surface.blit(dash_text, (x, y))
            y += 25
        
        # Extended Sword ability  
        if self.player.skill_tree.is_skill_unlocked("extended_sword"):
            sword_text = self.font.render(f"Extended Sword: Active", True, self.colors['text'])
            surface.blit(sword_text, (x, y))
            y += 25
            
        # Blink ability
        if self.player.skill_tree.is_skill_unlocked("blink"):
            blink_status = "Ready" if self.player.attributes.blink_timer == 0 else "Cooling Down"
            blink_color = self.colors['text'] if self.player.attributes.blink_timer == 0 else (255, 165, 0)
            blink_text = self.font.render(f"Blink: {blink_status}", True, blink_color)
            surface.blit(blink_text, (x, y))

    def display_world_info(self, surface, block_info):
        """Display information about the current world block"""
        block_text = self.font.render(f"Current: {block_info}", True, self.colors['text'])
        surface.blit(block_text, (self.screen_width - 150, 10))

    def display_controls(self, surface):
        """Display game controls"""
        controls_y = self.screen_height - 165  # Adjusted to fit the new control line
        controls_text = [
            "Controls:",
            "WASD or Arrow Keys: Move",
            "SPACE: Swing Sword",
            "E: Interact",
            "SHIFT: Dash (if unlocked)",
            "B: Blink (if unlocked)",
            "+: Level Up",
            "C: Show Collision Boxes",
            "M: Toggle Map",
            "ENTER: Character Screen"
        ]
        
        for i, text in enumerate(controls_text):
            text_surface = self.font.render(text, True, self.colors['text'])
            surface.blit(text_surface, (10, controls_y + i * 15))

    def draw_transition_effect(self, surface, fade_surface, fade_alpha, transition_direction):
        """Draw transition effect between blocks"""
        # Set alpha for fade surface
        fade_surface.set_alpha(fade_alpha)
        surface.blit(fade_surface, (0, 0))
        
        # Show transition text during fade
        if fade_alpha > 50 and transition_direction:
            direction_text = self.font.render(f"Moving {transition_direction.upper()}", True, self.colors['text'])
            text_rect = direction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(direction_text, text_rect)

    def display_enemy_debug(self, surface, entities):
        """Display debug info for each enemy instance."""
        x = self.screen_width - 450  # Right side
        y = 40  # Start below the world info
        line_gap = 20

        any_found = False

        for entity in entities:
            if isinstance(entity, Enemy):
                any_found = True
                name = getattr(entity, 'name', entity.__class__.__name__)
                level = entity.attributes.level
                speed = round(entity.speed,3)
                
                difficulty = getattr(entity, 'difficulty', 'normal')
                state = getattr(entity, 'state', 'unknown')

                attributes = getattr(entity, 'attributes', None)
                if not attributes:
                    continue

                max_health = getattr(attributes, 'max_health', 0)
                current_health = getattr(attributes, 'current_health', 0)
                attack = round(getattr(attributes, 'attack_power', 0),3)
                defense = round(getattr(attributes, 'defense', 0),3)

                # Choose color
                color = {
                    'normal': (200, 200, 200),
                    'fast': (0, 255, 0),
                    'strong': (255, 0, 0),
                }.get(difficulty, (255, 255, 255))

                text = f"{name} (Lvl {level}, {difficulty}) HP {current_health}/{max_health} ATK {attack} DEF {defense} SPEED: {speed} State: {state}"
                debug_surface = self.font.render(text, True, color)
                surface.blit(debug_surface, (x, y))
                y += line_gap

        if not any_found:
            no_data_text = self.font.render("No enemy debug info available.", True, (255, 255, 0))
            surface.blit(no_data_text, (x, y))

    def draw(self, surface, game_world, fade_surface=None, fade_alpha=0, transition_direction=None, transition_in_progress=False, entities=None, show_enemy_debug=False):
        """Draw all HUD elements"""
        # Draw status bars
        self.draw_status_bars(surface)
        
        # Display ability info (moved to separate area)
        self.render_ability_info(surface)
        
        # Display world info
        block_info = game_world.get_block_description()
        self.display_world_info(surface, block_info)
        
        # Display controls
        self.display_controls(surface)
        
        # Draw enemy debug info if enabled
        if show_enemy_debug and entities:
            self.display_enemy_debug(surface, entities)

        # Draw transition effect if in progress
        if transition_in_progress and fade_surface:
            self.draw_transition_effect(surface, fade_surface, fade_alpha, transition_direction)