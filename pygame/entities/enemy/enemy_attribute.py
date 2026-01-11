import random
import math

class EnemyAttributes:
    """Handles enemy attributes, level-based scaling and derived stats"""
    def __init__(self, enemy, level=1, enemy_type="normal", manual_attributes=None, use_auto_distribution=True):
        self.enemy = enemy
        
        # Level system (1-10)
        self.level = min(max(1, level), 10)  # Clamp between 1-10
        
        # Enemy type influences attribute distribution
        self.enemy_type = enemy_type  # "normal", "magic", "tank", "fast", etc.
        
        # Base attributes
        self.str = 1  # Strength - affects attack power
        self.con = 1  # Constitution - affects health
        self.dex = 1  # Dexterity - affects speed
        self.int = 0  # Intelligence - affects mana and magic abilities (if applicable)
        
        # Flag to control auto distribution
        self.use_auto_distribution = use_auto_distribution
        
        # Derived stats (will be calculated)
        self.max_health = 3
        self.current_health = 3
        self.attack_power = 1
        self.defense = 0
        self.speed_multiplier = 1.0
        self.max_mana = 0
        self.current_mana = 0
        self.knockback_resistance = 0
        
        # Apply manual attributes if provided
        if manual_attributes:
            self.set_manual_attributes(manual_attributes)
        # Otherwise, initialize attributes based on level and type
        elif use_auto_distribution:
            self.distribute_attributes()
        
        # Calculate derived stats
        self.calculate_stats()
    
    def distribute_attributes(self):
        """Distribute attribute points based on level and enemy type"""
        # Base attribute points = level + 2
        attr_points = self.level + 2
        
        # Distribution depends on enemy type
        if self.enemy_type == "magic":
            # Magic enemies focus on INT and have some CON
            self.str += math.floor(attr_points * 0.2)
            self.con += math.floor(attr_points * 0.3)
            self.dex += math.floor(attr_points * 0.1)
            self.int += math.floor(attr_points * 0.4)
            
        elif self.enemy_type == "tank":
            # Tank enemies focus on CON and STR
            self.str += math.floor(attr_points * 0.3)
            self.con += math.floor(attr_points * 0.6)
            self.dex += math.floor(attr_points * 0.1)
            
        elif self.enemy_type == "fast":
            # Fast enemies focus on DEX and have some STR
            self.str += math.floor(attr_points * 0.2)
            self.con += math.floor(attr_points * 0.1)
            self.dex += math.floor(attr_points * 0.7)
            
        elif self.enemy_type == "brute":
            # Brute enemies focus on STR with some CON
            self.str += math.floor(attr_points * 0.7)
            self.con += math.floor(attr_points * 0.2)
            self.dex += math.floor(attr_points * 0.1)
            
        else:
            # Normal enemies have balanced attributes
            remaining = attr_points
            while remaining > 0:
                # Randomly assign attributes with some bias
                # This creates some variety in "normal" enemies
                rand = random.random()
                if rand < 0.4:
                    self.str += 1
                elif rand < 0.7:
                    self.con += 1
                else:
                    self.dex += 1
                remaining -= 1
    
    def calculate_stats(self):
        """Calculate derived stats based on attributes"""
        # Health calculation
        base_health = 3  # Minimum health
        con_bonus = self.con * 2  # Same as player
        level_bonus = self.level * 0.5
        
        self.max_health = int(base_health + con_bonus + level_bonus)
        self.current_health = self.max_health
        
        # Attack power calculation
        base_attack = 1
        str_bonus = self.str * 0.5  # Similar to player
        level_bonus = self.level * 0.2
        
        self.attack_power = max(1, int(base_attack + str_bonus + level_bonus))
        
        # Speed calculation
        base_speed = getattr(self.enemy, 'speed', 1.0)
        dex_bonus = self.dex * 0.08  # 5% per DEX point
        
        self.speed_multiplier = 1.0 + dex_bonus
        
        # Apply new speed to enemy
        self.enemy.speed = base_speed * self.speed_multiplier
        
        # Defense calculation (scales with level)
        base_defense = getattr(self.enemy, 'defense', 0)
        con_bonus = self.con * 0.1  # 0.1 per CON
        level_bonus = self.level * 0.1
        
        self.defense = base_defense + con_bonus + level_bonus
        
        # Knockback resistance based on CON and level
        # Higher CON = harder to knock back
        max_resist = 0.8  # Maximum 80% reduction
        con_resist = self.con * 0.07
        level_resist = self.level * 0.02
        
        self.knockback_resistance = min(max_resist, con_resist + level_resist)
        
        # Mana calculations (if applicable)
        if self.enemy_type == "magic" or getattr(self.enemy, 'has_magic', False):
            base_mana = 1
            int_bonus = self.int
            
            self.max_mana = base_mana + int_bonus
            self.current_mana = self.max_mana
        else:
            self.max_mana = 0
            self.current_mana = 0
    
    def take_damage(self, amount):
        """Calculate damage reduction based on defense"""
        # Defense reduces damage by up to 80% (similar to player)
        defense_factor = 1.0 - min(0.8, (self.defense * 0.1))
        final_damage = max(1, int(amount * defense_factor))  # At least 1 damage
        
        self.current_health -= final_damage
        
        return final_damage
    
    def get_knockback_factor(self):
        """Return knockback resistance factor (0-1)"""
        return self.knockback_resistance
    
    def scale_by_difficulty(self, difficulty_factor):
        """Apply additional scaling based on area difficulty"""
        if difficulty_factor <= 1.0:
            return
        
        # Additional levels based on difficulty
        level_boost = min(5, int((difficulty_factor - 1) * 3))
        self.level = min(10, self.level + level_boost)
        
        # Recalculate with new level
        if self.use_auto_distribution:
            self.distribute_attributes()
        self.calculate_stats()
    
    def get_attack_power(self):
        """Get the current attack power"""
        return self.attack_power
    
    def use_mana(self, amount):
        """Use mana if available"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
    
    def restore_mana(self, amount):
        """Restore mana"""
        self.current_mana = min(self.current_mana + amount, self.max_mana)
    
    def get_info_text(self):
        """Return a string with enemy stats for debugging"""
        info = f"Lvl {self.level} {self.enemy_type}: "
        info += f"STR {self.str}, CON {self.con}, DEX {self.dex}"
        
        if self.int > 0:
            info += f", INT {self.int}"
            
        info += f" | HP: {self.current_health}/{self.max_health}"
        info += f" | ATK: {self.attack_power}, DEF: {self.defense:.1f}"
        
        if self.max_mana > 0:
            info += f" | MP: {self.current_mana}/{self.max_mana}"
            
        return info
        
    def set_manual_attributes(self, attr_dict):
        """
        Manually set attribute values from a dictionary
        
        attr_dict: Dictionary with keys 'str', 'con', 'dex', 'int'
        """
        # Update attributes from dictionary
        if 'str' in attr_dict:
            self.str = attr_dict['str']
        if 'con' in attr_dict:
            self.con = attr_dict['con']
        if 'dex' in attr_dict:
            self.dex = attr_dict['dex']
        if 'int' in attr_dict:
            self.int = attr_dict['int']
        
        # Disable auto-distribution for future updates
        self.use_auto_distribution = False
    
    def set_attribute(self, attr_name, value):
        """
        Set a specific attribute to a given value
        
        attr_name: String ('str', 'con', 'dex', 'int')
        value: Integer value to set
        """
        if attr_name in ['str', 'con', 'dex', 'int']:
            setattr(self, attr_name, value)
            # Disable auto-distribution for future updates
            self.use_auto_distribution = False
            # Recalculate derived stats
            self.calculate_stats()
            return True
        return False
        
    def override_stat(self, stat_name, value):
        """
        Directly override a derived stat
        
        stat_name: String (e.g., 'max_health', 'attack_power', 'defense')
        value: Value to set for the stat
        """
        if hasattr(self, stat_name):
            setattr(self, stat_name, value)
            # If overriding current health or mana, also update current values
            if stat_name == 'max_health':
                self.current_health = value
            elif stat_name == 'max_mana':
                self.current_mana = value
            return True
        return False