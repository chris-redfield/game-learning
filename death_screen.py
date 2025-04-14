import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DeathScreen:
    def __init__(self):
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.option_font = pygame.font.SysFont('Arial', 28)
        self.prompt_font = pygame.font.SysFont('Arial', 20)  # Smaller font for prompt
        
        # Text surfaces
        self.title_text = self.title_font.render("YOU DIED", True, (255, 255, 255))
        self.restart_text = self.option_font.render("Restart", True, (255, 255, 255))
        self.load_save_text = self.option_font.render("Load Save", True, (255, 255, 255))  # Changed to white
        self.button_prompt = self.prompt_font.render("press A", True, (255, 255, 0))  # Yellow "press A" text
        
        # Create overlay surface for darkening
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(180)  # Semi-transparent overlay
        
        # Menu options rects
        self.restart_rect = None
        self.load_save_rect = None
        
        # State
        self.active = False
        
        # Controller navigation
        self.selected_option = 0  # 0 for Restart, 1 for Load Save
        self.num_options = 2
        
    def activate(self):
        """Activate the death screen"""
        self.active = True
        # Default to selecting the Restart option
        self.selected_option = 0
    
    def is_active(self):
        """Check if death screen is active"""
        return self.active
    
    def handle_event(self, event):
        """Handle input events for death screen"""
        if not self.active:
            return False
            
        # Handle menu navigation with keyboard
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_option = (self.selected_option - 1) % self.num_options
                return False
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_option = (self.selected_option + 1) % self.num_options
                return False
            # Handle selection with Enter key
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Restart
                    self.active = False
                    return "restart"
                elif self.selected_option == 1:  # Load Save
                    return "load"
        
        # Handle menu navigation with joystick
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:  # Vertical axis
                if event.value < -0.5:  # Up
                    self.selected_option = (self.selected_option - 1) % self.num_options
                    return False
                elif event.value > 0.5:  # Down
                    self.selected_option = (self.selected_option + 1) % self.num_options
                    return False
        
        # Handle selection with controller button
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button
                if self.selected_option == 0:  # Restart
                    self.active = False
                    return "restart"
                elif self.selected_option == 1:  # Load Save
                    return "load"
            
        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
            mouse_pos = pygame.mouse.get_pos()
            if self.restart_rect and self.restart_rect.collidepoint(mouse_pos):
                self.active = False
                return "restart"
            elif self.load_save_rect and self.load_save_rect.collidepoint(mouse_pos):
                return "load"
        
        # Handle mouse hovering (update selected option based on mouse position)
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.restart_rect and self.restart_rect.collidepoint(mouse_pos):
                self.selected_option = 0
            elif self.load_save_rect and self.load_save_rect.collidepoint(mouse_pos):
                self.selected_option = 1
                
        return False
    
    def draw(self, screen, player=None):
        """Draw the death screen overlay and options"""
        if not self.active:
            return
        
        # Draw darkened overlay
        screen.blit(self.overlay, (0, 0))
        
        # If player is provided, draw just the player sprite
        if player:
            # Get the player to draw itself on the darkened screen
            player.draw(screen)
        
        # Center coordinates
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw "YOU DIED" text
        title_rect = self.title_text.get_rect(center=(center_x, center_y - 60))
        screen.blit(self.title_text, title_rect)
        
        # Draw menu options
        self.restart_rect = self.restart_text.get_rect(center=(center_x, center_y + 20))
        self.load_save_rect = self.load_save_text.get_rect(center=(center_x, center_y + 60))
        
        # Draw option backgrounds (hover/selection effect)
        
        # Restart option highlight
        if self.restart_rect.collidepoint(pygame.mouse.get_pos()) or self.selected_option == 0:
            # Draw a highlighted background for the selected option
            highlight_rect = self.restart_rect.inflate(20, 10)  # Make the highlight slightly larger
            pygame.draw.rect(screen, (80, 80, 80), highlight_rect, border_radius=5)
            
            # Add "press A" prompt to the right of the option with better spacing
            prompt_rect = self.button_prompt.get_rect(
                midleft=(self.restart_rect.right + 50, self.restart_rect.centery)
            )
            screen.blit(self.button_prompt, prompt_rect)
        
        # Load Save option highlight
        if self.load_save_rect.collidepoint(pygame.mouse.get_pos()) or self.selected_option == 1:
            # Draw a highlighted background for the selected option
            highlight_rect = self.load_save_rect.inflate(20, 10)  # Make the highlight slightly larger
            pygame.draw.rect(screen, (80, 80, 80), highlight_rect, border_radius=5)
            
            # Add "press A" prompt to the right of the option with better spacing
            prompt_rect = self.button_prompt.get_rect(
                midleft=(self.load_save_rect.right + 50, self.load_save_rect.centery)
            )
            screen.blit(self.button_prompt, prompt_rect)
        
        # Draw option text
        screen.blit(self.restart_text, self.restart_rect)
        screen.blit(self.load_save_text, self.load_save_rect)