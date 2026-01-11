/**
 * EnemyAttributes - Handles enemy stats, level scaling, and derived stats
 */
class EnemyAttributes {
    constructor(enemy, level = 1, enemyType = 'normal') {
        this.enemy = enemy;
        this.level = Math.min(Math.max(1, level), 10);
        this.enemyType = enemyType;

        // Base attributes
        this.str = 1;
        this.con = 1;
        this.dex = 1;
        this.int = 0;

        // Derived stats
        this.maxHealth = 3;
        this.currentHealth = 3;
        this.attackPower = 1;
        this.defense = 0;
        this.speedMultiplier = 1.0;
        this.knockbackResistance = 0;

        // Distribute attributes based on type
        this.distributeAttributes();
        this.calculateStats();
    }

    distributeAttributes() {
        const attrPoints = this.level + 2;

        switch (this.enemyType) {
            case 'fast':
                this.str += Math.floor(attrPoints * 0.2);
                this.con += Math.floor(attrPoints * 0.1);
                this.dex += Math.floor(attrPoints * 0.7);
                break;
            case 'brute':
                this.str += Math.floor(attrPoints * 0.7);
                this.con += Math.floor(attrPoints * 0.2);
                this.dex += Math.floor(attrPoints * 0.1);
                break;
            case 'tank':
                this.str += Math.floor(attrPoints * 0.3);
                this.con += Math.floor(attrPoints * 0.6);
                this.dex += Math.floor(attrPoints * 0.1);
                break;
            default: // normal
                this.str += Math.floor(attrPoints * 0.4);
                this.con += Math.floor(attrPoints * 0.3);
                this.dex += Math.floor(attrPoints * 0.3);
        }
    }

    calculateStats() {
        // Health
        const baseHealth = 3;
        const conBonus = this.con * 2;
        const levelBonus = this.level * 0.5;
        this.maxHealth = Math.floor(baseHealth + conBonus + levelBonus);
        this.currentHealth = this.maxHealth;

        // Attack power
        const baseAttack = 1;
        const strBonus = this.str * 0.5;
        const atkLevelBonus = this.level * 0.2;
        this.attackPower = Math.max(1, Math.floor(baseAttack + strBonus + atkLevelBonus));

        // Speed
        const dexBonus = this.dex * 0.08;
        this.speedMultiplier = 1.0 + dexBonus;
        this.enemy.speed = this.enemy.baseSpeed * this.speedMultiplier;

        // Defense
        const defConBonus = this.con * 0.1;
        const defLevelBonus = this.level * 0.1;
        this.defense = defConBonus + defLevelBonus;

        // Knockback resistance
        const maxResist = 0.8;
        const conResist = this.con * 0.07;
        const levelResist = this.level * 0.02;
        this.knockbackResistance = Math.min(maxResist, conResist + levelResist);
    }

    takeDamage(amount) {
        const defenseFactor = 1.0 - Math.min(0.8, this.defense * 0.1);
        const finalDamage = Math.max(1, Math.floor(amount * defenseFactor));
        this.currentHealth -= finalDamage;
        return finalDamage;
    }

    getAttackPower() {
        return this.attackPower;
    }

    getKnockbackFactor() {
        return this.knockbackResistance;
    }

    scaleByDifficulty(difficultyFactor) {
        if (difficultyFactor <= 1.0) return;

        const levelBoost = Math.min(5, Math.floor((difficultyFactor - 1) * 3));
        this.level = Math.min(10, this.level + levelBoost);
        this.distributeAttributes();
        this.calculateStats();
    }

    getInfoText() {
        let info = `Lvl ${this.level} ${this.enemyType}: `;
        info += `STR ${this.str}, CON ${this.con}, DEX ${this.dex}`;

        if (this.int > 0) {
            info += `, INT ${this.int}`;
        }

        info += ` | HP: ${this.currentHealth}/${this.maxHealth}`;
        info += ` | ATK: ${this.attackPower}, DEF: ${this.defense.toFixed(1)}`;

        return info;
    }
}

/**
 * Enemy - Base class for all enemies
 */
class Enemy {
    constructor(game, x, y, width, height, speed = 1) {
        this.game = game;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.speed = speed;
        this.baseSpeed = speed;

        // State
        this.state = 'idle';
        this.direction = Math.random() < 0.5 ? 'left' : 'right';
        this.frame = 0;
        this.animationSpeed = 0.1;
        this.animationCounter = 0;

        // Movement AI
        this.movementTimer = 0;
        this.movementPause = 60 + Math.random() * 120;
        this.movementDuration = 30 + Math.random() * 90;
        this.dx = 0;
        this.dy = 0;

        // Type
        this.enemyType = 'normal';

        // Attributes
        this.attributes = new EnemyAttributes(this, 1, this.enemyType);
        this.health = this.attributes.maxHealth;

        // Combat
        this.attackRange = 50;
        this.detectionRange = 150;

        // Hit effect
        this.hit = false;
        this.hitTimer = 0;
        this.hitDuration = 200;

        // Death
        this.deathTimer = 0;
        this.deathDuration = 500;
        this.shouldRemove = false;
        this.willDropSoul = false;
        this.deathParticles = [];

        // Knockback
        this.isBeingKnockedBack = false;
        this.knockbackTimer = 0;
        this.knockbackDuration = 300;
        this.knockbackDirection = { x: 0, y: 0 };
        this.currentKnockback = 0;

        // Recovery
        this.isRecovering = false;
        this.recoveryTimer = 0;
        this.recoveryDuration = 1000;
        this.shouldRecover = false;

        // Sprites
        this.sprites = {};
    }

    setLevel(level, difficultyFactor = 1.0) {
        this.attributes = new EnemyAttributes(this, level, this.enemyType);
        if (difficultyFactor > 1.0) {
            this.attributes.scaleByDifficulty(difficultyFactor);
        }
        this.health = this.attributes.maxHealth;
    }

    update(dt, player, obstacles) {
        const frameMs = 16.67;

        // Check for death
        if (this.health <= 0 && this.state !== 'dying') {
            this.die();
            return;
        }

        // Dying state
        if (this.state === 'dying') {
            this.deathTimer += frameMs;
            this.updateDeathParticles();
            if (this.deathTimer >= this.deathDuration) {
                this.shouldRemove = true;
                this.willDropSoul = true;
            }
            return;
        }

        // Recovery state
        if (this.isRecovering) {
            this.recoveryTimer += frameMs;
            if (this.recoveryTimer >= this.recoveryDuration) {
                this.isRecovering = false;
                this.recoveryTimer = 0;
            }
            this.updateAnimation();
            this.updateHitEffect(frameMs);
            return;
        }

        // Knockback
        if (this.isBeingKnockedBack) {
            this.knockbackTimer += frameMs;
            if (this.knockbackTimer < this.knockbackDuration) {
                const progress = this.knockbackTimer / this.knockbackDuration;
                const factor = 1 - progress;
                const moveX = this.knockbackDirection.x * this.currentKnockback * factor * 0.5;
                const moveY = this.knockbackDirection.y * this.currentKnockback * factor * 0.5;
                this.move(moveX, moveY, obstacles);
            } else {
                this.isBeingKnockedBack = false;
                if (this.shouldRecover) {
                    this.state = 'idle';
                    this.isRecovering = true;
                    this.recoveryTimer = 0;
                    this.shouldRecover = false;
                }
            }
            this.updateHitEffect(frameMs);
            return;
        }

        // Check player collision
        if (player && this.checkCollision(player)) {
            this.handlePlayerCollision(player);
        }

        // AI movement
        if (this.state !== 'dying' && this.state !== 'attacking') {
            this.movementTimer++;

            if (this.state === 'idle') {
                if (this.movementTimer >= this.movementPause) {
                    this.movementTimer = 0;
                    this.startMoving();
                }
            } else if (this.state === 'moving') {
                if (this.movementTimer >= this.movementDuration) {
                    this.movementTimer = 0;
                    this.stopMoving();
                } else {
                    this.move(this.dx, this.dy, obstacles);
                }
            }
        }

        this.updateAnimation();
        this.updateHitEffect(frameMs);
    }

    updateAnimation() {
        this.animationCounter += this.animationSpeed;
        const frames = this.getAnimationFrames();
        if (frames.length > 0) {
            if (this.animationCounter >= frames.length) {
                this.animationCounter = 0;
            }
            this.frame = Math.floor(this.animationCounter);
        }
    }

    updateHitEffect(frameMs) {
        if (this.hit) {
            this.hitTimer += frameMs;
            if (this.hitTimer >= this.hitDuration) {
                this.hit = false;
                this.hitTimer = 0;
            }
        }
    }

    getAnimationFrames() {
        const key = `${this.state}_${this.direction}`;
        if (this.sprites[key] && this.sprites[key].length > 0) {
            return this.sprites[key];
        }
        if (this.sprites[this.state] && this.sprites[this.state].length > 0) {
            return this.sprites[this.state];
        }
        return [];
    }

    startMoving() {
        this.state = 'moving';
        const angle = Math.random() * Math.PI * 2;
        this.dx = Math.cos(angle) * this.speed;
        this.dy = Math.sin(angle) * this.speed;
        this.direction = this.dx > 0 ? 'right' : 'left';
    }

    stopMoving() {
        this.state = 'idle';
        this.dx = 0;
        this.dy = 0;
    }

    move(dx, dy, obstacles) {
        if (dx === 0 && dy === 0) return;

        const screenWidth = this.game.width;
        const screenHeight = this.game.height;
        const margin = this.width * 0.75;

        // Test X movement
        let newX = this.x + dx;
        let xBlocked = newX < -margin || newX + this.width > screenWidth + margin;

        if (!xBlocked && obstacles) {
            for (const obs of obstacles) {
                if (obs === this) continue;
                if (this.wouldCollide(newX, this.y, obs)) {
                    xBlocked = true;
                    break;
                }
            }
        }

        if (!xBlocked) this.x = newX;

        // Test Y movement
        let newY = this.y + dy;
        let yBlocked = newY < -margin || newY + this.height > screenHeight + margin;

        if (!yBlocked && obstacles) {
            for (const obs of obstacles) {
                if (obs === this) continue;
                if (this.wouldCollide(this.x, newY, obs)) {
                    yBlocked = true;
                    break;
                }
            }
        }

        if (!yBlocked) this.y = newY;

        // Change direction if blocked
        if (xBlocked || yBlocked) {
            if (Math.random() < 0.5) {
                this.startMoving();
            }
        }
    }

    wouldCollide(x, y, obstacle) {
        if (!obstacle.getRect) return false;
        const rect = obstacle.getRect();
        return x < rect.x + rect.width &&
               x + this.width > rect.x &&
               y < rect.y + rect.height &&
               y + this.height > rect.y;
    }

    checkCollision(entity) {
        const rect = entity.getRect();
        return this.x < rect.x + rect.width &&
               this.x + this.width > rect.x &&
               this.y < rect.y + rect.height &&
               this.y + this.height > rect.y;
    }

    handlePlayerCollision(player) {
        if (this.isRecovering) return;

        const attackPower = this.attributes.getAttackPower();
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;
        player.takeDamage(attackPower, centerX, centerY);
    }

    takeDamage(damage, playerX = null, playerY = null) {
        if (this.state === 'dying') return false;

        const wasHit = this.hit;
        const finalDamage = this.attributes.takeDamage(damage);
        this.health = this.attributes.currentHealth;

        this.hit = true;
        this.hitTimer = 0;

        if (!wasHit) {
            this.shouldRecover = true;
        }

        this.startKnockback(damage, playerX, playerY);
        this.isRecovering = false;
        this.recoveryTimer = 0;

        if (this.health <= 0) {
            this.die();
            return true;
        }
        return false;
    }

    startKnockback(damageAmount, playerX, playerY) {
        if (this.state === 'dying') return;

        const resistance = this.attributes.getKnockbackFactor();
        const knockbackFactor = Math.min(1.0, damageAmount / this.attributes.maxHealth * 2);
        const baseKnockback = 40;
        const actualKnockback = baseKnockback * knockbackFactor * (1 - resistance);

        if (actualKnockback < 3) return;

        // Calculate direction
        if (playerX !== null && playerY !== null) {
            const centerX = this.x + this.width / 2;
            const centerY = this.y + this.height / 2;
            let dirX = centerX - playerX;
            let dirY = centerY - playerY;
            const length = Math.max(0.1, Math.sqrt(dirX * dirX + dirY * dirY));
            dirX /= length;
            dirY /= length;
            this.knockbackDirection = { x: dirX, y: dirY };
        } else {
            this.knockbackDirection = { x: this.direction === 'right' ? -1 : 1, y: 0 };
        }

        this.currentKnockback = actualKnockback;
        this.knockbackTimer = 0;
        this.isBeingKnockedBack = true;
    }

    die() {
        this.state = 'dying';
        this.animationCounter = 0;
        this.deathTimer = 0;
        this.shouldRemove = false;
        this.willDropSoul = true;
        this.createDeathParticles();
    }

    createDeathParticles() {
        this.deathParticles = [];
        const count = 15 + Math.floor(Math.random() * 6);
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;

        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * this.width / 3;
            const gray = 150 + Math.floor(Math.random() * 100);

            this.deathParticles.push({
                x: centerX + Math.cos(angle) * distance,
                y: centerY + Math.sin(angle) * distance,
                vx: Math.cos(angle) * (0.5 + Math.random() * 1.5),
                vy: Math.sin(angle) * (0.5 + Math.random() * 1.5),
                size: 5 + Math.floor(Math.random() * 8),
                color: `rgb(${gray}, ${gray}, ${gray})`,
                life: 15 + Math.floor(Math.random() * 16),
                maxLife: 30
            });
        }
    }

    updateDeathParticles() {
        for (const p of this.deathParticles) {
            p.x += p.vx;
            p.y += p.vy;
            p.vy -= 0.05;
            p.vx *= 0.95;
            p.vy *= 0.95;
            p.life--;
        }
        this.deathParticles = this.deathParticles.filter(p => p.life > 0);
    }

    getRect() {
        if (this.state === 'dying') {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        return { x: this.x, y: this.y, width: this.width, height: this.height };
    }

    getXpValue() {
        // XP value equals enemy level (matches Soul value in original)
        return this.attributes.level;
    }

    render(ctx, game) {
        // Death particles only
        if (this.state === 'dying') {
            this.renderDeathParticles(ctx);
            return;
        }

        // Get sprite - to be implemented by subclasses
        this.renderSprite(ctx, game);

        // Debug
        if (game.showDebug) {
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 1;
            ctx.strokeRect(this.x, this.y, this.width, this.height);

            // Detection range
            ctx.strokeStyle = 'rgba(0, 150, 255, 0.3)';
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.detectionRange, 0, Math.PI * 2);
            ctx.stroke();
        }
    }

    renderSprite(ctx, game) {
        // Default fallback - subclasses override this
        ctx.fillStyle = this.hit && Math.floor(this.hitTimer / 40) % 2 === 0 ? '#ff8888' : '#888888';
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    renderDeathParticles(ctx) {
        for (const p of this.deathParticles) {
            const alpha = p.life / p.maxLife;
            ctx.globalAlpha = alpha;
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size / 2, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;
    }

    renderDebugInfo(ctx, x, y) {
        if (this.attributes) {
            // Get state text
            let stateText = `State: ${this.state}`;
            if (this.isRecovering) {
                stateText += ' (recovering)';
            } else if (this.isBeingKnockedBack) {
                stateText += ' (knockback)';
            }

            const infoText = this.attributes.getInfoText() + ' | ' + stateText;

            ctx.font = '10px monospace';
            ctx.fillStyle = this.enemyType === 'fast' ? '#00b400' : '#dcdcdc';
            ctx.fillText(infoText, x, y);
        }
    }
}

/**
 * Slime - Fast, small enemy using GIF assets with frame-by-frame animation
 */
class Slime extends Enemy {
    constructor(game, x, y) {
        super(game, x, y, 32, 24, 0.5);
        this.enemyType = 'fast';
        this.attributes = new EnemyAttributes(this, 1, this.enemyType);
        this.health = this.attributes.maxHealth;
        this.animationSpeed = 0.15; // Animation speed for frame cycling

        // GIF animation frames
        this.idleFrames = [];
        this.moveFrames = [];
        this.framesLoaded = false;

        // Frame timing
        this.frameTimer = 0;
        this.frameDelay = 100; // ms between frames (from GIF)

        // Load GIF frames
        this.loadGifFrames();
    }

    async loadGifFrames() {
        if (window.gifLoader) {
            try {
                // Load idle animation
                const idleGif = await window.gifLoader.loadGif('assets/slime_idle.gif');
                this.idleFrames = idleGif.frames;
                this.frameDelay = idleGif.delays[0] || 100;

                // Load move animation
                const moveGif = await window.gifLoader.loadGif('assets/slime_move.gif');
                this.moveFrames = moveGif.frames;

                this.framesLoaded = true;
                console.log(`Slime GIF loaded: ${this.idleFrames.length} idle frames, ${this.moveFrames.length} move frames`);
            } catch (error) {
                console.error('Error loading slime GIF frames:', error);
            }
        }
    }

    update(dt, player, obstacles) {
        // Update frame timer for animation
        this.frameTimer += 16.67; // ~60 FPS

        if (this.frameTimer >= this.frameDelay) {
            this.frameTimer = 0;
            // Advance frame
            const frames = this.state === 'moving' ? this.moveFrames : this.idleFrames;
            if (frames.length > 0) {
                this.frame = (this.frame + 1) % frames.length;
            }
        }

        // Call parent update
        super.update(dt, player, obstacles);
    }

    handlePlayerCollision(player) {
        // Slimes don't stop when attacking - they keep moving
        if (this.isRecovering) return;
        const attackPower = this.attributes.getAttackPower();
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;
        player.takeDamage(attackPower, centerX, centerY);
    }

    createDeathParticles() {
        this.deathParticles = [];
        const count = 20 + Math.floor(Math.random() * 6);
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;

        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * this.width / 2;
            const green = 150 + Math.floor(Math.random() * 100);
            const red = 30 + Math.floor(Math.random() * 70);
            const blue = 30 + Math.floor(Math.random() * 70);

            this.deathParticles.push({
                x: centerX + Math.cos(angle) * distance,
                y: centerY + Math.sin(angle) * distance,
                vx: Math.cos(angle) * (0.8 + Math.random() * 1.7),
                vy: Math.sin(angle) * (0.8 + Math.random() * 1.7),
                size: 4 + Math.floor(Math.random() * 7),
                color: `rgb(${red}, ${green}, ${blue})`,
                life: 15 + Math.floor(Math.random() * 16),
                maxLife: 30
            });
        }
    }

    renderSprite(ctx, game) {
        const visible = !this.hit || Math.floor(this.hitTimer / 40) % 2 === 0;
        if (!visible) return;

        // Get the appropriate frames based on state
        const frames = this.state === 'moving' ? this.moveFrames : this.idleFrames;

        if (this.framesLoaded && frames.length > 0) {
            // Use parsed GIF frames
            const frameIndex = Math.min(this.frame, frames.length - 1);
            const frameCanvas = frames[frameIndex];
            if (frameCanvas) {
                ctx.drawImage(frameCanvas, this.x, this.y, this.width, this.height);
            }
        } else {
            // Fallback: use static image or green rectangle
            const spriteKey = this.state === 'moving' ? 'slime_move' : 'slime_idle';
            const sprite = game.getImage(spriteKey);

            if (sprite) {
                ctx.drawImage(sprite, this.x, this.y, this.width, this.height);
            } else {
                ctx.fillStyle = '#00cc00';
                ctx.fillRect(this.x, this.y, this.width, this.height);
            }
        }
    }
}

/**
 * Skeleton - Normal/brute enemy with sprite sheet and chasing AI
 */
class Skeleton extends Enemy {
    constructor(game, x, y) {
        super(game, x, y, 48, 52, 1);
        this.enemyType = 'normal';
        this.attributes = new EnemyAttributes(this, 1, this.enemyType);
        this.health = this.attributes.maxHealth;
        this.animationSpeed = 0.15; // Faster animation speed

        // Sprite frame definitions (x-positions in sprite sheet)
        this.idleFramePositions = [0, 95, 191, 287, 383, 479, 575];
        this.walkFramePositions = [0, 95, 191, 287, 383, 479, 575, 671, 767];
        this.frameWidth = 42;

        // Current frame index (separate from animation counter)
        this.currentFrameIndex = 0;

        // Attack properties
        this.attackTimer = 0;
        this.attackDuration = 500;
        this.attackCooldown = 800;
        this.attackCooldownTimer = 0;
        this.canAttack = true;
    }

    // Override updateAnimation to properly cycle through frames
    updateAnimation() {
        this.animationCounter += this.animationSpeed;

        // Get the appropriate frame array based on state
        const framePositions = this.state === 'moving' ? this.walkFramePositions : this.idleFramePositions;
        const numFrames = framePositions.length;

        if (numFrames > 0) {
            // Cycle animation counter
            if (this.animationCounter >= numFrames) {
                this.animationCounter = this.animationCounter % numFrames;
            }

            // Update current frame index
            this.currentFrameIndex = Math.floor(this.animationCounter);
            this.frame = this.currentFrameIndex;
        }
    }

    update(dt, player, obstacles) {
        const frameMs = 16.67;

        // Check for death
        if (this.health <= 0 && this.state !== 'dying') {
            this.die();
            return;
        }

        // Dying state
        if (this.state === 'dying') {
            this.deathTimer += frameMs;
            this.updateDeathParticles();
            if (this.deathTimer >= this.deathDuration) {
                this.shouldRemove = true;
                this.willDropSoul = true;
            }
            return;
        }

        // Recovery state - skeleton pauses after being hit
        if (this.isRecovering) {
            this.recoveryTimer += frameMs;
            if (this.recoveryTimer >= this.recoveryDuration) {
                this.isRecovering = false;
                this.recoveryTimer = 0;
            }
            this.updateAnimation();
            this.updateHitEffect(frameMs);
            return;
        }

        // Knockback
        if (this.isBeingKnockedBack) {
            this.knockbackTimer += frameMs;
            if (this.knockbackTimer < this.knockbackDuration) {
                const progress = this.knockbackTimer / this.knockbackDuration;
                const factor = 1 - progress;
                const moveX = this.knockbackDirection.x * this.currentKnockback * factor * 0.5;
                const moveY = this.knockbackDirection.y * this.currentKnockback * factor * 0.5;
                this.move(moveX, moveY, obstacles);
            } else {
                this.isBeingKnockedBack = false;
                if (this.shouldRecover) {
                    this.state = 'idle';
                    this.isRecovering = true;
                    this.recoveryTimer = 0;
                    this.shouldRecover = false;
                }
            }
            this.updateHitEffect(frameMs);
            return;
        }

        // Update attack cooldown
        if (!this.canAttack) {
            this.attackCooldownTimer += frameMs;
            if (this.attackCooldownTimer >= this.attackCooldown) {
                this.canAttack = true;
                this.attackCooldownTimer = 0;
            }
        }

        // Attack state
        if (this.state === 'attacking') {
            this.attackTimer += frameMs;
            if (this.attackTimer >= this.attackDuration) {
                this.attackTimer = 0;
                this.state = 'idle';
                this.canAttack = false;
                this.attackCooldownTimer = 0;
            }
            this.updateAnimation();
            this.updateHitEffect(frameMs);
            return;
        }

        // Check player collision
        if (player && this.checkCollision(player)) {
            this.handlePlayerCollision(player);
        }

        // CHASING AI - Skeleton chases player when in detection range
        if (player && this.state !== 'attacking') {
            const playerRect = player.getRect();
            const skeletonCenterX = this.x + this.width / 2;
            const skeletonCenterY = this.y + this.height / 2;
            const playerCenterX = playerRect.x + playerRect.width / 2;
            const playerCenterY = playerRect.y + playerRect.height / 2;

            const dx = playerCenterX - skeletonCenterX;
            const dy = playerCenterY - skeletonCenterY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // If player is within detection range but outside attack range, chase
            if (distance < this.detectionRange && distance > this.attackRange) {
                this.state = 'moving';

                // Calculate direction to player
                if (distance > 0) {
                    this.dx = (dx / distance) * this.speed;
                    this.dy = (dy / distance) * this.speed;

                    // Update facing direction
                    if (Math.abs(dx) > Math.abs(dy)) {
                        this.direction = dx > 0 ? 'right' : 'left';
                    }
                }

                // Move toward player
                this.move(this.dx, this.dy, obstacles);
            }
            // If within attack range and can attack, attack
            else if (distance <= this.attackRange && this.canAttack) {
                this.attack(player);
            }
            // If player is outside detection range, use normal wandering AI
            else if (distance >= this.detectionRange) {
                this.movementTimer++;

                if (this.state === 'idle') {
                    if (this.movementTimer >= this.movementPause) {
                        this.movementTimer = 0;
                        this.startMoving();
                    }
                } else if (this.state === 'moving') {
                    if (this.movementTimer >= this.movementDuration) {
                        this.movementTimer = 0;
                        this.stopMoving();
                    } else {
                        this.move(this.dx, this.dy, obstacles);
                    }
                }
            }
        } else {
            // No player or in attack state - normal wandering
            this.movementTimer++;

            if (this.state === 'idle') {
                if (this.movementTimer >= this.movementPause) {
                    this.movementTimer = 0;
                    this.startMoving();
                }
            } else if (this.state === 'moving') {
                if (this.movementTimer >= this.movementDuration) {
                    this.movementTimer = 0;
                    this.stopMoving();
                } else {
                    this.move(this.dx, this.dy, obstacles);
                }
            }
        }

        this.updateAnimation();
        this.updateHitEffect(frameMs);
    }

    handlePlayerCollision(player) {
        // Skip if attacking, knocked back, or recovering
        if (this.state === 'attacking' || this.isBeingKnockedBack || this.isRecovering) {
            return;
        }

        this.stopMoving();

        const attackPower = this.attributes.getAttackPower();
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;
        player.takeDamage(attackPower, centerX, centerY);

        // Start attacking state
        this.attack(player);
    }

    attack(player) {
        if (this.state === 'attacking' || this.isBeingKnockedBack || !this.canAttack || this.isRecovering) {
            return;
        }

        this.state = 'attacking';
        this.animationCounter = 0;
        this.attackTimer = 0;

        const attackPower = this.attributes.getAttackPower();
        const centerX = this.x + this.width / 2;
        const centerY = this.y + this.height / 2;
        player.takeDamage(attackPower, centerX, centerY);
    }

    renderSprite(ctx, game) {
        const visible = !this.hit || Math.floor(this.hitTimer / 40) % 2 === 0;
        if (!visible) return;

        // Get appropriate sprite sheet and frame positions
        const isMoving = this.state === 'moving';
        const spriteKey = isMoving ? 'skeleton_walk' : 'skeleton_idle';
        const sprite = game.getImage(spriteKey);
        const framePositions = isMoving ? this.walkFramePositions : this.idleFramePositions;

        if (sprite && framePositions.length > 0) {
            const frameIndex = Math.min(this.currentFrameIndex, framePositions.length - 1);
            const sx = framePositions[frameIndex];
            const frameHeight = sprite.height;

            ctx.save();

            // Flip if facing left
            if (this.direction === 'left') {
                ctx.translate(this.x + this.width, this.y);
                ctx.scale(-1, 1);
                ctx.drawImage(
                    sprite,
                    sx, 0, this.frameWidth, frameHeight,
                    0, 0, this.width, this.height
                );
            } else {
                ctx.drawImage(
                    sprite,
                    sx, 0, this.frameWidth, frameHeight,
                    this.x, this.y, this.width, this.height
                );
            }

            ctx.restore();
        } else {
            // Fallback
            ctx.fillStyle = '#cccccc';
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.strokeStyle = '#888888';
            ctx.strokeRect(this.x, this.y, this.width, this.height);
        }
    }
}

// Export
window.EnemyAttributes = EnemyAttributes;
window.Enemy = Enemy;
window.Slime = Slime;
window.Skeleton = Skeleton;
