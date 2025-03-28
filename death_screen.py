import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DeathScreen:
    def __init__(self):
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.option_font = pygame.font.SysFont('Arial', 28)
        
        # Text surfaces
        self.title_text = self.title_font.render("YOU DIED", True, (255, 255, 255))
        self.restart_text = self.option_font.render("Restart", True, (255, 255, 255))
        self.load_save_text = self.option_font.render("Load Save", True, (100, 100, 100))  # Grayed out
        
        # Create overlay surface for darkening
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(180)  # Semi-transparent overlay
        
        # Menu options rects
        self.restart_rect = None
        self.load_save_rect = None
        
        # State
        self.active = False
        
    def activate(self):
        """Activate the death screen"""
        self.active = True
    
    def is_active(self):
        """Check if death screen is active"""
        return self.active
    
    def handle_event(self, event):
        """Handle input events for death screen"""
        if not self.active:
            return False
            
        # Handle restart option click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
            mouse_pos = pygame.mouse.get_pos()
            if self.restart_rect and self.restart_rect.collidepoint(mouse_pos):
                self.active = False
                return "restart"
                
        return False
    
    def draw(self, screen, player_rect=None):
        """Draw the death screen overlay and options"""
        if not self.active:
            return
        
        # Create a copy of the screen before adding the overlay
        screen_copy = screen.copy()
        
        # Draw darkened overlay
        screen.blit(self.overlay, (0, 0))
        
        # If player_rect is provided, draw the player from the original screen
        if player_rect:
            # Extract player sprite from original screen
            player_sprite = screen_copy.subsurface(player_rect)
            # Draw the player sprite back on top of the darkened overlay
            screen.blit(player_sprite, player_rect)
        
        # Center coordinates
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw "YOU DIED" text
        title_rect = self.title_text.get_rect(center=(center_x, center_y - 60))
        screen.blit(self.title_text, title_rect)
        
        # Draw menu options
        self.restart_rect = self.restart_text.get_rect(center=(center_x, center_y + 20))
        self.load_save_rect = self.load_save_text.get_rect(center=(center_x, center_y + 60))
        
        # Draw option backgrounds (hover effect)
        mouse_pos = pygame.mouse.get_pos()
        if self.restart_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (50, 50, 50), self.restart_rect)
        
        # Draw option text
        screen.blit(self.restart_text, self.restart_rect)
        screen.blit(self.load_save_text, self.load_save_rect)