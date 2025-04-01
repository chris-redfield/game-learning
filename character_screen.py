import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class CharacterScreen:
    def __init__(self, player):
        self.player = player
        self.visible = False
        
        # Colors
        self.colors = {
            'background': (30, 33, 41, 230),  # Dark blue-gray, semi-transparent
            'text': (255, 255, 255),          # White text
            'title': (255, 215, 0),           # Gold for titles
            'stat_text': (0, 255, 0),         # Green for stat values
            'button': (100, 100, 120),        # Button background
            'button_hover': (130, 130, 150),  # Button hover state
            'button_disabled': (70, 70, 80),  # Disabled button
            'border': (180, 180, 200),        # Border color
            'health': (220, 50, 50),          # Health bar
            'mana': (50, 50, 220),            # Mana bar
            'portrait_bg': (30, 30, 40),      # Portrait background
            'cursor': (255, 255, 0),          # Cursor highlight color
            'grid_bg': (40, 40, 50),          # Item grid background
            'grid_border': (100, 100, 120)    # Item grid cell border
        }
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.stat_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.button_font = pygame.font.SysFont('Arial', 16)
        
        # Load portrait
        self.portrait = self.load_portrait()
        
        # UI components
        self.buttons = {}
        self.init_buttons()
        
        # Controller navigation
        self.selected_index = 0
        self.button_order = ['inc_str', 'inc_con', 'inc_dex', 'inc_int']
        
        # Item grid configuration
        self.grid_cols = 5
        self.grid_rows = 3
        self.cell_size = 50
        self.grid_padding = 5
        
        # Placeholder items (replace with actual player items later)
        self.items = [
            {"id": "potion", "name": "Health Potion", "count": 3},
            {"id": "key", "name": "Dungeon Key", "count": 1},
            {"id": "sword", "name": "Silver Sword", "count": 1},
            {"id": "shield", "name": "Wooden Shield", "count": 1},
            {"id": "arrow", "name": "Arrows", "count": 20}
        ]
        
    def load_portrait(self):
        """Load Link portrait from file with fallback to placeholder"""
        portrait_size = 220
        
        try:
            # Try loading the portrait image
            portrait_img = pygame.image.load('assets/portrait-pixel-art.png')
            
            # Scale it to fit the portrait area while maintaining aspect ratio
            original_width, original_height = portrait_img.get_size()
            scaling_factor = min(portrait_size / original_width, portrait_size / original_height)
            
            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)
            
            scaled_portrait = pygame.transform.scale(portrait_img, (new_width, new_height))
            
            # Create a surface with border
            portrait = pygame.Surface((portrait_size, portrait_size))
            portrait.fill(self.colors['portrait_bg'])
            
            # Center the image in the portrait
            x_offset = (portrait_size - new_width) // 2
            y_offset = (portrait_size - new_height) // 2
            
            portrait.blit(scaled_portrait, (x_offset, y_offset))
            
            # Add border
            pygame.draw.rect(portrait, self.colors['border'], (0, 0, portrait_size, portrait_size), 3)
            
            print("Loaded Link portrait successfully")
            return portrait
            
        except Exception as e:
            print(f"Error loading portrait: {e}")
            # Fall back to placeholder
            return self.create_placeholder_portrait()
        
    def create_placeholder_portrait(self):
        """Create a placeholder portrait if the image can't be loaded"""
        portrait_size = 150
        portrait = pygame.Surface((portrait_size, portrait_size))
        portrait.fill(self.colors['portrait_bg'])
        
        # Draw a simple face
        pygame.draw.circle(portrait, (200, 180, 150), (portrait_size//2, portrait_size//2), portrait_size//3)  # Head
        pygame.draw.circle(portrait, (50, 50, 70), (portrait_size//2 - 15, portrait_size//2 - 10), 5)  # Left eye
        pygame.draw.circle(portrait, (50, 50, 70), (portrait_size//2 + 15, portrait_size//2 - 10), 5)  # Right eye
        
        # Draw a happy face
        pygame.draw.arc(portrait, (50, 50, 70), 
                       (portrait_size//2 - 20, portrait_size//2 - 10, 40, 30), 
                       0, 3.14, 2)  # Smile
        
        # Add a border
        pygame.draw.rect(portrait, self.colors['border'], (0, 0, portrait_size, portrait_size), 3)
        
        print("Using placeholder portrait")
        return portrait
        
    def init_buttons(self):
        """Initialize button elements"""
        # Stat increase buttons positioned to the right of each attribute name
        button_width = 30
        button_height = 30
        
        # These buttons will now be positioned relative to the attribute section
        # Will be used in draw() method to position them correctly
        stats = ['str', 'con', 'dex', 'int']
        for i, stat in enumerate(stats):
            # Just initialize with temporary positions, we'll update them in draw()
            self.buttons[f'inc_{stat}'] = {
                'rect': pygame.Rect(0, 0, button_width, button_height),
                'text': '+',
                'action': lambda s=stat: self.player.increase_stat(s)
            }
    
    def toggle(self):
        """Toggle the character screen visibility"""
        self.visible = not self.visible
        # Reset selection on open
        if self.visible:
            self.selected_index = 0
        return self.visible
        
    def is_visible(self):
        """Check if character screen is currently visible"""
        return self.visible
    
    def select_next(self):
        """Move to next button"""
        self.selected_index = (self.selected_index + 1) % len(self.button_order)
        
    def select_prev(self):
        """Move to previous button"""
        self.selected_index = (self.selected_index - 1) % len(self.button_order)
        
    def handle_event(self, event):
        """Handle mouse and controller events for the character screen"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button clicks
            for button_id, button in self.buttons.items():
                if button['rect'].collidepoint(mouse_pos):
                    # Only allow clicking if player has stat points
                    if self.player.attributes.stat_points > 0:
                        result = button['action']()
                        return True
        
        # Controller button handling
        elif event.type == pygame.JOYBUTTONDOWN:
               
            # Button 0 (A) to activate selected button
            if event.button == 0:
                if self.player.attributes.stat_points > 0:
                    button_id = self.button_order[self.selected_index]
                    result = self.buttons[button_id]['action']()
                    return True
                    
        # D-pad handling
        elif event.type == pygame.JOYHATMOTION:
            hat_value = event.value
            if hat_value[1] == 1:  # D-pad up
                self.select_prev()
                return True
            elif hat_value[1] == -1:  # D-pad down
                self.select_next()
                return True
            
        # Keyboard handling for navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.select_prev()
                return True
            elif event.key == pygame.K_DOWN:
                self.select_next()
                return True
            
        return False
        
    def draw(self, surface):
        """Draw the character screen"""
        if not self.visible:
            return
            
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.colors['background'])
        surface.blit(overlay, (0, 0))
        
        # Draw border
        border_width = 4
        margin = 30
        pygame.draw.rect(surface, self.colors['border'], 
                        (margin, margin, SCREEN_WIDTH - margin*2, SCREEN_HEIGHT - margin*2), 
                        border_width)
        
        # Draw title
        title = self.title_font.render("CHARACTER SHEET", True, self.colors['title'])
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, margin + 20))
        
        # Draw close instructions with controller info
        close_text = self.text_font.render("Press ENTER or START to close", True, self.colors['text'])
        surface.blit(close_text, (SCREEN_WIDTH - close_text.get_width() - margin - 10, margin + 20))
        
        # Draw portrait section
        portrait_x = margin + 50
        portrait_y = margin + 80
        surface.blit(self.portrait, (portrait_x, portrait_y))
        
        # Draw character stats to the RIGHT of the portrait instead of below it
        stats_x = portrait_x + self.portrait.get_width() + 30
        stats_y = portrait_y
        
        # Draw level info next to portrait
        level_text = self.stat_font.render(f"Level: {self.player.attributes.level}", True, self.colors['stat_text'])
        surface.blit(level_text, (stats_x, stats_y))
        
        # Draw stat points
        stat_points_y = stats_y + 30
        stat_points_text = self.stat_font.render(f"Stat Points: {self.player.attributes.stat_points}", True, self.colors['title'])
        surface.blit(stat_points_text, (stats_x, stat_points_y))
        
        # Draw attribute values next to portrait
        attributes_text = [
            f"STR: {self.player.attributes.str}",
            f"CON: {self.player.attributes.con}",
            f"DEX: {self.player.attributes.dex}",
            f"INT: {self.player.attributes.int}"
        ]
        
        for i, text in enumerate(attributes_text):
            attr_text = self.text_font.render(text, True, self.colors['stat_text'])
            surface.blit(attr_text, (stats_x, stat_points_y + 30 + i * 25))
        
        # Draw health and mana bars next to portrait
        self.draw_resource_bars(surface, stats_x, stat_points_y + 150)
        
        # Draw attributes section
        attributes_x = SCREEN_WIDTH // 2
        attributes_y = 90
        
        attribute_title = self.stat_font.render("ATTRIBUTES", True, self.colors['title'])
        surface.blit(attribute_title, (attributes_x, attributes_y))
        
        # Draw attributes with buttons
        attribute_data = [
            {"name": "Strength", "key": "str"},
            {"name": "Constitution", "key": "con"},
            {"name": "Dexterity", "key": "dex"},
            {"name": "Intelligence", "key": "int"}
        ]
        
        for i, attr in enumerate(attribute_data):
            y_pos = attributes_y + 40 + i * 40
            
            # Attribute name
            name_text = self.text_font.render(attr["name"], True, self.colors['text'])
            surface.blit(name_text, (attributes_x, y_pos))
            
            # Update button position (to the right of the attribute name)
            button_id = f'inc_{attr["key"]}'
            button = self.buttons[button_id]
            
            # Position button to the right of the attributes section
            button_x = attributes_x + 200  # Fixed position on the right
            button_y = y_pos - 5  # Align vertically with attribute name
            button['rect'].x = button_x
            button['rect'].y = button_y
            
            button_color = self.colors['button_disabled']
            if self.player.attributes.stat_points > 0:
                button_color = self.colors['button']
                # Check hover
                if button['rect'].collidepoint(pygame.mouse.get_pos()):
                    button_color = self.colors['button_hover']
            
            # Check if this is the selected button with controller
            is_selected = self.button_order[self.selected_index] == button_id
            
            # Draw button with potentially highlighted background
            pygame.draw.rect(surface, button_color, button['rect'])
            
            # Draw selection cursor if this button is selected
            if is_selected:
                highlight_rect = button['rect'].inflate(6, 6)
                pygame.draw.rect(surface, self.colors['cursor'], highlight_rect, 2)
                
                # Show "A" prompt if points available
                if self.player.attributes.stat_points > 0:
                    a_text = self.button_font.render("A", True, self.colors['cursor'])
                    a_x = button['rect'].right + 10
                    a_y = button['rect'].centery - a_text.get_height() // 2
                    surface.blit(a_text, (a_x, a_y))
            
            # Button border
            pygame.draw.rect(surface, self.colors['border'], button['rect'], 1)
            
            # Button text
            button_text = self.button_font.render(button['text'], True, self.colors['text'])
            text_x = button['rect'].x + (button['rect'].width - button_text.get_width()) // 2
            text_y = button['rect'].y + (button['rect'].height - button_text.get_height()) // 2
            surface.blit(button_text, (text_x, text_y))
        
        # Draw abilities section based on level
        self.draw_abilities_section(surface, attributes_x, attributes_y + 210)
        
        # NEW: Draw items grid below the portrait
        self.draw_items_grid(surface, portrait_x, portrait_y + self.portrait.get_height() + 30)
        
    def draw_resource_bars(self, surface, x, y):
        """Draw health and mana bars"""
        bar_width = 200
        bar_height = 20
        
        # Health bar
        health_percent = self.player.attributes.current_health / self.player.attributes.max_health
        health_fill_width = int(bar_width * health_percent)
        
        pygame.draw.rect(surface, (60, 20, 20), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, self.colors['health'], (x, y, health_fill_width, bar_height))
        pygame.draw.rect(surface, self.colors['border'], (x, y, bar_width, bar_height), 1)
        
        health_text = self.text_font.render(f"Health: {self.player.attributes.current_health}/{self.player.attributes.max_health}", 
                                          True, self.colors['text'])
        surface.blit(health_text, (x + 10, y + 2))
        
        # Mana bar
        mana_percent = self.player.attributes.current_mana / self.player.attributes.max_mana
        mana_fill_width = int(bar_width * mana_percent)
        
        pygame.draw.rect(surface, (20, 20, 60), (x, y + 30, bar_width, bar_height))
        pygame.draw.rect(surface, self.colors['mana'], (x, y + 30, mana_fill_width, bar_height))
        pygame.draw.rect(surface, self.colors['border'], (x, y + 30, bar_width, bar_height), 1)
        
        mana_text = self.text_font.render(f"Mana: {self.player.attributes.current_mana}/{self.player.attributes.max_mana}", 
                                          True, self.colors['text'])
        surface.blit(mana_text, (x + 10, y + 32))
        
    def draw_abilities_section(self, surface, x, y):
        """Draw unlocked abilities based on player level"""
        abilities_title = self.stat_font.render("ABILITIES", True, self.colors['title'])
        surface.blit(abilities_title, (x, y))
        
        abilities = [
            {"name": "Sword Attack", "level": 1, "desc": "Basic sword attack (SPACE/Button 2)"},
            {"name": "Dash", "level": 2, "desc": "Temporary speed boost (SHIFT/Button 4)"},
            {"name": "Extended Sword", "level": 3, "desc": "Increased sword reach"},
            {"name": "Blink", "level": 4, "desc": "Short-range teleport (B/Button 1)"}
        ]
        
        # Use more vertical space for abilities
        for i, ability in enumerate(abilities):
            ability_y = y + 40 + i * 60  # Increased spacing between abilities
            
            # Ability name and status
            if self.player.attributes.level >= ability["level"]:
                status_color = self.colors['stat_text']  # Green for unlocked
                status_text = "UNLOCKED"
            else:
                status_color = (150, 150, 150)  # Gray for locked
                status_text = f"Unlocks at Level {ability['level']}"
                
            name_text = self.text_font.render(ability["name"], True, self.colors['text'])
            surface.blit(name_text, (x, ability_y))
            
            status_text = self.text_font.render(status_text, True, status_color)
            surface.blit(status_text, (x + 200, ability_y))
            
            # Description on next line (now with proper spacing)
            if self.player.attributes.level >= ability["level"]:
                desc_text = self.text_font.render(ability["desc"], True, (180, 180, 180))
                surface.blit(desc_text, (x + 20, ability_y + 25))
                
    def draw_items_grid(self, surface, x, y):
            """Draw an item grid below the portrait"""
            # Title for items section
            items_title = self.stat_font.render("ITEMS", True, self.colors['title'])
            surface.blit(items_title, (x, y))
            
            # Calculate grid dimensions
            grid_width = self.cell_size * self.grid_cols + self.grid_padding * (self.grid_cols + 1)
            grid_height = self.cell_size * self.grid_rows + self.grid_padding * (self.grid_rows + 1)
            
            # Draw grid background
            grid_rect = pygame.Rect(x, y + 35, grid_width, grid_height)
            pygame.draw.rect(surface, self.colors['grid_bg'], grid_rect)
            pygame.draw.rect(surface, self.colors['border'], grid_rect, 2)
            
            # Get player inventory items
            if hasattr(self.player, 'inventory'):
                inventory_items = self.player.inventory.get_items_and_counts()
            else:
                # Use placeholder items if player doesn't have inventory
                inventory_items = [
                    {"item": None, "count": 0} for _ in range(min(len(self.items), self.grid_cols * self.grid_rows))
                ]
            
            # Draw grid cells
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    cell_x = x + col * (self.cell_size + self.grid_padding) + self.grid_padding
                    cell_y = y + 35 + row * (self.cell_size + self.grid_padding) + self.grid_padding
                    
                    # Draw cell background
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    pygame.draw.rect(surface, self.colors['grid_border'], cell_rect, 1)
                    
                    # Get item index
                    item_idx = row * self.grid_cols + col
                    
                    # Draw item if it exists in inventory
                    if item_idx < len(inventory_items):
                        item_data = inventory_items[item_idx]
                        item = item_data['item']
                        count = item_data['count']
                        
                        if item:
                            # Get item icon if available
                            if hasattr(item, 'get_icon'):
                                icon = item.get_icon()
                                # Center the icon in the cell
                                icon_x = cell_x + (self.cell_size - icon.get_width()) // 2
                                icon_y = cell_y + (self.cell_size - icon.get_height()) // 2
                                surface.blit(icon, (icon_x, icon_y))
                            else:
                                # Fallback to a colored rectangle
                                icon_rect = pygame.Rect(cell_x + 5, cell_y + 5, self.cell_size - 10, self.cell_size - 10)
                                pygame.draw.rect(surface, (150, 150, 150), icon_rect)
                            
                            # Draw item count if more than 1
                            if count > 1:
                                count_text = self.text_font.render(f"{count}", True, self.colors['text'])
                                count_x = cell_x + self.cell_size - count_text.get_width() - 5
                                count_y = cell_y + self.cell_size - count_text.get_height() - 3
                                surface.blit(count_text, (count_x, count_y))
