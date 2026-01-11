/**
 * Player - Main player class with movement, animation, and combat
 */
class Player {
    constructor(game, x, y, characterName = 'link') {
        this.game = game;
        this.x = x;
        this.y = y;
        this.width = 35;
        this.height = 41;
        this.speed = 3;
        this.baseSpeed = 3;
        this.characterName = characterName;

        // Direction and movement
        this.facing = 'down';
        this.moving = false;
        this.frame = 0;
        this.animationSpeed = 0.2;
        this.animationCounter = 0;

        // Track dominant direction for diagonal movement
        // The first direction pressed becomes dominant until released
        this.dominantAxis = null; // 'horizontal' or 'vertical'
        this.lastDx = 0;
        this.lastDy = 0;

        // Sword swing states
        this.swinging = false;
        this.swingFrame = 0;
        this.swingAnimationCounter = 0;
        this.swingAnimationSpeed = 0.31;
        this.swingFramesTotal = 5;

        // Damage animation
        this.isTakingDamage = false;
        this.damageAnimationTimer = 0;
        this.damageAnimationDuration = 500;
        this.damageKnockbackDistance = 20;
        this.knockbackDirection = null;
        this.currentKnockback = 0;
        this.invulnerable = false;
        this.invulnerabilityDuration = 1000;
        this.invulnerabilityTimer = 0;
        this.flashInterval = 100;
        this.visible = true;

        // Combat tracking
        this.hitEnemies = new Set();

        // Attributes
        this.attributes = new PlayerAttributes(this);

        // Abilities
        this.dashEndTime = 0;
        this.dashTimer = 0;
        this.dashing = false;
        this.blinkTimer = 0;

        // Skill tree for ability tracking
        this.skillTree = new SkillTree(this);

        // Inventory
        this.inventory = new Inventory(24);

        // Sprites
        this.sprites = null;
        this.sword = null;
        this.loadSprites();

        // Timing
        this.lastUpdateTime = 0;
    }

    loadSprites() {
        const spriteSheet = new SpriteSheet(this.game, this.characterName);
        const result = spriteSheet.loadCharacterSprites(
            this.characterName,
            this.width,
            this.height
        );
        this.sprites = result.sprites;
        this.sword = result.sword;
    }

    update(dt, game) {
        const currentTime = performance.now();
        const timeDelta = currentTime - this.lastUpdateTime;

        // Handle movement animation
        if (this.moving) {
            this.animationCounter += this.animationSpeed;

            const walkKey = this.facing === 'left' ? 'right_walk' : `${this.facing}_walk`;
            const frameCount = this.sprites[walkKey]?.length || 1;

            if (this.animationCounter >= frameCount) {
                this.animationCounter = 0;
            }
            this.frame = Math.floor(this.animationCounter);
        } else {
            this.frame = 0;
            this.animationCounter = 0;
        }

        // Handle sword swing animation
        if (this.swinging) {
            this.swingAnimationCounter += this.swingAnimationSpeed;

            if (this.swingAnimationCounter >= this.swingFramesTotal) {
                this.swinging = false;
                this.swingAnimationCounter = 0;
                this.hitEnemies.clear();
            }
            this.swingFrame = Math.floor(this.swingAnimationCounter);
        }

        // Update dash status
        if (this.dashing && currentTime > this.dashEndTime) {
            this.dashing = false;
            this.speed = this.baseSpeed;
        }

        // Clear dash cooldown
        if (this.dashTimer > 0 && currentTime > this.dashTimer) {
            this.dashTimer = 0;
        }

        // Clear blink cooldown
        if (this.blinkTimer > 0 && currentTime > this.blinkTimer) {
            this.blinkTimer = 0;
        }

        // Handle damage animation and knockback
        if (this.isTakingDamage) {
            this.damageAnimationTimer += timeDelta;

            if (this.damageAnimationTimer < this.damageAnimationDuration) {
                const progress = this.damageAnimationTimer / this.damageAnimationDuration;
                const knockbackFactor = 1 - progress;

                if (this.knockbackDirection) {
                    const moveX = this.knockbackDirection.x * this.currentKnockback * knockbackFactor * 0.5;
                    const moveY = this.knockbackDirection.y * this.currentKnockback * knockbackFactor * 0.5;

                    // Apply knockback (collision check would go here)
                    this.x += moveX;
                    this.y += moveY;
                }
            } else {
                this.isTakingDamage = false;
            }
        }

        // Handle invulnerability flashing
        if (this.invulnerable) {
            this.invulnerabilityTimer += timeDelta;

            this.visible = Math.floor(this.invulnerabilityTimer / this.flashInterval) % 2 === 0;

            if (this.invulnerabilityTimer >= this.invulnerabilityDuration) {
                this.invulnerable = false;
                this.visible = true;
            }
        }

        this.lastUpdateTime = currentTime;
    }

    move(dx, dy, obstacles = []) {
        if (dx !== 0 || dy !== 0) {
            this.moving = true;

            // Determine dominant axis for diagonal movement
            // The first direction pressed becomes dominant
            const wasMovingHorizontal = this.lastDx !== 0;
            const wasMovingVertical = this.lastDy !== 0;
            const nowMovingHorizontal = dx !== 0;
            const nowMovingVertical = dy !== 0;

            // If we just started moving in a new axis, that becomes dominant
            if (nowMovingHorizontal && nowMovingVertical) {
                // Diagonal movement
                if (!wasMovingHorizontal && nowMovingHorizontal) {
                    // Just started horizontal, but was already moving vertical - vertical stays dominant
                    this.dominantAxis = 'vertical';
                } else if (!wasMovingVertical && nowMovingVertical) {
                    // Just started vertical, but was already moving horizontal - horizontal stays dominant
                    this.dominantAxis = 'horizontal';
                }
                // If both were already pressed or neither, keep current dominant
                if (this.dominantAxis === null) {
                    // Default: first press wins, check which has larger magnitude
                    this.dominantAxis = Math.abs(dx) >= Math.abs(dy) ? 'horizontal' : 'vertical';
                }
            } else if (nowMovingHorizontal && !nowMovingVertical) {
                this.dominantAxis = 'horizontal';
            } else if (nowMovingVertical && !nowMovingHorizontal) {
                this.dominantAxis = 'vertical';
            }

            // Set facing direction based on dominant axis
            if (this.dominantAxis === 'horizontal') {
                this.facing = dx > 0 ? 'right' : 'left';
            } else {
                this.facing = dy > 0 ? 'down' : 'up';
            }

            // Store current movement for next frame comparison
            this.lastDx = dx;
            this.lastDy = dy;

            // Simple collision detection
            let canMove = true;
            const testX = this.x + dx;
            const testY = this.y + dy;

            for (const obstacle of obstacles) {
                if (obstacle === this) continue;
                if (this.checkCollision(testX, testY, obstacle)) {
                    canMove = false;
                    break;
                }
            }

            if (canMove) {
                this.x += dx;
                this.y += dy;
            }
        } else {
            this.moving = false;
            // Reset dominant axis when not moving
            this.dominantAxis = null;
            this.lastDx = 0;
            this.lastDy = 0;
        }
    }

    checkCollision(x, y, obstacle) {
        if (!obstacle.getRect) return false;
        const rect = obstacle.getRect();
        return (
            x < rect.x + rect.width &&
            x + this.width > rect.x &&
            y < rect.y + rect.height &&
            y + this.height > rect.y
        );
    }

    getRect() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    startSwing() {
        if (!this.swinging) {
            this.swinging = true;
            this.swingAnimationCounter = 0;
            this.swingFrame = 0;
            this.hitEnemies.clear();
        }
    }

    isSwinging() {
        return this.swinging;
    }

    dash(currentTime) {
        if (this.dashing || currentTime < this.dashTimer) {
            return false;
        }

        this.dashing = true;
        this.speed = this.baseSpeed * 1.5;

        this.dashEndTime = currentTime + this.attributes.dashDuration;
        this.dashTimer = currentTime + this.attributes.dashCooldown + this.attributes.dashDuration;

        return true;
    }

    blink(obstacles, currentTime) {
        if (currentTime < this.blinkTimer) {
            return false;
        }

        let blinkDx = 0;
        let blinkDy = 0;

        switch (this.facing) {
            case 'right': blinkDx = this.attributes.blinkDistance; break;
            case 'left': blinkDx = -this.attributes.blinkDistance; break;
            case 'down': blinkDy = this.attributes.blinkDistance; break;
            case 'up': blinkDy = -this.attributes.blinkDistance; break;
        }

        this.move(blinkDx, blinkDy, obstacles);
        this.blinkTimer = currentTime + this.attributes.blinkCooldown;

        return true;
    }

    takeDamage(amount, attackerX = null, attackerY = null) {
        if (this.isTakingDamage || this.invulnerable) {
            return false;
        }

        const finalDamage = this.attributes.takeDamage(amount);
        this.attributes.currentHealth -= finalDamage;

        if (this.attributes.currentHealth < 0) {
            this.attributes.currentHealth = 0;
        }

        // Calculate knockback direction
        if (attackerX !== null && attackerY !== null) {
            const dirX = (this.x + this.width / 2) - attackerX;
            const dirY = (this.y + this.height / 2) - attackerY;
            const length = Math.max(0.1, Math.sqrt(dirX * dirX + dirY * dirY));
            this.knockbackDirection = { x: dirX / length, y: dirY / length };
        } else {
            // Default knockback based on facing
            const dirs = {
                right: { x: -1, y: 0 },
                left: { x: 1, y: 0 },
                down: { x: 0, y: -1 },
                up: { x: 0, y: 1 }
            };
            this.knockbackDirection = dirs[this.facing] || { x: 0, y: 0 };
        }

        this.isTakingDamage = true;
        this.damageAnimationTimer = 0;
        this.invulnerable = true;
        this.invulnerabilityTimer = 0;

        // Calculate knockback with constitution reduction
        const knockbackReduction = Math.min(0.8, this.attributes.con * 0.1);
        this.currentKnockback = this.damageKnockbackDistance * (1 - knockbackReduction);

        return true;
    }

    heal(amount) {
        this.attributes.heal(amount);
    }

    gainXp(amount) {
        return this.attributes.gainXp(amount);
    }

    getSwordRect() {
        if (!this.swinging) return null;

        // Start from player center
        let centerX = this.x + this.width / 2;
        let centerY = this.y + this.height / 2;

        // Offset the sword rotation center IN FRONT of the player
        const frontOffset = 15; // Distance in front of player
        switch (this.facing) {
            case 'right': centerX += frontOffset; break;
            case 'left': centerX -= frontOffset; break;
            case 'up': centerY -= frontOffset; break;
            case 'down': centerY += frontOffset; break;
        }

        let hitboxSize = 24;
        let baseDistance = 20;

        const lengthScale = this.attributes.swordLength / this.attributes.baseSwordLength;
        let scaledDistance = baseDistance * lengthScale;

        if (lengthScale > 1) {
            hitboxSize = Math.floor(hitboxSize * (1 + (lengthScale - 1) * 0.5));
        }

        // Base direction
        let baseDirX = 0, baseDirY = 0;
        switch (this.facing) {
            case 'right': baseDirX = 1; break;
            case 'left': baseDirX = -1; break;
            case 'up': baseDirY = -1; scaledDistance *= 1.2; break;
            case 'down': baseDirY = 1; scaledDistance *= 1.2; break;
        }

        // Calculate swing angle
        const swingProgress = Math.min(1.0, this.swingAnimationCounter / this.swingFramesTotal);
        const swingAngle = (-45 + 90 * swingProgress) * Math.PI / 180;

        const cosAngle = Math.cos(swingAngle);
        const sinAngle = Math.sin(swingAngle);

        const dirX = baseDirX * cosAngle - baseDirY * sinAngle;
        const dirY = baseDirX * sinAngle + baseDirY * cosAngle;

        const hitboxX = centerX + dirX * scaledDistance - hitboxSize / 2;
        const hitboxY = centerY + dirY * scaledDistance - hitboxSize / 2;

        return {
            x: hitboxX,
            y: hitboxY,
            width: hitboxSize,
            height: hitboxSize
        };
    }

    render(ctx, game) {
        // Don't render if invisible (flashing)
        if (!this.visible) {
            if (this.swinging) {
                this.renderSword(ctx);
            }
            return;
        }

        // Get the appropriate sprite
        let spriteData;
        const walkKey = `${this.facing}_walk`;
        const idleKey = `${this.facing}_idle`;

        if (this.moving && this.sprites[walkKey] && this.sprites[walkKey].length > 0) {
            const frameIndex = Math.min(this.frame, this.sprites[walkKey].length - 1);
            spriteData = this.sprites[walkKey][frameIndex];
        } else if (this.sprites[idleKey] && this.sprites[idleKey].length > 0) {
            spriteData = this.sprites[idleKey][0];
        }

        if (spriteData && spriteData.image) {
            ctx.save();

            if (spriteData.flipped) {
                // Flip horizontally
                ctx.translate(this.x + this.width, this.y);
                ctx.scale(-1, 1);
                ctx.drawImage(
                    spriteData.image,
                    spriteData.sx, spriteData.sy,
                    spriteData.sw, spriteData.sh,
                    0, 0,
                    spriteData.width, spriteData.height
                );
            } else {
                ctx.drawImage(
                    spriteData.image,
                    spriteData.sx, spriteData.sy,
                    spriteData.sw, spriteData.sh,
                    this.x, this.y,
                    spriteData.width, spriteData.height
                );
            }

            ctx.restore();
        } else {
            // Fallback: draw a colored rectangle
            ctx.fillStyle = '#4488ff';
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        // Draw sword if swinging
        if (this.swinging) {
            this.renderSword(ctx);
        }

        // Debug: draw collision box
        if (game.showDebug) {
            ctx.strokeStyle = 'lime';
            ctx.lineWidth = 1;
            ctx.strokeRect(this.x, this.y, this.width, this.height);

            // Draw sword hitbox
            if (this.swinging) {
                const swordRect = this.getSwordRect();
                if (swordRect) {
                    ctx.strokeStyle = 'red';
                    ctx.strokeRect(swordRect.x, swordRect.y, swordRect.width, swordRect.height);
                }
            }
        }
    }

    renderSword(ctx) {
        if (!this.swinging || !this.sword || !this.sword.image) return;

        // Start from player center
        let centerX = this.x + this.width / 2;
        let centerY = this.y + this.height / 2;

        // Offset the sword rotation center IN FRONT of the player
        const frontOffset = 15; // Distance in front of player
        switch (this.facing) {
            case 'right': centerX += frontOffset; break;
            case 'left': centerX -= frontOffset; break;
            case 'up': centerY -= frontOffset; break;
            case 'down': centerY += frontOffset; break;
        }

        // Base angles
        const baseAngles = {
            right: 0,
            left: Math.PI,
            up: -Math.PI / 2,
            down: Math.PI / 2
        };

        const baseAngle = baseAngles[this.facing];
        const angleOffset = (this.swingAnimationCounter / this.swingFramesTotal) * Math.PI / 2 - Math.PI / 4;
        const rotationAngle = baseAngle + angleOffset;

        const swordLength = this.attributes.swordLength;
        const swordX = centerX + Math.cos(rotationAngle) * swordLength;
        const swordY = centerY + Math.sin(rotationAngle) * swordLength;

        ctx.save();
        ctx.translate(swordX, swordY);
        ctx.rotate(rotationAngle + Math.PI / 2);

        // Draw sword sprite
        ctx.drawImage(
            this.sword.image,
            this.sword.sx, this.sword.sy,
            this.sword.sw, this.sword.sh,
            -this.sword.width / 2, -this.sword.height * 0.2,
            this.sword.width, this.sword.height
        );

        ctx.restore();
    }
}

/**
 * PlayerAttributes - Handles player stats, leveling, and abilities
 */
class PlayerAttributes {
    constructor(player) {
        this.player = player;

        // Base stats
        this.str = 1;  // Strength
        this.con = 1;  // Constitution
        this.dex = 1;  // Dexterity
        this.int = 1;  // Intelligence

        // Health and mana
        this.maxHealth = 3 + (this.con * 3);
        this.currentHealth = this.maxHealth;
        this.maxMana = 1 + (this.int * 2);
        this.currentMana = this.maxMana;

        // Stat points
        this.statPoints = 0;
        this.skillPoints = 0;

        // XP system
        this.xp = 0;
        this.level = 1;
        this.maxLevel = 50;
        this.xpTable = this.generateXpTable(1.5);
        this.xpNeeded = this.getXpNeeded();

        // Progression items
        this.foundAncientScroll = false;
        this.foundDragonHeart = false;

        // Dash ability
        this.canDash = false;  // Must be unlocked via skill tree
        this.dashDuration = 1500;
        this.dashCooldown = 3000;

        // Blink ability
        this.canBlink = false;  // Must be unlocked via skill tree
        this.blinkDistance = 80;
        this.blinkCooldown = 2000;

        // Sword
        this.swordLength = 24;
        this.baseSwordLength = 24;
    }

    generateXpTable(multiplier) {
        const table = [10];
        for (let i = 0; i < 49; i++) {
            table.push(Math.floor(table[table.length - 1] * multiplier));
        }
        return table;
    }

    getXpNeeded() {
        if (this.level >= this.maxLevel) return 0;

        let multiplier = 1.5;
        if (this.foundDragonHeart) multiplier = 1.2;
        else if (this.foundAncientScroll) multiplier = 1.3;

        this.xpTable = this.generateXpTable(multiplier);
        return this.xpTable[this.level - 1];
    }

    gainXp(amount) {
        if (this.level >= this.maxLevel) return false;

        this.xp += amount;

        if (this.xp >= this.xpNeeded) {
            const excessXp = this.xp - this.xpNeeded;
            this.levelUp();
            this.xp = excessXp;
            return this.gainXp(0);
        }

        return false;
    }

    levelUp() {
        if (this.level < this.maxLevel) {
            this.level++;
            this.statPoints++;

            // Skill points every 3 levels starting at 4
            if (this.level >= 4 && (this.level - 4) % 3 === 0) {
                this.skillPoints++;
            }

            // Milestone bonuses
            const milestones = { 10: 1, 20: 2, 30: 3, 40: 4, 50: 5 };
            if (milestones[this.level]) {
                this.statPoints += milestones[this.level];
            }

            this.xpNeeded = this.getXpNeeded();
            return true;
        }
        return false;
    }

    increaseStat(statName) {
        if (this.statPoints <= 0) return false;

        switch (statName) {
            case 'str':
                this.str++;
                this.statPoints--;
                return true;
            case 'con':
                this.con++;
                const oldMaxHealth = this.maxHealth;
                this.maxHealth = 3 + (this.con * 3);
                this.currentHealth += (this.maxHealth - oldMaxHealth);
                this.statPoints--;
                return true;
            case 'dex':
                this.dex++;
                this.player.baseSpeed = 3 + (this.dex * 0.08);
                this.player.speed = this.player.baseSpeed;
                this.statPoints--;
                return true;
            case 'int':
                this.int++;
                const oldMaxMana = this.maxMana;
                this.maxMana = 1 + (this.int * 2);
                this.currentMana += (this.maxMana - oldMaxMana);
                this.statPoints--;
                return true;
        }
        return false;
    }

    getAttackPower() {
        return 1 + Math.floor(this.str * 0.5);
    }

    takeDamage(amount) {
        const defenseFactor = 1.0 - (this.con * 0.05);
        return Math.max(1, Math.floor(amount * defenseFactor));
    }

    heal(amount) {
        this.currentHealth = Math.min(this.currentHealth + amount, this.maxHealth);
    }

    useMana(amount) {
        if (this.currentMana >= amount) {
            this.currentMana -= amount;
            return true;
        }
        return false;
    }

    restoreMana(amount) {
        this.currentMana = Math.min(this.currentMana + amount, this.maxMana);
    }
}

/**
 * Skill class - Represents a skill in the skill tree
 * Mirrors Python entities/player/skill_tree.py
 */
class Skill {
    constructor(id, name, description, levelRequired = 1, parent = null, implemented = true) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.levelRequired = levelRequired;
        this.parent = parent;  // Parent skill ID if this is a dependent skill
        this.unlocked = false;
        this.implemented = implemented;  // Whether the skill is implemented in the game
    }

    canUnlock(player) {
        // Must have required level
        if (player.attributes.level < this.levelRequired) {
            return false;
        }
        // If it has a parent, the parent must be unlocked first
        if (this.parent && !player.skillTree.isSkillUnlocked(this.parent)) {
            return false;
        }
        // Must be implemented
        if (!this.implemented) {
            return false;
        }
        return true;
    }

    unlock(player) {
        if (!this.canUnlock(player)) {
            return false;
        }
        this.unlocked = true;

        // Apply skill effects
        if (this.id === 'dash') {
            player.attributes.canDash = true;
        } else if (this.id === 'extended_sword') {
            player.attributes.swordLength = Math.floor(player.attributes.baseSwordLength * 1.5);
        } else if (this.id === 'blink') {
            player.attributes.canBlink = true;
        }
        // firebolt has no additional attributes needed

        return true;
    }
}

/**
 * SkillTree class - Manages the skill tree and skill point system
 * Mirrors Python entities/player/skill_tree.py
 */
class SkillTree {
    constructor(player) {
        this.player = player;
        this.skills = {};
        this.initializeSkills();
    }

    initializeSkills() {
        // Mind branch
        this.skills['heal'] = new Skill('heal', 'Heal', 'Restore health', 4, null, false);
        this.skills['firebolt'] = new Skill('firebolt', 'Firebolt', 'Cast a firebolt', 4, null, true);
        this.skills['bless'] = new Skill('bless', 'Bless', 'Temporary stat boost', 7, 'heal', false);
        this.skills['fireball'] = new Skill('fireball', 'Fireball', 'More powerful fireball', 7, 'firebolt', false);

        // Body branch
        this.skills['dash'] = new Skill('dash', 'Dash', 'Temporary speed boost (SHIFT)', 2, null, true);
        this.skills['blink'] = new Skill('blink', 'Blink', 'Short-range teleport (B)', 4, null, true);
        this.skills['dash_speed'] = new Skill('dash_speed', 'Increased Dash Speed', 'Dash moves faster', 7, 'dash', false);
        this.skills['dash_cooldown'] = new Skill('dash_cooldown', 'Reduced Dash Cooldown', 'Use dash more often', 10, 'dash_speed', false);
        this.skills['blink_extend1'] = new Skill('blink_extend1', 'Extended Blink', 'Blink farther', 7, 'blink', false);
        this.skills['blink_extend2'] = new Skill('blink_extend2', 'Extended Blink II', 'Blink even farther', 10, 'blink_extend1', false);
        this.skills['ghost_blink'] = new Skill('ghost_blink', 'Ghost Blink', 'Blink through obstacles', 13, 'blink_extend2', false);

        // Magic Sword branch
        this.skills['basic_sword'] = new Skill('basic_sword', 'Basic Sword', 'Regular sword swing', 1, null, true);
        this.skills['throw_sword'] = new Skill('throw_sword', 'Throw Sword', 'Throw your sword', 7, 'basic_sword', false);
        this.skills['extended_sword'] = new Skill('extended_sword', 'Extended Sword', 'Increased sword reach', 3, 'basic_sword', true);
        this.skills['extended_sword2'] = new Skill('extended_sword2', 'Extended Sword II', 'Further increased sword reach', 10, 'extended_sword', false);
        this.skills['extended_sword3'] = new Skill('extended_sword3', 'Extended Sword III', 'Maximum sword reach', 13, 'extended_sword2', false);
        this.skills['teleport_sword'] = new Skill('teleport_sword', 'Teleport Sword', 'Teleport to sword location', 16, 'throw_sword', false);

        // Only basic_sword is unlocked at game start
        // All other skills must be unlocked via skill points
        this.skills['basic_sword'].unlocked = true;
    }

    isSkillUnlocked(skillId) {
        if (this.skills[skillId]) {
            return this.skills[skillId].unlocked;
        }
        return false;
    }

    unlockSkill(skillId) {
        if (!this.skills[skillId]) return false;

        const skill = this.skills[skillId];

        // Check if player has skill points and skill is not already unlocked
        if (this.player.attributes.skillPoints <= 0 || skill.unlocked) {
            return false;
        }

        // Check if skill can be unlocked
        if (!skill.canUnlock(this.player)) {
            return false;
        }

        // Use a skill point and unlock the skill
        this.player.attributes.skillPoints--;
        const result = skill.unlock(this.player);

        if (result) {
            console.log(`Unlocked skill: ${skill.name}`);
        }

        return result;
    }

    getSkillsByBranch() {
        const branches = {
            mind: [],
            body: [],
            magic_sword: []
        };

        // Categorize skills
        for (const [skillId, skill] of Object.entries(this.skills)) {
            if (['heal', 'firebolt', 'bless', 'fireball'].includes(skillId)) {
                branches.mind.push(skill);
            } else if (['dash', 'blink', 'dash_speed', 'dash_cooldown', 'blink_extend1', 'blink_extend2', 'ghost_blink'].includes(skillId)) {
                branches.body.push(skill);
            } else {
                branches.magic_sword.push(skill);
            }
        }

        return branches;
    }
}

// Export
window.Player = Player;
window.PlayerAttributes = PlayerAttributes;
window.SkillTree = SkillTree;
window.Skill = Skill;
