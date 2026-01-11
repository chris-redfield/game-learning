/**
 * WorldBlock - Represents a single block/chunk of the world
 */
class WorldBlock {
    constructor(blockId, xCoord, yCoord) {
        this.blockId = blockId;
        this.xCoord = xCoord;
        this.yCoord = yCoord;
        this.entities = [];
        this.visited = false;
    }

    addEntity(entity) {
        this.entities.push(entity);
    }

    removeEntity(entity) {
        const index = this.entities.indexOf(entity);
        if (index > -1) {
            this.entities.splice(index, 1);
        }
    }

    getEntities() {
        return this.entities;
    }

    getEntitiesByType(entityType) {
        return this.entities.filter(entity => entity instanceof entityType);
    }

    markAsVisited() {
        this.visited = true;
    }

    isVisited() {
        return this.visited;
    }
}

/**
 * World - Manages the entire game world made up of multiple blocks
 */
class World {
    constructor(game) {
        this.game = game;
        this.blocks = {};
        this.currentBlockCoords = { x: 0, y: 0 };
        this.nextBlockId = 0;

        // Screen dimensions from game
        this.screenWidth = game.width;
        this.screenHeight = game.height;
    }

    /**
     * Generate a new block at the specified coordinates
     */
    generateBlock(xCoord, yCoord, playerEntryPoint = null) {
        const blockKey = `${xCoord},${yCoord}`;

        // If block already exists, return it
        if (this.blocks[blockKey]) {
            return this.blocks[blockKey];
        }

        // Create new block
        const blockId = `block_${this.nextBlockId}`;
        this.nextBlockId++;

        console.log(`Creating block at (${xCoord}, ${yCoord})`);
        const newBlock = new WorldBlock(blockId, xCoord, yCoord);
        this.blocks[blockKey] = newBlock;

        // Populate the block with entities
        this._populateBlock(newBlock, playerEntryPoint, xCoord, yCoord);

        return newBlock;
    }

    /**
     * Populate a block with entities
     */
    _populateBlock(block, playerEntryPoint = null, xCoord = 0, yCoord = 0) {
        // Create safe area around player entry point
        let safeArea = null;
        if (playerEntryPoint) {
            safeArea = {
                x: playerEntryPoint.x - 100,
                y: playerEntryPoint.y - 100,
                width: 200,
                height: 200
            };
        }

        // Special case for origin block (0, 0)
        if (xCoord === 0 && yCoord === 0) {
            const centerX = this.screenWidth / 2;
            const centerY = this.screenHeight / 2;

            // Create larger safe area for origin block
            safeArea = {
                x: centerX - 150,
                y: centerY - 150,
                width: 300,
                height: 300
            };

            // Note: Bonfire and NPCs will be added in Phase 9
        }

        // Add environment entities
        const grassCount = 5 + Math.floor(Math.random() * 11); // 5-15
        const rockCount = 1 + Math.floor(Math.random() * 5);    // 1-5

        this._addGrassPatches(block, grassCount, safeArea);
        this._addRockPatches(block, rockCount, safeArea);

        // Add enemies (not at origin block)
        if (!(xCoord === 0 && yCoord === 0)) {
            this._addEnemies(block, safeArea, xCoord, yCoord);
        }

        block.markAsVisited();
    }

    /**
     * Add grass patches to a block
     */
    _addGrassPatches(block, count, safeArea = null) {
        const minDistance = 64;
        let grassAdded = 0;
        let attempts = 0;

        while (grassAdded < count && attempts < 100) {
            const x = 50 + Math.random() * (this.screenWidth - 100);
            const y = 50 + Math.random() * (this.screenHeight - 100);

            const newRect = { x, y, width: 32, height: 32 };

            // Check safe area
            if (safeArea && this._rectsOverlap(newRect, safeArea)) {
                attempts++;
                continue;
            }

            // Check distance from other entities
            let tooClose = false;
            for (const entity of block.getEntities()) {
                const entityRect = entity.getRect();
                if (this._rectsOverlap(newRect, entityRect) ||
                    this._distance(newRect, entityRect) < minDistance) {
                    tooClose = true;
                    break;
                }
            }

            if (!tooClose) {
                const grass = new Grass(this.game, x, y);
                block.addEntity(grass);
                grassAdded++;
            }

            attempts++;
        }
    }

    /**
     * Add rock patches to a block
     */
    _addRockPatches(block, count, safeArea = null) {
        const minDistance = 64;
        let rocksAdded = 0;
        let attempts = 0;

        while (rocksAdded < count && attempts < 100) {
            const x = 50 + Math.random() * (this.screenWidth - 100);
            const y = 50 + Math.random() * (this.screenHeight - 100);

            const newRect = { x, y, width: 32, height: 32 };

            // Check safe area
            if (safeArea && this._rectsOverlap(newRect, safeArea)) {
                attempts++;
                continue;
            }

            // Check distance from other entities
            let tooClose = false;
            for (const entity of block.getEntities()) {
                const entityRect = entity.getRect();
                if (this._rectsOverlap(newRect, entityRect) ||
                    this._distance(newRect, entityRect) < minDistance) {
                    tooClose = true;
                    break;
                }
            }

            if (!tooClose) {
                const rock = new Rock(this.game, x, y);
                block.addEntity(rock);
                rocksAdded++;
            }

            attempts++;
        }
    }

    /**
     * Add enemies to a block based on difficulty
     */
    _addEnemies(block, safeArea, xCoord, yCoord) {
        const difficultyLevel = this.getDifficultyLevel(xCoord, yCoord);
        const difficultyFactor = this.getDifficultyFactor(xCoord, yCoord);

        // Calculate total difficulty points
        const baseDifficultyPoints = difficultyLevel * difficultyLevel + 2;
        const totalPoints = Math.max(2, baseDifficultyPoints + Math.floor(Math.random() * 5) - 2);

        // Enemy tier definitions
        const tiers = {
            1: [{ type: 'slime', weight: 100 }],
            2: [{ type: 'slime', weight: 80 }, { type: 'skeleton', weight: 20 }],
            3: [{ type: 'slime', weight: 60 }, { type: 'skeleton', weight: 40 }],
            4: [{ type: 'slime', weight: 50 }, { type: 'skeleton', weight: 50 }],
            5: [{ type: 'slime', weight: 30 }, { type: 'skeleton', weight: 70, subtype: 'brute' }],
            6: [{ type: 'slime', weight: 20 }, { type: 'skeleton', weight: 80, subtype: 'brute' }]
        };

        const tierData = tiers[Math.min(difficultyLevel, 6)];
        let remainingPoints = totalPoints;
        const maxEnemyLevel = Math.max(1, Math.round(totalPoints * 0.25));
        let attempts = 0;

        while (remainingPoints > 0 && attempts < 50) {
            // Select enemy type by weight
            const totalWeight = tierData.reduce((sum, t) => sum + t.weight, 0);
            let roll = Math.random() * totalWeight;
            let selectedType = tierData[0];

            for (const t of tierData) {
                roll -= t.weight;
                if (roll <= 0) {
                    selectedType = t;
                    break;
                }
            }

            // Determine level
            const maxLevel = Math.min(maxEnemyLevel, remainingPoints);
            if (maxLevel < 1) break;
            const enemyLevel = 1 + Math.floor(Math.random() * maxLevel);

            // Try to place enemy
            if (this._addSingleEnemy(block, selectedType.type, enemyLevel, selectedType.subtype || 'normal', safeArea, difficultyFactor)) {
                remainingPoints -= enemyLevel;
            }

            attempts++;
        }
    }

    /**
     * Add a single enemy to the block
     */
    _addSingleEnemy(block, type, level, subtype, safeArea, difficultyFactor) {
        const width = type === 'skeleton' ? 48 : 32;
        const height = type === 'skeleton' ? 52 : 24;

        for (let attempt = 0; attempt < 20; attempt++) {
            const x = 100 + Math.random() * (this.screenWidth - 200);
            const y = 100 + Math.random() * (this.screenHeight - 200);

            const enemyRect = { x, y, width, height };

            // Check safe area
            if (safeArea && this._rectsOverlap(enemyRect, safeArea)) {
                continue;
            }

            // Check collision with existing entities
            let collision = false;
            for (const entity of block.getEntities()) {
                if (this._rectsOverlap(enemyRect, entity.getRect())) {
                    collision = true;
                    break;
                }
            }

            if (!collision) {
                let enemy;
                if (type === 'skeleton') {
                    enemy = new Skeleton(this.game, x, y);
                    enemy.enemyType = subtype;
                } else {
                    enemy = new Slime(this.game, x, y);
                }

                enemy.setLevel(level, difficultyFactor);
                block.addEntity(enemy);
                return true;
            }
        }

        return false;
    }

    /**
     * Check if two rectangles overlap
     */
    _rectsOverlap(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }

    /**
     * Calculate distance between two rectangle centers
     */
    _distance(rect1, rect2) {
        const cx1 = rect1.x + rect1.width / 2;
        const cy1 = rect1.y + rect1.height / 2;
        const cx2 = rect2.x + rect2.width / 2;
        const cy2 = rect2.y + rect2.height / 2;
        return Math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2);
    }

    /**
     * Get difficulty level based on distance from origin
     */
    getDifficultyLevel(xCoord, yCoord) {
        const distance = Math.abs(xCoord) + Math.abs(yCoord);

        if (distance === 0) return 1;
        if (distance <= 1) return 2;
        if (distance <= 2) return 3;
        if (distance <= 4) return 4;
        if (distance <= 6) return 5;
        return 6;
    }

    /**
     * Get difficulty scaling factor
     */
    getDifficultyFactor(xCoord, yCoord) {
        const distance = Math.abs(xCoord) + Math.abs(yCoord);

        if (distance === 0) return 1.0;
        if (distance <= 1) return 1.2;
        if (distance <= 2) return 1.4;
        if (distance <= 4) return 1.6;
        if (distance <= 6) return 1.8;
        return 2.0 + Math.min(1.0, (distance - 6) * 0.1);
    }

    /**
     * Get the current block
     */
    getCurrentBlock() {
        const blockKey = `${this.currentBlockCoords.x},${this.currentBlockCoords.y}`;
        return this.blocks[blockKey];
    }

    /**
     * Get block at coordinates, generating if needed
     */
    getBlockAt(xCoord, yCoord) {
        const blockKey = `${xCoord},${yCoord}`;

        if (!this.blocks[blockKey]) {
            return this.generateBlock(xCoord, yCoord);
        }

        return this.blocks[blockKey];
    }

    /**
     * Check if player has moved out of current block and handle transition
     * Returns { changed: boolean, direction: string|null, newPlayerPos: {x, y}|null }
     */
    checkPlayerBlockTransition(player) {
        const playerRect = player.getRect();

        let blockChanged = false;
        let newPlayerPos = null;
        let direction = null;
        let newX = this.currentBlockCoords.x;
        let newY = this.currentBlockCoords.y;

        // Check boundaries
        if (playerRect.x <= 0) {
            // Moving left
            direction = 'left';
            blockChanged = true;
            newX = this.currentBlockCoords.x - 1;
            newPlayerPos = {
                x: this.screenWidth - player.width - 10,
                y: playerRect.y
            };
        } else if (playerRect.x + playerRect.width >= this.screenWidth) {
            // Moving right
            direction = 'right';
            blockChanged = true;
            newX = this.currentBlockCoords.x + 1;
            newPlayerPos = {
                x: 10,
                y: playerRect.y
            };
        } else if (playerRect.y <= 0) {
            // Moving up
            direction = 'up';
            blockChanged = true;
            newY = this.currentBlockCoords.y - 1;
            newPlayerPos = {
                x: playerRect.x,
                y: this.screenHeight - player.height - 10
            };
        } else if (playerRect.y + playerRect.height >= this.screenHeight) {
            // Moving down
            direction = 'down';
            blockChanged = true;
            newY = this.currentBlockCoords.y + 1;
            newPlayerPos = {
                x: playerRect.x,
                y: 10
            };
        }

        if (blockChanged) {
            // Get or generate new block
            let newBlock = this.getBlockAt(newX, newY);

            // If new block hasn't been populated, do it now
            if (!newBlock.isVisited()) {
                this._populateBlock(newBlock, newPlayerPos, newX, newY);
            }

            // Find safe spawn position
            newPlayerPos = this._findSafeSpawnPosition(newBlock, player, newPlayerPos, direction);

            // Update current block coordinates
            this.currentBlockCoords = { x: newX, y: newY };

            console.log(`Moved to block (${newX}, ${newY}) - Difficulty: ${this.getDifficultyLevel(newX, newY)}`);

            return {
                changed: true,
                direction,
                newPlayerPos
            };
        }

        return { changed: false, direction: null, newPlayerPos: null };
    }

    /**
     * Find a safe position for player to spawn without overlapping obstacles
     */
    _findSafeSpawnPosition(block, player, initialPos, direction) {
        const entities = block.getEntities();
        const playerRect = {
            x: initialPos.x,
            y: initialPos.y,
            width: player.width,
            height: player.height
        };

        // Check if initial position is safe (check both Grass and Rock)
        let collision = false;
        for (const entity of entities) {
            if ((entity instanceof Grass || entity instanceof Rock) &&
                this._rectsOverlap(playerRect, entity.getRect())) {
                collision = true;
                break;
            }
        }

        if (!collision) {
            return initialPos;
        }

        // Try to find nearby safe position
        const offsetDistance = 40;
        const maxAttempts = 10;

        for (let i = 1; i <= maxAttempts; i++) {
            const testPositions = [];

            if (direction === 'left' || direction === 'right') {
                testPositions.push({ x: initialPos.x, y: initialPos.y + i * offsetDistance });
                testPositions.push({ x: initialPos.x, y: initialPos.y - i * offsetDistance });
            } else {
                testPositions.push({ x: initialPos.x + i * offsetDistance, y: initialPos.y });
                testPositions.push({ x: initialPos.x - i * offsetDistance, y: initialPos.y });
            }

            for (const testPos of testPositions) {
                // Ensure within bounds
                if (testPos.x < 0 || testPos.x > this.screenWidth - player.width ||
                    testPos.y < 0 || testPos.y > this.screenHeight - player.height) {
                    continue;
                }

                const testRect = {
                    x: testPos.x,
                    y: testPos.y,
                    width: player.width,
                    height: player.height
                };

                let testCollision = false;
                for (const entity of entities) {
                    if ((entity instanceof Grass || entity instanceof Rock) &&
                        this._rectsOverlap(testRect, entity.getRect())) {
                        testCollision = true;
                        break;
                    }
                }

                if (!testCollision) {
                    console.log(`Found safe spawn position at (${testPos.x}, ${testPos.y})`);
                    return testPos;
                }
            }
        }

        // If no safe position found and it's grass, remove it at spawn point
        for (const entity of entities) {
            if (entity instanceof Grass && this._rectsOverlap(playerRect, entity.getRect())) {
                block.removeEntity(entity);
                console.log('Removed grass at player spawn position');
                break;
            }
        }

        return initialPos;
    }

    /**
     * Get all entities in current block
     */
    getCurrentEntities() {
        const currentBlock = this.getCurrentBlock();
        if (currentBlock) {
            return currentBlock.getEntities();
        }
        return [];
    }

    /**
     * Get description of current block
     */
    getBlockDescription() {
        const { x, y } = this.currentBlockCoords;
        const difficulty = this.getDifficultyLevel(x, y);
        return `Block (${x}, ${y}) - Difficulty: ${difficulty}`;
    }

    /**
     * Get obstacles for collision detection
     */
    getObstacles() {
        const entities = this.getCurrentEntities();
        return entities.filter(e => e.isObstacle);
    }

    /**
     * Get all enemies in current block
     */
    getEnemies() {
        const entities = this.getCurrentEntities();
        return entities.filter(e => e instanceof Enemy || e instanceof Slime || e instanceof Skeleton);
    }

    /**
     * Remove dead enemies and return XP to award
     */
    cleanupDeadEnemies() {
        const currentBlock = this.getCurrentBlock();
        if (!currentBlock) return [];

        const deadEnemies = [];
        const entities = currentBlock.getEntities();

        for (const entity of entities) {
            if ((entity instanceof Enemy || entity instanceof Slime || entity instanceof Skeleton) && entity.shouldRemove) {
                deadEnemies.push(entity);
            }
        }

        for (const dead of deadEnemies) {
            currentBlock.removeEntity(dead);
        }

        return deadEnemies;
    }
}

// Export
window.WorldBlock = WorldBlock;
window.World = World;
