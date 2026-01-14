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

        // Entity type flag for fast filtering (avoids instanceof)
        this.entityType = 'environment';

        // Cached rect for collision detection (avoids object allocation)
        this._rect = { x: 0, y: 0, width: 0, height: 0 };

        this.isObstacle = true; // Grass/bushes block movement

        // Randomly select bush sprite
        const bushOptions = ['bush1', 'bush2', 'bush3'];
        this.spriteKey = bushOptions[Math.floor(Math.random() * bushOptions.length)];
    }

    getRect() {
        this._rect.x = this.x;
        this._rect.y = this.y;
        this._rect.width = this.width;
        this._rect.height = this.height;
        return this._rect;
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

        // Entity type flag for fast filtering (avoids instanceof)
        this.entityType = 'environment';

        // Cached rect for collision detection (avoids object allocation)
        this._rect = { x: 0, y: 0, width: 0, height: 0 };

        this.isObstacle = true; // Rocks block movement

        // Randomly select rock sprite
        const rockOptions = ['rock1', 'rock2', 'rock3'];
        this.spriteKey = rockOptions[Math.floor(Math.random() * rockOptions.length)];
    }

    getRect() {
        this._rect.x = this.x;
        this._rect.y = this.y;
        this._rect.width = this.width;
        this._rect.height = this.height;
        return this._rect;
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
