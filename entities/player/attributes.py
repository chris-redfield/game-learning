import math
import random

class PlayerAttributes:
    """Handles player attributes, leveling and XP system"""
    def __init__(self, player):
        self.player = player
        
        # Starting attributes
        self.str = 1  # Strength
        self.con = 1  # Constitution
        self.dex = 1  # Dexterity
        self.int = 1  # Intelligence

        # Health and mana
        self.max_health = 3 + (self.con * 2)  # Base health + CON bonus
        self.current_health = self.max_health
        self.max_mana = 1 + self.int  # Base mana + INT bonus
        self.current_mana = self.max_mana
        self.stat_points = 0  # Available points to spend

        # XP system
        self.xp = 0
        self.xp_needed = 10  # XP needed for first level up
        
        # Level system
        self.level = 1
        self.max_level = 4
        
        # Level 2: Dash (temporary speed boost)
        self.can_dash = False  # Level 2 ability
        self.dash_duration = 1500  # 1.5 seconds in milliseconds
        self.dash_cooldown = 3000  # 3 seconds in milliseconds
        self.dash_timer = 0  # For cooldown tracking
        self.dash_end_time = 0  # For duration tracking
        self.dashing = False
        
        # Level 4: Blink (teleport)
        self.can_blink = False  # Level 4 ability
        self.blink_distance = 80
        self.blink_cooldown = 2000  # in milliseconds
        self.blink_timer = 0
        
        # Default sword length (will be increased at level 3)
        self.sword_length = 24
        self.base_sword_length = 24  # Store the base value for reference
    
    def increase_stat(self, stat_name):
        """Increase a stat if stat points are available"""
        if self.stat_points <= 0:
            return False
            
        if stat_name == "str":
            self.str += 1
            # Strength increases attack power
            self.stat_points -= 1
            return True
        elif stat_name == "con":
            self.con += 1
            # Constitution increases health
            old_max_health = self.max_health
            self.max_health = 3 + (self.con * 2)  # Using consistent formula with init
            # Increase current health by the difference
            self.current_health += (self.max_health - old_max_health)
            self.stat_points -= 1
            return True
        elif stat_name == "dex":
            self.dex += 1
            # Dexterity increases movement speed slightly
            self.player.base_speed = 3 + (self.dex * 0.05)
            self.player.speed = self.player.base_speed  # Update current speed
            self.stat_points -= 1
            return True
        elif stat_name == "int":
            self.int += 1
            # Intelligence increases mana
            old_max_mana = self.max_mana
            self.max_mana = 1 + self.int
            # Increase current mana by the difference
            self.current_mana += (self.max_mana - old_max_mana)
            self.stat_points -= 1
            return True
            
        return False

    def level_up(self):
        """Increase player level and unlock abilities"""
        if self.level < self.max_level:
            self.level += 1
            self.stat_points += 1  # Gain a stat point on level up
            print(f"Level up! Player is now level {self.level} and gained a stat point!")
            
            # Level 2: Unlock dash ability (temporary speed boost)
            if self.level == 2:
                self.can_dash = True
                print("Unlocked dash ability! Press SHIFT for a temporary speed boost.")
            
            # Level 3: Increase sword length by 50%
            elif self.level == 3:
                self.sword_length = int(self.base_sword_length * 1.5)
                print(f"Increased sword length! ({self.base_sword_length} -> {self.sword_length})")
                
            # Level 4: Unlock blink ability (teleport)
            elif self.level == 4:
                self.can_blink = True
                print("Unlocked blink ability! Press B to teleport in the direction you're facing.")
            
            return True
        else:
            print(f"Already at max level ({self.max_level})! No more levels available.")
            return False
    
    def gain_xp(self, amount):
        """Add XP to the player and check for level up"""
        self.xp += amount
        
        # Check for level up
        if self.xp >= self.xp_needed and self.level < self.max_level:
            self.level_up()
            
            # Increase XP requirement for next level (50% more each time)
            self.xp_needed = int(self.xp_needed * 1.5)
            
            # Display message
            print(f"LEVEL UP! Now level {self.level}. Next level at {self.xp_needed} XP")
            return True
        
        return False
    
    def get_attack_power(self):
        """Calculate attack power based on strength"""
        return 1 + int(self.str * 0.5)  # Base attack + STR bonus
        
    def take_damage(self, amount):
        """Calculate damage reduction based on constitution"""
        defense_factor = 1.0 - (self.con * 0.05)  # 5% reduction per CON point
        final_damage = max(1, int(amount * defense_factor))  # Minimum 1 damage
        return final_damage
        
    def heal(self, amount):
        """Heal the player"""
        self.current_health = min(self.current_health + amount, self.max_health)
        
    def use_mana(self, amount):
        """Use mana if available"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
        
    def restore_mana(self, amount):
        """Restore mana"""
        self.current_mana = min(self.current_mana + amount, self.max_mana)

    def render_info(self, surface, font, x, y):
        """Display player level information on screen"""
        level_text = font.render(f"Level: {self.level}/{self.max_level}", True, (255, 255, 255))
        surface.blit(level_text, (x, y))
        
        # Display XP info
        xp_text = font.render(f"XP: {self.xp}/{self.xp_needed}", True, (255, 215, 0))  # Gold text
        surface.blit(xp_text, (x, y + 20))
        
        # Adjust the starting position for abilities
        abilities_y = y + 45
        
        # Display ability info
        # Level 2: Dash
        if self.level >= 2:
            if self.dashing:
                dash_status = "ACTIVE"
                color = (0, 255, 0)  # Green when active
            elif self.dash_timer == 0:
                dash_status = "Ready"
                color = (255, 255, 255)  # White when ready
            else:
                dash_status = "Cooling Down"
                color = (255, 165, 0)  # Orange when on cooldown
                
            dash_text = font.render(f"Dash: {dash_status}", True, color)
            surface.blit(dash_text, (x, abilities_y))
            abilities_y += 25
        
        # Level 3: Extended Sword    
        if self.level >= 3:
            sword_text = font.render(f"Extended Sword: Active", True, (255, 255, 255))
            surface.blit(sword_text, (x, abilities_y))
            abilities_y += 25
            
        # Level 4: Blink
        if self.level >= 4:
            blink_status = "Ready" if self.blink_timer == 0 else "Cooling Down"
            blink_color = (255, 255, 255) if self.blink_timer == 0 else (255, 165, 0)
            blink_text = font.render(f"Blink: {blink_status}", True, blink_color)
            surface.blit(blink_text, (x, abilities_y))