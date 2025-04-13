import pygame
import os
import datetime

class Dialog:
    def __init__(self, title, options=None, callback=None):
        """
        Initialize a dialog box
        
        Args:
            title: The title of the dialog
            options: List of option strings
            callback: Function to call when an option is selected, receives option index
        """
        self.title = title
        self.options = options or []
        self.callback = callback
        self.visible = False
        self.selected_option = 0
        
        # Colors
        self.colors = {
            'background': (30, 33, 41, 230),  # Dark blue-gray, semi-transparent
            'text': (255, 255, 255),          # White text
            'title': (255, 215, 0),           # Gold for titles
            'option': (200, 200, 200),        # Light gray for options
            'selected': (255, 255, 0),        # Yellow for selected option
            'border': (180, 180, 200),        # Border color
        }
        
        # Fonts (will be initialized in set_fonts method)
        self.title_font = None
        self.option_font = None
    
    def set_fonts(self, title_size=24, option_size=20):
        """Set fonts for the dialog (called after pygame.font is initialized)"""
        self.title_font = pygame.font.SysFont('Arial', title_size, bold=True)
        self.option_font = pygame.font.SysFont('Arial', option_size)
    
    def show(self):
        """Show the dialog"""
        self.visible = True
        self.selected_option = 0
    
    def hide(self):
        """Hide the dialog"""
        self.visible = False
    
    def is_visible(self):
        """Check if the dialog is visible"""
        return self.visible
    
    def select_next(self):
        """Select the next option"""
        if self.options:
            self.selected_option = (self.selected_option + 1) % len(self.options)
    
    def select_prev(self):
        """Select the previous option"""
        if self.options:
            self.selected_option = (self.selected_option - 1) % len(self.options)
    
    def select_option(self):
        """Select the current option and trigger callback"""
        if self.callback and self.options:
            self.callback(self.selected_option)
    
    def handle_event(self, event):
        """Handle events for the dialog"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.select_prev()
                return True
            elif event.key == pygame.K_DOWN:
                self.select_next()
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                return True
        
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button
                self.select_option()
                return True
            elif event.button == 1:  # B button
                self.hide()
                return True
        
        elif event.type == pygame.JOYHATMOTION:
            hat_value = event.value
            
            if hat_value[1] == 1:  # D-pad up
                self.select_prev()
                return True
            elif hat_value[1] == -1:  # D-pad down
                self.select_next()
                return True
        
        return False
    
    def draw(self, surface):
        """Draw the dialog box"""
        if not self.visible or not self.title_font or not self.option_font:
            return
        
        # Calculate dialog size based on content
        padding = 20
        option_height = 30
        
        dialog_width = 500
        dialog_height = 100 + len(self.options) * option_height
        
        # Center dialog on screen
        screen_width, screen_height = surface.get_size()
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        # Create dialog background (semi-transparent)
        dialog_bg = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_bg.fill(self.colors['background'])
        surface.blit(dialog_bg, (dialog_x, dialog_y))
        
        # Draw border
        pygame.draw.rect(surface, self.colors['border'], 
                         (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Draw title
        title_text = self.title_font.render(self.title, True, self.colors['title'])
        title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
        title_y = dialog_y + padding
        surface.blit(title_text, (title_x, title_y))
        
        # Draw options
        for i, option in enumerate(self.options):
            option_color = self.colors['selected'] if i == self.selected_option else self.colors['option']
            option_text = self.option_font.render(option, True, option_color)
            
            option_x = dialog_x + padding + 20  # Add some indent
            option_y = dialog_y + padding + 40 + i * option_height
            
            # Indicate selected option with a cursor
            if i == self.selected_option:
                cursor_text = self.option_font.render("> ", True, self.colors['selected'])
                surface.blit(cursor_text, (option_x - 20, option_y))
            
            surface.blit(option_text, (option_x, option_y))


class FileDialog(Dialog):
    def __init__(self, title, message="", files=None, callback=None):
        """
        Initialize a file selection dialog
        
        Args:
            title: The title of the dialog
            message: Optional message to display
            files: List of file names
            callback: Function to call when a file is selected, receives file index and file list
        """
        super().__init__(title, files, None)
        self.message = message
        self.file_callback = callback
    
    def select_option(self):
        """Select the current file and trigger callback"""
        if self.file_callback and self.options:
            self.file_callback(self.selected_option, self.options)
    
    def draw(self, surface):
        """Draw the file dialog box"""
        if not self.visible or not self.title_font or not self.option_font:
            return
        
        # Calculate dialog size based on content
        padding = 20
        option_height = 30
        
        dialog_width = 500  # Wider for filenames
        
        # Extra height for message
        message_height = 40 if self.message else 0
        dialog_height = 100 + message_height + len(self.options) * option_height
        
        # Center dialog on screen
        screen_width, screen_height = surface.get_size()
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        # Create dialog background (semi-transparent)
        dialog_bg = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_bg.fill(self.colors['background'])
        surface.blit(dialog_bg, (dialog_x, dialog_y))
        
        # Draw border
        pygame.draw.rect(surface, self.colors['border'], 
                         (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Draw title
        title_text = self.title_font.render(self.title, True, self.colors['title'])
        title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
        title_y = dialog_y + padding
        surface.blit(title_text, (title_x, title_y))
        
        # Draw message if present
        current_y = title_y + title_text.get_height() + 10
        if self.message:
            message_text = self.option_font.render(self.message, True, self.colors['text'])
            message_x = dialog_x + padding
            surface.blit(message_text, (message_x, current_y))
            current_y += message_height
        
        # Draw file options
        for i, option in enumerate(self.options):
            option_color = self.colors['selected'] if i == self.selected_option else self.colors['option']
            option_text = self.option_font.render(option, True, option_color)
            
            option_x = dialog_x + padding + 20  # Add some indent
            option_y = current_y + i * option_height
            
            # Indicate selected option with a cursor
            if i == self.selected_option:
                cursor_text = self.option_font.render("> ", True, self.colors['selected'])
                surface.blit(cursor_text, (option_x - 20, option_y))
            
            surface.blit(option_text, (option_x, option_y))

class SaveOverwriteDialog(FileDialog):
    def __init__(self, save_manager, callback=None):
        self.save_manager = save_manager
        self.callback = callback

        self.creating_new = False
        self.editing_name = False
        self.entered_name = ""
        self.default_name = self.generate_default_name()

        self.message = "Choose a save file to overwrite, or create a new one:"
        self.files = self.get_save_files() + ["<Create New Save>"]

        super().__init__("Save Game", self.message, self.files, self.on_select)

    def generate_default_name(self):
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d_%H%M%S") + ".sav"

    def get_save_files(self):
        save_dir = self.save_manager.save_directory
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        return [f for f in os.listdir(save_dir) if f.endswith('.sav')]

    def on_select(self, index, options):
        selected = options[index]

        if selected == "<Create New Save>":
            self.creating_new = True
            self.editing_name = True
            self.entered_name = ""
        else:
            self.save_to_file(selected)

    def handle_event(self, event):
        if self.editing_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    final_name = self.entered_name or self.default_name
                    if not final_name.endswith(".sav"):
                        final_name += ".sav"
                    self.save_to_file(final_name)
                elif event.key == pygame.K_BACKSPACE:
                    self.entered_name = self.entered_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.hide()
                else:
                    self.entered_name += event.unicode
            return True
        return super().handle_event(event)

    def save_to_file(self, filename):
        filepath = os.path.join(self.save_manager.save_directory, filename)
        self.save_manager.save_game_to(filepath)
        self.hide()
        if self.callback:
            self.callback(filepath)

    def draw(self, surface):
        super().draw(surface)

        if self.editing_name and self.visible:
            padding = 20
            screen_width, screen_height = surface.get_size()
            text = f"Enter filename: {self.entered_name or self.default_name}"
            font = self.option_font
            text_surf = font.render(text, True, (255, 255, 255))
            x = (screen_width - text_surf.get_width()) // 2
            y = screen_height // 2 + 150
            surface.blit(text_surf, (x, y))

    def reset(self):
        self.creating_new = False
        self.editing_name = False
        self.entered_name = ""
        self.default_name = self.generate_default_name()
        self.files = self.get_save_files() + ["<Create New Save>"]
        self.options = self.files
        self.selected_option = 0