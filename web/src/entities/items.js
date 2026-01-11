/**
 * Item - Base class for all items in the game
 * Mirrors Python items/item.py
 */
class Item {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 32;
        this.height = 32;
        this.name = "Generic Item";
        this.description = "An item in the game world";
        this.collected = false;
        this.stackable = true;
        this.oneTimeUse = false;

        // Animation properties
        this.bobHeight = 4;
        this.bobSpeed = 0.03;
        this.bobOffset = 0;
        this.bobCounter = 0;

        // Sprite (subclasses should override)
        this.sprite = null;
        this.icon = null;
    }

    getRect() {
        return {
            x: this.x,
            y: this.y + this.bobOffset,
            width: this.width,
            height: this.height
        };
    }

    update(player = null) {
        // Update bobbing animation
        this.bobCounter += this.bobSpeed;
        this.bobOffset = Math.floor(this.bobHeight * Math.sin(this.bobCounter));

        // Check for collection if player is provided
        if (player && !this.collected) {
            const playerRect = player.getRect();
            const itemRect = this.getRect();

            // Expand player rect for easier pickup
            const expanded = {
                x: playerRect.x - 4,
                y: playerRect.y - 4,
                width: playerRect.width + 8,
                height: playerRect.height + 8
            };

            if (this.rectsOverlap(expanded, itemRect)) {
                return this.collect(player);
            }
        }
        return false;
    }

    rectsOverlap(r1, r2) {
        return r1.x < r2.x + r2.width &&
               r1.x + r1.width > r2.x &&
               r1.y < r2.y + r2.height &&
               r1.y + r1.height > r2.y;
    }

    draw(ctx) {
        if (this.collected) return;

        if (this.sprite) {
            ctx.drawImage(this.sprite, this.x, this.y + this.bobOffset, this.width, this.height);
        } else {
            // Default gray placeholder
            ctx.fillStyle = 'rgb(200, 200, 200)';
            ctx.fillRect(this.x, this.y + this.bobOffset, this.width, this.height);
        }
    }

    render(ctx, game) {
        this.draw(ctx);
    }

    collect(player) {
        if (this.collected) return false;

        // Try to add item to player inventory
        if (player.inventory) {
            if (player.inventory.addItem(this)) {
                this.collected = true;
                console.log(`Collected ${this.name}`);
                return true;
            } else {
                console.log(`Could not collect ${this.name} - inventory full`);
                return false;
            }
        } else {
            this.collected = true;
            console.log(`Collected ${this.name} (no inventory)`);
            return true;
        }
    }

    use(player) {
        // Base use method - to be implemented by subclasses
        return false;
    }
}

/**
 * AncientScroll - Reduces XP multiplier from 1.5 to 1.3
 * Mirrors Python items/ancient_scroll.py
 */
class AncientScroll extends Item {
    constructor(x, y) {
        super(x, y);
        this.name = "Ancient Scroll";
        this.description = "A weathered scroll with arcane knowledge that enhances your learning (Effect applied on pickup)";
        this.oneTimeUse = true;  // Can't be used from inventory
        this.stackable = false;

        this.width = 40;
        this.height = 40;

        // Different bobbing properties
        this.bobHeight = 3;
        this.bobSpeed = 0.025;

        // Glow effect
        this.glowCounter = 0;
        this.glowSpeed = 0.02;
        this.glowIntensity = 0;

        // Create placeholder sprite (canvas-based)
        this.createSprite();
    }

    createSprite() {
        // Create an offscreen canvas for the sprite
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');

        // Draw a scroll shape
        const scrollColor = 'rgb(220, 190, 120)';  // Parchment color
        const edgeColor = 'rgb(180, 140, 80)';     // Darker edge
        const lineColor = 'rgb(60, 40, 20)';       // Text color

        // Main scroll body
        ctx.fillStyle = scrollColor;
        ctx.fillRect(5, 5, 30, 30);

        // Scroll edges
        ctx.strokeStyle = edgeColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(3, 3, 34, 34);

        // Text lines
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 1;
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.moveTo(10, 10 + i * 5);
            ctx.lineTo(30, 10 + i * 5);
            ctx.stroke();
        }

        this.sprite = canvas;
    }

    update(player = null) {
        super.update(null);  // Update bobbing

        if (!this.collected) {
            // Update glow effect
            this.glowCounter += this.glowSpeed;
            this.glowIntensity = Math.abs(Math.sin(this.glowCounter)) * 0.5;

            // Check for collection
            if (player) {
                const playerRect = player.getRect();
                const itemRect = this.getRect();
                const expanded = {
                    x: playerRect.x - 4,
                    y: playerRect.y - 4,
                    width: playerRect.width + 8,
                    height: playerRect.height + 8
                };

                if (this.rectsOverlap(expanded, itemRect)) {
                    return this.collect(player);
                }
            }
        }
        return false;
    }

    draw(ctx) {
        if (this.collected) return;

        // Draw glow effect
        if (this.glowIntensity > 0) {
            const glowSize = 6;
            ctx.save();
            ctx.globalAlpha = this.glowIntensity * 0.4;
            ctx.fillStyle = 'rgb(255, 220, 100)';
            ctx.beginPath();
            ctx.arc(
                this.x + this.width / 2,
                this.y + this.bobOffset + this.height / 2,
                this.width / 2 + glowSize,
                0,
                Math.PI * 2
            );
            ctx.fill();
            ctx.restore();
        }

        // Draw the scroll
        if (this.sprite) {
            ctx.drawImage(this.sprite, this.x, this.y + this.bobOffset);
        }
    }

    render(ctx, game) {
        this.draw(ctx);
    }

    collect(player) {
        if (this.collected) return false;

        // Try to activate the scroll effect
        let effectApplied = false;
        if (player.attributes && player.attributes.findAncientScroll) {
            effectApplied = player.attributes.findAncientScroll();

            if (effectApplied) {
                console.log(`Obtained the ${this.name}! Your mind expands with ancient knowledge.`);
                console.log("XP requirements are now reduced! (Using 1.3x progression)");

                // Add to inventory
                if (player.inventory) {
                    player.inventory.addItem(this);
                }
            } else {
                console.log("You already possess this knowledge.");
            }
        }

        this.collected = true;
        return true;
    }

    use(player) {
        return `The ${this.name} has already imparted its knowledge to you.`;
    }
}

/**
 * DragonHeart - Reduces XP multiplier to 1.2
 * Mirrors Python items/dragon_heart.py
 */
class DragonHeart extends Item {
    constructor(x, y) {
        super(x, y);
        this.name = "Dragon Heart";
        this.description = "The still-beating heart of an ancient dragon, pulsing with magical energy (Effect applied on pickup)";
        this.oneTimeUse = true;
        this.stackable = false;

        this.width = 36;
        this.height = 36;

        // Heart beat effect
        this.bobHeight = 2;
        this.bobSpeed = 0.04;
        this.beatCounter = Math.random() * Math.PI;
        this.beatSpeed = 0.03;
        this.beatSize = 1.0;

        // Particles
        this.particles = [];
        this.particleTimer = 0;

        this.createSprite();
    }

    createSprite() {
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');

        // Draw a heart shape
        const heartColor = 'rgb(200, 30, 30)';
        const highlightColor = 'rgb(250, 100, 100)';

        ctx.fillStyle = heartColor;

        // Two circles for top of heart
        ctx.beginPath();
        ctx.arc(10, 15, 8, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(26, 15, 8, 0, Math.PI * 2);
        ctx.fill();

        // Triangle for bottom
        ctx.beginPath();
        ctx.moveTo(4, 18);
        ctx.lineTo(this.width / 2, 32);
        ctx.lineTo(this.width - 4, 18);
        ctx.closePath();
        ctx.fill();

        // Highlight
        ctx.fillStyle = highlightColor;
        ctx.beginPath();
        ctx.arc(12, 12, 3, 0, Math.PI * 2);
        ctx.fill();

        this.sprite = canvas;
    }

    update(player = null) {
        super.update(null);

        // Update heartbeat effect
        this.beatCounter += this.beatSpeed;
        this.beatSize = 1.0 + 0.1 * Math.abs(Math.sin(this.beatCounter));

        // Update particles
        this.updateParticles();

        // Create new particles
        this.particleTimer++;
        if (this.particleTimer >= 10 && !this.collected) {
            this.particleTimer = 0;
            this.createParticle();
        }

        // Check for collection
        if (player && !this.collected) {
            const playerRect = player.getRect();
            const itemRect = this.getRect();
            const expanded = {
                x: playerRect.x - 4,
                y: playerRect.y - 4,
                width: playerRect.width + 8,
                height: playerRect.height + 8
            };

            if (this.rectsOverlap(expanded, itemRect)) {
                return this.collect(player);
            }
        }
        return false;
    }

    createParticle() {
        const startX = this.x + 8 + Math.random() * (this.width - 16);
        const startY = this.y + 8 + Math.random() * (this.height - 16);

        this.particles.push({
            x: startX,
            y: startY,
            size: 2 + Math.random() * 2,
            speedX: (Math.random() - 0.5) * 0.4,
            speedY: -0.2 - Math.random() * 0.3,
            life: 30 + Math.random() * 30,
            maxLife: 30 + Math.random() * 30,
            color: {
                r: 200 + Math.floor(Math.random() * 55),
                g: 20 + Math.floor(Math.random() * 60),
                b: 20 + Math.floor(Math.random() * 60)
            }
        });
    }

    updateParticles() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.speedX;
            p.y += p.speedY;
            p.life--;

            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }

    draw(ctx) {
        if (this.collected) return;

        // Draw particles
        for (const p of this.particles) {
            const alpha = p.life / p.maxLife;
            ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${alpha})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw heart with beat effect
        if (this.sprite) {
            const scaledWidth = Math.floor(this.width * this.beatSize);
            const scaledHeight = Math.floor(this.height * this.beatSize);
            const xOffset = (scaledWidth - this.width) / 2;
            const yOffset = (scaledHeight - this.height) / 2;

            ctx.drawImage(
                this.sprite,
                this.x - xOffset,
                this.y + this.bobOffset - yOffset,
                scaledWidth,
                scaledHeight
            );
        }
    }

    render(ctx, game) {
        this.draw(ctx);
    }

    collect(player) {
        if (this.collected) return false;

        let effectApplied = false;
        if (player.attributes && player.attributes.findDragonHeart) {
            effectApplied = player.attributes.findDragonHeart();

            if (effectApplied) {
                console.log(`Obtained the ${this.name}! Its power flows through your veins.`);
                console.log("Your magical abilities are enhanced!");

                if (player.inventory) {
                    player.inventory.addItem(this);
                }
            } else {
                console.log("You cannot absorb any more dragon hearts.");
            }
        }

        this.collected = true;
        return true;
    }

    use(player) {
        return `The ${this.name} has already been absorbed into your being.`;
    }
}

/**
 * HealthPotion - Restores health when used
 * Mirrors Python items/health_potion.py
 */
class HealthPotion extends Item {
    constructor(x, y) {
        super(x, y);
        this.name = "Health Potion";
        this.description = "Restores 15 health when consumed";
        this.healAmount = 15;
        this.stackable = true;
        this.oneTimeUse = false;  // Can be used from inventory

        this.createSprite();
    }

    createSprite() {
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');

        // Draw a potion bottle
        const bottleColor = 'rgb(220, 50, 50)';
        const capColor = 'rgb(150, 150, 150)';
        const shineColor = 'rgb(250, 200, 200)';

        // Bottle body
        ctx.fillStyle = bottleColor;
        ctx.fillRect(8, 12, 16, 16);

        // Bottle neck
        ctx.fillRect(10, 6, 12, 6);

        // Bottle cap
        ctx.fillStyle = capColor;
        ctx.fillRect(11, 4, 10, 2);

        // Shine effect
        ctx.fillStyle = shineColor;
        ctx.beginPath();
        ctx.arc(12, 15, 2, 0, Math.PI * 2);
        ctx.fill();

        this.sprite = canvas;
    }

    use(player) {
        if (player.attributes.currentHealth < player.attributes.maxHealth) {
            player.attributes.currentHealth = Math.min(
                player.attributes.currentHealth + this.healAmount,
                player.attributes.maxHealth
            );
            return true;  // Item was used successfully
        } else {
            return "Health is already full!";
        }
    }
}

// Export
window.Item = Item;
window.AncientScroll = AncientScroll;
window.DragonHeart = DragonHeart;
window.HealthPotion = HealthPotion;
