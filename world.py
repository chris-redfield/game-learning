import pygame
import random
import math
from entities.grass import Grass
from entities.rock import Rock
from entities.enemy.skeleton import Skeleton
from entities.enemy.slime import Slime
from entities.bonfire import Bonfire  # Import the new Bonfire class
from items.health_potion import HealthPotion  # Import the HealthPotion class
from items.ancient_scroll import AncientScroll  # Import the Ancient Scroll class
from items.dragon_heart import DragonHeart  # Import the Dragon Heart class
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Define enemy tiers based on difficulty levels
ENEMY_TIERS = {
    # Level 1: Only slimes (easiest)
    1: [
        {"type": Slime, "weight": 100, "enemy_type": "fast"}
    ],
    # Level 2: Mostly slimes, few skeletons
    2: [
        {"type": Slime, "weight": 80, "enemy_type": "fast"},
        {"type": Skeleton, "weight": 20, "enemy_type": "normal"}
    ],
    # Level 3: Mix of slimes and skeletons
    3: [
        {"type": Slime, "weight": 60, "enemy_type": "fast"},
        {"type": Skeleton, "weight": 40, "enemy_type": "normal"}
    ],
    # Level 4: Balanced mix
    4: [
        {"type": Slime, "weight": 50, "enemy_type": "fast"},
        {"type": Skeleton, "weight": 50, "enemy_type": "normal"}
    ],
    # Level 5: More skeletons than slimes
    5: [
        {"type": Slime, "weight": 30, "enemy_type": "fast"},
        {"type": Skeleton, "weight": 70, "enemy_type": "brute"}
    ],
    # Level 6+: Mostly skeletons (hardest)
    6: [
        {"type": Slime, "weight": 20, "enemy_type": "fast"},
        {"type": Skeleton, "weight": 80, "enemy_type": "brute"}
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
        # entity_type = type(entity).__name__
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
        self._populate_block(new_block, player_entry_point, x_coord, y_coord)
        
        return new_block
    
    def _populate_block(self, block, player_entry_point=None, x_coord=None, y_coord=None):
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
        
        # Special case for origin block (0,0) - add a bonfire northeast of player spawn
        if x_coord == 0 and y_coord == 0:
            # The player spawns at the center of the screen, so place bonfire northeast of that
            player_center_x = SCREEN_WIDTH // 2
            player_center_y = SCREEN_HEIGHT // 2
            
            # Calculate position for bonfire (northeast of player)
            bonfire_x = player_center_x + 100  # 100 pixels to the right
            bonfire_y = player_center_y - 100  # 100 pixels up
            
            # Create and add the bonfire
            bonfire = Bonfire(bonfire_x, bonfire_y)
            # Set block coordinates so the bonfire knows it's at the origin
            bonfire.set_block_coordinates(x_coord, y_coord)
            block.add_entity(bonfire)
            print(f"DEBUG: Added bonfire to origin block at ({bonfire_x}, {bonfire_y})")
            
            # Add a health potion near player using the _add_items method
            potion_x = player_center_x - 80  # 80 pixels to the left
            potion_y = player_center_y + 50   # 50 pixels down
            
            # Use the enhanced _add_items method with specific position
            self._add_items(
                block=block,
                count=1, 
                item_type=HealthPotion, 
                positions=[(potion_x, potion_y)]
            )
            
            # Extend safe area to include bonfire and potion
            if safe_area:
                # Create a new larger safe area that includes player, bonfire, and potion
                safe_area = pygame.Rect(
                    min(player_center_x - 100, bonfire_x - 50, potion_x - 50),
                    min(player_center_y - 100, bonfire_y - 50, potion_y - 50),
                    max(200, abs(bonfire_x - player_center_x) + 150, abs(potion_x - player_center_x) + 150),
                    max(200, abs(bonfire_y - player_center_y) + 150, abs(potion_y - player_center_y) + 150)
                )
            else:
                # Create a safe area around bonfire and potion if there wasn't one already
                safe_area = pygame.Rect(
                    min(bonfire_x - 50, potion_x - 50),
                    min(bonfire_y - 50, potion_y - 50),
                    max(150, abs(bonfire_x - potion_x) + 100),
                    max(150, abs(bonfire_y - potion_y) + 100)
                )
        
        # Add world entities patches
        entity_map = {
            "grass": random.choice(list(range(5, 16))),
            "rock": random.choice(list(range(1, 6)))
        }
        self._add_world_entities(block, entity_map, safe_area)
        
        # Add enemies
        self._add_enemies(block, safe_area)
        
        # Mark as populated
        block.mark_as_visited()
    
    def place_special_items(self, item_type=None, coords=None):
        """Place special items like XP modifiers in specific world locations or random locations
        
        Args:
            item_type (str, optional): Type of item to place ("ancient_scroll" or "dragon_heart")
            coords (list, optional): [x, y] coordinates for the block where the item should be placed.
                                    If None, a random suitable location will be chosen.
        """
        # If no specific item type is requested, place both items
        if item_type is None or item_type.lower() == "ancient_scroll":
            # Place Ancient Scroll
            if coords is None:
                # If no coordinates provided, place at origin by default
                scroll_coords = [0, 0]
            else:
                scroll_coords = coords
                
            scroll_block = self.get_or_generate_block(scroll_coords[0], scroll_coords[1])
            
            # If placing at origin, use a specific position relative to player spawn
            if scroll_coords[0] == 0 and scroll_coords[1] == 0:
                player_center_x = SCREEN_WIDTH // 2
                player_center_y = SCREEN_HEIGHT // 2
                scroll_x = player_center_x + 50  # 50 pixels to the right
                scroll_y = player_center_y + 80  # 80 pixels down
                positions = [(scroll_x, scroll_y)]
            else:
                # For other blocks, place it randomly
                positions = None
                
            # Add the Ancient Scroll
            added = self._add_items(
                block=scroll_block,
                count=1,
                item_type=AncientScroll,
                positions=positions
            )
            
            if added > 0:
                print(f"Ancient Scroll placed in block ({scroll_coords[0]}, {scroll_coords[1]})")
            else:
                print(f"Failed to place Ancient Scroll in block ({scroll_coords[0]}, {scroll_coords[1]})")
        
        # Place Dragon Heart if requested or if placing all items
        if item_type is None or item_type.lower() == "dragon_heart":
            # Place Dragon Heart
            if coords is None:
                # If no coordinates provided, place in a challenging location
                heart_coords = [5, 5]
            else:
                heart_coords = coords
                
            heart_block = self.get_or_generate_block(heart_coords[0], heart_coords[1])
            
            # Add the Dragon Heart with random position in the block
            added = self._add_items(
                block=heart_block,
                count=1,
                item_type=DragonHeart
            )
            
            if added > 0:
                print(f"Dragon Heart placed in block ({heart_coords[0]}, {heart_coords[1]})")
            else:
                print(f"Failed to place Dragon Heart in block ({heart_coords[0]}, {heart_coords[1]})")
    
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
    
    def _calculate_difficulty_points(self, x_coord, y_coord):
        """Calculate total difficulty points for a block based on distance from origin"""
        # Base difficulty level (1-6)
        base_difficulty = self._get_difficulty_level(x_coord, y_coord)
        
        # Convert to difficulty points - higher levels have more points
        # We'll use a simple formula: difficulty^2 + 2
        difficulty_points = base_difficulty * base_difficulty + 2
        
        # Add some randomness (-2 to +2)
        difficulty_points += random.randint(-2, 2)
        
        # Ensure minimum of 2 difficulty points
        return max(2, difficulty_points)
    
    def _get_difficulty_factor(self, x_coord, y_coord):
        """Calculate a difficulty scaling factor based on distance from origin"""
        # Calculate the Manhattan distance from origin
        distance = abs(x_coord) + abs(y_coord)
        
        # Calculate base difficulty factor (1.0 = normal, higher = harder)
        if distance == 0:
            return 1.0  # Normal difficulty at origin
        elif distance <= 1:
            return 1.2  # 20% harder at distance 1
        elif distance <= 2:
            return 1.4  # 40% harder at distance 2
        elif distance <= 4:
            return 1.6  # 60% harder at distance 4
        elif distance <= 6:
            return 1.8  # 80% harder at distance 6
        else:
            return 2.0 + min(1.0, (distance - 6) * 0.1)  # +10% per distance beyond 6, up to +100%
    
    def _add_enemies(self, block, safe_area=None):
        """Add enemies to a block using difficulty points system"""
        # Get block coordinates
        x_coord, y_coord = block.x_coord, block.y_coord
        
        # Calculate total difficulty points for this block
        total_difficulty_points = self._calculate_difficulty_points(x_coord, y_coord)
        remaining_points = total_difficulty_points
        
        # Get difficulty level for enemy selection
        difficulty_level = self._get_difficulty_level(x_coord, y_coord)
        
        # Get enemy tier data for this difficulty level
        max_tier = max(ENEMY_TIERS.keys())
        tier_data = ENEMY_TIERS.get(min(difficulty_level, max_tier))
        
        print(f"DEBUG: Block ({x_coord}, {y_coord}) - Difficulty level: {difficulty_level}, Points: {total_difficulty_points}")
        
        # Get existing entities to check for collisions
        existing_entities = block.get_entities()
        
        # Calculate max level for enemies in this block (25% of total difficulty points)
        max_enemy_level = max(1, round(total_difficulty_points * 0.25))
        
        # Extract enemy types and weights
        enemy_types = []
        weights = []
        enemy_type_map = {}
        
        for enemy_data in tier_data:
            enemy_types.append(enemy_data["type"])
            weights.append(enemy_data["weight"])
            enemy_type_map[enemy_data["type"]] = enemy_data["enemy_type"]
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Keep adding enemies until we run out of difficulty points
        enemies_added = 0
        max_attempts = 100  # Prevent infinite loops
        attempts = 0
        
        print(f"DEBUG: Adding enemies with max level {max_enemy_level}, total difficulty points: {total_difficulty_points}")
        
        while remaining_points > 0 and attempts < max_attempts:
            # Select enemy type based on weights
            enemy_type = random.choices(enemy_types, weights=normalized_weights, k=1)[0]
            
            # Determine enemy level based on remaining points and max level
            max_level_for_this_enemy = min(max_enemy_level, remaining_points)
            
            if max_level_for_this_enemy < 1:
                # Not enough points for even a level 1 enemy
                break
                
            # Randomly select a level between 1 and max allowed
            enemy_level = random.randint(1, max_level_for_this_enemy)
            
            # Get the enemy_type string (fast, normal, brute, etc.)
            enemy_type_string = enemy_type_map[enemy_type]
            
            # Try to add the enemy
            if self._add_single_enemy(block, enemy_type, enemy_level, enemy_type_string, existing_entities, safe_area):
                # Successfully added an enemy, subtract its level from remaining points
                remaining_points -= enemy_level
                enemies_added += 1
                print(f"DEBUG: Added level {enemy_level} {enemy_type.__name__} ({enemy_type_string}), remaining points: {remaining_points}")
            
            attempts += 1
        
        print(f"DEBUG: Added {enemies_added} enemies to block ({x_coord}, {y_coord}), using {total_difficulty_points - remaining_points} difficulty points")
        
        # If we have unused points but couldn't place more enemies, we might need to increase existing enemy levels
        if remaining_points > 0 and enemies_added > 0 and attempts >= max_attempts:
            print(f"DEBUG: Had {remaining_points} unused difficulty points, could not place more enemies")
    
    def _add_single_enemy(self, block, enemy_type, enemy_level, enemy_type_string, existing_entities, safe_area=None):
        """Add a single enemy of specified type and level to the block"""
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
                # Create the enemy
                enemy = enemy_type(pos_x, pos_y)
                
                # Set enemy type
                enemy.enemy_type = enemy_type_string
                
                # Get difficulty factor for the block
                difficulty_factor = self._get_difficulty_factor(block.x_coord, block.y_coord)
                
                # Set enemy level with the specified level
                enemy.set_level(enemy_level, difficulty_factor)
                
                # Add to block and collision list
                block.add_entity(enemy)
                return True
        
        return False  # Failed to add enemy after max attempts
    
    def _add_world_entities(self, block, entity_map, safe_area):
        """entity_map example: {"grass":15, "rock":10}"""
        if "grass" in entity_map:
            grass_qtd = entity_map["grass"]
        else:
            grass_qtd = 10
        if "rock" in entity_map:
            rock_qtd = entity_map["rock"]
        else:
            rock_qtd = 5

        # Add grass patches first
        self._add_grass_patches(block, grass_qtd, safe_area)
        
        # When adding rocks, check against all existing entities (including grass)
        self._add_rock_patches(block, rock_qtd, safe_area)

    def _add_grass_patches(self, block, count, safe_area=None):
        """Add grass patches to a block"""
        min_distance_between_entities = 64
        existing_entities = block.get_entities()  # Get all existing entities to check against
        
        attempts = 0
        grass_added = 0
        while grass_added < count and attempts < 100:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            new_grass_rect = pygame.Rect(x, y, 32, 32)
            
            # Check if in safe area
            if safe_area and safe_area.colliderect(new_grass_rect):
                attempts += 1
                continue
                
            # Check distance from other entities
            too_close = False
            for entity in existing_entities:
                entity_rect = entity.get_rect()
                if new_grass_rect.colliderect(entity_rect) or \
                pygame.math.Vector2(new_grass_rect.center).distance_to(
                    pygame.math.Vector2(entity_rect.center)) < min_distance_between_entities:
                    too_close = True
                    break
            
            if not too_close:
                new_grass = Grass(x, y)
                existing_entities.append(new_grass)  # Add to our tracking list
                block.add_entity(new_grass)
                grass_added += 1
            
            attempts += 1

    def _add_rock_patches(self, block, count, safe_area=None):
        """Add rock patches to a block"""
        min_distance_between_entities = 64
        existing_entities = block.get_entities()  # Get all existing entities to check against
        
        attempts = 0
        rocks_added = 0
        while rocks_added < count and attempts < 100:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            new_rock_rect = pygame.Rect(x, y, 32, 32)
            
            # Check if in safe area
            if safe_area and safe_area.colliderect(new_rock_rect):
                attempts += 1
                continue
                
            # Check distance from other entities
            too_close = False
            for entity in existing_entities:
                entity_rect = entity.get_rect()
                if new_rock_rect.colliderect(entity_rect) or \
                pygame.math.Vector2(new_rock_rect.center).distance_to(
                    pygame.math.Vector2(entity_rect.center)) < min_distance_between_entities:
                    too_close = True
                    break
            
            if not too_close:
                new_rock = Rock(x, y)
                existing_entities.append(new_rock)  # Add to our tracking list
                block.add_entity(new_rock)
                rocks_added += 1
            
            attempts += 1

    def _add_items(self, block, count, item_type, safe_area=None, positions=None):
        """Add items of a specific type to a block
        
        Args:
            block: The world block to add items to
            count: Number of items to add
            item_type: The class of item to create
            safe_area: Area where items shouldn't be placed (unless explicit positions given)
            positions: Optional list of (x,y) tuples for precise placement. If provided, overrides random placement.
        
        Returns:
            Number of items successfully added
        """
        min_distance_between_items = 48
        existing_entities = block.get_entities()
        
        items_added = 0
        attempts = 0
        
        # If specific positions are provided, use those instead of random placement
        if positions and len(positions) > 0:
            for pos in positions[:count]:  # Limit to requested count
                x, y = pos
                
                # Create and add the item at the specified position
                new_item = item_type(x, y)
                block.add_entity(new_item)
                items_added += 1
                print(f"DEBUG: Added {new_item.name} to block at specified position ({x}, {y})")
                
            return items_added
        
        # Random placement if no specific positions were provided
        while items_added < count and attempts < 100:
            x = random.randint(80, SCREEN_WIDTH - 80)
            y = random.randint(80, SCREEN_HEIGHT - 80)
            
            new_item_rect = pygame.Rect(x, y, 32, 32)
            
            # Check if in safe area
            if safe_area and safe_area.colliderect(new_item_rect):
                attempts += 1
                continue
                
            # Check collision with existing entities
            collision = False
            for entity in existing_entities:
                entity_rect = entity.get_rect()
                if new_item_rect.colliderect(entity_rect) or \
                   pygame.math.Vector2(new_item_rect.center).distance_to(
                       pygame.math.Vector2(entity_rect.center)) < min_distance_between_items:
                    collision = True
                    break
            
            if not collision:
                new_item = item_type(x, y)
                block.add_entity(new_item)
                existing_entities.append(new_item)
                items_added += 1
                print(f"DEBUG: Added {new_item.name} to block at random position ({x}, {y})")
            
            attempts += 1
            
        return items_added
    
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
    
    def get_or_generate_block(self, x_coord, y_coord):
        """Get or generate a block without changing the current block"""
        block_key = (x_coord, y_coord)
        
        if block_key not in self.blocks:
            # Create a new block
            block_id = f"block_{self.next_block_id}"
            self.next_block_id += 1
            
            print(f"DEBUG: Creating block at ({x_coord}, {y_coord}) with ID {block_id}")
            new_block = WorldBlock(block_id, x_coord, y_coord)
            self.blocks[block_key] = new_block
            return new_block
        
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
                self._populate_block(new_block, entry_point, new_x, new_y)
            
            # Update current block
            self.current_block_coords = new_block_coords
            
            # ADDED: Check if there's grass at the spawn position and find a safe position if needed
            new_player_rect = pygame.Rect(new_player_pos[0], new_player_pos[1], player.width, player.height)
            safe_position = self._find_safe_spawn_position(new_block, new_player_rect, direction)
            
            # Move player to safe position
            player.x, player.y = safe_position
            
            player.set_current_block(new_x, new_y)
            
            # Log difficulty level and points of the new block
            difficulty = self._get_difficulty_level(new_x, new_y)
            difficulty_points = self._calculate_difficulty_points(new_x, new_y)
            print(f"DEBUG: Moved to block ({new_x}, {new_y}) - Difficulty level: {difficulty}, Points: {difficulty_points}")
            
            return True, direction
        
        return False, None

    def _find_safe_spawn_position(self, block, player_rect, direction):
        """Find a safe position for the player to spawn without overlapping grass or other obstacles"""
        # Get all entities in the block
        entities = block.get_entities()
        
        # Check if the initial position is safe
        initial_x, initial_y = player_rect.x, player_rect.y
        
        # Check for collisions with any entity in the target position
        collision = False
        for entity in entities:
            if isinstance(entity, Grass) and player_rect.colliderect(entity.get_rect()):
                collision = True
                break
        
        # If no collision, return the initial position
        if not collision:
            return initial_x, initial_y
        
        # If there's a collision, find a nearby safe position
        # Try moving along the edge based on the entry direction
        offset_distance = 40  # pixels to move for each attempt
        max_attempts = 10
        
        for i in range(1, max_attempts + 1):
            test_positions = []
            
            # Generate test positions based on entry direction
            if direction == "left" or direction == "right":
                # Try positions along the vertical edge
                test_positions.append((initial_x, initial_y + (i * offset_distance)))
                test_positions.append((initial_x, initial_y - (i * offset_distance)))
            else:  # up or down
                # Try positions along the horizontal edge
                test_positions.append((initial_x + (i * offset_distance), initial_y))
                test_positions.append((initial_x - (i * offset_distance), initial_y))
            
            # Check each test position
            for test_x, test_y in test_positions:
                # Ensure position is within screen bounds
                if test_x < 0 or test_x > SCREEN_WIDTH - player_rect.width or \
                test_y < 0 or test_y > SCREEN_HEIGHT - player_rect.height:
                    continue
                    
                # Create test rect
                test_rect = pygame.Rect(test_x, test_y, player_rect.width, player_rect.height)
                
                # Check for collisions
                collision = False
                for entity in entities:
                    if isinstance(entity, Grass) and test_rect.colliderect(entity.get_rect()):
                        collision = True
                        break
                
                # If no collision, return this position
                if not collision:
                    print(f"DEBUG: Found safe spawn position at ({test_x}, {test_y})")
                    return test_x, test_y
        
        # If we couldn't find a safe position, try to remove grass at the initial position
        for entity in entities[:]:  # Create a copy of the list to safely modify it during iteration
            if isinstance(entity, Grass) and player_rect.colliderect(entity.get_rect()):
                block.remove_entity(entity)
                print(f"DEBUG: Removed grass at player spawn position ({initial_x}, {initial_y})")
                break
        
        print(f"DEBUG: Using initial spawn position after removing grass: ({initial_x}, {initial_y})")
        return initial_x, initial_y

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
        difficulty_points = self._calculate_difficulty_points(x, y)
        return f"Block ({x}, {y}) - Difficulty: {difficulty}, Points: {difficulty_points}"