/**
 * Projectile - Base class for all projectiles
 * Mirrors Python entities/projectile/projectile.py
 */
class Projectile {
    constructor(player, speed = 5, damage = 1, lifespan = 2000) {
        const direction = player.facing;
        const offset = 20;

        // Set initial position based on player facing direction
        if (direction === 'up') {
            this.x = player.x + player.width / 2;
            this.y = player.y - offset;
            this.vx = 0;
            this.vy = -speed;
        } else if (direction === 'down') {
            this.x = player.x + player.width / 2;
            this.y = player.y + player.height + offset;
            this.vx = 0;
            this.vy = speed;
        } else if (direction === 'left') {
            this.x = player.x - offset;
            this.y = player.y + player.height / 2;
            this.vx = -speed;
            this.vy = 0;
        } else { // right
            this.x = player.x + player.width + offset;
            this.y = player.y + player.height / 2;
            this.vx = speed;
            this.vy = 0;
        }

        this.damage = damage;
        this.lifespan = lifespan;
        this.creationTime = Date.now();
        this.alive = true;

        this.width = 8;
        this.height = 8;
    }

    update(currentTime, enemies, obstacles = []) {
        // Don't update if dead
        if (!this.alive) return;

        // Check lifespan
        if (currentTime - this.creationTime > this.lifespan) {
            this.alive = false;
            return;
        }

        // Move projectile
        this.x += this.vx;
        this.y += this.vy;

        // Collision detection with enemies
        const rect = this.getRect();
        for (const enemy of enemies) {
            if (enemy.state === 'dying') continue;

            const enemyRect = enemy.getRect();
            if (this.rectsOverlap(rect, enemyRect)) {
                enemy.takeDamage(this.damage, this.x, this.y);
                this.onHit(enemy);
                return; // Stop after first hit
            }
        }

        // Collision detection with obstacles (bushes, rocks, etc.)
        for (const obstacle of obstacles) {
            if (!obstacle.getRect) continue;

            const obsRect = obstacle.getRect();
            if (this.rectsOverlap(rect, obsRect)) {
                this.onHit(obstacle);
                return; // Stop after hitting obstacle
            }
        }
    }

    getRect() {
        return {
            x: this.x - this.width / 2,
            y: this.y - this.height / 2,
            width: this.width,
            height: this.height
        };
    }

    rectsOverlap(a, b) {
        return a.x < b.x + b.width &&
               a.x + a.width > b.x &&
               a.y < b.y + b.height &&
               a.y + a.height > b.y;
    }

    render(ctx) {
        if (!this.alive) return;

        ctx.fillStyle = '#ffff00';
        const rect = this.getRect();
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    }

    renderDebug(ctx) {
        const rect = this.getRect();
        ctx.strokeStyle = '#ff8800';
        ctx.lineWidth = 1;
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
    }

    onHit(enemy) {
        this.alive = false;
    }
}

/**
 * Firebolt - Fire projectile spell
 * Mirrors Python entities/projectile/firebolt.py
 */
class Firebolt extends Projectile {
    constructor(player) {
        // Scale parameters based on player's intelligence attribute
        const intAttr = player.attributes.int;

        // Calculate speed: base 6, scales to 12 at int 15
        const speed = 6 + (intAttr - 1) * (6 / 14);

        // Calculate damage: base 3, scales to 15 at int 15
        const damage = 3 + (intAttr - 1) * (12 / 14);

        // Calculate lifespan: base 400, scales to 2000 at int 15
        const lifespan = 400 + (intAttr - 1) * (1600 / 14);

        // Call parent constructor
        super(player, speed, damage, lifespan);

        // Magic level is directly tied to intelligence
        this.magicLevel = intAttr;

        // Calculate size based on magic level (base size + level bonus)
        this.boltSize = 4 + Math.min(11, this.magicLevel); // Caps at size 15

        // Update collision rectangle to match new size
        this.width = this.boltSize * 2;
        this.height = this.boltSize * 2;

        // Firebolt-specific colors
        this.innerColor = 'rgb(255, 255, 0)';   // Bright yellow core
        this.outerColor = 'rgb(255, 100, 0)';   // Orange outer

        // Scale particle effects with magic level
        this.trailParticles = 1 + Math.floor(this.magicLevel / 2);
    }

    getRect() {
        return {
            x: this.x - this.boltSize,
            y: this.y - this.boltSize,
            width: this.width,
            height: this.height
        };
    }

    update(currentTime, enemies, obstacles = []) {
        // Don't update if dead
        if (!this.alive) return;

        // Call parent update (handles lifespan and collision)
        super.update(currentTime, enemies, obstacles);

        // If still alive, create fire trail using global particle system
        if (this.alive && window.particleSystem) {
            for (let i = 0; i < this.trailParticles; i++) {
                let offsetX = 0;
                let offsetY = 0;

                if (this.magicLevel > 1) {
                    offsetX = (Math.random() - 0.5) * this.boltSize;
                    offsetY = (Math.random() - 0.5) * this.boltSize;
                }

                window.particleSystem.createFireTrail(this.x + offsetX, this.y + offsetY);
            }
        }
    }

    render(ctx) {
        if (!this.alive) return;

        // Draw outer glow
        ctx.fillStyle = this.outerColor;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.boltSize, 0, Math.PI * 2);
        ctx.fill();

        // Draw inner core (smaller, brighter)
        const innerSize = Math.max(2, Math.floor(this.boltSize / 2));
        ctx.fillStyle = this.innerColor;
        ctx.beginPath();
        ctx.arc(this.x, this.y, innerSize, 0, Math.PI * 2);
        ctx.fill();
    }

    onHit(enemy) {
        // Create explosion using global particle system
        if (window.particleSystem) {
            this.createScaledExplosion();
        }
        super.onHit(enemy);
    }

    createScaledExplosion() {
        // Main explosion at impact point
        window.particleSystem.createFireExplosion(this.x, this.y);

        // For higher levels, add additional explosion points
        if (this.magicLevel >= 2) {
            const explosionRadius = 5 + (this.magicLevel * 2);
            const numExplosions = Math.min(8, this.magicLevel * 2);

            for (let i = 0; i < numExplosions; i++) {
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * explosionRadius;

                const ex = this.x + Math.cos(angle) * distance;
                const ey = this.y + Math.sin(angle) * distance;

                window.particleSystem.createFireExplosion(ex, ey);
            }
        }
    }
}

// Export
window.Projectile = Projectile;
window.Firebolt = Firebolt;
