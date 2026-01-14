import json
import os
import datetime
import pygame

class SaveManager:
    def __init__(self, game_world, player):
        self.game_world = game_world
        self.player = player
        self.save_directory = "saves"

        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def generate_save_filename(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}.sav"

    def save_game(self):
        filename = self.generate_save_filename()
        filepath = os.path.join(self.save_directory, filename)
        return self.save_game_to(filepath)

    def save_game_to(self, filepath):
        save_data = {
            "player": self.save_player_data(),
            "world": self.save_world_data()
        }

        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"Game saved to {filepath}")
        return filepath

    def load_game(self, filepath):
        if not os.path.exists(filepath):
            print(f"Save file not found: {filepath}")
            return False

        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)

            self.load_player_data(save_data.get("player", {}))
            self.load_world_data(save_data.get("world", {}))

            print(f"Game loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading save file: {e}")
            return False

    def save_player_data(self):
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
        skill_data = {}
        for skill_id, skill in self.player.skill_tree.skills.items():
            skill_data[skill_id] = {
                "unlocked": skill.unlocked
            }
        return skill_data

    def save_inventory_data(self):
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
        world_data = {
            "current_block_coords": self.game_world.current_block_coords,
            "next_block_id": self.game_world.next_block_id,
            "blocks": {}
        }

        for coords, block in self.game_world.blocks.items():
            block_x, block_y = coords

            block_data = {
                "id": block.block_id,
                "x_coord": block_x,
                "y_coord": block_y,
                "visited": block.visited,
                "entities": []
            }

            for entity in block.entities:
                if entity is self.player:
                    continue

                entity_type = type(entity).__name__
                entity_data = {
                    "type": entity_type,
                    "x": entity.x,
                    "y": entity.y
                }

                if hasattr(entity, 'enemy_type'):
                    entity_data["enemy_type"] = entity.enemy_type
                    entity_data["level"] = entity.attributes.level
                    if hasattr(entity, 'health'):
                        entity_data["health"] = entity.health
                    if hasattr(entity.attributes, 'max_health'):
                        entity_data["max_health"] = entity.attributes.max_health

                if hasattr(entity, 'name'):
                    entity_data["name"] = entity.name
                    if hasattr(entity, 'description'):
                        entity_data["description"] = entity.description
                    if hasattr(entity, 'collected'):
                        entity_data["collected"] = entity.collected

                block_data["entities"].append(entity_data)

            world_data["blocks"][f"{block_x},{block_y}"] = block_data

        return world_data

    def load_player_data(self, player_data):
        position = player_data.get("position", {})
        self.player.x = position.get("x", self.player.x)
        self.player.y = position.get("y", self.player.y)

        if "facing" in player_data:
            self.player.facing = player_data["facing"]

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

        # Update base speed based on loaded dexterity
        self.player.base_speed = 3 + (self.player.attributes.dex * 0.08)
        self.player.speed = self.player.base_speed

        # Recalculate XP needed for next level based on loaded level and found items
        self.player.attributes.xp_needed = self.player.attributes.get_xp_needed()

        self.load_skill_tree_data(player_data.get("skill_tree", {}))
        self.load_inventory_data(player_data.get("inventory", {}))

    def load_skill_tree_data(self, skill_data):
        for skill_id, skill_info in skill_data.items():
            if skill_id in self.player.skill_tree.skills:
                self.player.skill_tree.skills[skill_id].unlocked = skill_info.get("unlocked", False)

                if skill_info.get("unlocked", False):
                    skill = self.player.skill_tree.skills[skill_id]
                    if skill_id == "sprint":
                        self.player.attributes.can_sprint = True
                    elif skill_id == "extended_sword":
                        self.player.attributes.sword_length = int(self.player.attributes.base_sword_length * 1.5)
                    elif skill_id == "blink":
                        self.player.attributes.can_blink = True

    def load_inventory_data(self, inventory_data):
        self.player.inventory.clear()

        for item_data in inventory_data.get("items", []):
            item_type = item_data.get("type")
            item_name = item_data.get("name")
            item_count = item_data.get("count", 1)

            from items.health_potion import HealthPotion
            from items.ancient_scroll import AncientScroll
            from items.dragon_heart import DragonHeart

            item = None
            if item_type == "HealthPotion":
                item = HealthPotion(0, 0)
            elif item_type == "AncientScroll":
                item = AncientScroll(0, 0)
            elif item_type == "DragonHeart":
                item = DragonHeart(0, 0)

            if item:
                self.player.inventory.add_item(item)

                if hasattr(item, 'stackable') and item.stackable and item_count > 1:
                    self.player.inventory.item_counts[item.name] = item_count

    def load_world_data(self, world_data):
        self.game_world.blocks = {}
        self.game_world.next_block_id = world_data.get("next_block_id", 0)
        self.game_world.current_block_coords = tuple(world_data.get("current_block_coords", (0, 0)))

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

            block_id = block_data.get("id", f"block_{self.game_world.next_block_id}")
            new_block = self.game_world.get_or_generate_block(x, y)
            new_block.block_id = block_id
            new_block.entities = []

            if block_data.get("visited", False):
                new_block.mark_as_visited()

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

            entity_order = {
                "Bonfire": 1,
                "HealthPotion": 2,
                "AncientScroll": 3,
                "DragonHeart": 4,
                "Grass": 5,
                "Rock": 6,
                "Skeleton": 7,
                "Slime": 8
            }

            sorted_entities = sorted(
                block_data.get("entities", []),
                key=lambda e: entity_order.get(e.get("type", ""), 999)
            )

            loaded_entity_rects = []

            for entity_data in sorted_entities:
                entity_type = entity_data.get("type")
                entity_x = entity_data.get("x")
                entity_y = entity_data.get("y")

                if entity_type not in entity_mapping:
                    print(f"Unknown entity type: {entity_type}")
                    continue

                if entity_type in ["HealthPotion", "AncientScroll", "DragonHeart"]:
                    if entity_data.get("collected", False):
                        continue

                entity_width, entity_height = 32, 32
                if entity_type == "Skeleton":
                    entity_width, entity_height = 48, 52
                elif entity_type == "Slime":
                    entity_width, entity_height = 32, 24

                test_rect = pygame.Rect(entity_x, entity_y, entity_width, entity_height)

                if entity_type == "Rock":
                    if any(test_rect.colliderect(existing) for existing in loaded_entity_rects):
                        continue

                entity_class = entity_mapping[entity_type]
                entity = entity_class(entity_x, entity_y)

                loaded_entity_rects.append(test_rect)

                if entity_type in ["Skeleton", "Slime"]:
                    if "enemy_type" in entity_data:
                        entity.enemy_type = entity_data["enemy_type"]
                    if "level" in entity_data:
                        entity.set_level(entity_data.get("level"), 0)
                        entity.health = entity_data.get("health")
                        entity.attributes.max_health = entity_data.get("max_health")
                        entity.max_health = entity_data.get("max_health")
                        entity.attributes.current_health = entity_data.get("health")

                if entity_type == "Bonfire":
                    entity.set_block_coordinates(x, y)

                if entity_type in ["HealthPotion", "AncientScroll", "DragonHeart"]:
                    if "collected" in entity_data:
                        entity.collected = entity_data.get("collected")

                new_block.add_entity(entity)
