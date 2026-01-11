/**
 * Particle System - Manages all game particles (blood, fire, XP, etc.)
 * Mirrors Python entities/player/particles.py
 */
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.bloodParticles = [];
        this.maxParticles = 500;
    }

    /**
     * Create fire trail particles behind projectile
     */
    createFireTrail(x, y, size = null, life = null) {
        if (size === null) size = 2 + Math.random() * 2;
        if (life === null) life = 3 + Math.floor(Math.random() * 4);

        for (let i = 0; i < 2; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                size: size,
                color: { r: 255, g: 50 + Math.floor(Math.random() * 100), b: 0 },
                life: life,
                maxLife: life,
                type: 'fire'
            });
        }
    }

    /**
     * Create fire explosion at impact point
     */
    createFireExplosion(x, y) {
        const particleCount = 15 + Math.floor(Math.random() * 11);

        // Main fire particles
        for (let i = 0; i < particleCount; i++) {
            const angle = Math.random() * Math.PI * 2;
            const dirX = Math.cos(angle);
            const dirY = Math.sin(angle);
            const distance = Math.random() * 8;

            const velocityMult = 0.8 + Math.random() * 1.7;

            this.particles.push({
                x: x + dirX * distance,
                y: y + dirY * distance,
                vx: dirX * velocityMult,
                vy: dirY * velocityMult,
                size: 3 + Math.random() * 5,
                color: { r: 255, g: 50 + Math.floor(Math.random() * 150), b: Math.floor(Math.random() * 50) },
                life: 10 + Math.floor(Math.random() * 15),
                maxLife: 25,
                type: 'fire'
            });
        }

        // Embers/sparks
        for (let i = 0; i < 5; i++) {
            const angle = Math.random() * Math.PI * 2;
            const velocityMult = 2.0 + Math.random() * 1.5;

            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * velocityMult,
                vy: Math.sin(angle) * velocityMult,
                size: 1 + Math.random() * 2,
                color: { r: 255, g: 255, b: 100 + Math.floor(Math.random() * 100) },
                life: 5 + Math.floor(Math.random() * 10),
                maxLife: 15,
                type: 'ember'
            });
        }

        // Central flash
        this.particles.push({
            x: x,
            y: y,
            vx: 0,
            vy: 0,
            size: 10 + Math.random() * 5,
            color: { r: 255, g: 255, b: 200 },
            life: 3 + Math.floor(Math.random() * 5),
            maxLife: 8,
            type: 'flash'
        });
    }

    /**
     * Spawn blood particles from enemy when hit
     */
    spawnEnemyBlood(enemy, playerX, playerY) {
        // Direction from player to enemy
        const enemyCenterX = enemy.x + enemy.width / 2;
        const enemyCenterY = enemy.y + enemy.height / 2;

        let dirX = enemyCenterX - playerX;
        let dirY = enemyCenterY - playerY;

        // Normalize
        const length = Math.max(0.1, Math.sqrt(dirX * dirX + dirY * dirY));
        dirX /= length;
        dirY /= length;

        // Impact point on enemy facing player
        const impactOffset = Math.min(enemy.width, enemy.height) * 0.4;
        const impactX = enemyCenterX - dirX * impactOffset;
        const impactY = enemyCenterY - dirY * impactOffset;

        // Create particles
        const particleCount = 8 + Math.floor(Math.random() * 5);

        for (let i = 0; i < particleCount; i++) {
            // Angle biased away from player
            const baseAngle = Math.atan2(dirY, dirX);
            const angleVariation = (Math.random() - 0.5) * 1.4; // +/- 40 degrees
            const angle = baseAngle + angleVariation;

            const particleDirX = Math.cos(angle);
            const particleDirY = Math.sin(angle);

            // Random offset from impact point
            const randOffset = 3.0;
            const startX = impactX + (Math.random() - 0.5) * randOffset * 2;
            const startY = impactY + (Math.random() - 0.5) * randOffset * 2;

            const speed = 1.0 + Math.random() * 3.0;
            const size = 4 + Math.floor(Math.random() * 5);

            this.bloodParticles.push({
                x: startX,
                y: startY,
                vx: particleDirX * speed,
                vy: particleDirY * speed,
                size: size,
                color: { r: 120 + Math.floor(Math.random() * 100), g: Math.floor(Math.random() * 30), b: Math.floor(Math.random() * 30) },
                life: 15 + Math.floor(Math.random() * 15),
                maxLife: 30,
                gravity: 0.2,
                friction: 0.95,
                stuck: false
            });
        }
    }

    /**
     * Create XP gain particles
     */
    createXpParticles(x, y, amount) {
        const particleCount = Math.min(20, amount * 5);

        for (let i = 0; i < particleCount; i++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = 10 + Math.random() * 20;

            this.particles.push({
                x: x + Math.cos(angle) * distance,
                y: y + Math.sin(angle) * distance,
                vx: 0,
                vy: -0.5 - Math.random(),
                size: 2 + Math.floor(Math.random() * 3),
                color: { r: 255, g: 215, b: 0 },
                life: 10 + Math.floor(Math.random() * 10),
                maxLife: 20,
                type: 'xp'
            });
        }
    }

    /**
     * Update all particles
     */
    update(obstacles = []) {
        // Update fire/effect particles
        this.particles = this.particles.filter(p => {
            // Move particle
            p.x += p.vx;
            p.y += p.vy;

            // Apply friction to velocity
            p.vx *= 0.95;
            p.vy *= 0.95;

            // Decrease life
            p.life--;

            // Shrink over time
            if (p.type === 'fire' || p.type === 'ember') {
                p.size *= 0.97;
            }

            return p.life > 0 && p.size > 0.5;
        });

        // Update blood particles
        this.bloodParticles = this.bloodParticles.filter(p => {
            if (p.stuck) {
                p.life--;
                return p.life > 0;
            }

            // Apply gravity
            p.vy += p.gravity;

            // Apply friction
            p.vx *= p.friction;
            p.vy *= p.friction;

            // Move
            p.x += p.vx;
            p.y += p.vy;

            // Check collision with obstacles
            for (const obs of obstacles) {
                if (obs.getRect) {
                    const rect = obs.getRect();
                    if (p.x >= rect.x && p.x <= rect.x + rect.width &&
                        p.y >= rect.y && p.y <= rect.y + rect.height) {
                        p.stuck = true;
                        break;
                    }
                }
            }

            p.life--;
            return p.life > 0;
        });

        // Cap particles
        if (this.particles.length > this.maxParticles) {
            this.particles = this.particles.slice(-this.maxParticles);
        }
        if (this.bloodParticles.length > this.maxParticles) {
            this.bloodParticles = this.bloodParticles.slice(-this.maxParticles);
        }
    }

    /**
     * Render all particles
     */
    render(ctx) {
        // Draw fire/effect particles
        for (const p of this.particles) {
            const alpha = Math.min(1, p.life / p.maxLife);
            ctx.globalAlpha = alpha;
            ctx.fillStyle = `rgb(${p.color.r}, ${p.color.g}, ${p.color.b})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw blood particles
        for (const p of this.bloodParticles) {
            const fadeStart = p.maxLife / 2;
            let alpha = 1;
            if (p.life < fadeStart) {
                alpha = p.life / fadeStart;
            }
            ctx.globalAlpha = alpha;
            ctx.fillStyle = `rgb(${p.color.r}, ${p.color.g}, ${p.color.b})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size / 2, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.globalAlpha = 1;
    }

    /**
     * Clear all particles (e.g., on block transition)
     */
    clear() {
        this.particles = [];
        this.bloodParticles = [];
    }
}

// Global instance
window.particleSystem = new ParticleSystem();
