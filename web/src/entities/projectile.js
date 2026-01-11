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

        // Flag for custom rect positioning
        this.hasCustomRect = false;
    }

    update(currentTime, enemies) {
        // Check lifespan
        if (currentTime - this.creationTime > this.lifespan) {
            this.alive = false;
            return;
        }

        // Move projectile
        this.x += this.vx;
        this.y += this.vy;

        // Update rect position (for subclasses to override)
        this.updateRectPosition();

        // Collision detection with enemies
        const rect = this.getRect();
        for (const enemy of enemies) {
            if (enemy.state === 'dying') continue;

            const enemyRect = enemy.getRect();
            if (this.rectsOverlap(rect, enemyRect)) {
                enemy.takeDamage(this.damage, this.x, this.y);
                this.onHit(enemy);
                break;
            }
        }
    }

    updateRectPosition() {
        // Hook for subclasses to update custom rectangle positions
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
        ctx.fillStyle = '#ffff00';
        const rect = this.getRect();
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
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
        this.hasCustomRect = true;

        // Firebolt-specific colors
        this.innerColor = 'rgb(255, 255, 0)';   // Bright yellow core
        this.outerColor = 'rgb(255, 100, 0)';   // Orange outer

        // Scale particle effects with magic level
        this.trailParticles = 1 + Math.floor(this.magicLevel / 2);
        this.explosionScale = 1.0 + (this.magicLevel * 0.2);

        // Particle storage for fire trail
        this.particles = [];
    }

    updateRectPosition() {
        // Keep rect centered on projectile position
    }

    getRect() {
        return {
            x: this.x - this.boltSize,
            y: this.y - this.boltSize,
            width: this.width,
            height: this.height
        };
    }

    update(currentTime, enemies) {
        super.update(currentTime, enemies);

        if (!this.alive) return;

        // Create fire trail particles
        for (let i = 0; i < this.trailParticles; i++) {
            let offsetX = 0;
            let offsetY = 0;

            if (this.magicLevel > 1) {
                offsetX = (Math.random() - 0.5) * this.boltSize;
                offsetY = (Math.random() - 0.5) * this.boltSize;
            }

            this.createFireTrailParticle(this.x + offsetX, this.y + offsetY);
        }

        // Update existing particles
        this.particles = this.particles.filter(p => {
            p.life--;
            p.size *= 0.95; // Shrink over time
            return p.life > 0;
        });
    }

    createFireTrailParticle(x, y) {
        const size = 2 + Math.random() * 2;
        const life = 3 + Math.floor(Math.random() * 4);

        // Orange-red colors
        const r = 255;
        const g = 50 + Math.floor(Math.random() * 100);
        const b = 0;

        this.particles.push({
            x: x,
            y: y,
            size: size,
            color: `rgb(${r}, ${g}, ${b})`,
            life: life
        });
    }

    render(ctx) {
        // Draw trail particles first (behind the bolt)
        for (const p of this.particles) {
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life / 6;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;

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
        // Create explosion effect
        this.createScaledExplosion();
        super.onHit(enemy);
    }

    createScaledExplosion() {
        // Main explosion at impact point
        this.createFireExplosion(this.x, this.y);

        // For higher levels, add additional explosion points
        if (this.magicLevel >= 2) {
            const explosionRadius = 5 + (this.magicLevel * 2);
            const numExplosions = Math.min(8, this.magicLevel * 2);

            for (let i = 0; i < numExplosions; i++) {
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * explosionRadius;

                const ex = this.x + Math.cos(angle) * distance;
                const ey = this.y + Math.sin(angle) * distance;

                this.createFireExplosion(ex, ey);
            }
        }
    }

    createFireExplosion(x, y) {
        const particleCount = 15 + Math.floor(Math.random() * 11);

        for (let i = 0; i < particleCount; i++) {
            const angle = Math.random() * Math.PI * 2;
            const dirX = Math.cos(angle);
            const dirY = Math.sin(angle);
            const distance = Math.random() * 8;

            const startX = x + dirX * distance;
            const startY = y + dirY * distance;

            const size = 3 + Math.random() * 5;
            const r = 255;
            const g = 50 + Math.floor(Math.random() * 150);
            const b = Math.floor(Math.random() * 50);

            this.particles.push({
                x: startX,
                y: startY,
                vx: dirX * (1 + Math.random() * 2),
                vy: dirY * (1 + Math.random() * 2),
                size: size,
                color: `rgb(${r}, ${g}, ${b})`,
                life: 10 + Math.floor(Math.random() * 10),
                isExplosion: true
            });
        }
    }

    // Override to also update explosion particles
    renderExplosionParticles(ctx) {
        for (const p of this.particles) {
            if (p.isExplosion) {
                // Move explosion particles
                if (p.vx !== undefined) {
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vx *= 0.95;
                    p.vy *= 0.95;
                }
            }

            const alpha = Math.min(1, p.life / 10);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = alpha;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;
    }
}

// Export
window.Projectile = Projectile;
window.Firebolt = Firebolt;
