import json
import os
import datetime
from collections import defaultdict

class SaveManager:
    def __init__(self, game_world, player):
        self.game_world = game_world
        self.player = player
        self.save_directory = "saves"
        
        # Ensure save directory exists
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def generate_save_filename(self):
        """Generate a filename based on current date and time"""
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}.sav"
    
    def save_game(self):
        """Save the current game state to a file"""
        save_data = {}
        
        # Save player data
        save_data["player"] = self.save_player_data()
        
        # Save world data
        save_data["world"] = self.save_world_data()
        
        # Write to file
        filename = self.generate_save_filename()
        filepath = os.path.join(self.save_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"Game saved to {filepath}")
        return filepath
    
    def load_game(self, filepath):
        """Load a game state from a file"""
        if not os.path.exists(filepath):
            print(f"Save file not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Load player data
            self.load_player_data(save_data.get("player", {}))
            
            # Load world data
            self.load_world_data(save_data.get("world", {}))
            
            print(f"Game loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading save file: {e}")
            return False
    
    def save_player_data(self):
        """Extract player data to a dictionary"""
        player_data = {
            "position": {
                "x": self.player.x,
                "y": self.player.y
            },
            "facing": self.player.facing,
            "attributes": {
                "level": self.player.attributes.level,
                "xp": self.player.attributes.xp,
                "str": self.player.attributes.str,
                "con": self.player.attributes.con,
                "dex": self.player.attributes.dex,
                "int": self.player.attributes.int,
                "max_health": self.player.attributes.max_health,
                "current_health": self.player.attributes.current_health,
                "max_mana": self.player.attributes.max_mana,
                "current_mana": self.player.attributes.current_mana,
                "stat_points": self.player.attributes.stat_points,
                "skill_points": self.player.attributes.skill_points,
                "found_ancient_scroll": self.player.attributes.found_ancient_scroll,
                "found_dragon_heart": self.player.attributes.found_dragon_heart
            },
            "skill_tree": self.save_skill_tree_data(),
            "inventory": self.save_inventory_data()
        }
        return player_data
    
    def save_skill_tree_data(self):
        """Extract skill tree data to a dictionary"""
        skill_data = {}
        for skill_id, skill in self.player.skill_tree.skills.items():
            skill_data[skill_id] = {
                "unlocked": skill.unlocked
            }
        return skill_data
    
    def save_inventory_data(self):
        """Extract inventory data to a dictionary"""
        inventory_data = {
            "items": []
        }
        
        for item in self.player.inventory.items:
            count = 1
            if hasattr(item, 'stackable') and item.stackable and item.name in self.player.inventory.item_counts:
                count = self.player.inventory.item_counts[item.name]
            
            item_data = {
                "type": type(item).__name__,
                "name": item.name,
                "count": count
            }
            inventory_data["items"].append(item_data)
        
        return inventory_data
    
    def save_world_data(self):
        """Extract world data to a dictionary"""
        world_data = {
            "current_block_coords": self.game_world.current_block_coords,
            "next_block_id": self.game_world.next_block_id,
            "blocks": {}
        }
        
        # Save each block's data
        for coords, block in self.game_world.blocks.items():
            block_x, block_y = coords
            
            block_data = {
                "id": block.block_id,
                "x_coord": block_x,
                "y_coord": block_y,
                "visited": block.visited,
                "entities": []
            }
            
            # Save entities in this block
            for entity in block.entities:
                # Skip player entity
                if entity is self.player:
                    continue
                
                entity_type = type(entity).__name__
                
                # Base entity data
                entity_data = {
                    "type": entity_type,
                    "x": entity.x,
                    "y": entity.y
                }
                
                # Add enemy-specific data
                if hasattr(entity, 'enemy_type') and hasattr(entity, 'level'):
                    entity_data["enemy_type"] = entity.enemy_type
                    entity_data["level"] = entity.level
                    if hasattr(entity, 'health'):
                        entity_data["health"] = entity.health
                    if hasattr(entity, 'max_health'):
                        entity_data["max_health"] = entity.max_health
                
                # Add item-specific data
                if hasattr(entity, 'name'):
                    entity_data["name"] = entity.name
                    if hasattr(entity, 'description'):
                        entity_data["description"] = entity.description
                
                block_data["entities"].append(entity_data)
            
            world_data["blocks"][f"{block_x},{block_y}"] = block_data
        
        return world_data
    
    def load_player_data(self, player_data):
        """Load player data from a dictionary"""
        # Load position
        position = player_data.get("position", {})
        self.player.x = position.get("x", self.player.x)
        self.player.y = position.get("y", self.player.y)
        
        # Load facing direction
        if "facing" in player_data:
            self.player.facing = player_data["facing"]
        
        # Load attributes
        attributes = player_data.get("attributes", {})
        self.player.attributes.level = attributes.get("level", self.player.attributes.level)
        self.player.attributes.xp = attributes.get("xp", self.player.attributes.xp)
        self.player.attributes.str = attributes.get("str", self.player.attributes.str)
        self.player.attributes.con = attributes.get("con", self.player.attributes.con)
        self.player.attributes.dex = attributes.get("dex", self.player.attributes.dex)
        self.player.attributes.int = attributes.get("int", self.player.attributes.int)
        self.player.attributes.max_health = attributes.get("max_health", self.player.attributes.max_health)
        self.player.attributes.current_health = attributes.get("current_health", self.player.attributes.current_health)
        self.player.attributes.max_mana = attributes.get("max_mana", self.player.attributes.max_mana)
        self.player.attributes.current_mana = attributes.get("current_mana", self.player.attributes.current_mana)
        self.player.attributes.stat_points = attributes.get("stat_points", self.player.attributes.stat_points)
        self.player.attributes.skill_points = attributes.get("skill_points", self.player.attributes.skill_points)
        self.player.attributes.found_ancient_scroll = attributes.get("found_ancient_scroll", self.player.attributes.found_ancient_scroll)
        self.player.attributes.found_dragon_heart = attributes.get("found_dragon_heart", self.player.attributes.found_dragon_heart)
        
        # Update player speed if dexterity has changed
        self.player.base_speed = 3 + (self.player.attributes.dex * 0.08)
        self.player.speed = self.player.base_speed
        
        # Load skill tree
        self.load_skill_tree_data(player_data.get("skill_tree", {}))
        
        # Load inventory
        self.load_inventory_data(player_data.get("inventory", {}))
    
    def load_skill_tree_data(self, skill_data):
        """Load skill tree data from a dictionary"""
        for skill_id, skill_info in skill_data.items():
            if skill_id in self.player.skill_tree.skills:
                self.player.skill_tree.skills[skill_id].unlocked = skill_info.get("unlocked", False)
                
                # Apply skill effects if unlocked
                if skill_info.get("unlocked", False):
                    skill = self.player.skill_tree.skills[skill_id]
                    if skill_id == "dash":
                        self.player.attributes.can_dash = True
                    elif skill_id == "extended_sword":
                        self.player.attributes.sword_length = int(self.player.attributes.base_sword_length * 1.5)
                    elif skill_id == "blink":
                        self.player.attributes.can_blink = True
    
    def load_inventory_data(self, inventory_data):
        """Load inventory data from a dictionary"""
        # Clear current inventory
        self.player.inventory.clear()
        
        # Load items
        for item_data in inventory_data.get("items", []):
            item_type = item_data.get("type")
            item_name = item_data.get("name")
            item_count = item_data.get("count", 1)
            
            # Create and add the item
            # This will require importing all item classes
            from items.health_potion import HealthPotion
            from items.ancient_scroll import AncientScroll
            from items.dragon_heart import DragonHeart
            
            item = None
            if item_type == "HealthPotion":
                item = HealthPotion(0, 0)  # Position doesn't matter for inventory items
            elif item_type == "AncientScroll":
                item = AncientScroll(0, 0)
            elif item_type == "DragonHeart":
                item = DragonHeart(0, 0)
            
            if item:
                # Add the item to inventory
                self.player.inventory.add_item(item)
                
                # Adjust count for stackable items
                if hasattr(item, 'stackable') and item.stackable and item_count > 1:
                    self.player.inventory.item_counts[item.name] = item_count
    
    def load_world_data(self, world_data):
        """Load world data from a dictionary"""
        # Clear current world blocks
        self.game_world.blocks = {}
        
        # Load world metadata
        self.game_world.next_block_id = world_data.get("next_block_id", 0)
        self.game_world.current_block_coords = tuple(world_data.get("current_block_coords", (0, 0)))
        
        # Load blocks
        from entities.grass import Grass
        from entities.rock import Rock
        from entities.enemy.skeleton import Skeleton
        from entities.enemy.slime import Slime
        from entities.bonfire import Bonfire
        from items.health_potion import HealthPotion
        from items.ancient_scroll import AncientScroll
        from items.dragon_heart import DragonHeart
        
        for coords_str, block_data in world_data.get("blocks", {}).items():
            x, y = map(int, coords_str.split(","))
            
            # Create a new block
            block_id = block_data.get("id", f"block_{self.game_world.next_block_id}")
            new_block = self.game_world.get_or_generate_block(x, y)
            new_block.block_id = block_id
            
            # Clear any auto-generated entities (the block might have been auto-populated)
            new_block.entities = []
            
            # Set visited status
            if block_data.get("visited", False):
                new_block.mark_as_visited()
            
            # Load entities
            entity_mapping = {
                "Grass": Grass,
                "Rock": Rock,
                "Skeleton": Skeleton,
                "Slime": Slime,
                "Bonfire": Bonfire,
                "HealthPotion": HealthPotion,
                "AncientScroll": AncientScroll,
                "DragonHeart": DragonHeart
            }
            
            for entity_data in block_data.get("entities", []):
                entity_type = entity_data.get("type")
                entity_x = entity_data.get("x")
                entity_y = entity_data.get("y")
                
                if entity_type not in entity_mapping:
                    print(f"Unknown entity type: {entity_type}")
                    continue
                
                # Create the entity
                entity_class = entity_mapping[entity_type]
                entity = entity_class(entity_x, entity_y)
                
                # Set entity-specific attributes
                if entity_type in ["Skeleton", "Slime"]:
                    if "enemy_type" in entity_data:
                        entity.enemy_type = entity_data.get("enemy_type")
                    if "level" in entity_data:
                        # Need to re-calculate difficulty factor
                        difficulty_factor = self.game_world._get_difficulty_factor(x, y)
                        entity.set_level(entity_data.get("level"), difficulty_factor)
                    if "health" in entity_data and "max_health" in entity_data:
                        entity.health = entity_data.get("health")
                        entity.max_health = entity_data.get("max_health")
                
                # Set bonfire-specific attributes
                if entity_type == "Bonfire":
                    # Set block coordinates so the bonfire knows where it is
                    entity.set_block_coordinates(x, y)
                
                # Add the entity to the block
                new_block.add_entity(entity)