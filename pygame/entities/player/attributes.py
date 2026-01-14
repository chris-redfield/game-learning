import math
import random

# XP Tables for different progression rates
XP_TABLE_1_5 = [10]  # Base XP needed for level 1 -> 2
XP_TABLE_1_3 = [10]  # Initialize with just the base value, will be populated during initialization
XP_TABLE_1_2 = [10]  # Initialize with just the base value, will be populated during initialization

# Generate all XP tables up to level 50
for i in range(49):  # 49 more levels for a total of 50
    XP_TABLE_1_5.append(int(XP_TABLE_1_5[-1] * 1.5))
    XP_TABLE_1_3.append(int(XP_TABLE_1_3[-1] * 1.3))
    XP_TABLE_1_2.append(int(XP_TABLE_1_2[-1] * 1.2))

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
        self.max_health = 3 + (self.con * 3)  # Base health + CON bonus
        self.current_health = self.max_health
        self.max_mana = 1 + (self.int * 2) # Base mana + INT bonus
        self.current_mana = self.max_mana
        self.stat_points = 0  # Available points to spend
        self.skill_points = 0  # Available skill points for the skill tree

        # XP system with tables
        self.xp = 0
        self.current_xp_table = "1.5"  # Default table uses 1.5 multiplier
        self.xp_table_1_5 = XP_TABLE_1_5  # Original progression
        self.xp_table_1_3 = XP_TABLE_1_3  # Medium progression
        self.xp_table_1_2 = XP_TABLE_1_2  # Fast progression
        
        # Level system
        self.level = 1
        self.max_level = 50  # Increased from 4 to 50
        # XP table progression items
        self.found_ancient_scroll = False  # When found, enable 1.3 progression
        self.found_dragon_heart = False   # When found, enable 1.2 progression
        self.xp_needed = self.get_xp_needed()  # Get XP needed for next level

        # Level 2: Sprint (temporary speed boost)
        self.can_sprint = False  # Unlocked at level 2
        self.sprint_duration = 1500  # 1.5 seconds in milliseconds
        self.sprint_cooldown = 3000  # 3 seconds in milliseconds
        self.sprint_timer = 0  # For cooldown tracking
        self.sprint_end_time = 0  # For duration tracking
        self.sprinting = False

        # Level 3: Dash (quick burst movement)
        self.can_dash = False  # Unlocked at level 3
        self.dash_duration = 150  # 150ms burst
        self.dash_cooldown = 2700  # 2.7s cooldown (can be reduced by skills)
        self.dash_speed = 5  # Multiplier for base speed
        self.dash_timer = 0  # For cooldown tracking
        self.dash_end_time = 0  # For duration tracking
        self.dashing = False
        self.dash_direction = (0, 0)

        # Level 4: Blink (teleport)
        self.can_blink = False  # Unlocked at level 4
        self.blink_distance = 80
        self.blink_cooldown = 2000  # in milliseconds
        self.blink_timer = 0

        # Default sword length (will be increased at level 3)
        self.sword_length = 24
        self.base_sword_length = 24  # Store the base value for reference

        # Initialize any abilities the player should have at level 1
        self.initialize_abilities()
    
    def get_xp_needed(self):
        """Get XP needed for next level based on current level and XP table"""
        if self.level >= self.max_level:
            return 0  # Max level reached
            
        # Get appropriate XP table based on which artifacts have been found
        if self.found_dragon_heart:
            return self.xp_table_1_2[self.level - 1]
        elif self.found_ancient_scroll:
            return self.xp_table_1_3[self.level - 1]
        else:
            return self.xp_table_1_5[self.level - 1]
            
    def find_ancient_scroll(self):
        """Player has found the Ancient Scroll, enabling faster leveling"""
        if not self.found_ancient_scroll:
            self.found_ancient_scroll = True
            self.current_xp_table = "1.3"
            self.xp_needed = self.get_xp_needed()
            print("You found an Ancient Scroll of Knowledge! Your XP gains are now more efficient.")
            return True
        return False
        
    def find_dragon_heart(self):
        """Player has found the Dragon Heart, enabling fastest leveling"""
        if not self.found_dragon_heart:
            self.found_dragon_heart = True
            self.current_xp_table = "1.2"
            self.xp_needed = self.get_xp_needed()
            print("You found a Dragon Heart! Your XP gains are now greatly amplified!")
            return True
        return False
    
    def initialize_abilities(self):
        """Initialize default abilities based on starting level"""
        # This is now handled by the skill tree system
        # The basic sword is always available
        pass
    
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
            self.max_health = 3 + (self.con * 3)  # Using consistent formula with init
            # Increase current health by the difference
            self.current_health += (self.max_health - old_max_health)
            self.stat_points -= 1
            return True
        elif stat_name == "dex":
            self.dex += 1
            # Dexterity increases movement speed slightly
            self.player.base_speed = 3 + (self.dex * 0.08)
            self.player.speed = self.player.base_speed  # Update current speed
            self.stat_points -= 1
            return True
        elif stat_name == "int":
            self.int += 1
            # Intelligence increases mana
            old_max_mana = self.max_mana
            self.max_mana = 1 + (self.int * 2)
            # Increase current mana by the difference
            self.current_mana += (self.max_mana - old_max_mana)
            self.stat_points -= 1
            return True
            
        return False

    def level_up(self):
        """Increase player level and unlock abilities"""
        if self.level < self.max_level:
            old_level = self.level
            self.level += 1
            self.stat_points += 1  # Gain a stat point on level up
            
            # Award skill points every 3 levels starting at level 4
            if self.level >= 4 and (self.level - 4) % 3 == 0:
                self.skill_points += 1
                print(f"Gained a skill point! Total skill points: {self.skill_points}")
            
            # Log level up
            print(f"Level up! Player is now level {self.level} and gained a stat point!")
            
            # No longer automatically unlock abilities - this is now handled by the skill tree
            
            # Update XP needed for next level
            self.xp_needed = self.get_xp_needed()
            
            # Apply any level milestone bonuses
            if self.level == 10:
                self.stat_points += 1  # Extra stat point at level 10
                print("Reached level 10! Gained an additional stat point!")
            elif self.level == 20:
                self.stat_points += 2  # Extra stat points at level 20
                print("Reached level 20! Gained two additional stat points!")
            elif self.level == 30:
                self.stat_points += 3  # Extra stat points at level 30
                print("Reached level 30! Gained three additional stat points!")
            elif self.level == 40:
                self.stat_points += 4  # Extra stat points at level 40
                print("Reached level 40! Gained four additional stat points!")
            elif self.level == 50:
                self.stat_points += 5  # Extra stat points at max level
                print("Reached level 50! Gained five additional stat points!")
            
            return True
        else:
            print(f"Already at max level ({self.max_level})! No more levels available.")
            return False
    
    def gain_xp(self, amount):
        """Add XP to the player and check for level up"""
        # Don't add XP if already at max level
        if self.level >= self.max_level:
            return False
            
        self.xp += amount
        
        # Check for level up
        if self.xp >= self.xp_needed:
            # Store excess XP
            excess_xp = self.xp - self.xp_needed
            
            # Perform level up
            self.level_up()
            
            # Apply excess XP toward next level
            self.xp = excess_xp
            
            # Check if we can level up again with the excess XP
            return self.gain_xp(0)  # Pass 0 to just check for level up, don't add more XP
            
        # Display message for current progress
        print(f"XP: {self.xp}/{self.xp_needed} ({(self.xp/self.xp_needed*100):.1f}%)")
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
        
        # Display XP info with progress percentage
        if self.level < self.max_level:
            xp_percentage = (self.xp / self.xp_needed * 100) if self.xp_needed > 0 else 100
            xp_text = font.render(f"XP: {self.xp}/{self.xp_needed} ({xp_percentage:.1f}%)", True, (255, 215, 0))
        else:
            xp_text = font.render(f"MAX LEVEL", True, (255, 215, 0))
        surface.blit(xp_text, (x, y + 20))
        
        # Display XP table info
        xp_table_text = font.render(f"XP Table: {self.current_xp_table}x", True, (200, 200, 200))
        surface.blit(xp_table_text, (x, y + 40))
        
        # Display stats
        stats_text = font.render(f"STR:{self.str} CON:{self.con} DEX:{self.dex} INT:{self.int}", True, (200, 255, 200))
        surface.blit(stats_text, (x, y + 60))
        
        # Show available stat points
        if self.stat_points > 0:
            points_text = font.render(f"Stat Points: {self.stat_points}", True, (255, 255, 100))
            surface.blit(points_text, (x, y + 80))
            
        # Show available skill points
        if self.skill_points > 0:
            skill_points_text = font.render(f"Skill Points: {self.skill_points}", True, (255, 255, 100))
            surface.blit(skill_points_text, (x, y + 100))
            abilities_y = y + 125
        else:
            abilities_y = y + 105
        
        # Display ability info based on skill tree unlocks
        # Sprint ability
        if self.player.skill_tree.is_skill_unlocked("sprint"):
            if self.sprinting:
                sprint_status = "ACTIVE"
                color = (0, 255, 0)  # Green when active
            elif self.sprint_timer == 0:
                sprint_status = "Ready"
                color = (255, 255, 255)  # White when ready
            else:
                sprint_status = "Cooling Down"
                color = (255, 165, 0)  # Orange when on cooldown

            sprint_text = font.render(f"Sprint: {sprint_status}", True, color)
            surface.blit(sprint_text, (x, abilities_y))
            abilities_y += 25

        # Dash ability
        if self.player.skill_tree.is_skill_unlocked("dash"):
            if self.dashing:
                dash_status = "ACTIVE"
                color = (0, 255, 255)  # Cyan when active
            elif self.dash_timer == 0:
                dash_status = "Ready"
                color = (255, 255, 255)  # White when ready
            else:
                dash_status = "Cooling Down"
                color = (255, 165, 0)  # Orange when on cooldown

            dash_text = font.render(f"Dash: {dash_status}", True, color)
            surface.blit(dash_text, (x, abilities_y))
            abilities_y += 25

        # Extended Sword ability
        if self.player.skill_tree.is_skill_unlocked("extended_sword"):
            sword_text = font.render(f"Extended Sword: Active", True, (255, 255, 255))
            surface.blit(sword_text, (x, abilities_y))
            abilities_y += 25
            
        # Blink ability
        if self.player.skill_tree.is_skill_unlocked("blink"):
            blink_status = "Ready" if self.blink_timer == 0 else "Cooling Down"
            blink_color = (255, 255, 255) if self.blink_timer == 0 else (255, 165, 0)
            blink_text = font.render(f"Blink: {blink_status}", True, blink_color)
            surface.blit(blink_text, (x, abilities_y))
            abilities_y += 25
            
        # Skill/stat points available indicator
        if self.stat_points > 0 or self.skill_points > 0:
            points_text = font.render(f"Press ENTER to open menu", True, (255, 255, 100))
            surface.blit(points_text, (x, abilities_y))
            abilities_y += 25