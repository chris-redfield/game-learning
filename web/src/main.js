/**
 * The Dark Garden of Z - Web Version
 * Main entry point
 */

// Game instance
let game;

// Game state
const gameState = {
    player: null,
    world: null,
    hud: null, // HUD instance
    characterScreen: null, // Character screen instance
    souls: [], // XP orbs dropped by enemies
    projectiles: [], // Active projectiles (firebolt, etc.)
    transitioning: false,
    transitionCallback: null,
    lastFireboltTime: 0 // Cooldown tracking
};

// Initialize game
async function init() {
    console.log('Initializing The Dark Garden of Z...');

    // Create game instance
    game = new Game('game-canvas');

    // Load assets
    console.log('Loading assets...');
    await game.loadAssets();
    console.log('Assets loaded!');

    // Create world
    gameState.world = new World(game);

    // Generate the starting block (origin)
    const startBlock = gameState.world.generateBlock(0, 0, { x: game.width / 2, y: game.height / 2 });

    // Initialize particle system with starting block
    if (window.particleSystem) {
        window.particleSystem.setCurrentBlock(0, 0);
    }

    // Create player at center of screen
    const centerX = game.width / 2 - 17;
    const centerY = game.height / 2 - 20;
    gameState.player = new Player(game, centerX, centerY, 'link');

    // Create HUD
    gameState.hud = new HUD(gameState.player, game.width, game.height);

    // Create Character Screen
    gameState.characterScreen = new CharacterScreen(gameState.player, game.width, game.height);

    // Set up custom update handler
    game.onUpdate = (dt) => {
        updateGame(dt);
    };

    // Set up custom render handler
    game.onRender = (ctx) => {
        renderGame(ctx);
    };

    // Start the game loop
    game.start();

    // Display controls info
    showControlsInfo();

    console.log('Game started!');
}

// Game update logic
function updateGame(dt) {
    // Don't update during transitions
    if (gameState.transitioning) {
        return;
    }

    const player = gameState.player;
    const world = gameState.world;
    const currentTime = performance.now();

    // Get obstacles for collision
    const obstacles = world.getObstacles();

    // Handle movement
    const movement = game.input.getMovementVector();
    const dx = movement.x * player.speed;
    const dy = movement.y * player.speed;
    player.move(dx, dy, obstacles);

    // Handle attack
    if (game.input.isKeyJustPressed('attack')) {
        player.startSwing();
    }

    // Handle dash
    if (game.input.isKeyJustPressed('dash')) {
        if (player.dash(currentTime)) {
            console.log('Dash activated!');
        }
    }

    // Handle blink
    if (game.input.isKeyJustPressed('blink')) {
        if (player.blink(obstacles, currentTime)) {
            console.log('Blink!');
        }
    }

    // Handle firebolt
    if (game.input.isKeyJustPressed('firebolt')) {
        castFirebolt(currentTime);
    }

    // Handle interact
    if (game.input.isKeyJustPressed('interact')) {
        player.gainXp(5);
        console.log(`XP: ${player.attributes.xp}/${player.attributes.xpNeeded} | Level: ${player.attributes.level}`);
    }

    // Toggle map
    if (game.input.isKeyJustPressed('map')) {
        game.showMap = !game.showMap;
    }

    // Toggle character screen
    if (game.input.isKeyJustPressed('character')) {
        gameState.characterScreen.toggle();
    }

    // Handle character screen input when visible
    if (gameState.characterScreen.isVisible()) {
        gameState.characterScreen.handleInput(game.input);
    }

    // Update player
    player.update(dt, game);

    // Get all obstacles (for enemy collision)
    const allObstacles = [...obstacles];

    // Update enemies
    const enemies = world.getEnemies();
    for (const enemy of enemies) {
        enemy.update(dt, player, allObstacles);
    }

    // Check sword collisions with enemies
    if (player.isSwinging()) {
        const swordRect = player.getSwordRect();
        if (swordRect) {
            const playerCenterX = player.x + player.width / 2;
            const playerCenterY = player.y + player.height / 2;

            for (const enemy of enemies) {
                if (enemy.state === 'dying') continue;
                if (player.hitEnemies.has(enemy)) continue;

                const enemyRect = enemy.getRect();
                if (rectsOverlap(swordRect, enemyRect)) {
                    const damage = player.attributes.getAttackPower();
                    enemy.takeDamage(damage, playerCenterX, playerCenterY);
                    player.hitEnemies.add(enemy);

                    // Spawn blood particles
                    if (window.particleSystem) {
                        window.particleSystem.spawnEnemyBlood(enemy, playerCenterX, playerCenterY);
                    }
                }
            }
        }
    }

    // Update projectiles (check collision with enemies AND obstacles)
    for (const projectile of gameState.projectiles) {
        projectile.update(currentTime, enemies, obstacles);
    }

    // Clean up dead projectiles
    gameState.projectiles = gameState.projectiles.filter(p => p.alive);

    // Update particle system
    if (window.particleSystem) {
        window.particleSystem.update(obstacles);
    }

    // Clean up dead enemies and spawn souls
    const deadEnemies = world.cleanupDeadEnemies();
    for (const dead of deadEnemies) {
        if (dead.willDropSoul) {
            // Spawn a soul at enemy's center position
            const centerX = dead.x + dead.width / 2 - 3;
            const centerY = dead.y + dead.height / 2 - 3;
            const xpValue = dead.getXpValue();
            const soul = new Soul(centerX, centerY, xpValue);
            gameState.souls.push(soul);
            console.log(`Soul spawned with ${xpValue} XP from ${dead.constructor.name}`);
        }
    }

    // Update souls
    gameState.souls = gameState.souls.filter(soul => {
        const collected = soul.update(player);
        return !soul.shouldRemove;
    });

    // Check for block transition
    const transition = world.checkPlayerBlockTransition(player);
    if (transition.changed) {
        // Start fade out transition
        gameState.transitioning = true;

        game.startTransition(false, () => {
            // Move player to new position
            player.x = transition.newPlayerPos.x;
            player.y = transition.newPlayerPos.y;

            // Clear souls, projectiles, and active particles when changing blocks
            gameState.souls = [];
            gameState.projectiles = [];
            if (window.particleSystem) {
                window.particleSystem.clear();
                // Update current block for stuck particle tracking
                const newBlock = world.currentBlockCoords;
                window.particleSystem.setCurrentBlock(newBlock.x, newBlock.y);
            }

            // Start fade in
            game.startTransition(true, () => {
                gameState.transitioning = false;
            });
        });
    }
}

// Game render logic
function renderGame(ctx) {
    const player = gameState.player;
    const world = gameState.world;

    // Get all entities in current block
    const entities = world.getCurrentEntities();

    // Combine entities with player and souls for depth sorting
    const allRenderables = [...entities, ...gameState.souls];
    if (player) {
        allRenderables.push(player);
    }

    // Sort by Y position for depth (items lower on screen drawn on top)
    allRenderables.sort((a, b) => {
        const ay = a.y + (a.height || 0);
        const by = b.y + (b.height || 0);
        return ay - by;
    });

    // Render stuck blood FIRST (under entities, like ground stains)
    if (window.particleSystem) {
        window.particleSystem.renderStuckBlood(ctx);
    }

    // Render all entities
    for (const entity of allRenderables) {
        if (entity.render) {
            entity.render(ctx, game);
        }
    }

    // Render active particles AFTER entities (fire trail, explosions, flying blood)
    if (window.particleSystem) {
        window.particleSystem.renderActiveParticles(ctx);
    }

    // Render projectiles
    for (const projectile of gameState.projectiles) {
        projectile.render(ctx);
    }

    // Draw debug info when debug mode is on
    if (game.showDebug) {
        // Enemy debug info
        const enemies = world.getEnemies();
        for (const enemy of enemies) {
            if (enemy.renderDebugInfo && enemy.state !== 'dying') {
                enemy.renderDebugInfo(ctx, enemy.x, enemy.y - 15);
            }
        }

        // Projectile debug (bounding boxes)
        for (const projectile of gameState.projectiles) {
            if (projectile.renderDebug) {
                projectile.renderDebug(ctx);
            }
        }
    }

    // Draw HUD
    const enemies = world.getEnemies();
    gameState.hud.draw(ctx, world, {
        entities: enemies,
        showEnemyDebug: game.showDebug
    });

    // Draw overlays
    if (game.showMap) {
        drawMapOverlay(ctx, world);
    }

    if (gameState.characterScreen.isVisible()) {
        gameState.characterScreen.draw(ctx);
    }
}

// Map overlay
function drawMapOverlay(ctx, world) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(0, 0, game.width, game.height);

    ctx.fillStyle = 'white';
    ctx.font = '32px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('WORLD MAP', game.width / 2, 60);

    // Draw block grid
    const gridSize = 50;
    const gridRange = 5; // Show 5x5 grid around current position
    const offsetX = game.width / 2 - gridSize * gridRange / 2;
    const offsetY = game.height / 2 - gridSize * gridRange / 2;

    const currentX = world.currentBlockCoords.x;
    const currentY = world.currentBlockCoords.y;

    for (let dy = -Math.floor(gridRange / 2); dy <= Math.floor(gridRange / 2); dy++) {
        for (let dx = -Math.floor(gridRange / 2); dx <= Math.floor(gridRange / 2); dx++) {
            const blockX = currentX + dx;
            const blockY = currentY + dy;
            const blockKey = `${blockX},${blockY}`;

            const px = offsetX + (dx + Math.floor(gridRange / 2)) * gridSize;
            const py = offsetY + (dy + Math.floor(gridRange / 2)) * gridSize;

            // Check if block has been visited
            const visited = world.blocks[blockKey]?.isVisited();

            if (dx === 0 && dy === 0) {
                // Current block
                ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
                ctx.fillRect(px, py, gridSize - 2, gridSize - 2);
            } else if (visited) {
                // Visited blocks
                ctx.fillStyle = 'rgba(100, 100, 100, 0.5)';
                ctx.fillRect(px, py, gridSize - 2, gridSize - 2);
            }

            // Draw border
            ctx.strokeStyle = visited || (dx === 0 && dy === 0) ? '#666' : '#333';
            ctx.lineWidth = 1;
            ctx.strokeRect(px, py, gridSize - 2, gridSize - 2);

            // Draw coordinates for current block
            if (dx === 0 && dy === 0) {
                ctx.fillStyle = 'white';
                ctx.font = '10px Arial';
                ctx.fillText(`${blockX},${blockY}`, px + gridSize / 2, py + gridSize / 2 + 3);
            }
        }
    }

    // Draw difficulty indicator
    const difficulty = world.getDifficultyLevel(currentX, currentY);
    ctx.fillStyle = '#ffaa00';
    ctx.font = '18px Arial';
    ctx.fillText(`Current Block: (${currentX}, ${currentY}) | Difficulty: ${difficulty}`, game.width / 2, game.height - 80);

    ctx.font = '16px Arial';
    ctx.fillStyle = '#888';
    ctx.fillText('Press M to close', game.width / 2, game.height - 40);
    ctx.textAlign = 'left';
}

// Cast firebolt spell
function castFirebolt(currentTime) {
    const player = gameState.player;
    if (!player) return false;

    // Check cooldown (250ms between casts, matching Python)
    if (currentTime - gameState.lastFireboltTime < 250) {
        return false;
    }

    // Create firebolt projectile
    const firebolt = new Firebolt(player);
    gameState.projectiles.push(firebolt);
    gameState.lastFireboltTime = currentTime;

    console.log(`Firebolt cast! Damage: ${firebolt.damage.toFixed(1)}, Size: ${firebolt.boltSize}`);
    return true;
}

// Show controls info
function showControlsInfo() {
    console.log(`
=== The Dark Garden of Z - Controls ===
WASD / Arrow Keys - Move
Space - Attack (Sword Swing)
F - Firebolt (magic projectile)
E - Interact (+5 XP for testing)
Shift - Dash (speed boost)
B - Blink (teleport forward)
M - Map (shows visited blocks)
Enter - Character Screen
C - Debug Mode

Walk to screen edge to transition to new block!

Gamepad:
Left Stick - Move
A - Attack
B - Blink
X - Firebolt
Y - Interact
LB/RB - Dash
Start - Character Screen
===================================
    `);
}

// Helper function to check if two rectangles overlap
function rectsOverlap(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

// Start the game when page loads
window.addEventListener('load', init);
