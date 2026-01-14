/**
 * Soul - Experience orb that can be collected by the player
 * Dropped by enemies when they die
 */
class Soul {
    constructor(x, y, value = 1) {
        // Position
        this.x = x;
        this.y = y;

        // Visual size (30% of original)
        this.width = 6;
        this.height = 6;

        // Value (XP amount)
        this.value = value;

        // Attraction properties
        this.attractionRadius = 100;  // Distance at which soul starts getting attracted to player
        this.collectionRadius = 10;   // Distance at which soul is collected
        this.maxAttractionSpeed = 3.0; // Maximum speed when close to player

        // Animation properties
        this.bobOffset = 0;
        this.bobSpeed = 0.05;
        this.bobDirection = 1;
        this.bobMax = 1.5;
        this.rotation = 0;
        this.rotationSpeed = 1;

        // Particle effects
        this.particles = [];
        this.particleTimer = 0;
        this.particleInterval = 5; // Frames between particle creation

        // Glow effect
        this.glowSize = 9;
        this.glowAlpha = 160;
        this.pulseCounter = 0;
        this.pulseSpeed = 0.02;

        // State
        this.collected = false;
        this.shouldRemove = false;

        // Debug flag
        this.debugShowRadius = false;

        // Cached rect for collision detection (avoids object allocation)
        this._rect = { x: 0, y: 0, width: 0, height: 0 };
    }

    update(player) {
        if (this.collected) {
            this.shouldRemove = true;
            return true;
        }

        // Bobbing motion
        this.bobOffset += this.bobSpeed * this.bobDirection;
        if (Math.abs(this.bobOffset) >= this.bobMax) {
            this.bobDirection *= -1;
        }

        // Rotation
        this.rotation = (this.rotation + this.rotationSpeed) % 360;

        // Update glow effect
        this.pulseCounter += this.pulseSpeed;
        this.glowAlpha = 120 + Math.floor(40 * Math.sin(this.pulseCounter));

        // Create particles occasionally
        this.particleTimer++;
        if (this.particleTimer >= this.particleInterval) {
            this.particleTimer = 0;
            this.createParticle();
        }

        // Update particles
        this.particles = this.particles.filter(p => {
            p.life--;
            return p.life > 0;
        });

        // Check for player proximity and handle attraction/collection
        if (player) {
            const playerRect = player.getRect();
            const playerCenterX = playerRect.x + playerRect.width / 2;
            const playerCenterY = playerRect.y + playerRect.height / 2;

            const soulCenterX = this.x + this.width / 2;
            const soulCenterY = this.y + this.height / 2;

            const dx = playerCenterX - soulCenterX;
            const dy = playerCenterY - soulCenterY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // If within attraction radius, move toward player
            if (distance < this.attractionRadius) {
                // Calculate normalized direction vector
                let ndx = 0, ndy = 0;
                if (distance > 0) {
                    ndx = dx / distance;
                    ndy = dy / distance;
                }

                // Speed increases as soul gets closer to player
                const attractionFactor = 1.0 - (distance / this.attractionRadius);
                const speed = this.maxAttractionSpeed * attractionFactor;

                // Move soul toward player
                this.x += ndx * speed;
                this.y += ndy * speed;

                // Create extra particles when being attracted
                if (Math.random() < 0.3) {
                    this.createParticle();
                }
            }

            // If very close to player, collect
            if (distance < this.collectionRadius) {
                this.collect(player);
                return true;
            }
        }

        return false;
    }

    createParticle() {
        // Random position around the soul
        const angle = Math.random() * Math.PI * 2;
        const distance = 1.5 + Math.random();

        const posX = this.x + 3 + Math.cos(angle) * distance;
        const posY = this.y + 3 + Math.sin(angle) * distance;

        // Random size
        const size = 1 + Math.floor(Math.random() * 2);

        // Blue-white color for soul particles
        const blue = 150 + Math.floor(Math.random() * 80);

        this.particles.push({
            x: posX,
            y: posY,
            size: size,
            color: `rgb(180, 220, ${blue})`,
            life: 10 + Math.floor(Math.random() * 10)
        });
    }

    collect(player) {
        // Add XP to player
        player.gainXp(this.value);

        // Create golden XP particles at player position
        if (window.particleSystem) {
            const playerRect = player.getRect();
            const playerCenterX = playerRect.x + playerRect.width / 2;
            const playerCenterY = playerRect.y + playerRect.height / 2;
            window.particleSystem.createXpParticles(playerCenterX, playerCenterY, this.value);
        }

        // Clear all particles
        this.particles = [];

        // Mark as collected
        this.collected = true;
        this.shouldRemove = true;

        console.log(`Soul collected! Player gained ${this.value} XP`);
    }

    getRect() {
        this._rect.x = this.x;
        this._rect.y = this.y;
        this._rect.width = this.width;
        this._rect.height = this.height;
        return this._rect;
    }

    isCollectible() {
        return true;
    }

    render(ctx, game) {
        if (this.collected) return;

        // Draw glow
        const gradient = ctx.createRadialGradient(
            this.x + 3, this.y + 3 + this.bobOffset, 0,
            this.x + 3, this.y + 3 + this.bobOffset, this.glowSize / 2
        );
        gradient.addColorStop(0, `rgba(100, 200, 255, ${this.glowAlpha / 255})`);
        gradient.addColorStop(1, 'rgba(100, 200, 255, 0)');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x + 3, this.y + 3 + this.bobOffset, this.glowSize / 2, 0, Math.PI * 2);
        ctx.fill();

        // Draw particles behind the soul
        for (const particle of this.particles) {
            ctx.fillStyle = particle.color;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw soul orb
        ctx.save();
        ctx.translate(this.x + 3, this.y + 3 + this.bobOffset);
        ctx.rotate(this.rotation * Math.PI / 180);

        // Inner core (bright blue)
        ctx.fillStyle = 'rgb(100, 200, 255)';
        ctx.beginPath();
        ctx.arc(0, 0, 2, 0, Math.PI * 2);
        ctx.fill();

        // Outer glow
        ctx.fillStyle = 'rgba(150, 230, 255, 0.7)';
        ctx.beginPath();
        ctx.arc(0, 0, 3, 0, Math.PI * 2);
        ctx.fill();

        // Highlight
        ctx.fillStyle = 'rgba(220, 240, 255, 0.8)';
        ctx.beginPath();
        ctx.arc(-1, -1, 1, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Debug: Draw attraction/collection radius
        if (this.debugShowRadius || (game && game.showDebug)) {
            ctx.strokeStyle = 'rgba(0, 255, 0, 0.3)';
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.attractionRadius, 0, Math.PI * 2);
            ctx.stroke();

            ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.collectionRadius, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

// Export
window.Soul = Soul;
