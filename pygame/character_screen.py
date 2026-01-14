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
            'feedback_text': (255, 220, 100), # Item feedback message text
            'skill_unlocked': (0, 150, 0),    # Unlocked skill
            'skill_available': (150, 150, 0), # Available to unlock
            'skill_unavailable': (100, 100, 100) # Unavailable skill
        }
        
        # Current tab and skill selection
        self.current_tab = "attributes"  # Can be "attributes" or "skills"
        self.skill_selected = None  # Currently selected skill for viewing details
        
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
        
        # Add cursor position for tooltip rendering
        self.cursor_pos = (0, 0)  # Default position for cursor-based tooltips
        
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
            self.current_tab = "attributes"  # Default to attributes tab
            self.skill_selected = None       # Reset skill selection
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
            # If we're at the last stat and pressing right, move to inventory
            if self.selected_index == len(self.button_order) - 1 and pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.switch_section()
                # Start with the first item in the inventory
                if hasattr(self.player, 'inventory') and len(self.player.inventory.get_items_and_counts()) > 0:
                    self.grid_selected_row = 0
                    self.grid_selected_col = 0
                    self.selected_item_index = 0
                return
            # Otherwise just move down in the stats list
            self.selected_index = (self.selected_index + 1) % len(self.button_order)
        elif self.current_section == "inventory":
            # If we're in the last column and pressing right, move to the stats section
            last_col = min(self.grid_cols - 1, 
                        (len(self.player.inventory.get_items_and_counts()) - 1) % self.grid_cols) if hasattr(self.player, 'inventory') else 0
            
            if self.grid_selected_col == last_col and pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.switch_section()
                # Set selection to the first stat button
                self.selected_index = 0
                return
                
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
        
        # Update cursor position if in inventory section
        if self.current_section == "inventory":
            self.update_selected_item_position()
        
    def select_prev(self):
        """Move to previous button or inventory item based on current section"""
        if self.current_section == "stats":
            # If we're already at the first stat and pressing left, move to inventory
            if self.selected_index == 0 and pygame.key.get_pressed()[pygame.K_LEFT]:
                self.switch_section()
                # Set selection to the first column of inventory
                if hasattr(self.player, 'inventory') and len(self.player.inventory.get_items_and_counts()) > 0:
                    self.grid_selected_col = 0
                    self.selected_item_index = self.grid_selected_row * self.grid_cols
                return
            # Otherwise just move up in the stats list
            self.selected_index = (self.selected_index - 1) % len(self.button_order)
        elif self.current_section == "inventory":
            # If we're in the first column and pressing left, move to the stats section
            if self.grid_selected_col == 0 and pygame.key.get_pressed()[pygame.K_LEFT]:
                self.switch_section()
                # Set selection to the last stat button
                self.selected_index = len(self.button_order) - 1
                return
            
            # Otherwise, normal inventory navigation
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
        
        # Update cursor position if in inventory section
        if self.current_section == "inventory":
            self.update_selected_item_position()
    
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
            
            # Update cursor position
            self.update_selected_item_position()
    
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
            
            # Update cursor position
            self.update_selected_item_position()
    
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
        
        # Update cursor position if we switched to inventory
        if self.current_section == "inventory" and self.selected_item_index >= 0:
            self.update_selected_item_position()
    
    def update_selected_item_position(self):
        """Update the cursor position for the currently selected inventory item"""
        if self.current_section != "inventory" or self.selected_item_index < 0:
            return
            
        # Calculate the position of the currently selected item
        row = self.selected_item_index // self.grid_cols
        col = self.selected_item_index % self.grid_cols
        
        # Calculate grid starting position (must match draw_items_grid)
        portrait_x = 50 + 30  # Margin + portrait offset
        portrait_y = 80 + 30  # Margin + portrait offset
        grid_start_y = portrait_y + self.portrait.get_height() + 30 + 35  # Below portrait + title
        
        cell_x = portrait_x + col * (self.cell_size + self.grid_padding) + self.grid_padding
        cell_y = grid_start_y + row * (self.cell_size + self.grid_padding) + self.grid_padding
        
        # Update cursor position for tooltip
        self.cursor_pos = (cell_x + self.cell_size + 10, cell_y)
    
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
                            
    def navigate_skills(self, direction):
        """Navigate through the skill tree with controller/keyboard"""
        if not hasattr(self, 'skill_rects') or not self.skill_rects:
            return False
            
        branches = self.player.skill_tree.get_skills_by_branch()
        branch_ids = ["mind", "body", "magic_sword"]
        
        # If no skill is currently selected, select the first available one
        if not self.skill_selected:
            for branch_id in branch_ids:
                if branches[branch_id]:
                    self.skill_selected = branches[branch_id][0].id
                    return True
            return False
            
        # Get current branch and position
        current_skill = self.player.skill_tree.skills[self.skill_selected]
        current_branch = None
        current_index = -1
        
        for branch_id in branch_ids:
            for i, skill in enumerate(branches[branch_id]):
                if skill.id == current_skill.id:
                    current_branch = branch_id
                    current_index = i
                    break
            if current_branch:
                break
                
        if not current_branch:
            return False
            
        # Current branch index
        branch_index = branch_ids.index(current_branch)
        
        # Handle navigation based on direction
        if direction == "up":
            # Move to previous skill in same branch
            if current_index > 0:
                self.skill_selected = branches[current_branch][current_index - 1].id
                return True
        elif direction == "down":
            # Move to next skill in same branch
            if current_index < len(branches[current_branch]) - 1:
                self.skill_selected = branches[current_branch][current_index + 1].id
                return True
        elif direction == "left":
            # Move to previous branch
            if branch_index > 0:
                new_branch = branch_ids[branch_index - 1]
                # Try to select skill at same position or closest available
                if branches[new_branch]:
                    new_index = min(current_index, len(branches[new_branch]) - 1)
                    self.skill_selected = branches[new_branch][new_index].id
                    return True
        elif direction == "right":
            # Move to next branch
            if branch_index < len(branch_ids) - 1:
                new_branch = branch_ids[branch_index + 1]
                # Try to select skill at same position or closest available
                if branches[new_branch]:
                    new_index = min(current_index, len(branches[new_branch]) - 1)
                    self.skill_selected = branches[new_branch][new_index].id
                    return True
                    
        return False
    
    def handle_event(self, event):
        """Handle mouse and controller events for the character screen"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            # Check tab clicks
            if hasattr(self, 'tab_rects'):
                for tab_id, tab_rect in self.tab_rects.items():
                    if tab_rect.collidepoint(mouse_pos):
                        self.current_tab = tab_id
                        self.skill_selected = None  # Reset selected skill
                        return True
            
            # Handle tab-specific clicks
            if self.current_tab == "attributes":
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
                                    use_result = item.use(self.player)
                                    # Check the type of result
                                    if isinstance(use_result, str):
                                        # Show feedback message instead of using
                                        self.item_feedback_message = use_result
                                        self.item_feedback_timer = 120
                                    elif use_result is True:
                                        # Only remove if True was returned
                                        actual_index = self.player.inventory.items.index(item)
                                        self.player.inventory.remove_item(actual_index)

                            else:
                                # Select this item
                                self.selected_item_index = idx
                                self.grid_selected_row = row
                                self.grid_selected_col = col
                                self.current_section = "inventory"
                                
                                # Update cursor position for tooltip
                                self.update_selected_item_position()
                            
                            return True
            
            elif self.current_tab == "skills":
                # Check skill clicks
                if hasattr(self, 'skill_rects'):
                    for skill_id, skill_rect in self.skill_rects.items():
                        if skill_rect.collidepoint(mouse_pos):
                            self.skill_selected = skill_id
                            return True
                
                # Check unlock button click
                if hasattr(self, 'unlock_button_rect') and self.unlock_button_rect and self.unlock_button_rect.collidepoint(mouse_pos):
                    if self.skill_selected:
                        # Try to unlock the selected skill
                        self.player.skill_tree.unlock_skill(self.skill_selected)
                        return True
        
        # Mouse movement for item hovering
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Reset tooltip state for mouse hovering
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
                if self.current_tab == "attributes":
                    if self.current_section == "stats":
                        if self.player.attributes.stat_points > 0:
                            button_id = self.button_order[self.selected_index]
                            result = self.buttons[button_id]['action']()
                            return True
                    elif self.current_section == "inventory" and self.selected_item_index >= 0:
                        self.use_selected_item()
                        return True
                elif self.current_tab == "skills" and self.skill_selected:
                    # Try to unlock the selected skill
                    if not self.player.skill_tree.skills[self.skill_selected].unlocked:
                        self.player.skill_tree.unlock_skill(self.skill_selected)
                        return True
            
            # Button 1 (B) to switch between stats and inventory sections or go back
            elif event.button == 1:
                if self.current_tab == "attributes":
                    self.switch_section()
                    return True
                elif self.current_tab == "skills":
                    self.skill_selected = None  # Clear skill selection
                    return True
                
            # Button 2 (X) for switching tabs (attributes/skills)
            elif event.button == 2:
                self.current_tab = "skills" if self.current_tab == "attributes" else "attributes"
                self.skill_selected = None  # Clear skill selection when switching tabs
                return True
                
        # D-pad handling
        elif event.type == pygame.JOYHATMOTION:
            hat_value = event.value
            
            # D-pad up/down
            if hat_value[1] == 1:  # D-pad up
                if self.current_tab == "attributes":
                    if self.current_section == "stats":
                        self.select_prev()
                    else:
                        self.select_up()
                elif self.current_tab == "skills":
                    # Navigate skills - implementation depends on layout
                    self.navigate_skills("up")
                return True
            elif hat_value[1] == -1:  # D-pad down
                if self.current_tab == "attributes":
                    if self.current_section == "stats":
                        self.select_next()
                    else:
                        self.select_down()
                elif self.current_tab == "skills":
                    # Navigate skills - implementation depends on layout
                    self.navigate_skills("down")
                return True
                
            # D-pad left/right - modified to work in both sections
            if hat_value[0] == -1:  # D-pad left
                if self.current_tab == "attributes":
                    self.select_prev()
                elif self.current_tab == "skills":
                    # Navigate skills - implementation depends on layout
                    self.navigate_skills("left")
                return True
            elif hat_value[0] == 1:  # D-pad right
                if self.current_tab == "attributes":
                    self.select_next()
                elif self.current_tab == "skills":
                    # Navigate skills - implementation depends on layout
                    self.navigate_skills("right")
                return True
            
        # Keyboard handling for navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.current_tab == "attributes":
                    if self.current_section == "stats":
                        self.select_prev()
                    else:
                        self.select_up()
                elif self.current_tab == "skills":
                    self.navigate_skills("up")
                return True
            elif event.key == pygame.K_DOWN:
                if self.current_tab == "attributes":
                    if self.current_section == "stats":
                        self.select_next()
                    else:
                        self.select_down()
                elif self.current_tab == "skills":
                    self.navigate_skills("down")
                return True
            elif event.key == pygame.K_LEFT:
                if self.current_tab == "attributes":
                    self.select_prev()
                elif self.current_tab == "skills":
                    self.navigate_skills("left")
                return True
            elif event.key == pygame.K_RIGHT:
                if self.current_tab == "attributes":
                    self.select_next()
                elif self.current_tab == "skills":
                    self.navigate_skills("right")
                return True
            elif event.key == pygame.K_TAB:
                if self.current_tab == "attributes":
                    self.switch_section()
                return True
            elif event.key == pygame.K_e:
                if self.current_tab == "attributes":
                    if self.current_section == "inventory" and self.selected_item_index >= 0:
                        self.use_selected_item()
                        return True
                elif self.current_tab == "skills" and self.skill_selected:
                    # Try to unlock the selected skill
                    if not self.player.skill_tree.skills[self.skill_selected].unlocked:
                        self.player.skill_tree.unlock_skill(self.skill_selected)
                        return True
            elif event.key == pygame.K_1 or event.key == pygame.K_a:
                self.current_tab = "attributes"
                self.skill_selected = None
                return True
            elif event.key == pygame.K_2 or event.key == pygame.K_s:
                self.current_tab = "skills"
                self.skill_selected = None
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
        
        # Draw tabs at the bottom of the character sheet
        self.draw_tabs(surface, margin)
        
        # Draw the appropriate tab content
        if self.current_tab == "attributes":
            self.draw_attributes_tab(surface, margin)
        elif self.current_tab == "skills":
            self.draw_skills_tab(surface, margin)
        
        # Draw item tooltip if needed - only once (for attributes tab)
        if self.current_tab == "attributes" and self.tooltip_visible and self.tooltip_item:
            # Determine tooltip position - prefer mouse position if mouse is hovering, 
            # otherwise use stored cursor position
            tooltip_pos = pygame.mouse.get_pos() if self.hovered_item_index >= 0 else self.cursor_pos
            self.draw_item_tooltip(surface, self.tooltip_item, tooltip_pos)

    def draw_tabs(self, surface, margin):
        """Draw tabs for switching between attributes and skills at the bottom of the screen"""
        tab_width = 150
        tab_height = 30
        
        # Position tabs at the bottom of the character sheet
        tab_y = SCREEN_HEIGHT - margin - tab_height - 10  # 10px padding from the bottom margin
        
        # Attributes tab
        attr_tab_x = SCREEN_WIDTH // 2 - tab_width - 5
        attr_tab_rect = pygame.Rect(attr_tab_x, tab_y, tab_width, tab_height)
        attr_color = self.colors['button_hover'] if self.current_tab == "attributes" else self.colors['button']
        pygame.draw.rect(surface, attr_color, attr_tab_rect)
        pygame.draw.rect(surface, self.colors['border'], attr_tab_rect, 1)
        
        attr_text = self.button_font.render("ATTRIBUTES", True, self.colors['text'])
        surface.blit(attr_text, (attr_tab_x + (tab_width - attr_text.get_width()) // 2, 
                            tab_y + (tab_height - attr_text.get_height()) // 2))
        
        # Skills tab
        skills_tab_x = SCREEN_WIDTH // 2 + 5
        skills_tab_rect = pygame.Rect(skills_tab_x, tab_y, tab_width, tab_height)
        skills_color = self.colors['button_hover'] if self.current_tab == "skills" else self.colors['button']
        pygame.draw.rect(surface, skills_color, skills_tab_rect)
        pygame.draw.rect(surface, self.colors['border'], skills_tab_rect, 1)
        
        skills_text = self.button_font.render("SKILLS", True, self.colors['text'])
        surface.blit(skills_text, (skills_tab_x + (tab_width - skills_text.get_width()) // 2, 
                            tab_y + (tab_height - skills_text.get_height()) // 2))
        
        # Store tab rects for click detection
        self.tab_rects = {
            "attributes": attr_tab_rect,
            "skills": skills_tab_rect
        }
        
        # Draw a separator line above the tabs
        sep_y = tab_y - 10
        pygame.draw.line(surface, self.colors['border'], (margin + 10, sep_y), (SCREEN_WIDTH - margin - 10, sep_y), 1)

    def draw_attributes_tab(self, surface, margin):
        """Draw the attributes tab with character stats and inventory"""
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

    def draw_skills_tab(self, surface, margin):
        """Draw the skills tab with skill tree"""
        # Header and skill points display
        skill_points_text = self.stat_font.render(f"Skill Points: {self.player.attributes.skill_points}", True, self.colors['title'])
        surface.blit(skill_points_text, (margin + 50, margin + 90))
        
        # Instructions
        instructions = self.text_font.render("Click on a skill to view details and unlock it", True, self.colors['text'])
        surface.blit(instructions, (margin + 50, margin + 120))
        
        # Get skill data
        branches = self.player.skill_tree.get_skills_by_branch()
        
        # Define branch positions and names
        branch_names = ["Mind", "Body", "Magic Sword"]
        branch_ids = ["mind", "body", "magic_sword"]
        
        screen_width = SCREEN_WIDTH - margin * 2 - 100
        branch_width = screen_width // 3
        start_y = margin + 170  # Move branch headers down to avoid collision with instructions
        
        # Draw branch headers (diamond shapes)
        for i, branch_name in enumerate(branch_names):
            branch_x = margin + 50 + i * branch_width + branch_width // 2
            
            # Draw diamond for branch header
            diamond_size = 20
            diamond_points = [
                (branch_x, start_y),  # Top
                (branch_x + diamond_size, start_y + diamond_size),  # Right
                (branch_x, start_y + diamond_size * 2),  # Bottom
                (branch_x - diamond_size, start_y + diamond_size)   # Left
            ]
            
            # Draw branch diamond
            pygame.draw.polygon(surface, (100, 200, 100), diamond_points)
            pygame.draw.polygon(surface, self.colors['border'], diamond_points, 2)
            
            # Draw branch name
            branch_text = self.text_font.render(branch_name, True, self.colors['text'])
            text_x = branch_x - branch_text.get_width() // 2
            text_y = start_y - branch_text.get_height() - 5
            surface.blit(branch_text, (text_x, text_y))
        
        # Map to store skill positions for drawing connections
        skill_positions = {}
        self.skill_rects = {}
        
        # Draw skills for each branch
        for branch_idx, branch_id in enumerate(branch_ids):
            skills = branches[branch_id]
            
            # Center position for this branch
            branch_x = margin + 50 + branch_idx * branch_width + branch_width // 2
            
            # First level skills (direct children of the branch)
            first_level_skills = [skill for skill in skills if not skill.parent]
            first_level_count = len(first_level_skills)
            
            level_spacing = 110  # Increased vertical spacing between levels
            skill_spacing = 170  # Much wider horizontal spacing between siblings
            
            # Draw first level skills (top row)
            if first_level_count > 0:
                # For first level, spread skills horizontally
                for i, skill in enumerate(first_level_skills):
                    # Calculate position spreading skills horizontally
                    skill_x = branch_x
                    if first_level_count > 1:
                        # Spread skills horizontally if more than one
                        offset = (i - (first_level_count - 1) / 2) * skill_spacing
                        skill_x += offset
                    
                    skill_y = start_y + 80  # Increased vertical space from branch header to first skills
                    
                    # Draw connection from branch to skill
                    pygame.draw.line(surface, self.colors['border'], 
                                    (branch_x, start_y + diamond_size * 2), 
                                    (skill_x, skill_y - 18), 2)
                    
                    # Draw the skill
                    self.draw_skill_node(surface, skill, skill_x, skill_y)
                    
                    # Store position for drawing connections to children
                    skill_positions[skill.id] = (skill_x, skill_y)
            
            # Group skills by their parent to organize them by levels
            skill_levels = {}
            for skill in skills:
                if skill.parent:
                    if skill.parent not in skill_levels:
                        skill_levels[skill.parent] = []
                    skill_levels[skill.parent].append(skill)
            
            # Draw remaining levels of skills
            current_level = 1  # First level already drawn
            done = False
            
            while not done:
                done = True
                next_parents = []
                
                # Process each parent at this level
                for parent_id in list(skill_levels.keys()):
                    if parent_id in skill_positions:
                        parent_x, parent_y = skill_positions[parent_id]
                        children = skill_levels.pop(parent_id)
                        done = False
                        
                        # Draw children of this parent
                        child_count = len(children)
                        for i, child in enumerate(children):
                            # Calculate position for this child
                            child_x = parent_x
                            if child_count > 1:
                                # If multiple children, spread them horizontally
                                offset = (i - (child_count - 1) / 2) * skill_spacing
                                child_x += offset
                            
                            child_y = parent_y + level_spacing
                            
                            # Draw connection from parent to child
                            pygame.draw.line(surface, self.colors['border'], 
                                            (parent_x, parent_y + 18), 
                                            (child_x, child_y - 18), 2)
                            
                            # Draw the skill
                            self.draw_skill_node(surface, child, child_x, child_y)
                            
                            # Store position for drawing connections to children
                            skill_positions[child.id] = (child_x, child_y)
                            next_parents.append(child.id)
                
                current_level += 1
        
        # If a skill is selected, draw its details
        if self.skill_selected and self.skill_selected in self.player.skill_tree.skills:
            skill = self.player.skill_tree.skills[self.skill_selected]
            
            # Draw skill detail panel (moved up to make room for bottom tabs)
            tab_height = 30
            tab_margin = 20  # Space between detail panel and tabs
            detail_rect = pygame.Rect(margin + 50, 
                                    SCREEN_HEIGHT - margin - 150 - tab_height - tab_margin, 
                                    SCREEN_WIDTH - margin * 2 - 100, 
                                    120)
            pygame.draw.rect(surface, self.colors['background'], detail_rect)
            pygame.draw.rect(surface, self.colors['border'], detail_rect, 2)
            
            # Draw skill name
            detail_name = self.stat_font.render(skill.name, True, self.colors['title'])
            surface.blit(detail_name, (detail_rect.x + 10, detail_rect.y + 10))
            
            # Draw skill description
            detail_desc = self.text_font.render(skill.description, True, self.colors['text'])
            surface.blit(detail_desc, (detail_rect.x + 10, detail_rect.y + 40))
            
            # Draw unlock button if the skill can be unlocked
            if not skill.unlocked and skill.can_unlock(self.player) and self.player.attributes.skill_points > 0:
                unlock_button = pygame.Rect(detail_rect.right - 120, detail_rect.bottom - 40, 100, 30)
                pygame.draw.rect(surface, self.colors['button'], unlock_button)
                pygame.draw.rect(surface, self.colors['border'], unlock_button, 1)
                
                unlock_text = self.button_font.render("Unlock", True, self.colors['text'])
                surface.blit(unlock_text, (unlock_button.centerx - unlock_text.get_width() // 2,
                                        unlock_button.centery - unlock_text.get_height() // 2))
                
                # Store unlock button for click detection
                self.unlock_button_rect = unlock_button
            else:
                self.unlock_button_rect = None
                
                # Show status message
                if skill.unlocked:
                    status_text = self.text_font.render("Skill Unlocked", True, (0, 150, 0))
                elif not skill.implemented:
                    status_text = self.text_font.render("Not Yet Implemented", True, (150, 0, 0))
                elif self.player.attributes.level < skill.level_required:
                    status_text = self.text_font.render(f"Requires Level {skill.level_required}", True, (150, 0, 0))
                elif skill.parent and not self.player.skill_tree.is_skill_unlocked(skill.parent):
                    parent_skill = self.player.skill_tree.skills[skill.parent]
                    status_text = self.text_font.render(f"Requires {parent_skill.name} Skill", True, (150, 0, 0))
                elif self.player.attributes.skill_points <= 0:
                    status_text = self.text_font.render("No Skill Points Available", True, (150, 0, 0))
                else:
                    status_text = self.text_font.render("Cannot Unlock Now", True, (150, 0, 0))
                    
                surface.blit(status_text, (detail_rect.right - status_text.get_width() - 10, detail_rect.bottom - 30))

    def draw_skill_node(self, surface, skill, x, y):
        """Draw a skill node in the skill tree with diamond shape"""
        # Determine skill color based on state
        if skill.unlocked:
            node_color = self.colors['skill_unlocked']  # Green for unlocked
        elif skill.can_unlock(self.player) and self.player.attributes.skill_points > 0:
            node_color = self.colors['skill_available']  # Yellow for available to unlock
        else:
            node_color = self.colors['skill_unavailable']  # Gray for unavailable
        
        # Create diamond shape points
        diamond_size = 18  # Slightly larger diamonds
        diamond_points = [
            (x, y - diamond_size),  # Top
            (x + diamond_size, y),  # Right
            (x, y + diamond_size),  # Bottom
            (x - diamond_size, y)   # Left
        ]
        
        # Draw skill diamond
        pygame.draw.polygon(surface, node_color, diamond_points)
        
        # Highlight selected skill
        if self.skill_selected == skill.id:
            # Draw a thicker border for selected skill
            pygame.draw.polygon(surface, self.colors['cursor'], diamond_points, 3)
        else:
            pygame.draw.polygon(surface, self.colors['border'], diamond_points, 1)
        
        # Draw skill name above the diamond
        skill_name = self.text_font.render(skill.name, True, self.colors['text'])
        name_x = x - skill_name.get_width() // 2
        name_y = y - diamond_size - skill_name.get_height() - 5  # Increased spacing
        surface.blit(skill_name, (name_x, name_y))
        
        # Draw level requirement below the diamond
        level_text = self.text_font.render(f"Level {skill.level_required}+", True, self.colors['text'])
        level_x = x - level_text.get_width() // 2
        level_y = y + diamond_size + 5  # Increased spacing
        surface.blit(level_text, (level_x, level_y))
        
        # Create a rectangular hitbox for the skill (for mouse interaction)
        # Make it larger than the diamond to be more user-friendly
        hitbox_size = 50  # Larger hitbox for easier selection
        hitbox_rect = pygame.Rect(x - hitbox_size//2, y - hitbox_size//2, hitbox_size, hitbox_size)
        self.skill_rects[skill.id] = hitbox_rect

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
        """Draw unlocked abilities based on skill tree"""
        abilities_title = self.stat_font.render("ABILITIES", True, self.colors['title'])
        surface.blit(abilities_title, (x, y))
        
        abilities = [
            {"id": "basic_sword", "name": "Sword Attack", "desc": "Basic sword attack (SPACE/Button 2)"},
            {"id": "sprint", "name": "Sprint", "desc": "Temporary speed boost (SHIFT/Button 4)"},
            {"id": "extended_sword", "name": "Extended Sword", "desc": "Increased sword reach"},
            {"id": "blink", "name": "Blink", "desc": "Short-range teleport (B/Button 1)"}
        ]
        
        # Use more vertical space for abilities
        abilities_y = y + 40
        has_abilities = False
        
        # Draw only unlocked abilities
        for ability in abilities:
            if self.player.skill_tree.is_skill_unlocked(ability["id"]):
                has_abilities = True
                
                # Get ability status
                status_color = self.colors['stat_text']  # Green for unlocked
                status_text = "UNLOCKED"
                    
                name_text = self.text_font.render(ability["name"], True, self.colors['text'])
                surface.blit(name_text, (x, abilities_y))
                
                status_text_render = self.text_font.render(status_text, True, status_color)
                surface.blit(status_text_render, (x + 200, abilities_y))
                
                # Description on next line
                desc_text = self.text_font.render(ability["desc"], True, (180, 180, 180))
                surface.blit(desc_text, (x + 20, abilities_y + 25))
                
                abilities_y += 60  # Increased spacing
                
        if not has_abilities:
            no_abilities_text = self.text_font.render("No abilities unlocked yet", True, (180, 180, 180))
            surface.blit(no_abilities_text, (x, abilities_y))
                
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
                            
                            # Store selected item for tooltip rendering
                            # We'll set tooltip_visible flag to true only if it's not already 
                            # being rendered due to mouse hover
                            if self.hovered_item_index != item_idx:
                                self.tooltip_visible = True
                                self.tooltip_item = item
                                # Store cursor position for tooltip placement
                                self.cursor_pos = (cell_x + self.cell_size + 10, cell_y)
        
        # Draw feedback message BELOW the grid if active
        if self.item_feedback_message and self.item_feedback_timer > 0:
            self.item_feedback_timer -= 1
            self.draw_item_feedback(surface, x + 100, y + 35 + grid_height + 10)  # Position below the grid with 10px padding
        
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