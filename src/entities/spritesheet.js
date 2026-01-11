/**
 * SpriteSheet - Handles sprite loading and extraction
 */
class SpriteSheet {
    constructor(game, characterName = 'link') {
        this.game = game;
        this.characterName = characterName;
        this.spritesheet = null;
    }

    /**
     * Get sprite definitions for Link character from the spritesheet
     */
    getLinkSpriteDefinitions() {
        return {
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
            ],
            'sword': { x: 1, y: 269, w: 8, h: 16 }
        };
    }

    /**
     * Get Ark character sprite definitions (uses separate files)
     */
    getArkFrameCoordinates(direction) {
        const coords = {
            'down_walk': [
                { x: 4, y: 0, w: 16, h: 24 },
                { x: 24, y: 0, w: 16, h: 24 },
                { x: 44, y: 0, w: 16, h: 24 },
                { x: 64, y: 0, w: 16, h: 24 },
                { x: 84, y: 0, w: 16, h: 24 },
                { x: 104, y: 0, w: 16, h: 24 },
                { x: 124, y: 0, w: 16, h: 24 },
                { x: 144, y: 0, w: 16, h: 24 }
            ],
            'up_walk': [
                { x: 0, y: 0, w: 16, h: 24 },
                { x: 16, y: 0, w: 16, h: 24 },
                { x: 32, y: 0, w: 16, h: 24 },
                { x: 48, y: 0, w: 16, h: 24 },
                { x: 64, y: 0, w: 16, h: 24 },
                { x: 80, y: 0, w: 16, h: 24 },
                { x: 96, y: 0, w: 16, h: 24 },
                { x: 112, y: 0, w: 16, h: 24 }
            ],
            'right_walk': [
                { x: 0, y: 0, w: 16, h: 24 },
                { x: 19, y: 1, w: 16, h: 24 },
                { x: 36, y: 1, w: 16, h: 24 },
                { x: 53, y: 0, w: 16, h: 24 },
                { x: 72, y: 0, w: 16, h: 24 },
                { x: 90, y: 1, w: 16, h: 24 },
                { x: 107, y: 1, w: 16, h: 24 },
                { x: 124, y: 0, w: 16, h: 24 }
            ]
        };
        return coords[direction] || [];
    }

    /**
     * Load sprites for a character
     */
    loadCharacterSprites(characterName, targetWidth, targetHeight) {
        this.characterName = characterName;

        if (characterName.toLowerCase() === 'link') {
            return this.loadLinkSprites(targetWidth, targetHeight);
        } else if (characterName.toLowerCase() === 'ark') {
            return this.loadArkSprites(targetWidth, targetHeight);
        }

        // Default to Link
        return this.loadLinkSprites(targetWidth, targetHeight);
    }

    /**
     * Load Link's sprites from the main spritesheet
     */
    loadLinkSprites(targetWidth, targetHeight) {
        const spritesheet = this.game.getImage('sprites');
        const defs = this.getLinkSpriteDefinitions();

        const sprites = {
            down_idle: [],
            down_walk: [],
            up_idle: [],
            up_walk: [],
            right_idle: [],
            right_walk: [],
            left_idle: [],
            left_walk: []
        };

        // Extract sprites from spritesheet
        for (const [key, frames] of Object.entries(defs)) {
            if (key === 'sword') continue;

            sprites[key] = frames.map(frame => ({
                image: spritesheet,
                sx: frame.x,
                sy: frame.y,
                sw: frame.w,
                sh: frame.h,
                width: targetWidth,
                height: targetHeight,
                flipped: false
            }));
        }

        // Create left sprites by marking right sprites as flipped
        sprites.left_idle = sprites.right_idle.map(sprite => ({
            ...sprite,
            flipped: true
        }));
        sprites.left_walk = sprites.right_walk.map(sprite => ({
            ...sprite,
            flipped: true
        }));

        // Sword sprite
        const swordDef = defs.sword;
        const sword = {
            image: spritesheet,
            sx: swordDef.x,
            sy: swordDef.y,
            sw: swordDef.w,
            sh: swordDef.h,
            width: swordDef.w * 2,
            height: swordDef.h * 2
        };

        return { sprites, sword };
    }

    /**
     * Load Ark's sprites from separate image files
     */
    loadArkSprites(targetWidth, targetHeight) {
        const sprites = {
            down_idle: [],
            down_walk: [],
            up_idle: [],
            up_walk: [],
            right_idle: [],
            right_walk: [],
            left_idle: [],
            left_walk: []
        };

        // Idle sprites (single images)
        const idleDirections = ['down', 'up', 'right', 'left'];
        for (const dir of idleDirections) {
            const img = this.game.getImage(`ark_stand_${dir}`);
            if (img) {
                sprites[`${dir}_idle`] = [{
                    image: img,
                    sx: 0,
                    sy: 0,
                    sw: img.width,
                    sh: img.height,
                    width: targetWidth,
                    height: targetHeight,
                    flipped: false
                }];
            }
        }

        // Walk sprites (sprite sheets)
        const walkDirections = ['down', 'up', 'right'];
        for (const dir of walkDirections) {
            const img = this.game.getImage(`ark_walk_${dir}`);
            const coords = this.getArkFrameCoordinates(`${dir}_walk`);

            if (img && coords.length > 0) {
                sprites[`${dir}_walk`] = coords.map(frame => ({
                    image: img,
                    sx: frame.x,
                    sy: frame.y,
                    sw: frame.w,
                    sh: frame.h,
                    width: targetWidth,
                    height: targetHeight,
                    flipped: false
                }));
            }
        }

        // Left walk uses flipped right walk
        sprites.left_walk = sprites.right_walk.map(sprite => ({
            ...sprite,
            flipped: true
        }));

        // Use Link's sword from main spritesheet
        const spritesheet = this.game.getImage('sprites');
        const sword = {
            image: spritesheet,
            sx: 1,
            sy: 269,
            sw: 8,
            sh: 16,
            width: 16,
            height: 32
        };

        return { sprites, sword };
    }
}

// Export
window.SpriteSheet = SpriteSheet;
