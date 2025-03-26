import pygame
import random
from entities.grass import Grass
from entities.skeleton import Skeleton
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class WorldBlock:
    """Represents a single block/chunk of the world"""
    def __init__(self, block_id, x_coord, y_coord):
        self.block_id = block_id  # Unique identifier for this block
        self.x_coord = x_coord  # X coordinate in the world grid
        self.y_coord = y_coord  # Y coordinate in the world grid
        self.entities = []  # List of all entities in this block
        self.visited = False  # Whether the player has visited this block before
        print(f"DEBUG: Created new WorldBlock with ID {block_id} at ({x_coord}, {y_coord})")
        
    def add_entity(self, entity):
        """Add an entity to this block"""
        self.entities.append(entity)
        entity_type = type(entity).__name__
        print(f"DEBUG: Added {entity_type} to block ({self.x_coord}, {self.y_coord})")
        
    def remove_entity(self, entity):
        """Remove an entity from this block"""
        if entity in self.entities:
            self.entities.remove(entity)
            
    def get_entities(self):
        """Get all entities in this block"""
        return self.entities
        
    def get_entities_by_type(self, entity_type):
        """Get all entities of a specific type in this block"""
        return [entity for entity in self.entities if isinstance(entity, entity_type)]
        
    def mark_as_visited(self):
        """Mark this block as visited by the player"""
        self.visited = True
        
    def is_visited(self):
        """Check if this block has been visited by the player"""
        return self.visited

class World:
    """Manages the entire game world made up of multiple blocks"""
    def __init__(self):
        self.blocks = {}  # Dictionary to store blocks by their coordinates (x, y)
        self.current_block_coords = (0, 0)  # Start at origin block
        self.next_block_id = 0  # Counter for generating unique block IDs
        
    def generate_block(self, x_coord, y_coord, player_entry_point=None):
        """Generate a new block at the specified coordinates"""
        # If block already exists, just return it
        block_key = (x_coord, y_coord)
        if block_key in self.blocks:
            print(f"DEBUG: Block ({x_coord}, {y_coord}) already exists, returning existing block")
            return self.blocks[block_key]
            
        # Create a new block
        block_id = f"block_{self.next_block_id}"
        self.next_block_id += 1
        
        print(f"DEBUG: Creating NEW block at ({x_coord}, {y_coord}) with ID {block_id}")
        new_block = WorldBlock(block_id, x_coord, y_coord)
        self.blocks[block_key] = new_block
        
        # Generate content for the block (grass patches, etc.)
        self._populate_block(new_block, player_entry_point)
        
        return new_block
    
    def _populate_block(self, block, player_entry_point=None):
        """Fill a block with entities like grass, enemies, etc."""
        print(f"DEBUG: Populating block ({block.x_coord}, {block.y_coord})")
        
        # Create safe area around player entry point (if specified)
        safe_area = None
        if player_entry_point:
            # Create a safe rectangle around the entry point
            safe_area = pygame.Rect(
                player_entry_point[0] - 100,  # X - 100
                player_entry_point[1] - 100,  # Y - 100
                200,  # Width of safe area
                200   # Height of safe area
            )
        
        # Add grass patches
        self._add_grass_patches(block, 15, safe_area)
        
        # Add enemies
        self._add_enemies(block, safe_area)
        
        # Mark as populated
        block.mark_as_visited()
    
    def _add_enemies(self, block, safe_area=None):
        """Add enemies to a block"""
        
        # For the initial block, add 2 skeletons
        skeleton_positions = [
            (200, 200),  # First skeleton position
            (400, 400)   # Second skeleton position
        ]
        
        for pos_x, pos_y in skeleton_positions:
            enemy_rect = pygame.Rect(pos_x, pos_y, 32, 32)
            
            # Don't place enemy if in safe area
            if safe_area and safe_area.colliderect(enemy_rect):
                # print(f"DEBUG: Skipping skeleton at ({pos_x}, {pos_y}) - in safe area")
                continue
                
            skeleton = Skeleton(pos_x, pos_y)
            block.add_entity(skeleton)
            # print(f"DEBUG: Added skeleton at ({pos_x}, {pos_y})")
    
    def _add_grass_patches(self, block, count, safe_area=None):
        """Add grass patches to a block"""
        min_distance_between_grass = 64
        existing_grass = []
        
        attempts = 0
        while len(existing_grass) < count and attempts < 100:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            new_grass_rect = pygame.Rect(x, y, 32, 32)
            
            # Check if in safe area
            if safe_area and safe_area.colliderect(new_grass_rect):
                attempts += 1
                continue
                
            # Check distance from other grass
            too_close = False
            for grass in existing_grass:
                grass_rect = grass.get_rect()
                if new_grass_rect.colliderect(grass_rect) or \
                   pygame.math.Vector2(new_grass_rect.center).distance_to(
                       pygame.math.Vector2(grass_rect.center)) < min_distance_between_grass:
                    too_close = True
                    break
            
            if not too_close:
                new_grass = Grass(x, y)
                existing_grass.append(new_grass)
                block.add_entity(new_grass)
            
            attempts += 1
    
    def get_current_block(self):
        """Get the current block the player is in"""
        return self.blocks.get(self.current_block_coords)
    
    def get_block_at(self, x_coord, y_coord):
        """Get the block at the specified coordinates, generating it if needed"""
        block_key = (x_coord, y_coord)
        
        if block_key not in self.blocks:
            # Generate a new block if it doesn't exist
            return self.generate_block(x_coord, y_coord)
        
        return self.blocks[block_key]
    
    def check_player_block_transition(self, player):
        """Check if player has moved out of the current block and handle transition"""
        # Get player position
        player_rect = player.get_rect()
        
        block_changed = False
        new_player_pos = None
        direction = None
        new_x, new_y = self.current_block_coords
        
        # Check if player is out of bounds
        if player_rect.left <= 0:  # Moving left

            direction = "left"
            block_changed = True
            new_x = self.current_block_coords[0] - 1
            new_player_pos = (SCREEN_WIDTH - player.width - 10, player_rect.top)
            
        elif player_rect.right >= SCREEN_WIDTH:  # Moving right
            direction = "right"
            block_changed = True
            new_x = self.current_block_coords[0] + 1
            new_player_pos = (10, player_rect.top)
            
        elif player_rect.top <= 0:  # Moving up
            direction = "up"
            block_changed = True
            new_y = self.current_block_coords[1] - 1
            new_player_pos = (player_rect.left, SCREEN_HEIGHT - player.height - 10)
            
        elif player_rect.bottom >= SCREEN_HEIGHT:  # Moving down
            direction = "down"
            block_changed = True
            new_y = self.current_block_coords[1] + 1
            new_player_pos = (player_rect.left, 10)
        
        if block_changed:
            # Transition to new block
            new_block_coords = (new_x, new_y)
            new_block = self.get_block_at(new_x, new_y)
            
            # If this is a new block, set player entry point for safe area
            if not new_block.is_visited():
                entry_point = new_player_pos
                self._populate_block(new_block, entry_point)
            
            # Update current block
            self.current_block_coords = new_block_coords
            
            # Move player to new position
            player.x, player.y = new_player_pos
            
            return True, direction
        
        return False, None
    
    def get_current_entities(self):
        """Get all entities in the current block"""
        current_block = self.get_current_block()
        if current_block:
            return current_block.get_entities()
        return []
    
    def get_block_description(self):
        """Get a description of the current block for display"""
        x, y = self.current_block_coords
        return f"Block ({x}, {y})"