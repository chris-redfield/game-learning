/**
 * NPC - Non-Player Character base class
 * Mirrors Python entities/npc/npc.py (simplified version)
 * Exactly like it was implemented at the python code
 */
class NPC {
    constructor(x, y, characterName = 'default_npc', game = null) {
        this.x = x;
        this.y = y;
        this.width = 35;
        this.height = 41;
        this.speed = 2;
        this.baseSpeed = 2;
        this.game = game;

        // NPC is an obstacle (player can't walk through)
        this.isObstacle = true;

        // Character info
        this.characterName = characterName;
        this.name = characterName;

        // Direction and animation
        this.facing = 'down';
        this.moving = false;
        this.frame = 0;
        this.animationSpeed = 0.15;
        this.animationCounter = 0;

        // AI movement
        this.state = 'idle';
        this.movementTimer = 0;
        this.movementPause = 120 + Math.floor(Math.random() * 180);
        this.movementDuration = 60 + Math.floor(Math.random() * 120);
        this.dx = 0;
        this.dy = 0;

        // Interaction
        this.interactionRange = 80;
        this.isInteractable = true;
        this.dialogueState = 'none';

        // Visibility (for invulnerability flashing if needed)
        this.visible = true;

        // Sprites (will load directly from image)
        this.sprites = {};
        this.spritesLoaded = false;
        this.spriteImage = null;

        this.loadSprites();
    }

    loadSprites() {
        // Load sprites directly from image file (without needing game object)
        if (this.characterName.toLowerCase() === 'link') {
            this.spriteImage = new Image();
            this.spriteImage.onload = () => {
                this.extractLinkSprites();
                this.spritesLoaded = true;
                console.log(`NPC sprites loaded for ${this.characterName}`);
            };
            this.spriteImage.onerror = () => {
                console.log(`Could not load sprites for ${this.characterName}, using placeholder`);
                this.createPlaceholderSprites();
            };
            this.spriteImage.src = 'assets/sprites.png';
        } else {
            // Use placeholder for unknown characters
            this.createPlaceholderSprites();
        }
    }

    extractLinkSprites() {
        // Link sprite definitions (same as SpriteSheet)
        const defs = {
            'down_idle': [{ x: 1, y: 3, w: 16, h: 24 }],
            'down_walk': [
                { x: 1, y: 3, w: 16, h: 24 },
                { x: 19, y: 3, w: 16, h: 24 },
                { x: 36, y: 3, w: 16, h: 24 },
                { x: 53, y: 3, w: 16, h: 24 },
                { x: 70, y: 3, w: 16, h: 24 },
                { x: 87, y: 3, w: 16, h: 24 },
                { x: 104, y: 3, w: 16, h: 24 },
                { x: 121, y: 3, w: 16, h: 24 },
                { x: 138, y: 3, w: 16, h: 24 }
            ],
            'up_idle': [{ x: 1, y: 111, w: 16, h: 24 }],
            'up_walk': [
                { x: 1, y: 111, w: 16, h: 24 },
                { x: 19, y: 111, w: 16, h: 24 },
                { x: 36, y: 111, w: 16, h: 24 },
                { x: 53, y: 111, w: 16, h: 24 },
                { x: 70, y: 111, w: 16, h: 24 },
                { x: 87, y: 111, w: 16, h: 24 },
                { x: 104, y: 111, w: 16, h: 24 },
                { x: 121, y: 111, w: 16, h: 24 },
                { x: 138, y: 111, w: 16, h: 24 }
            ],
            'right_idle': [{ x: 1, y: 56, w: 16, h: 24 }],
            'right_walk': [
                { x: 1, y: 56, w: 16, h: 24 },
                { x: 19, y: 56, w: 16, h: 24 },
                { x: 36, y: 56, w: 16, h: 24 },
                { x: 54, y: 56, w: 16, h: 24 },
                { x: 72, y: 56, w: 16, h: 24 },
                { x: 89, y: 56, w: 16, h: 24 },
                { x: 107, y: 56, w: 16, h: 24 },
                { x: 125, y: 56, w: 16, h: 24 },
                { x: 142, y: 56, w: 16, h: 24 }
            ]
        };

        // Create sprite frames using canvas extraction
        for (const [key, frames] of Object.entries(defs)) {
            this.sprites[key] = frames.map(frame => {
                const canvas = document.createElement('canvas');
                canvas.width = this.width;
                canvas.height = this.height;
                const ctx = canvas.getContext('2d');
                ctx.imageSmoothingEnabled = false;
                ctx.drawImage(
                    this.spriteImage,
                    frame.x, frame.y, frame.w, frame.h,
                    0, 0, this.width, this.height
                );
                return canvas;
            });
        }

        // Create left sprites by flipping right
        this.sprites['left_idle'] = this.sprites['right_idle'].map(canvas => this.flipCanvas(canvas));
        this.sprites['left_walk'] = this.sprites['right_walk'].map(canvas => this.flipCanvas(canvas));
    }

    flipCanvas(sourceCanvas) {
        const flipped = document.createElement('canvas');
        flipped.width = sourceCanvas.width;
        flipped.height = sourceCanvas.height;
        const ctx = flipped.getContext('2d');
        ctx.translate(flipped.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(sourceCanvas, 0, 0);
        return flipped;
    }

    createPlaceholderSprites() {
        const directions = ['down', 'up', 'right', 'left'];

        for (const dir of directions) {
            // Create simple colored rectangle placeholders
            const idleCanvas = document.createElement('canvas');
            idleCanvas.width = this.width;
            idleCanvas.height = this.height;
            const idleCtx = idleCanvas.getContext('2d');
            idleCtx.fillStyle = '#8844aa'; // Purple for NPC
            idleCtx.fillRect(0, 0, this.width, this.height);
            idleCtx.fillStyle = '#ffffff';
            idleCtx.font = '10px Arial';
            idleCtx.fillText('NPC', 5, this.height / 2);

            this.sprites[`${dir}_idle`] = [idleCanvas];
            this.sprites[`${dir}_walk`] = [idleCanvas];
        }
        this.spritesLoaded = true;
    }

    getRect() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    startMoving() {
        this.state = 'moving';
        this.moving = true;

        // Random direction
        const angle = Math.random() * Math.PI * 2;
        this.dx = Math.cos(angle) * this.speed;
        this.dy = Math.sin(angle) * this.speed;

        // Set facing
        if (Math.abs(this.dx) > Math.abs(this.dy)) {
            this.facing = this.dx > 0 ? 'right' : 'left';
        } else {
            this.facing = this.dy > 0 ? 'down' : 'up';
        }
    }

    stopMoving() {
        this.state = 'idle';
        this.moving = false;
        this.dx = 0;
        this.dy = 0;
    }

    updateAI(obstacles) {
        if (this.state === 'idle') {
            this.movementTimer++;
            if (this.movementTimer >= this.movementPause) {
                this.movementTimer = 0;
                if (Math.random() < 0.7) {
                    this.startMoving();
                } else {
                    this.movementPause = 120 + Math.floor(Math.random() * 180);
                }
            }
        } else if (this.state === 'moving') {
            this.movementTimer++;
            if (this.movementTimer >= this.movementDuration) {
                this.movementTimer = 0;
                this.stopMoving();
                this.movementPause = 120 + Math.floor(Math.random() * 180);
            } else {
                this.move(this.dx, this.dy, obstacles);
            }
        }
    }

    move(dx, dy, obstacles) {
        if (dx === 0 && dy === 0) return false;

        const screenWidth = 1280;
        const screenHeight = 720;
        const marginX = this.width * 0.5;
        const marginY = this.height * 0.5;

        // Test new positions
        const newX = this.x + dx;
        const newY = this.y + dy;

        // Check boundaries
        const xBoundaryViolation = newX < -marginX || newX + this.width > screenWidth + marginX;
        const yBoundaryViolation = newY < -marginY || newY + this.height > screenHeight + marginY;

        // Check X collision
        let xCollision = xBoundaryViolation;
        if (!xCollision) {
            const testRectX = { x: newX, y: this.y, width: this.width, height: this.height };
            for (const obs of obstacles) {
                if (obs === this) continue;
                if (obs.isCollectible && obs.isCollectible()) continue;
                const obsRect = obs.getRect ? obs.getRect() : obs;
                if (this.rectsOverlap(testRectX, obsRect)) {
                    xCollision = true;
                    break;
                }
            }
        }

        if (!xCollision) {
            this.x = newX;
        }

        // Check Y collision
        let yCollision = yBoundaryViolation;
        if (!yCollision) {
            const testRectY = { x: this.x, y: newY, width: this.width, height: this.height };
            for (const obs of obstacles) {
                if (obs === this) continue;
                if (obs.isCollectible && obs.isCollectible()) continue;
                const obsRect = obs.getRect ? obs.getRect() : obs;
                if (this.rectsOverlap(testRectY, obsRect)) {
                    yCollision = true;
                    break;
                }
            }
        }

        if (!yCollision) {
            this.y = newY;
        }

        // Change direction if hit obstacle
        if (xCollision || yCollision) {
            if (Math.random() < 0.8) {
                this.startMoving();
            }
            return false;
        }

        return true;
    }

    rectsOverlap(a, b) {
        return a.x < b.x + b.width &&
               a.x + a.width > b.x &&
               a.y < b.y + b.height &&
               a.y + a.height > b.y;
    }

    checkPlayerInteraction(player) {
        const playerRect = player.getRect();
        const npcCenterX = this.x + this.width / 2;
        const npcCenterY = this.y + this.height / 2;
        const playerCenterX = playerRect.x + playerRect.width / 2;
        const playerCenterY = playerRect.y + playerRect.height / 2;

        const dx = playerCenterX - npcCenterX;
        const dy = playerCenterY - npcCenterY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance <= this.interactionRange) {
            this.onPlayerNearby(player);
        }
    }

    onPlayerNearby(player) {
        // Override in subclasses
    }

    interact(player) {
        if (window.dialogBalloonSystem) {
            window.dialogBalloonSystem.addDialog(
                `Hello, I'm ${this.characterName}!`,
                this.x, this.y, this.width, this.height
            );
        }
    }

    update(dt, currentTime, obstacles = [], player = null) {
        // Animation
        if (this.moving) {
            this.animationCounter += this.animationSpeed;

            const walkKey = this.facing === 'left' ? 'right_walk' : `${this.facing}_walk`;
            const walkFrames = this.sprites[walkKey] || [];

            if (this.animationCounter >= walkFrames.length) {
                this.animationCounter = 0;
            }
            this.frame = Math.floor(this.animationCounter);
        } else {
            this.frame = 0;
        }

        // AI movement
        this.updateAI(obstacles);

        // Player interaction check
        if (player && this.isInteractable) {
            this.checkPlayerInteraction(player);
        }
    }

    render(ctx) {
        if (!this.visible) return;

        let sprite;

        // Get sprite based on facing and movement state
        if (this.facing === 'left') {
            // Flip right sprite for left
            const key = this.moving ? 'right_walk' : 'right_idle';
            const frames = this.sprites[key] || [];
            if (frames.length > 0) {
                const sourceSprite = frames[this.frame % frames.length];
                // Flip horizontally
                ctx.save();
                ctx.scale(-1, 1);
                ctx.drawImage(sourceSprite, -this.x - this.width, this.y);
                ctx.restore();
                return;
            }
        } else {
            const key = this.moving ? `${this.facing}_walk` : `${this.facing}_idle`;
            const frames = this.sprites[key] || [];
            if (frames.length > 0) {
                sprite = frames[this.frame % frames.length];
            }
        }

        if (sprite) {
            ctx.drawImage(sprite, this.x, this.y);
        } else {
            // Placeholder
            ctx.fillStyle = '#8844aa';
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.fillStyle = '#ffffff';
            ctx.font = '10px Arial';
            ctx.fillText('NPC', this.x + 5, this.y + this.height / 2);
        }
    }

    renderDebug(ctx) {
        const rect = this.getRect();
        ctx.strokeStyle = '#ff00ff';
        ctx.lineWidth = 1;
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);

        // Draw interaction range
        ctx.strokeStyle = 'rgba(255, 0, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(
            this.x + this.width / 2,
            this.y + this.height / 2,
            this.interactionRange,
            0, Math.PI * 2
        );
        ctx.stroke();
    }
}

/**
 * LinkNPC - The Link character as an NPC
 * Exactly like it was implemented at the python code (link.py)
 */
class LinkNPC extends NPC {
    constructor(x, y, game = null) {
        super(x, y, 'link', game);

        // Link-specific dialog lines (matching Python)
        this.dialogLines = [
            "Hello, friend!",
            "It's kinda dangerous to go alone!",
            "I'm looking for Zelda...",
            "Have you seen any rupees around?",
            "This reminds me of Hyrule."
        ];
        this.lastDialogIndex = -1;

        // Dialog cooldown
        this.dialogCooldown = 0;
        this.dialogCooldownDuration = 3000; // 3 seconds
        this.lastTime = 0;

        // Link is more interactive
        this.interactionRange = 100;
    }

    update(dt, currentTime, obstacles = [], player = null) {
        // Update dialog cooldown
        if (this.dialogCooldown > 0 && currentTime > this.dialogCooldown) {
            this.dialogCooldown = 0;
        }
        this.lastTime = currentTime;

        // Call parent update
        super.update(dt, currentTime, obstacles, player);
    }

    onPlayerNearby(player) {
        // Small chance to say something when player is nearby
        if (this.dialogCooldown === 0 && Math.random() < 0.01) {
            this.sayRandomDialogue();
        }
    }

    sayRandomDialogue() {
        if (this.dialogCooldown > 0) return;

        // Set cooldown
        this.dialogCooldown = this.lastTime + this.dialogCooldownDuration;

        // Pick a random line (different from last)
        let index;
        do {
            index = Math.floor(Math.random() * this.dialogLines.length);
        } while (index === this.lastDialogIndex && this.dialogLines.length > 1);

        this.lastDialogIndex = index;
        const line = this.dialogLines[index];

        if (window.dialogBalloonSystem) {
            window.dialogBalloonSystem.addDialog(
                line,
                this.x, this.y, this.width, this.height
            );
        }
    }

    interact(player) {
        if (this.dialogCooldown === 0) {
            // 80% chance to say dialogue, 20% chance to offer help
            if (Math.random() < 0.8) {
                this.sayRandomDialogue();
            } else {
                this.offerHelp(player);
            }
        }
    }

    offerHelp(player) {
        if (this.dialogCooldown > 0) return;

        this.dialogCooldown = this.lastTime + this.dialogCooldownDuration;

        const helpTypes = ['rupees', 'wisdom', 'heal'];
        const helpType = helpTypes[Math.floor(Math.random() * helpTypes.length)];

        if (helpType === 'rupees') {
            const xpAmount = 5 + Math.floor(Math.random() * 11); // 5-15
            if (player && player.gainXp) {
                player.gainXp(xpAmount);
            }
            if (window.dialogBalloonSystem) {
                window.dialogBalloonSystem.addDialog(
                    `Here, take these ${xpAmount} rupees!`,
                    this.x, this.y, this.width, this.height
                );
            }
        } else if (helpType === 'wisdom') {
            const wisdomQuotes = [
                "The Master Sword sleeps in the forest...",
                "Courage need not be remembered, for it is never forgotten!",
                "Sometimes you need to take a step back to move forward."
            ];
            const quote = wisdomQuotes[Math.floor(Math.random() * wisdomQuotes.length)];
            if (window.dialogBalloonSystem) {
                window.dialogBalloonSystem.addDialog(
                    quote,
                    this.x, this.y, this.width, this.height
                );
            }
        } else if (helpType === 'heal') {
            if (player && player.attributes &&
                player.attributes.currentHealth < player.attributes.maxHealth) {
                const healAmount = 10 + Math.floor(Math.random() * 16); // 10-25
                if (player.heal) {
                    player.heal(healAmount);
                }
                if (window.dialogBalloonSystem) {
                    window.dialogBalloonSystem.addDialog(
                        `My fairy healed you for ${healAmount} HP!`,
                        this.x, this.y, this.width, this.height
                    );
                }
            } else {
                if (window.dialogBalloonSystem) {
                    window.dialogBalloonSystem.addDialog(
                        "You're already at full health!",
                        this.x, this.y, this.width, this.height
                    );
                }
            }
        }
    }
}

// Export
window.NPC = NPC;
window.LinkNPC = LinkNPC;
