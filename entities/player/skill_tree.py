class Skill:
    """Represents a skill in the skill tree"""
    def __init__(self, id, name, description, level_required=1, parent=None, implemented=True):
        self.id = id
        self.name = name
        self.description = description
        self.level_required = level_required  # Minimum level required
        self.parent = parent  # Parent skill ID if this is a dependent skill
        self.unlocked = False
        self.implemented = implemented  # Whether the skill is implemented in the game
        
    def can_unlock(self, player):
        """Check if the skill can be unlocked"""
        # Must have required level
        if player.attributes.level < self.level_required:
            return False
            
        # If it has a parent, the parent must be unlocked first
        if self.parent and not player.skill_tree.is_skill_unlocked(self.parent):
            return False
            
        # Must be implemented
        if not self.implemented:
            return False
            
        return True
        
    def unlock(self, player):
        """Unlock the skill and apply its effects"""
        if not self.can_unlock(player):
            return False
            
        self.unlocked = True
        
        # Apply skill effects
        if self.id == "dash":
            player.attributes.can_dash = True
        elif self.id == "extended_sword":
            player.attributes.sword_length = int(player.attributes.base_sword_length * 1.5)
        elif self.id == "blink":
            player.attributes.can_blink = True
        elif self.id == "firebolt":
            # No additional attributes needed as we check for this skill directly
            pass
            
        return True

class SkillTree:
    """Manages the skill tree and skill point system"""
    def __init__(self, player):
        self.player = player
        self.skills = {}
        self.initialize_skills()
        
    def initialize_skills(self):
        """Initialize the skill tree with all available skills"""
        # Mind branch
        self.skills["heal"] = Skill("heal", "Heal", "Restore health", level_required=4, implemented=False)
        self.skills["firebolt"] = Skill("firebolt", "Firebolt", "Cast a firebolt", level_required=4, implemented=True)
        self.skills["bless"] = Skill("bless", "Bless", "Temporary stat boost", level_required=7, parent="heal", implemented=False)
        self.skills["fireball"] = Skill("fireball", "Fireball", "More powerful fireball", level_required=7, parent="firebolt", implemented=False)
        
        # Body branch
        self.skills["dash"] = Skill("dash", "Dash", "Temporary speed boost (SHIFT/Button 4)", level_required=2, implemented=True)
        self.skills["blink"] = Skill("blink", "Blink", "Short-range teleport (B/Button 1)", level_required=4, implemented=True)
        self.skills["dash_speed"] = Skill("dash_speed", "Increased Dash Speed", "Dash moves faster", level_required=7, parent="dash", implemented=False)
        self.skills["dash_cooldown"] = Skill("dash_cooldown", "Reduced Dash Cooldown", "Use dash more often", level_required=10, parent="dash_speed", implemented=False)
        self.skills["blink_extend1"] = Skill("blink_extend1", "Extended Blink", "Blink farther", level_required=7, parent="blink", implemented=False)
        self.skills["blink_extend2"] = Skill("blink_extend2", "Extended Blink II", "Blink even farther", level_required=10, parent="blink_extend1", implemented=False)
        self.skills["ghost_blink"] = Skill("ghost_blink", "Ghost Blink", "Blink through obstacles", level_required=13, parent="blink_extend2", implemented=False)
        
        # Magic Sword branch
        self.skills["basic_sword"] = Skill("basic_sword", "Basic Sword", "Regular sword swing", level_required=1, implemented=True)
        self.skills["throw_sword"] = Skill("throw_sword", "Throw Sword", "Throw your sword", level_required=7, parent="basic_sword", implemented=False)
        self.skills["extended_sword"] = Skill("extended_sword", "Extended Sword", "Increased sword reach", level_required=3, parent="basic_sword", implemented=True)
        self.skills["extended_sword2"] = Skill("extended_sword2", "Extended Sword II", "Further increased sword reach", level_required=10, parent="extended_sword", implemented=False)
        self.skills["extended_sword3"] = Skill("extended_sword3", "Extended Sword III", "Maximum sword reach", level_required=13, parent="extended_sword2", implemented=False)
        self.skills["teleport_sword"] = Skill("teleport_sword", "Teleport Sword", "Teleport to sword location", level_required=16, parent="throw_sword", implemented=False)
        
        # Unlocks that should be present at game start
        self.skills["basic_sword"].unlocked = True
        
        # Check if any skills should be unlocked based on current level/state
        # This ensures existing save games maintain their abilities
        if self.player.attributes.can_dash:
            self.skills["dash"].unlocked = True
        
        if self.player.attributes.sword_length > self.player.attributes.base_sword_length:
            self.skills["extended_sword"].unlocked = True
            
        if self.player.attributes.can_blink:
            self.skills["blink"].unlocked = True
            
    def is_skill_unlocked(self, skill_id):
        """Check if a skill is unlocked"""
        if skill_id in self.skills:
            return self.skills[skill_id].unlocked
        return False
        
    def unlock_skill(self, skill_id):
        """Try to unlock a skill"""
        if skill_id not in self.skills:
            return False
            
        skill = self.skills[skill_id]
        
        # Check if player has skill points and skill is not already unlocked
        if self.player.attributes.skill_points <= 0 or skill.unlocked:
            return False
            
        # Check if skill can be unlocked
        if not skill.can_unlock(self.player):
            return False
            
        # Use a skill point and unlock the skill
        self.player.attributes.skill_points -= 1
        result = skill.unlock(self.player)
        
        if result:
            print(f"Unlocked skill: {skill.name}")
        
        return result
        
    def get_skills_by_branch(self):
        """Get skills organized by branch for UI display"""
        branches = {
            "mind": [],
            "body": [],
            "magic_sword": []
        }
        
        # Categorize skills
        for skill_id, skill in self.skills.items():
            if skill_id in ["heal", "firebolt", "bless", "fireball"]:
                branches["mind"].append(skill)
            elif skill_id in ["dash", "blink", "dash_speed", "dash_cooldown", "blink_extend1", "blink_extend2", "ghost_blink"]:
                branches["body"].append(skill)
            else:
                branches["magic_sword"].append(skill)
                
        return branches