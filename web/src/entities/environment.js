/**
 * Grass - Environment decoration/obstacle
 */
class Grass {
    constructor(game, x, y) {
        this.game = game;
        this.x = x;
        this.y = y;
        this.width = 32;
        this.height = 32;

        // Randomly select bush sprite
        const bushOptions = ['bush1', 'bush2', 'bush3'];
        this.spriteKey = bushOptions[Math.floor(Math.random() * bushOptions.length)];
    }

    getRect() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    update(dt, game) {
        // Grass doesn't need updates
    }

    render(ctx, game) {
        const sprite = game.getImage(this.spriteKey);

        if (sprite) {
            ctx.drawImage(sprite, this.x, this.y, this.width, this.height);
        } else {
            // Fallback: draw green rectangle
            ctx.fillStyle = '#3c8c3c';
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        // Debug: draw collision box
        if (game.showDebug) {
            ctx.strokeStyle = 'green';
            ctx.lineWidth = 1;
            ctx.strokeRect(this.x, this.y, this.width, this.height);
        }
    }
}

/**
 * Rock - Environment obstacle with collision
 */
class Rock {
    constructor(game, x, y) {
        this.game = game;
        this.x = x;
        this.y = y;
        this.width = 32;
        this.height = 32;
        this.isObstacle = true; // Rocks block movement

        // Randomly select rock sprite
        const rockOptions = ['rock1', 'rock2', 'rock3'];
        this.spriteKey = rockOptions[Math.floor(Math.random() * rockOptions.length)];
    }

    getRect() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    update(dt, game) {
        // Rocks don't need updates
    }

    render(ctx, game) {
        const sprite = game.getImage(this.spriteKey);

        if (sprite) {
            ctx.drawImage(sprite, this.x, this.y, this.width, this.height);
        } else {
            // Fallback: draw gray rectangle
            ctx.fillStyle = '#787878';
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        // Debug: draw collision box
        if (game.showDebug) {
            ctx.strokeStyle = 'gray';
            ctx.lineWidth = 1;
            ctx.strokeRect(this.x, this.y, this.width, this.height);
        }
    }
}

// Export
window.Grass = Grass;
window.Rock = Rock;
