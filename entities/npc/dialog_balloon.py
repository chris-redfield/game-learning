import pygame


class DialogBalloon:
    def __init__(self):
        """Initialize the dialog balloon system"""
        self.active_balloons = []
        
        # Styling
        self.padding = 10
        self.margin = 5
        self.max_width = 250  # Maximum width before text wraps
        self.line_height = 20
        self.display_duration = 2000  # 3 seconds
        self.fade_duration = 200  # 0.5 seconds fade out
        
        # Colors
        self.bg_color = (30, 33, 41, 230)  # Dark blue-gray, semi-transparent
        self.text_color = (255, 255, 255)  # White text
        self.border_color = (180, 180, 200)  # Light border
        
        # Font (will be set later)
        self.font = None
        
        # Tail properties for speech bubble
        self.tail_height = 10
        self.tail_width = 15
    
    def set_font(self, font_size=14):
        """Set the font for dialog balloons"""
        self.font = pygame.font.SysFont('Arial', font_size)
    
    def add_dialog(self, text, x, y, entity_width=35, entity_height=41):
        """Add a new dialog balloon"""
        if not self.font:
            self.set_font()
        
        # Wrap text if needed
        wrapped_lines = self._wrap_text(text)
        
        # Calculate balloon dimensions
        text_width = max(self.font.size(line)[0] for line in wrapped_lines)
        text_height = len(wrapped_lines) * self.line_height
        
        balloon_width = text_width + (self.padding * 3)
        balloon_height = text_height + (self.padding * 3)
        
        # Position balloon above entity's head
        balloon_x = x + (entity_width // 2) - (balloon_width // 2)
        balloon_y = y - balloon_height - self.tail_height - 10  # 10px above head
        
        # Keep balloon on screen
        balloon_x = max(5, min(balloon_x, pygame.display.get_surface().get_width() - balloon_width - 5))
        balloon_y = max(5, balloon_y)
        
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
    
    def _wrap_text(self, text):
        """Wrap text to fit within max width"""
        if not self.font:
            return [text]
        
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width = self.font.size(test_line)[0]
            
            if width <= self.max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, force break
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
                (balloon['width'] + 4, balloon['height'] + self.tail_height + 4),
                pygame.SRCALPHA
            )
            
            # Draw balloon background
            bg_color = (*self.bg_color[:3], min(self.bg_color[3], balloon['alpha']))
            pygame.draw.rect(
                balloon_surface,
                bg_color,
                (2, 2, balloon['width'], balloon['height']),
                border_radius=8
            )
            
            # Draw balloon border
            border_color = (*self.border_color, balloon['alpha'])
            pygame.draw.rect(
                balloon_surface,
                border_color,
                (2, 2, balloon['width'], balloon['height']),
                width=2,
                border_radius=8
            )
            
            # Draw tail (speech bubble pointer)
            tail_points = [
                (balloon['width'] // 2 - self.tail_width // 2, balloon['height']),
                (balloon['width'] // 2 + self.tail_width // 2, balloon['height']),
                (balloon['width'] // 2, balloon['height'] + self.tail_height)
            ]
            
            # Adjust tail position relative to balloon surface
            tail_points = [(p[0] + 2, p[1] + 2) for p in tail_points]
            
            pygame.draw.polygon(balloon_surface, bg_color, tail_points)
            pygame.draw.lines(balloon_surface, border_color, False, 
                            [tail_points[0], tail_points[2], tail_points[1]], 2)
            
            # Draw text
            y_offset = self.padding + 2
            for line in balloon['lines']:
                text_color = (*self.text_color, balloon['alpha'])
                text_surface = self.font.render(line, True, text_color)
                text_x = (balloon['width'] - text_surface.get_width()) // 2 + 2
                balloon_surface.blit(text_surface, (text_x, y_offset))
                y_offset += self.line_height
            
            # Blit balloon to main surface
            surface.blit(balloon_surface, (balloon['x'] - 2, balloon['y'] - 2))
    
    def clear(self):
        """Clear all active dialog balloons"""
        self.active_balloons.clear()
    
    def has_active_dialog(self):
        """Check if there are any active dialog balloons"""
        return len(self.active_balloons) > 0


# Singleton instance
dialog_balloon_system = DialogBalloon()