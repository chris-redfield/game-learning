import pygame
import os

class SpriteSheet:
    """
    A class to handle loading, extracting, and managing sprites from a sprite sheet
    or separate image files depending on the character
    """
    def __init__(self, character_name="link"):
        """
        Initialize the sprite sheet for the specified character
        
        Args:
            character_name (str): Name of the character ("link", "gojou", "ark", etc.)
        """
        self.character_name = character_name
        self.spritesheet = None
        
        # Load the appropriate sprite sheet for characters that use it
        if character_name.lower() in ["link", "gojou"]:
            self.load_spritesheet()
    
    def load_spritesheet(self):
        """Load the sprite sheet image"""
        try:
            self.spritesheet = pygame.image.load('assets/sprites.png').convert_alpha()
        except Exception as e:
            print(f"Error loading sprites: {e}")
            self.spritesheet = None
    
    def get_sprite_definitions(self, character_name):
        """Define sprite locations based on character name"""
        if character_name.lower() == "link":
            # Define Link's sprite locations (x, y, width, height)
            sprite_defs = {
                'down_idle': [(1, 3, 16, 24)],
                'down_walk': [(1, 3, 16, 24), (19, 3, 16, 24), (36, 3, 16, 24), 
                             (53, 3, 16, 24), (70, 3, 16, 24), (87, 3, 16, 24), 
                             (104, 3, 16, 24), (121, 3, 16, 24), (138, 3, 16, 24)],
                'up_idle': [(1, 111, 16, 24)],
                'up_walk': [(1, 111, 16, 24), (19, 111, 16, 24), (36, 111, 16, 24), 
                           (53, 111, 16, 24), (70, 111, 16, 24), (87, 111, 16, 24), 
                           (104, 111, 16, 24), (121, 111, 16, 24), (138, 111, 16, 24)],
                'right_idle': [(1, 56, 16, 24)],
                'right_walk': [(1, 56, 16, 24), (19, 56, 16, 24), (36, 56, 16, 24), 
                              (54, 56, 16, 24), (72, 56, 16, 24), (89, 56, 16, 24), 
                              (107, 56, 16, 24), (125, 56, 16, 24), (142, 56, 16, 24)]
                # We'll use flipped right sprites for left-facing animations
            }
            
            # Define sword sprite location
            sword_def = (1, 269, 8, 16)
            
        elif character_name.lower() == "gojou":
            # Example: Define Gojou's sprite locations (placeholders - would need actual coordinates)
            sprite_defs = {
                'down_idle': [(10, 10, 16, 24)],
                'down_walk': [(10, 10, 16, 24), (30, 10, 16, 24), (50, 10, 16, 24), 
                             (70, 10, 16, 24), (90, 10, 16, 24), (110, 10, 16, 24),
                             (130, 10, 16, 24), (150, 10, 16, 24), (170, 10, 16, 24)],
                'up_idle': [(10, 120, 16, 24)],
                'up_walk': [(10, 120, 16, 24), (30, 120, 16, 24), (50, 120, 16, 24),
                           (70, 120, 16, 24), (90, 120, 16, 24), (110, 120, 16, 24),
                           (130, 120, 16, 24), (150, 120, 16, 24), (170, 120, 16, 24)],
                'right_idle': [(10, 60, 16, 24)],
                'right_walk': [(10, 60, 16, 24), (30, 60, 16, 24), (50, 60, 16, 24),
                              (70, 60, 16, 24), (90, 60, 16, 24), (110, 60, 16, 24),
                              (130, 60, 16, 24), (150, 60, 16, 24), (170, 60, 16, 24)]
            }
            
            # Define sword sprite location for Gojou
            sword_def = (10, 280, 8, 16)
            
        elif character_name.lower() == "ark":
            # Ark uses separate files, but we still need a sword definition
            sprite_defs = {}
            sword_def = (1, 269, 8, 16)  # Use Link's sword for now
            
        else:
            # Default to Link if character not recognized
            print(f"Character '{character_name}' not recognized. Using Link as default.")
            return self.get_sprite_definitions("link")
            
        return sprite_defs, sword_def
    
    def get_sprite(self, x, y, width, height, target_width=None, target_height=None):
        """
        Extract a sprite from the spritesheet
        
        Args:
            x, y: Coordinates in the spritesheet
            width, height: Size in the spritesheet
            target_width, target_height: Size to scale to (optional)
        
        Returns:
            A pygame Surface with the extracted sprite
        """
        if self.spritesheet is None:
            # Create a placeholder if spritesheet failed to load
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.fill((50, 50, 150))
            return sprite
            
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        
        if target_width and target_height:
            return pygame.transform.scale(sprite, (target_width, target_height))
        return sprite
    
    def get_sword_sprite(self, character_name):
        """
        Extract a sword sprite from the spritesheet with proper dimensions
        
        Args:
            character_name: Name of the character to get sword for
        """
        # Get sword definition for this character
        _, sword_def = self.get_sprite_definitions(character_name)
        x, y, width, height = sword_def
        
        # Load the original spritesheet if not already loaded
        if self.spritesheet is None:
            try:
                self.spritesheet = pygame.image.load('assets/sprites.png').convert_alpha()
            except Exception as e:
                print(f"Error loading sprites for sword: {e}")
                # Create placeholder
                sword_sprite = pygame.Surface((width, height), pygame.SRCALPHA)
                sword_sprite.fill((200, 200, 200))
                return pygame.transform.scale(sword_sprite, (width * 2, height * 2))
        
        # Extract the sword sprite
        sprite = self.get_sprite(x, y, width, height)
        # Keep the original aspect ratio for the sword
        return pygame.transform.scale(sprite, (width * 2, height * 2))
    
    # Methods for loading separate image files
    def load_image(self, file_path):
        """
        Load an individual image file
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Loaded pygame Surface or None if loading failed
        """
        try:
            return pygame.image.load(file_path).convert_alpha()
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
    
    def get_sprite_from_file(self, file_path, target_width=None, target_height=None):
        """
        Load a sprite from a file and optionally scale it
        
        Args:
            file_path: Path to the image file
            target_width, target_height: Size to scale to (optional)
        
        Returns:
            A pygame Surface with the loaded sprite
        """
        sprite = self.load_image(file_path)
        
        if sprite is None:
            # Create a placeholder if image failed to load
            sprite = pygame.Surface((16, 24), pygame.SRCALPHA)
            sprite.fill((50, 50, 150))
            
            if target_width and target_height:
                return pygame.transform.scale(sprite, (target_width, target_height))
            return sprite
            
        if target_width and target_height:
            return pygame.transform.scale(sprite, (target_width, target_height))
        
        return sprite
    
    def extract_frames_from_spritesheet(self, file_path, num_frames, character_name, direction, target_width=None, target_height=None):
        """
        Extract individual frames from a walk animation spritesheet using specific coordinates
        
        Args:
            file_path: Path to the spritesheet image
            num_frames: Number of frames to extract
            character_name: Name of the character (for coordinate selection)
            direction: Direction of movement ('down_walk', 'up_walk', etc.)
            target_width, target_height: Size to scale each frame to (optional)
            
        Returns:
            List of pygame Surfaces containing the individual frames
        """
        spritesheet = self.load_image(file_path)
        frames = []
        
        if spritesheet is None:
            # Create placeholder frames if spritesheet failed to load
            for _ in range(num_frames):
                frame = pygame.Surface((16, 24), pygame.SRCALPHA)
                frame.fill((50, 50, 150))
                
                if target_width and target_height:
                    frame = pygame.transform.scale(frame, (target_width, target_height))
                    
                frames.append(frame)
            return frames
        
        # Get specific frame coordinates based on character and direction
        frame_coords = self.get_frame_coordinates(character_name, direction)
        
        # Extract each frame using the specific coordinates
        for coords in frame_coords:
            x, y, width, height = coords
            
            # Create a frame with the standard 16x24 size
            frame = pygame.Surface((16, 24), pygame.SRCALPHA)
            
            # Blit the sprite onto the frame
            frame.blit(spritesheet, (0, 0), (x, y, width, height))
            
            if target_width and target_height:
                frame = pygame.transform.scale(frame, (target_width, target_height))
                
            frames.append(frame)
            
        return frames
    
    def get_frame_coordinates(self, character_name, direction):
        """
        Get specific frame coordinates for a character's animation
        
        Args:
            character_name: Name of the character
            direction: Direction of movement ('down_walk', 'up_walk', etc.)
            
        Returns:
            List of (x, y, width, height) tuples for each frame
        """
        if character_name.lower() == "ark":
            # Based on the analysis, it seems the ark walk spritesheets may be 160px wide with 8 frames (20px per frame)
            # These coordinates center the 16px frame within each 20px section
            if direction == 'down_walk':
                return [
                    (4, 0, 16, 24),    # Frame 1
                    (24, 0, 16, 24),   # Frame 2
                    (44, 0, 16, 24),   # Frame 3
                    (64, 0, 16, 24),   # Frame 4
                    (84, 0, 16, 24),   # Frame 5
                    (104, 0, 16, 24),  # Frame 6
                    (124, 0, 16, 24),  # Frame 7
                    (144, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'up_walk':
                return [
                    (0, 0, 16, 24),    # Frame 1
                    (16, 0, 16, 24),   # Frame 2
                    (32, 0, 16, 24),   # Frame 3
                    (48, 0, 16, 24),   # Frame 4
                    (64, 0, 16, 24),   # Frame 5
                    (80, 0, 16, 24),  # Frame 6
                    (96, 0, 16, 24),  # Frame 7
                    (112, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'right_walk':
                return [
                    (0, 0, 16, 24),    # Frame 1
                    (18.7, 0.61, 16, 24),   # Frame 2
                    (36.01, 0.8, 16, 24),   # Frame 3
                    (52.85, 0, 16, 24),   # Frame 4
                    (71.73, 0, 16, 24),   # Frame 5
                    (89.56, 0.83, 16, 24),  # Frame 6
                    (106.84, 0.73, 16, 24),  # Frame 7
                    (123.63, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'left_walk':
                return [
                    # This is being loaded and reflected from the right_walk
                    # To keep the animation standardized
                ]
        elif character_name.lower() == "gojou":
            # Template for Gojou's walk animations - to be filled in later
            # For now, using a similar approach as Ark assuming similar dimensions
            if direction == 'down_walk':
                return [
                    (2, 0, 16, 24),    # Frame 1
                    (22, 0, 16, 24),   # Frame 2
                    (42, 0, 16, 24),   # Frame 3
                    (62, 0, 16, 24),   # Frame 4
                    (82, 0, 16, 24),   # Frame 5
                    (102, 0, 16, 24),  # Frame 6
                    (122, 0, 16, 24),  # Frame 7
                    (142, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'up_walk':
                return [
                    (2, 0, 16, 24),    # Frame 1
                    (22, 0, 16, 24),   # Frame 2
                    (42, 0, 16, 24),   # Frame 3
                    (62, 0, 16, 24),   # Frame 4
                    (82, 0, 16, 24),   # Frame 5
                    (102, 0, 16, 24),  # Frame 6
                    (122, 0, 16, 24),  # Frame 7
                    (142, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'right_walk':
                return [
                    (2, 0, 16, 24),    # Frame 1
                    (22, 0, 16, 24),   # Frame 2
                    (42, 0, 16, 24),   # Frame 3
                    (62, 0, 16, 24),   # Frame 4
                    (82, 0, 16, 24),   # Frame 5
                    (102, 0, 16, 24),  # Frame 6
                    (122, 0, 16, 24),  # Frame 7
                    (142, 0, 16, 24)   # Frame 8
                ]
            elif direction == 'left_walk':
                return [
                    (2, 0, 16, 24),    # Frame 1
                    (22, 0, 16, 24),   # Frame 2
                    (42, 0, 16, 24),   # Frame 3
                    (62, 0, 16, 24),   # Frame 4
                    (82, 0, 16, 24),   # Frame 5
                    (102, 0, 16, 24),  # Frame 6
                    (122, 0, 16, 24),  # Frame 7
                    (142, 0, 16, 24)   # Frame 8
                ]
        
        # Default to evenly spaced frames if character or direction not recognized
        # This calculates the default coordinates as in the previous version
        return self.calculate_default_frame_coordinates(character_name, direction)
    
    def calculate_default_frame_coordinates(self, character_name, direction):
        """
        Calculate default evenly-spaced frame coordinates for unknown characters or directions
        
        Args:
            character_name: Name of the character
            direction: Direction of movement
            
        Returns:
            List of (x, y, width, height) tuples for each frame
        """
        # Get the spritesheet path
        base_dir = f"assets/{character_name.lower()}"
        file_path = os.path.join(base_dir, f"{character_name.lower()}_walk_{direction.split('_')[0]}_speed-70.png")
        
        try:
            # Get the spritesheet dimensions
            spritesheet = self.load_image(file_path)
            if spritesheet is None:
                return [(0, 0, 16, 24) for _ in range(8)]  # Default placeholders
                
            sheet_width = spritesheet.get_width()
            num_frames = 8  # Default number of frames
            
            # Calculate frame width
            frame_width = sheet_width // num_frames
            
            # Generate evenly-spaced coordinates
            return [(i * frame_width, 0, 16, 24) for i in range(num_frames)]
            
        except Exception as e:
            print(f"Error calculating default frame coordinates: {e}")
            return [(0, 0, 16, 24) for _ in range(8)]  # Default placeholders
    
    def load_character_sprites_from_files(self, character_name, player_width, player_height):
        """
        Load all sprites for the character from separate image files
        
        Args:
            character_name: Name of the character to load
            player_width, player_height: Size to scale sprites to
            
        Returns:
            Dictionary of sprites
        """
        sprites = {}
        base_dir = f"assets/{character_name.lower()}"
        
        # Define file paths for different animations
        file_paths = {
            'down_idle': os.path.join(base_dir, f"{character_name.lower()}_stand_down.png"),
            'up_idle': os.path.join(base_dir, f"{character_name.lower()}_stand_up.png"),
            'right_idle': os.path.join(base_dir, f"{character_name.lower()}_stand_right.png"),
            'left_idle': os.path.join(base_dir, f"{character_name.lower()}_stand_left.png"),
            'down_walk': os.path.join(base_dir, f"{character_name.lower()}_walk_down_speed-70.png"),
            'up_walk': os.path.join(base_dir, f"{character_name.lower()}_walk_up_speed-70.png"),
            'right_walk': os.path.join(base_dir, f"{character_name.lower()}_walk_right_speed-70.png"),
            'left_walk': os.path.join(base_dir, f"{character_name.lower()}_walk_left_speed-70.png")
        }
        
        # Character-specific adjustments
        num_walk_frames = 8
        if character_name.lower() == "ark":
            # If you need specific frame counts for different characters
            num_walk_frames = 8  # Update this if Ark has a different number of frames
        
        # Load single frame sprites (idle animations)
        for direction in ['down_idle', 'up_idle', 'right_idle', 'left_idle']:
            sprites[direction] = [self.get_sprite_from_file(file_paths[direction], player_width, player_height)]
        
        # Load and extract frames from walk animation spritesheets
        for direction in ['down_walk', 'up_walk', 'right_walk', 'left_walk']:
            sprites[direction] = self.extract_frames_from_spritesheet(
                file_paths[direction], 
                num_frames=num_walk_frames,
                character_name=character_name,
                direction=direction,
                target_width=player_width, 
                target_height=player_height
            )
        
        return sprites
    
    def load_character_sprites_from_spritesheet(self, character_name, player_width, player_height):
        """
        Load all sprites for the character from the spritesheet
        
        Args:
            character_name: Name of the character to load
            player_width, player_height: Size to scale sprites to
            
        Returns:
            Dictionary of sprites
        """
        sprites = {}
        
        # Get sprite definitions for this character
        sprite_defs, _ = self.get_sprite_definitions(character_name)
        
        # Check if sprite sheet was loaded successfully
        if not self.spritesheet:
            # Create colored rectangle placeholders
            sprites = {
                'down_idle': [pygame.Surface((16, 24), pygame.SRCALPHA)],
                'down_walk': [pygame.Surface((16, 24), pygame.SRCALPHA) for _ in range(9)],
                'up_idle': [pygame.Surface((16, 24), pygame.SRCALPHA)],
                'up_walk': [pygame.Surface((16, 24), pygame.SRCALPHA) for _ in range(9)],
                'right_idle': [pygame.Surface((16, 24), pygame.SRCALPHA)],
                'right_walk': [pygame.Surface((16, 24), pygame.SRCALPHA) for _ in range(9)]
            }
            
            # Fill placeholders with colors
            for key in sprites:
                for sprite in sprites[key]:
                    sprite.fill((50, 50, 150))
                    
            return sprites
        
        # Extract and scale sprites based on definitions
        for key, positions in sprite_defs.items():
            sprites[key] = []
            for (x, y, w, h) in positions:
                sprite = self.get_sprite(x, y, w, h, player_width, player_height)
                sprites[key].append(sprite)
        
        # Create left animations by flipping right animations
        if 'left_idle' not in sprites and 'right_idle' in sprites:
            sprites['left_idle'] = [pygame.transform.flip(sprite, True, False) for sprite in sprites['right_idle']]
        if 'left_walk' not in sprites and 'right_walk' in sprites:
            sprites['left_walk'] = [pygame.transform.flip(sprite, True, False) for sprite in sprites['right_walk']]
        
        return sprites
    
    def load_character_sprites(self, character_name, player_width, player_height):
        """
        Load all sprites for the character and scale them to the player size.
        Uses the appropriate loading method based on the character.
        
        Args:
            character_name: Name of the character to load
            player_width, player_height: Size to scale sprites to
            
        Returns:
            Dictionary of sprites and sword sprite
        """
        self.character_name = character_name
        
        # Choose the appropriate loading method based on character
        if character_name.lower() in ["link", "gojou"]:
            # Use the original spritesheet method for Link and Gojou
            sprites = self.load_character_sprites_from_spritesheet(character_name, player_width, player_height)
        elif character_name.lower() == "ark":
            # Use separate image files for Ark
            sprites = self.load_character_sprites_from_files(character_name, player_width, player_height)
        else:
            # Default to Link's method for unknown characters
            print(f"Character '{character_name}' not recognized. Using Link as default.")
            sprites = self.load_character_sprites_from_spritesheet("link", player_width, player_height)
        
        # Get the sword sprite (always from the original spritesheet)
        sword_sprite = self.get_sword_sprite(character_name)
        
        return sprites, sword_sprite