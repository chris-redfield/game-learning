/**
 * Bonfire - Healing station and save point
 * Mirrors Python entities/bonfire.py
 */
class Bonfire {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 48;
        this.height = 48;

        // Bonfire is an obstacle - player cannot walk through it
        this.isObstacle = true;

        // Animation
        this.frameIndex = 0;
        this.animationTimer = 0;
        this.frameCount = 4;
        this.animationSpeed = 10; // Frames between animation updates

        // Healing effect
        this.healParticlesActive = false;
        this.healParticlesTimer = 0;

        // Block coordinates
        this.blockX = 0;
        this.blockY = 0;

        // Save/load callback (set by main.js for origin bonfire)
        this.saveLoadCallback = null;

        // Load sprites
        this.sprites = [];
        this.loadSprites();
    }

    async loadSprites() {
        try {
            const img = new Image();
            img.src = 'assets/bonfire-sprites.png';

            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });

            // Frame positions in the sprite sheet
            const frameWidth = 32;
            const frameHeight = 32;
            const framePositions = [0, 32, 64, 96];

            // Create offscreen canvas for each frame
            for (const xPos of framePositions) {
                const canvas = document.createElement('canvas');
                canvas.width = this.width;
                canvas.height = this.height;
                const ctx = canvas.getContext('2d');

                // Draw and scale frame
                ctx.drawImage(
                    img,
                    xPos, 0, frameWidth, frameHeight,
                    0, 0, this.width, this.height
                );

                this.sprites.push(canvas);
            }

            console.log('Bonfire sprites loaded');
        } catch (e) {
            console.log('Could not load bonfire sprites, using placeholder');
            // Create placeholder
            const canvas = document.createElement('canvas');
            canvas.width = this.width;
            canvas.height = this.height;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = 'rgb(200, 100, 0)';
            ctx.fillRect(0, 0, this.width, this.height);
            this.sprites = [canvas];
        }
    }

    getRect() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    setBlockCoordinates(x, y) {
        this.blockX = x;
        this.blockY = y;
    }

    isOriginBonfire() {
        return this.blockX === 0 && this.blockY === 0;
    }

    update(dt, currentTime) {
        // Update animation
        this.animationTimer++;
        if (this.animationTimer >= this.animationSpeed) {
            this.frameIndex = (this.frameIndex + 1) % (this.sprites.length || 1);
            this.animationTimer = 0;
        }

        // Update heal particles
        if (this.healParticlesActive) {
            this.healParticlesTimer++;
            if (this.healParticlesTimer > 60) {
                this.healParticlesActive = false;
                this.healParticlesTimer = 0;
            }
        }
    }

    interact(player, currentTime) {
        console.log('Bonfire interact method called!');

        // Calculate heal amount
        const healAmount = player.attributes.maxHealth - player.attributes.currentHealth;

        console.log(`Player health before: ${player.attributes.currentHealth}/${player.attributes.maxHealth}`);

        let healed = false;
        if (healAmount > 0) {
            player.heal(healAmount);
            this.healParticlesActive = true;
            this.healParticlesTimer = 0;
            console.log(`Bonfire healed player for ${healAmount} HP`);
            healed = true;
        } else {
            console.log('Player already at full health');
        }

        // Restore mana to full as well
        const manaAmount = player.attributes.maxMana - player.attributes.currentMana;
        if (manaAmount > 0) {
            player.attributes.restoreMana(manaAmount);
            console.log(`Bonfire restored ${manaAmount} mana`);
        }

        // If this is the origin bonfire, show save/load dialog
        if (this.isOriginBonfire() && this.saveLoadCallback) {
            console.log('Origin bonfire - showing save/load dialog');
            this.saveLoadCallback();
        }

        return healed || this.isOriginBonfire();
    }

    render(ctx, game) {
        // Draw current frame
        if (this.sprites.length > 0) {
            const frame = this.sprites[this.frameIndex % this.sprites.length];
            ctx.drawImage(frame, this.x, this.y);
        } else {
            // Placeholder
            ctx.fillStyle = 'rgb(255, 100, 0)';
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        // Draw heal particles if active
        if (this.healParticlesActive) {
            const centerX = this.x + this.width / 2;
            const centerY = this.y + this.height / 2;

            for (let i = 0; i < 8; i++) {
                const particleSize = 3 + (this.healParticlesTimer % 3);
                const angle = i * Math.PI / 4;
                const distance = 20 + this.healParticlesTimer / 5;
                const particleX = centerX + Math.cos(angle) * distance;
                const particleY = centerY + Math.sin(angle) * distance - this.healParticlesTimer / 3;

                ctx.fillStyle = 'rgb(100, 255, 100)';
                ctx.beginPath();
                ctx.arc(particleX, particleY, particleSize, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Draw debug collision box when C is held
        if (game && game.showDebug) {
            const rect = this.getRect();
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 2;
            ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
        }
    }
}

// Export
window.Bonfire = Bonfire;
