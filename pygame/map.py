import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Map:
    def __init__(self, world):
        """Initialize the map with a reference to the world"""
        self.world = world
        self.visible = False
        self.cell_size = 28  # Reduced cell size to fit more cells on screen
        self.grid_size = 20  # Increased to 20x20 grid
        self.colors = {
            'background': (20, 20, 40),
            'grid': (60, 60, 80),
            'current': (65, 185, 105),  # Current block (green)
            'visited': (100, 140, 160),  # Visited blocks (blue-gray)
            'unexplored': (40, 40, 60),  # Unexplored but known blocks (dark)
            'player': (230, 230, 50),    # Player marker (yellow)
            'text': (220, 220, 220)
        }
        
        # Font for labels
        self.font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 24)
    
    def toggle(self):
        """Toggle map visibility"""
        self.visible = not self.visible
        return self.visible
    
    def is_visible(self):
        """Check if map is currently visible"""
        return self.visible
    
    def draw(self, screen):
        """Draw the map on the screen"""
        if not self.visible:
            return
            
        # Fill background
        screen.fill(self.colors['background'])
        
        # Draw title
        title = self.title_font.render("WORLD MAP", True, self.colors['text'])
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw current coordinates info
        curr_x, curr_y = self.world.current_block_coords
        coords_text = self.font.render(f"Current Position: ({curr_x}, {curr_y})", True, self.colors['text'])
        screen.blit(coords_text, (SCREEN_WIDTH // 2 - coords_text.get_width() // 2, 50))
        
        # Calculate map center position
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Calculate offset for centered grid
        offset_x = center_x - (self.grid_size // 2) * self.cell_size
        offset_y = center_y - (self.grid_size // 2) * self.cell_size
        
        # Get current block coordinates
        current_x, current_y = self.world.current_block_coords
        
        # Draw the grid and blocks
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Calculate world coordinates for this cell
                world_x = current_x - (self.grid_size // 2) + x
                world_y = current_y - (self.grid_size // 2) + y
                
                # Calculate screen position for this cell
                screen_x = offset_x + x * self.cell_size
                screen_y = offset_y + y * self.cell_size
                
                # Draw cell
                cell_rect = pygame.Rect(
                    screen_x, 
                    screen_y, 
                    self.cell_size, 
                    self.cell_size
                )
                
                # Check if block exists at these coordinates
                block_exists = (world_x, world_y) in self.world.blocks
                
                # Determine cell color
                if world_x == current_x and world_y == current_y:
                    # Current block
                    color = self.colors['current']
                elif block_exists and self.world.blocks[(world_x, world_y)].is_visited():
                    # Visited block
                    color = self.colors['visited']
                elif block_exists:
                    # Known but unexplored block
                    color = self.colors['unexplored']
                else:
                    # Draw only grid for unknown blocks
                    pygame.draw.rect(screen, self.colors['grid'], cell_rect, 1)
                    continue
                
                # Draw filled cell with border
                pygame.draw.rect(screen, color, cell_rect)
                pygame.draw.rect(screen, self.colors['grid'], cell_rect, 1)
                
                # Draw coordinates in the cell if cell is large enough
                coord_text = f"({world_x},{world_y})"
                text_surf = self.font.render(coord_text, True, self.colors['text'])
                
                # Only draw text if it fits in the cell
                if text_surf.get_width() < self.cell_size - 4:
                    text_pos = (
                        screen_x + self.cell_size // 2 - text_surf.get_width() // 2,
                        screen_y + self.cell_size // 2 - text_surf.get_height() // 2
                    )
                    screen.blit(text_surf, text_pos)
        
        # Draw player marker (centered in current block)
        current_screen_x = offset_x + (self.grid_size // 2) * self.cell_size
        current_screen_y = offset_y + (self.grid_size // 2) * self.cell_size
        
        # Draw a triangle for player direction
        player_color = self.colors['player']
        center_x = current_screen_x + self.cell_size // 2
        center_y = current_screen_y + self.cell_size // 2
        marker_size = max(self.cell_size // 5, 5)  # Ensure marker is visible even with small cells
        
        # Draw player position
        pygame.draw.circle(screen, player_color, (center_x, center_y), marker_size)
        
        # Draw legend
        legend_x = 20
        legend_y = SCREEN_HEIGHT - 120
        
        legend_items = [
            ("Current Location", self.colors['current']),
            ("Visited Areas", self.colors['visited']),
            ("Unexplored", self.colors['unexplored']),
            ("Player", self.colors['player'])
        ]
        
        legend_title = self.font.render("Legend:", True, self.colors['text'])
        screen.blit(legend_title, (legend_x, legend_y))
        
        for i, (text, color) in enumerate(legend_items):
            y_pos = legend_y + 25 + i * 20
            
            # Draw color sample
            pygame.draw.rect(screen, color, (legend_x, y_pos, 15, 15))
            
            # Draw text
            text_surf = self.font.render(text, True, self.colors['text'])
            screen.blit(text_surf, (legend_x + 25, y_pos))
        
        # Draw instructions with controller button info
        instructions = [
            "Press 'M' or LB to close map",
            "Explore the world by crossing",
            "the borders of each area"
        ]
        
        for i, text in enumerate(instructions):
            instruction_text = self.font.render(text, True, self.colors['text'])
            x_pos = SCREEN_WIDTH - instruction_text.get_width() - 20
            y_pos = SCREEN_HEIGHT - 80 + i * 20
            screen.blit(instruction_text, (x_pos, y_pos))