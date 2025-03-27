import pygame
import random
from entities.grass import Grass
from entities.skeleton import Skeleton
from entities.slime import Slime
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Define enemy tiers based on difficulty levels
ENEMY_TIERS = {
    # Level 1: Only slimes (easiest)
    1: [
        {"type": Slime, "weight": 100, "min_count": 1, "max_count": 3}
    ],
    # Level 2: Mostly slimes, few skeletons
    2: [
        {"type": Slime, "weight": 80, "min_count": 2, "max_count": 4},
        {"type": Skeleton, "weight": 20, "min_count": 0, "max_count": 1}
    ],
    # Level 3: Mix of slimes and skeletons
    3: [
        {"type": Slime, "weight": 60, "min_count": 2, "max_count": 5},
        {"type": Skeleton, "weight": 40, "min_count": 1, "max_count": 2}
    ],
    # Level 4: Balanced mix
    4: [
        {"type": Slime, "weight": 50, "min_count": 2, "max_count": 6},
        {"type": Skeleton, "weight": 50, "min_count": 2, "max_count": 3}
    ],
    # Level 5: More skeletons than slimes
    5: [
        {"type": Slime, "weight": 30, "min_count": 1, "max_count": 4},
        {"type": Skeleton, "weight": 70, "min_count": 3, "max_count": 5}
    ],
    # Level 6+: Mostly skeletons (hardest)
    6: [
        {"type": Slime, "weight": 20, "min_count": 1, "max_count": 3},
        {"type": Skeleton, "weight": 80, "min_count": 4, "max_count": 8}
    ]
}

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
        # print(f"DEBUG: Added {entity_type} to block ({self.x_coord}, {self.y_coord})")
        
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
    
    def _get_difficulty_level(self, x_coord, y_coord):
        """Calculate difficulty level based on distance from origin"""
        # Calculate the Manhattan distance from origin
        distance = abs(x_coord) + abs(y_coord)
        
        # Map distance to difficulty tiers
        if distance == 0:  # Origin
            return 1
        elif distance <= 1:
            return 2
        elif distance <= 2:
            return 3
        elif distance <= 4:
            return 4
        elif distance <= 6:
            return 5
        else:
            return 6  # Max difficulty level
    
    def _add_enemies(self, block, safe_area=None):
        """Add enemies to a block with dynamic scaling based on distance from origin"""
        # Calculate difficulty level based on distance from origin
        x_coord, y_coord = block.x_coord, block.y_coord
        difficulty_level = self._get_difficulty_level(x_coord, y_coord)
        
        # Get enemy tier data for this difficulty level
        # If difficulty level exceeds our defined tiers, use the highest tier
        max_tier = max(ENEMY_TIERS.keys())
        tier_data = ENEMY_TIERS.get(min(difficulty_level, max_tier))
        
        print(f"DEBUG: Block ({x_coord}, {y_coord}) - Difficulty level: {difficulty_level}")
        
        # Calculate total enemies based on difficulty
        base_count = 3 + difficulty_level  # Base count increases with difficulty
        variation = random.randint(-1, 2)  # Add some randomness
        total_enemies = max(1, base_count + variation)
        
        # Get existing entities to check for collisions
        existing_entities = block.get_entities()
        
        print(f"DEBUG: Adding approximately {total_enemies} enemies to block ({x_coord}, {y_coord})")
        
        # Weighted selection of enemy types
        enemy_types = []
        weights = []
        
        for enemy_data in tier_data:
            enemy_types.append(enemy_data["type"])
            weights.append(enemy_data["weight"])
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Add enemies of different types
        enemies_added = 0
        max_attempts = 100  # Limit attempts
        
        # First, ensure minimum requirements for each enemy type
        for enemy_data in tier_data:
            enemy_type = enemy_data["type"]
            min_count = enemy_data["min_count"]
            
            # Add minimum number of this enemy type
            for _ in range(min_count):
                if self._add_single_enemy(block, enemy_type, existing_entities, safe_area):
                    enemies_added += 1
        
        # Then add remaining enemies based on weighted probabilities
        remaining_enemies = total_enemies - enemies_added
        
        attempts = 0
        while enemies_added < total_enemies and attempts < max_attempts:
            # Select enemy type based on weights
            enemy_type = random.choices(enemy_types, weights=normalized_weights, k=1)[0]
            
            if self._add_single_enemy(block, enemy_type, existing_entities, safe_area):
                enemies_added += 1
            
            attempts += 1
    
    def _add_single_enemy(self, block, enemy_type, existing_entities, safe_area=None):
        """Add a single enemy of specified type to the block"""
        # Determine entity dimensions based on type
        if enemy_type == Skeleton:
            width, height = 48, 52
        elif enemy_type == Slime:
            width, height = 32, 24
        else:
            width, height = 32, 32  # Default size
        
        # Try to find a valid position
        max_attempts = 20
        for _ in range(max_attempts):
            pos_x = random.randint(100, SCREEN_WIDTH - 100)
            pos_y = random.randint(100, SCREEN_HEIGHT - 100)
            
            # Create a test rect for the new enemy
            enemy_rect = pygame.Rect(pos_x, pos_y, width, height)
            
            # Don't place enemy if in safe area
            if safe_area and safe_area.colliderect(enemy_rect):
                continue
            
            # Check collision with existing entities
            collision = False
            for entity in existing_entities:
                if enemy_rect.colliderect(entity.get_rect()):
                    collision = True
                    break
            
            # If there's no collision, add the enemy
            if not collision:
                enemy = enemy_type(pos_x, pos_y)
                block.add_entity(enemy)
                existing_entities.append(enemy)  # Add to collision check list
                return True
        
        return False  # Failed to add enemy after max attempts
    
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
            
            player.current_block = (new_x, new_y)
            
            # Log difficulty level of the new block
            difficulty = self._get_difficulty_level(new_x, new_y)
            print(f"DEBUG: Moved to block ({new_x}, {new_y}) - Difficulty level: {difficulty}")
            
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
        difficulty = self._get_difficulty_level(x, y)
        return f"Block ({x}, {y}) - Difficulty: {difficulty}"