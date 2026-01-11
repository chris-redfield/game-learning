import pygame


class DialogBalloon:
    def __init__(self):
        """Initialize the dialog balloon system"""
        self.active_balloons = []
        
        # Styling
        self.padding = 12
        self.margin = 5
        self.max_width = 600  # Much larger width to accommodate longer text
        self.line_height = 22
        self.display_duration = 4000  # Longer duration for longer text
        self.fade_duration = 300
        
        # Colors
        self.bg_color = (30, 33, 41, 230)  # Dark blue-gray, semi-transparent
        self.text_color = (255, 255, 255)  # White text
        self.border_color = (180, 180, 200)  # Light border
        
        # Font (will be set later)
        self.font = None
        
        # Tail properties for speech bubble
        self.tail_height = 12
        self.tail_width = 18
    
    def set_font(self, font_size=15):
        """Set the font for dialog balloons"""
        self.font = pygame.font.SysFont('Arial', font_size)
    
    def get_dynamic_max_width(self, text):
        """Calculate appropriate width based on text length and screen size"""
        if not pygame.display.get_surface():
            return self.max_width
        
        screen_width = pygame.display.get_surface().get_width()
        text_length = len(text)
        
        # Base width on text length - longer text gets wider balloons
        if text_length > 100:
            desired_width = min(800, int(screen_width * 0.8))
        elif text_length > 60:
            desired_width = min(600, int(screen_width * 0.7))
        elif text_length > 30:
            desired_width = min(450, int(screen_width * 0.6))
        else:
            desired_width = min(350, int(screen_width * 0.5))
        
        return max(300, desired_width)  # Minimum 300px width
    
    def add_dialog(self, text, x, y, entity_width=35, entity_height=41):
        """Add a new dialog balloon"""
        if not self.font:
            self.set_font()
        
        # Get dynamic width for this specific text
        dynamic_width = self.get_dynamic_max_width(text)
        
        # Wrap text with the dynamic width
        wrapped_lines = self._wrap_text(text, dynamic_width)
        
        # Calculate balloon dimensions
        if wrapped_lines:
            text_width = max(self.font.size(line)[0] for line in wrapped_lines)
            text_height = len(wrapped_lines) * self.line_height
        else:
            text_width = self.font.size(text)[0]
            text_height = self.line_height
        
        balloon_width = text_width + (self.padding * 2)
        balloon_height = text_height + (self.padding * 2)
        
        # Position balloon above entity's head
        balloon_x = x + (entity_width // 2) - (balloon_width // 2)
        balloon_y = y - balloon_height - self.tail_height - 10  # 10px above head
        
        # Keep balloon on screen
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        balloon_x = max(10, min(balloon_x, screen_width - balloon_width - 10))
        balloon_y = max(10, min(balloon_y, screen_height - balloon_height - 10))
        
        balloon = {
            'text': text,
            'lines': wrapped_lines,
            'x': balloon_x,
            'y': balloon_y,
            'width': balloon_width,
            'height': balloon_height,
            'entity_x': x + entity_width // 2,  # Center of entity
            'entity_y': y,  # Top of entity
            'created_time': pygame.time.get_ticks(),
            'alpha': 255
        }
        
        self.active_balloons.append(balloon)
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max width - NO TRUNCATION"""
        if not self.font:
            return [text]
        
        # First check if the entire text fits on one line
        if self.font.size(text)[0] <= max_width:
            return [text]
        
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width = self.font.size(test_line)[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, but still add it (don't truncate)
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def update(self, current_time):
        """Update all active dialog balloons"""
        balloons_to_remove = []
        
        for balloon in self.active_balloons:
            elapsed = current_time - balloon['created_time']
            
            if elapsed > self.display_duration + self.fade_duration:
                balloons_to_remove.append(balloon)
            elif elapsed > self.display_duration:
                # Fade out
                fade_progress = (elapsed - self.display_duration) / self.fade_duration
                balloon['alpha'] = int(255 * (1 - fade_progress))
        
        # Remove expired balloons
        for balloon in balloons_to_remove:
            self.active_balloons.remove(balloon)
    
    def draw(self, surface):
        """Draw all active dialog balloons"""
        if not self.font:
            return
        
        for balloon in self.active_balloons:
            # Create a surface for the balloon with alpha
            balloon_surface = pygame.Surface(
                (balloon['width'] + 6, balloon['height'] + self.tail_height + 6),
                pygame.SRCALPHA
            )
            
            # Draw balloon background
            bg_color = (*self.bg_color[:3], min(self.bg_color[3], balloon['alpha']))
            pygame.draw.rect(
                balloon_surface,
                bg_color,
                (3, 3, balloon['width'], balloon['height']),
                border_radius=10
            )
            
            # Draw balloon border
            border_color = (*self.border_color, balloon['alpha'])
            pygame.draw.rect(
                balloon_surface,
                border_color,
                (3, 3, balloon['width'], balloon['height']),
                width=2,
                border_radius=10
            )
            
            # Draw tail (speech bubble pointer)
            tail_points = [
                (balloon['width'] // 2 - self.tail_width // 2, balloon['height']),
                (balloon['width'] // 2 + self.tail_width // 2, balloon['height']),
                (balloon['width'] // 2, balloon['height'] + self.tail_height)
            ]
            
            # Adjust tail position relative to balloon surface
            tail_points = [(p[0] + 3, p[1] + 3) for p in tail_points]
            
            pygame.draw.polygon(balloon_surface, bg_color, tail_points)
            pygame.draw.lines(balloon_surface, border_color, False, 
                            [tail_points[0], tail_points[2], tail_points[1]], 2)
            
            # Draw text - ALL LINES, NO TRUNCATION
            y_offset = self.padding + 3
            for line in balloon['lines']:
                text_color = (*self.text_color, balloon['alpha'])
                text_surface = self.font.render(line, True, text_color)
                text_x = (balloon['width'] - text_surface.get_width()) // 2 + 3
                balloon_surface.blit(text_surface, (text_x, y_offset))
                y_offset += self.line_height
            
            # Blit balloon to main surface
            surface.blit(balloon_surface, (balloon['x'] - 3, balloon['y'] - 3))
    
    def clear(self):
        """Clear all active dialog balloons"""
        self.active_balloons.clear()
    
    def has_active_dialog(self):
        """Check if there are any active dialog balloons"""
        return len(self.active_balloons) > 0


# Singleton instance
dialog_balloon_system = DialogBalloon()