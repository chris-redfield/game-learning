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

        // Sprite (subclasses should load their own)
        this.sprite = null;
        this.spriteLoaded = false;
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

        if (this.sprite && this.spriteLoaded) {
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

    /**
     * Load an image and return a promise
     */
    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load ${src}`));
            img.src = src;
        });
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
        this.oneTimeUse = false;

        // Rotation properties (matching Python)
        this.rotationAngle = -45;  // 45 degrees counter-clockwise
        this.originalSprite = null;
        this.rotatedCanvas = null;

        // Load the sprite
        this.loadSprite();
    }

    async loadSprite() {
        try {
            const img = await this.loadImage('assets/health-potion.png');
            console.log("Health potion sprite loaded successfully");

            // Create scaled original sprite canvas
            this.originalSprite = document.createElement('canvas');
            this.originalSprite.width = this.width;
            this.originalSprite.height = this.height;
            const origCtx = this.originalSprite.getContext('2d');
            origCtx.drawImage(img, 0, 0, this.width, this.height);

            // Create rotated sprite canvas
            // When rotating, the canvas needs to be larger to fit the rotated image
            const radians = this.rotationAngle * Math.PI / 180;
            const sin = Math.abs(Math.sin(radians));
            const cos = Math.abs(Math.cos(radians));
            const rotatedWidth = Math.ceil(this.width * cos + this.height * sin);
            const rotatedHeight = Math.ceil(this.width * sin + this.height * cos);

            this.rotatedCanvas = document.createElement('canvas');
            this.rotatedCanvas.width = rotatedWidth;
            this.rotatedCanvas.height = rotatedHeight;
            const rotCtx = this.rotatedCanvas.getContext('2d');

            // Rotate around center
            rotCtx.translate(rotatedWidth / 2, rotatedHeight / 2);
            rotCtx.rotate(radians);
            rotCtx.drawImage(this.originalSprite, -this.width / 2, -this.height / 2);

            this.sprite = this.rotatedCanvas;
            this.spriteLoaded = true;
        } catch (e) {
            console.log(`Error loading health potion sprite: ${e}`);
            this.createPlaceholder();
        }
    }

    createPlaceholder() {
        // Create a red potion placeholder (matching Python)
        this.originalSprite = document.createElement('canvas');
        this.originalSprite.width = this.width;
        this.originalSprite.height = this.height;
        const ctx = this.originalSprite.getContext('2d');

        // Draw a potion bottle shape
        const bottleColor = 'rgb(220, 50, 50)';
        ctx.fillStyle = bottleColor;
        ctx.fillRect(8, 12, 16, 16);  // Bottle body
        ctx.fillRect(10, 6, 12, 6);   // Bottle neck
        ctx.fillStyle = 'rgb(150, 150, 150)';
        ctx.fillRect(11, 4, 10, 2);   // Bottle cap

        // Add a shine effect
        ctx.fillStyle = 'rgb(250, 200, 200)';
        ctx.beginPath();
        ctx.arc(12, 15, 2, 0, Math.PI * 2);
        ctx.fill();

        // Create rotated version
        const radians = this.rotationAngle * Math.PI / 180;
        const sin = Math.abs(Math.sin(radians));
        const cos = Math.abs(Math.cos(radians));
        const rotatedWidth = Math.ceil(this.width * cos + this.height * sin);
        const rotatedHeight = Math.ceil(this.width * sin + this.height * cos);

        this.rotatedCanvas = document.createElement('canvas');
        this.rotatedCanvas.width = rotatedWidth;
        this.rotatedCanvas.height = rotatedHeight;
        const rotCtx = this.rotatedCanvas.getContext('2d');

        rotCtx.translate(rotatedWidth / 2, rotatedHeight / 2);
        rotCtx.rotate(radians);
        rotCtx.drawImage(this.originalSprite, -this.width / 2, -this.height / 2);

        this.sprite = this.rotatedCanvas;
        this.spriteLoaded = true;
    }

    draw(ctx) {
        if (this.collected) return;

        if (this.sprite && this.spriteLoaded) {
            // Get the size difference due to rotation
            const offsetX = (this.sprite.width - this.width) / 2;
            const offsetY = (this.sprite.height - this.height) / 2;

            // Draw with bobbing animation effect and adjusted position for rotation
            ctx.drawImage(this.sprite, this.x - offsetX, this.y + this.bobOffset - offsetY);
        } else {
            // Fallback while loading
            ctx.fillStyle = 'rgb(220, 50, 50)';
            ctx.fillRect(this.x, this.y + this.bobOffset, this.width, this.height);
        }
    }

    render(ctx, game) {
        this.draw(ctx);
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

    getRect() {
        if (!this.sprite || !this.spriteLoaded) {
            return super.getRect();
        }

        // For rotated potions, account for rotation in collision
        const rotatedWidth = Math.floor(this.sprite.width * 0.9);
        const rotatedHeight = Math.floor(this.sprite.height * 0.9);

        const offsetX = (this.sprite.width - this.width) / 2;
        const offsetY = (this.sprite.height - this.height) / 2;

        return {
            x: this.x - offsetX + (this.sprite.width - rotatedWidth) / 2,
            y: this.y + this.bobOffset - offsetY + (this.sprite.height - rotatedHeight) / 2,
            width: rotatedWidth,
            height: rotatedHeight
        };
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

        // Custom size for the scroll (matching Python)
        this.width = 40;
        this.height = 40;

        // Different bobbing properties (matching Python)
        this.bobHeight = 3;
        this.bobSpeed = 0.025;

        // Glow effect parameters
        this.glowCounter = 0;
        this.glowSpeed = 0.02;
        this.glowIntensity = 0;

        // Load the sprite
        this.loadSprite();
    }

    async loadSprite() {
        try {
            const img = await this.loadImage('assets/ancient_scroll.png');
            console.log("Ancient scroll sprite loaded successfully");

            // Create scaled sprite canvas
            this.sprite = document.createElement('canvas');
            this.sprite.width = this.width;
            this.sprite.height = this.height;
            const ctx = this.sprite.getContext('2d');
            ctx.drawImage(img, 0, 0, this.width, this.height);

            this.spriteLoaded = true;
        } catch (e) {
            console.log(`Error loading ancient scroll sprite: ${e}`);
            this.createPlaceholder();
        }
    }

    createPlaceholder() {
        // Create a scroll placeholder (matching Python)
        this.sprite = document.createElement('canvas');
        this.sprite.width = this.width;
        this.sprite.height = this.height;
        const ctx = this.sprite.getContext('2d');

        // Draw a scroll shape
        const scrollColor = 'rgb(220, 190, 120)';  // Parchment color
        const edgeColor = 'rgb(180, 140, 80)';     // Darker edge
        const lineColor = 'rgb(60, 40, 20)';       // Text color

        // Main scroll body with rounded corners
        ctx.fillStyle = scrollColor;
        ctx.beginPath();
        ctx.roundRect(5, 5, 30, 30, 2);
        ctx.fill();

        // Scroll edges
        ctx.strokeStyle = edgeColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(3, 3, 34, 34, 3);
        ctx.stroke();

        // Text lines
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 1;
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.moveTo(10, 10 + i * 5);
            ctx.lineTo(30, 10 + i * 5);
            ctx.stroke();
        }

        this.spriteLoaded = true;
    }

    update(player = null) {
        // Update bobbing animation
        this.bobCounter += this.bobSpeed;
        this.bobOffset = Math.floor(this.bobHeight * Math.sin(this.bobCounter));

        // Update glow effect
        if (!this.collected) {
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

        // Draw glow effect (matching Python)
        if (this.glowIntensity > 0 && this.spriteLoaded) {
            const glowSize = 6;
            ctx.save();
            ctx.globalAlpha = this.glowIntensity * 0.4;

            // Draw multiple circles for soft glow effect (matching Python)
            for (let radius = glowSize; radius > 0; radius--) {
                const alpha = this.glowIntensity * (radius / glowSize);
                ctx.globalAlpha = alpha * 0.3;
                ctx.fillStyle = 'rgb(255, 220, 100)';
                ctx.beginPath();
                ctx.arc(
                    this.x + this.width / 2,
                    this.y + this.bobOffset + this.height / 2,
                    radius + this.width / 2,
                    0,
                    Math.PI * 2
                );
                ctx.fill();
            }
            ctx.restore();
        }

        // Draw the scroll
        if (this.sprite && this.spriteLoaded) {
            ctx.drawImage(this.sprite, this.x, this.y + this.bobOffset);
        } else {
            // Fallback while loading
            ctx.fillStyle = 'rgb(220, 190, 120)';
            ctx.fillRect(this.x, this.y + this.bobOffset, this.width, this.height);
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

    getRect() {
        if (this.collected) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        return {
            x: this.x,
            y: this.y + this.bobOffset,
            width: this.width,
            height: this.height
        };
    }
}

/**
 * DragonHeart - Reduces XP multiplier to 1.2
 * Mirrors Python items/dragon_heart.py
 * Note: No asset exists for dragon_heart.png, so we use placeholder (same as Python)
 */
class DragonHeart extends Item {
    constructor(x, y) {
        super(x, y);
        this.name = "Dragon Heart";
        this.description = "The still-beating heart of an ancient dragon, pulsing with magical energy (Effect applied on pickup)";
        this.oneTimeUse = true;
        this.stackable = false;

        // Custom size (matching Python)
        this.width = 36;
        this.height = 36;

        // Heart beat effect (matching Python)
        this.bobHeight = 2;
        this.bobSpeed = 0.04;
        this.beatCounter = Math.random() * Math.PI;  // Start at random phase
        this.beatSpeed = 0.03;
        this.beatSize = 1.0;

        // Particles (matching Python)
        this.particles = [];
        this.particleTimer = 0;

        // Create placeholder sprite (no asset exists in Python either)
        this.createPlaceholder();
    }

    createPlaceholder() {
        // Create a heart placeholder (matching Python exactly)
        this.sprite = document.createElement('canvas');
        this.sprite.width = this.width;
        this.sprite.height = this.height;
        const ctx = this.sprite.getContext('2d');

        // Draw a heart shape (matching Python)
        const heartColor = 'rgb(200, 30, 30)';  // Deep red
        ctx.fillStyle = heartColor;

        // Draw two circles for top of heart
        ctx.beginPath();
        ctx.arc(10, 15, 8, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(26, 15, 8, 0, Math.PI * 2);
        ctx.fill();

        // Draw a triangle for the bottom of the heart
        ctx.beginPath();
        ctx.moveTo(4, 18);
        ctx.lineTo(this.width / 2, 32);
        ctx.lineTo(this.width - 4, 18);
        ctx.closePath();
        ctx.fill();

        // Add a highlight
        ctx.fillStyle = 'rgb(250, 100, 100)';
        ctx.beginPath();
        ctx.arc(12, 12, 3, 0, Math.PI * 2);
        ctx.fill();

        this.spriteLoaded = true;
    }

    update(player = null) {
        // Update bobbing animation
        this.bobCounter += this.bobSpeed;
        this.bobOffset = Math.floor(this.bobHeight * Math.sin(this.bobCounter));

        // Update heartbeat effect (matching Python)
        this.beatCounter += this.beatSpeed;
        this.beatSize = 1.0 + 0.1 * Math.abs(Math.sin(this.beatCounter));

        // Update particles
        this.updateParticles();

        // Create new particles (matching Python timing)
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
        // Matching Python particle creation
        const startX = this.x + 8 + Math.random() * (this.width - 16);
        const startY = this.y + 8 + Math.random() * (this.height - 16);

        this.particles.push({
            x: startX,
            y: startY,
            size: 2 + Math.floor(Math.random() * 3),  // 2-4
            speedX: (Math.random() - 0.5) * 0.4,      // -0.2 to 0.2
            speedY: -0.2 - Math.random() * 0.3,       // -0.5 to -0.2
            life: 30 + Math.floor(Math.random() * 31), // 30-60
            maxLife: 30 + Math.floor(Math.random() * 31),
            color: {
                r: 200 + Math.floor(Math.random() * 56),  // 200-255
                g: 20 + Math.floor(Math.random() * 61),   // 20-80
                b: 20 + Math.floor(Math.random() * 61),   // 20-80
                a: 150 + Math.floor(Math.random() * 71)   // 150-220
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

        // Draw particles below the heart (matching Python)
        for (const p of this.particles) {
            const alpha = (p.color.a / 255) * (p.life / p.maxLife);
            ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${alpha})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw heart with beat effect (matching Python)
        if (this.sprite && this.spriteLoaded) {
            const scaledWidth = Math.floor(this.width * this.beatSize);
            const scaledHeight = Math.floor(this.height * this.beatSize);
            const xOffset = (scaledWidth - this.width) / 2;
            const yOffset = (scaledHeight - this.height) / 2;

            ctx.drawImage(
                this.sprite,
                0, 0, this.width, this.height,
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
                console.log("Your magical abilities are enhanced! (Max mana increased)");

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

    getRect() {
        if (this.collected) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }

        // Calculate rect based on current beat size (matching Python)
        const scaledWidth = Math.floor(this.width * this.beatSize);
        const scaledHeight = Math.floor(this.height * this.beatSize);
        const xOffset = (scaledWidth - this.width) / 2;
        const yOffset = (scaledHeight - this.height) / 2;

        return {
            x: this.x - xOffset,
            y: this.y + this.bobOffset - yOffset,
            width: scaledWidth,
            height: scaledHeight
        };
    }
}

// Export
window.Item = Item;
window.AncientScroll = AncientScroll;
window.DragonHeart = DragonHeart;
window.HealthPotion = HealthPotion;
