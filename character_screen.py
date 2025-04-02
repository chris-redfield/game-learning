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
            'grid_border': (100, 100, 120),   # Item grid cell border
            'item_hover': (80, 80, 100),      # Highlighted item background
            'item_selected': (100, 100, 150), # Selected item background
            'usable': (100, 180, 100),        # Usable item indicator
            'unusable': (180, 100, 100),      # Unusable item indicator
            'feedback_bg': (0, 0, 0, 180),    # Item feedback message background
            'feedback_text': (255, 220, 100)  # Item feedback message text
        }
        
        # Item feedback message variables
        self.item_feedback_message = None
        self.item_feedback_timer = 0
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.stat_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.button_font = pygame.font.SysFont('Arial', 16)
        self.desc_font = pygame.font.SysFont('Arial', 16)
        
        # Load portrait
        self.portrait = self.load_portrait()
        
        # UI components
        self.buttons = {}
        self.init_buttons()
        
        # Controller navigation
        self.selected_index = 0
        self.button_order = ['inc_str', 'inc_con', 'inc_dex', 'inc_int']
        
        # Item grid configuration
        self.grid_cols = 6
        self.grid_rows = 4
        self.cell_size = 50
        self.grid_padding = 5
        
        # Item selection variables
        self.selected_item_index = -1  # No item selected initially
        self.hovered_item_index = -1   # No item hovered initially
        self.is_inventory_focused = False  # Whether navigation is focused on inventory grid
        self.tooltip_visible = False   # Whether to show item tooltip
        self.tooltip_item = None       # Current item for tooltip
        
        # Add variables for navigation mode
        self.current_section = "stats"  # Can be "stats" or "inventory"
        self.grid_selected_row = 0
        self.grid_selected_col = 0
        
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
            self.current_section = "stats"
            self.selected_item_index = -1
            self.grid_selected_row = 0
            self.grid_selected_col = 0
        return self.visible
        
    def is_visible(self):
        """Check if character screen is currently visible"""
        return self.visible
    
    def select_next(self):
        """Move to next button or inventory item based on current section"""
        if self.current_section == "stats":
            self.selected_index = (self.selected_index + 1) % len(self.button_order)
        elif self.current_section == "inventory":
            # Move to next column or wrap to next row
            self.grid_selected_col = (self.grid_selected_col + 1) % self.grid_cols
            # Update selected item index
            self.selected_item_index = self.grid_selected_row * self.grid_cols + self.grid_selected_col
            
            # Validate selection is within inventory bounds
            if hasattr(self.player, 'inventory'):
                inventory_size = len(self.player.inventory.get_items_and_counts())
                if self.selected_item_index >= inventory_size:
                    # Reset to first column
                    self.grid_selected_col = 0
                    # Move to next row or wrap around
                    self.grid_selected_row = (self.grid_selected_row + 1) % self.grid_rows
                    self.selected_item_index = self.grid_selected_row * self.grid_cols
                    
                    # Check again if we've gone past inventory bounds
                    if self.selected_item_index >= inventory_size:
                        self.grid_selected_row = 0
                        self.grid_selected_col = 0
                        self.selected_item_index = 0
        
    def select_prev(self):
        """Move to previous button or inventory item based on current section"""
        if self.current_section == "stats":
            self.selected_index = (self.selected_index - 1) % len(self.button_order)
        elif self.current_section == "inventory":
            # Move to previous column or wrap to previous row
            self.grid_selected_col = (self.grid_selected_col - 1) % self.grid_cols
            # Update selected item index
            self.selected_item_index = self.grid_selected_row * self.grid_cols + self.grid_selected_col
            
            # Validate selection is within inventory bounds
            if hasattr(self.player, 'inventory'):
                inventory_size = len(self.player.inventory.get_items_and_counts())
                if self.selected_item_index >= inventory_size:
                    # Set to last valid item
                    self.selected_item_index = inventory_size - 1
                    self.grid_selected_row = self.selected_item_index // self.grid_cols
                    self.grid_selected_col = self.selected_item_index % self.grid_cols
    
    def select_up(self):
        """Move selection up in the inventory grid"""
        if self.current_section == "inventory":
            # Move to previous row or wrap to bottom
            self.grid_selected_row = (self.grid_selected_row - 1) % self.grid_rows
            # Update selected item index
            self.selected_item_index = self.grid_selected_row * self.grid_cols + self.grid_selected_col
            
            # Validate selection is within inventory bounds
            if hasattr(self.player, 'inventory'):
                inventory_size = len(self.player.inventory.get_items_and_counts())
                if self.selected_item_index >= inventory_size:
                    # Set to last valid item in the previous row
                    if self.grid_selected_row > 0:
                        self.grid_selected_row -= 1
                    else:
                        # Wrap to bottom row
                        self.grid_selected_row = (inventory_size - 1) // self.grid_cols
                    
                    # Adjust column if needed
                    max_col = min(self.grid_cols - 1, inventory_size - 1 - (self.grid_selected_row * self.grid_cols))
                    if self.grid_selected_col > max_col:
                        self.grid_selected_col = max_col
                    
                    self.selected_item_index = self.grid_selected_row * self.grid_cols + self.grid_selected_col
    
    def select_down(self):
        """Move selection down in the inventory grid"""
        if self.current_section == "inventory":
            # Move to next row or wrap to top
            self.grid_selected_row = (self.grid_selected_row + 1) % self.grid_rows
            # Update selected item index
            self.selected_item_index = self.grid_selected_row * self.grid_cols + self.grid_selected_col
            
            # Validate selection is within inventory bounds
            if hasattr(self.player, 'inventory'):
                inventory_size = len(self.player.inventory.get_items_and_counts())
                if self.selected_item_index >= inventory_size:
                    # Wrap to first row
                    self.grid_selected_row = 0
                    self.selected_item_index = self.grid_selected_col
    
    def switch_section(self):
        """Switch between stats and inventory sections"""
        if self.current_section == "stats":
            self.current_section = "inventory"
            # Initialize inventory selection
            if hasattr(self.player, 'inventory') and len(self.player.inventory.get_items_and_counts()) > 0:
                self.selected_item_index = 0
                self.grid_selected_row = 0
                self.grid_selected_col = 0
            else:
                self.selected_item_index = -1
        else:
            self.current_section = "stats"
            self.selected_item_index = -1
    
    def use_selected_item(self):
        """Use the currently selected inventory item"""
        if self.current_section == "inventory" and self.selected_item_index >= 0:
            if hasattr(self.player, 'inventory'):
                inventory_items = self.player.inventory.get_items_and_counts()
                if self.selected_item_index < len(inventory_items):
                    item_data = inventory_items[self.selected_item_index]
                    item = item_data['item']
                    
                    if item and hasattr(item, 'use'):
                        # Try to use the item
                        use_result = item.use(self.player)
                        
                        # If use_result is a string, it's a message to display
                        if isinstance(use_result, str):
                            self.item_feedback_message = use_result
                            self.item_feedback_timer = 120  # Display for 120 frames (about 2 seconds)
                            return False
                        # If use_result is True, item was used successfully
                        elif use_result is True:
                            # Item was used successfully, remove from inventory
                            # Find the actual index in the items list
                            actual_index = self.player.inventory.items.index(item)
                            self.player.inventory.remove_item(actual_index)
                            
                            # If inventory is now empty, reset selection
                            if len(self.player.inventory.get_items_and_counts()) == 0:
                                self.selected_item_index = -1
                            # Otherwise adjust selection if it's now invalid
                            elif self.selected_item_index >= len(self.player.inventory.get_items_and_counts()):
                                self.selected_item_index = len(self.player.inventory.get_items_and_counts()) - 1
                                self.grid_selected_row = self.selected_item_index // self.grid_cols
                                self.grid_selected_col = self.selected_item_index % self.grid_cols
                            return True
        
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
            
            # Check inventory item clicks
            if hasattr(self.player, 'inventory'):
                inventory_items = self.player.inventory.get_items_and_counts()
                
                # Find the hovered item
                for idx, item_data in enumerate(inventory_items):
                    row = idx // self.grid_cols
                    col = idx % self.grid_cols
                    
                    # Calculate cell position
                    portrait_x = 50 + 30  # Same as in draw_items_grid
                    portrait_y = 80 + 30  # Same as in draw_items_grid
                    cell_x = portrait_x + col * (self.cell_size + self.grid_padding) + self.grid_padding
                    cell_y = portrait_y + self.portrait.get_height() + 30 + 35 + row * (self.cell_size + self.grid_padding) + self.grid_padding
                    
                    # Create a rect for the cell
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    
                    if cell_rect.collidepoint(mouse_pos):
                        item = item_data['item']
                        
                        # Toggle selection of this item
                        if self.selected_item_index == idx:
                            # If already selected, use the item
                            if item and hasattr(item, 'use'):
                                if item.use(self.player):
                                    # Item was used successfully, remove from inventory
                                    actual_index = self.player.inventory.items.index(item)
                                    self.player.inventory.remove_item(actual_index)
                        else:
                            # Select this item
                            self.selected_item_index = idx
                            self.grid_selected_row = row
                            self.grid_selected_col = col
                            self.current_section = "inventory"
                        
                        return True
        
        # Mouse movement for item hovering
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mouse is over inventory items
            self.hovered_item_index = -1
            self.tooltip_visible = False
            self.tooltip_item = None
            
            if hasattr(self.player, 'inventory'):
                inventory_items = self.player.inventory.get_items_and_counts()
                
                # Calculate grid starting position (must match draw_items_grid)
                portrait_x = 50 + 30  # Margin + portrait offset
                portrait_y = 80 + 30  # Margin + portrait offset
                grid_start_y = portrait_y + self.portrait.get_height() + 30 + 35  # Below portrait + title
                
                for idx, item_data in enumerate(inventory_items):
                    row = idx // self.grid_cols
                    col = idx % self.grid_cols
                    
                    # Calculate cell position
                    cell_x = portrait_x + col * (self.cell_size + self.grid_padding) + self.grid_padding
                    cell_y = grid_start_y + row * (self.cell_size + self.grid_padding) + self.grid_padding
                    
                    # Create a rect for the cell
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    
                    if cell_rect.collidepoint(mouse_pos):
                        self.hovered_item_index = idx
                        self.tooltip_visible = True
                        self.tooltip_item = item_data['item']
                        break
        
        # Controller button handling
        elif event.type == pygame.JOYBUTTONDOWN:
            # Button 0 (A) to activate selected button or use selected item
            if event.button == 0:
                if self.current_section == "stats":
                    if self.player.attributes.stat_points > 0:
                        button_id = self.button_order[self.selected_index]
                        result = self.buttons[button_id]['action']()
                        return True
                elif self.current_section == "inventory" and self.selected_item_index >= 0:
                    self.use_selected_item()
                    return True
            
            # Button 1 (B) to switch between stats and inventory sections
            elif event.button == 1:
                self.switch_section()
                return True
                
            # Button 2 (X) for secondary action (not used here)
            elif event.button == 2:
                # Additional functionality could be added here
                pass
                
        # D-pad handling
        elif event.type == pygame.JOYHATMOTION:
            hat_value = event.value
            
            # D-pad up/down
            if hat_value[1] == 1:  # D-pad up
                if self.current_section == "stats":
                    self.select_prev()
                else:
                    self.select_up()
                return True
            elif hat_value[1] == -1:  # D-pad down
                if self.current_section == "stats":
                    self.select_next()
                else:
                    self.select_down()
                return True
                
            # D-pad left/right
            if hat_value[0] == -1:  # D-pad left
                if self.current_section == "inventory":
                    self.select_prev()
                return True
            elif hat_value[0] == 1:  # D-pad right
                if self.current_section == "inventory":
                    self.select_next()
                return True
            
        # Keyboard handling for navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.current_section == "stats":
                    self.select_prev()
                else:
                    self.select_up()
                return True
            elif event.key == pygame.K_DOWN:
                if self.current_section == "stats":
                    self.select_next()
                else:
                    self.select_down()
                return True
            elif event.key == pygame.K_LEFT:
                if self.current_section == "inventory":
                    self.select_prev()
                return True
            elif event.key == pygame.K_RIGHT:
                if self.current_section == "inventory":
                    self.select_next()
                return True
            elif event.key == pygame.K_TAB:
                self.switch_section()
                return True
            elif event.key == pygame.K_e:
                if self.current_section == "inventory" and self.selected_item_index >= 0:
                    self.use_selected_item()
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
            is_selected = self.current_section == "stats" and self.button_order[self.selected_index] == button_id
            
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
        
        # Draw items grid below the portrait
        self.draw_items_grid(surface, portrait_x, portrait_y + self.portrait.get_height() + 30)
        
        # Draw item tooltip if needed
        if self.tooltip_visible and self.tooltip_item:
            self.draw_item_tooltip(surface, self.tooltip_item, pygame.mouse.get_pos())
        
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
        """Draw an item grid below the portrait with selection and usage indicators"""
        # Title for items section
        items_title = self.stat_font.render("ITEMS", True, self.colors['title'])
        surface.blit(items_title, (x, y))
        
        # Draw control instructions
        if self.current_section == "inventory" and hasattr(self.player, 'inventory') and len(self.player.inventory.get_items_and_counts()) > 0:
            instructions = "Press E/Button A to use selected item"
            instr_text = self.text_font.render(instructions, True, self.colors['text'])
            surface.blit(instr_text, (x + 100, y))
        
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
            inventory_items = []
        
        # Draw grid cells
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = x + col * (self.cell_size + self.grid_padding) + self.grid_padding
                cell_y = y + 35 + row * (self.cell_size + self.grid_padding) + self.grid_padding
                
                # Get item index
                item_idx = row * self.grid_cols + col
                
                # Determine cell background color based on selection status
                cell_color = self.colors['grid_border']
                
                # Check if this is the selected cell
                is_selected = item_idx == self.selected_item_index
                is_hovered = item_idx == self.hovered_item_index
                
                # Draw selected or hovered item with different background
                if is_selected and self.current_section == "inventory":
                    cell_color = self.colors['item_selected']
                elif is_hovered:
                    cell_color = self.colors['item_hover']
                
                # Draw cell background
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                pygame.draw.rect(surface, cell_color, cell_rect)
                pygame.draw.rect(surface, self.colors['grid_border'], cell_rect, 1)
                
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
                        
                        # Add visual indication if item is usable
                        if hasattr(item, 'use') and not getattr(item, 'one_time_use', False):
                            # Small indicator in the corner
                            usable_rect = pygame.Rect(cell_x + 2, cell_y + 2, 6, 6)
                            pygame.draw.rect(surface, self.colors['usable'], usable_rect)
                        
                        # Draw selection outline
                        if is_selected and self.current_section == "inventory":
                            # Draw a bright border around the selected item
                            selection_rect = cell_rect.inflate(4, 4)
                            pygame.draw.rect(surface, self.colors['cursor'], selection_rect, 2)
                            
                            # Show controller button prompt if using controller navigation
                            prompt_text = self.button_font.render("E/A", True, self.colors['cursor'])
                            prompt_x = cell_x + self.cell_size - prompt_text.get_width() - 2
                            prompt_y = cell_y + 2
                            surface.blit(prompt_text, (prompt_x, prompt_y))
        
        # Draw feedback message BELOW the grid if active
        if self.item_feedback_message and self.item_feedback_timer > 0:
            self.item_feedback_timer -= 1
            self.draw_item_feedback(surface, x + 100, y + 35 + grid_height + 10)  # Position below the grid with 10px padding
        
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
            inventory_items = []
        
        # Draw grid cells
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = x + col * (self.cell_size + self.grid_padding) + self.grid_padding
                cell_y = y + 35 + row * (self.cell_size + self.grid_padding) + self.grid_padding
                
                # Get item index
                item_idx = row * self.grid_cols + col
                
                # Determine cell background color based on selection status
                cell_color = self.colors['grid_border']
                
                # Check if this is the selected cell
                is_selected = item_idx == self.selected_item_index
                is_hovered = item_idx == self.hovered_item_index
                
                # Draw selected or hovered item with different background
                if is_selected and self.current_section == "inventory":
                    cell_color = self.colors['item_selected']
                elif is_hovered:
                    cell_color = self.colors['item_hover']
                
                # Draw cell background
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                pygame.draw.rect(surface, cell_color, cell_rect)
                pygame.draw.rect(surface, self.colors['grid_border'], cell_rect, 1)
                
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
                        
                        # Add visual indication if item is usable
                        if hasattr(item, 'use') and not getattr(item, 'one_time_use', False):
                            # Small indicator in the corner
                            usable_rect = pygame.Rect(cell_x + 2, cell_y + 2, 6, 6)
                            pygame.draw.rect(surface, self.colors['usable'], usable_rect)
                        
                        # Draw selection outline
                        if is_selected and self.current_section == "inventory":
                            # Draw a bright border around the selected item
                            selection_rect = cell_rect.inflate(4, 4)
                            pygame.draw.rect(surface, self.colors['cursor'], selection_rect, 2)
                            
                            # Show controller button prompt if using controller navigation
                            prompt_text = self.button_font.render("E/A", True, self.colors['cursor'])
                            prompt_x = cell_x + self.cell_size - prompt_text.get_width() - 2
                            prompt_y = cell_y + 2
                            surface.blit(prompt_text, (prompt_x, prompt_y))
    
    def draw_item_feedback(self, surface, x, y):
        """Draw a feedback message when an item can't be used"""
        if not self.item_feedback_message:
            return
            
        # Calculate message position - center horizontally at the specified position
        padding = 8
        message = self.stat_font.render(self.item_feedback_message, True, self.colors['feedback_text'])
        
        # Position centered at the given coordinates
        msg_x = x + (self.grid_cols * (self.cell_size + self.grid_padding)) // 2 - message.get_width() // 2
        msg_y = y  # Just use the provided y-coordinate
        
        # Draw message background
        bg_rect = pygame.Rect(
            msg_x - padding, 
            msg_y - padding,
            message.get_width() + padding * 2,
            message.get_height() + padding * 2
        )
        
        # Create semi-transparent background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.colors['feedback_bg'])
        surface.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        # Draw border
        pygame.draw.rect(surface, self.colors['border'], bg_rect, 2)
        
        # Draw message text
        surface.blit(message, (msg_x, msg_y))
        
        # If message is about to expire, start fading it out
        if self.item_feedback_timer < 30:
            # Apply alpha fade out
            alpha = int(255 * (self.item_feedback_timer / 30))
            message.set_alpha(alpha)
    
    def draw_item_tooltip(self, surface, item, mouse_pos):
        """Draw tooltip with item information"""
        if not item:
            return
            
        # Get item information
        name = item.name if hasattr(item, 'name') else "Unknown Item"
        description = item.description if hasattr(item, 'description') else "No description available."
        
        # Add usage hint if applicable
        usable = hasattr(item, 'use') and not getattr(item, 'one_time_use', False)
        if usable:
            description += " (Click to use)"
        
        # Calculate tooltip dimensions
        padding = 10
        max_width = 250
        
        # Render text
        name_text = self.stat_font.render(name, True, self.colors['title'])
        
        # Word wrap description if needed
        wrapped_desc = []
        words = description.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = self.desc_font.size(test_line)[0]
            
            if test_width < max_width:
                current_line = test_line
            else:
                wrapped_desc.append(current_line)
                current_line = word
                
        if current_line:
            wrapped_desc.append(current_line)
            
        # Render description lines
        desc_surfaces = [self.desc_font.render(line, True, self.colors['text']) for line in wrapped_desc]
        
        # Calculate tooltip size
        tooltip_width = max(max_width, name_text.get_width()) + padding * 2
        tooltip_height = padding * 2 + name_text.get_height() + sum(surf.get_height() for surf in desc_surfaces) + 5
        
        # Position tooltip near mouse but ensure it stays on screen
        tooltip_x = min(mouse_pos[0] + 15, SCREEN_WIDTH - tooltip_width - 10)
        tooltip_y = min(mouse_pos[1] + 15, SCREEN_HEIGHT - tooltip_height - 10)
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, self.colors['background'], tooltip_rect)
        pygame.draw.rect(surface, self.colors['border'], tooltip_rect, 2)
        
        # Draw name
        surface.blit(name_text, (tooltip_x + padding, tooltip_y + padding))
        
        # Draw description
        y_offset = tooltip_y + padding + name_text.get_height() + 5
        for desc_surface in desc_surfaces:
            surface.blit(desc_surface, (tooltip_x + padding, y_offset))
            y_offset += desc_surface.get_height()