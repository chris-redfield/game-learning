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

    // Toggle character screen (must work even when paused)
    if (game.input.isKeyJustPressed('character')) {
        gameState.characterScreen.toggle();
    }

    // Handle character screen input when visible (before pause check)
    if (gameState.characterScreen && gameState.characterScreen.isVisible()) {
        gameState.characterScreen.handleInput(game.input);
        // Pause game when character screen is open
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

    // Handle dash (only if unlocked)
    if (game.input.isKeyJustPressed('dash') && player.skillTree.isSkillUnlocked('dash')) {
        if (player.dash(currentTime)) {
            console.log('Dash activated!');
        }
    }

    // Handle blink (only if unlocked)
    if (game.input.isKeyJustPressed('blink') && player.skillTree.isSkillUnlocked('blink')) {
        if (player.blink(obstacles, currentTime)) {
            console.log('Blink!');
        }
    }

    // Handle firebolt (only if unlocked)
    if (game.input.isKeyJustPressed('firebolt') && player.skillTree.isSkillUnlocked('firebolt')) {
        castFirebolt(currentTime);
    }

    // Handle add XP (+ key for testing, matching Python)
    if (game.input.isKeyJustPressed('addXp')) {
        player.gainXp(5);
        console.log(`XP: ${player.attributes.xp}/${player.attributes.xpNeeded} | Level: ${player.attributes.level}`);
    }

    // Toggle map
    if (game.input.isKeyJustPressed('map')) {
        game.showMap = !game.showMap;
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

// Map overlay - Matches Python map.py
function drawMapOverlay(ctx, world) {
    // Colors matching Python
    const colors = {
        background: 'rgb(20, 20, 40)',
        grid: 'rgb(60, 60, 80)',
        current: 'rgb(65, 185, 105)',      // Green
        visited: 'rgb(100, 140, 160)',      // Blue-gray
        unexplored: 'rgb(40, 40, 60)',      // Dark
        player: 'rgb(230, 230, 50)',        // Yellow
        text: 'rgb(220, 220, 220)'
    };

    const cellSize = 28;
    const gridCount = 20;  // 20x20 grid

    // Fill background
    ctx.fillStyle = colors.background;
    ctx.fillRect(0, 0, game.width, game.height);

    // Draw title
    ctx.fillStyle = colors.text;
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('WORLD MAP', game.width / 2, 30);

    // Draw current coordinates info
    const currentX = world.currentBlockCoords.x;
    const currentY = world.currentBlockCoords.y;
    ctx.font = '14px Arial';
    ctx.fillText(`Current Position: (${currentX}, ${currentY})`, game.width / 2, 55);

    // Calculate map center position
    const centerX = game.width / 2;
    const centerY = game.height / 2;

    // Calculate offset for centered grid
    const offsetX = centerX - (gridCount / 2) * cellSize;
    const offsetY = centerY - (gridCount / 2) * cellSize;

    // Draw the grid and blocks
    for (let y = 0; y < gridCount; y++) {
        for (let x = 0; x < gridCount; x++) {
            // Calculate world coordinates for this cell
            const worldX = currentX - Math.floor(gridCount / 2) + x;
            const worldY = currentY - Math.floor(gridCount / 2) + y;

            // Calculate screen position for this cell
            const screenX = offsetX + x * cellSize;
            const screenY = offsetY + y * cellSize;

            // Check if block exists at these coordinates
            const blockKey = `${worldX},${worldY}`;
            const blockExists = world.blocks[blockKey] !== undefined;

            // Determine cell color
            let color = null;
            if (worldX === currentX && worldY === currentY) {
                // Current block
                color = colors.current;
            } else if (blockExists && world.blocks[blockKey].isVisited()) {
                // Visited block
                color = colors.visited;
            } else if (blockExists) {
                // Known but unexplored block
                color = colors.unexplored;
            }

            if (color) {
                // Draw filled cell
                ctx.fillStyle = color;
                ctx.fillRect(screenX, screenY, cellSize, cellSize);
            }

            // Draw grid border
            ctx.strokeStyle = colors.grid;
            ctx.lineWidth = 1;
            ctx.strokeRect(screenX, screenY, cellSize, cellSize);

            // Draw coordinates in cell if current block
            if (worldX === currentX && worldY === currentY) {
                const coordText = `${worldX},${worldY}`;
                ctx.font = '10px Arial';
                ctx.fillStyle = colors.text;
                ctx.textAlign = 'center';
                ctx.fillText(coordText, screenX + cellSize / 2, screenY + cellSize / 2 + 3);
            }
        }
    }

    // Draw player marker (yellow circle in center of current block)
    const playerScreenX = offsetX + Math.floor(gridCount / 2) * cellSize + cellSize / 2;
    const playerScreenY = offsetY + Math.floor(gridCount / 2) * cellSize + cellSize / 2;
    const markerSize = Math.max(cellSize / 5, 5);

    ctx.fillStyle = colors.player;
    ctx.beginPath();
    ctx.arc(playerScreenX, playerScreenY, markerSize, 0, Math.PI * 2);
    ctx.fill();

    // Draw legend at bottom left
    const legendX = 20;
    let legendY = game.height - 120;

    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillStyle = colors.text;
    ctx.fillText('Legend:', legendX, legendY);

    const legendItems = [
        { text: 'Current Location', color: colors.current },
        { text: 'Visited Areas', color: colors.visited },
        { text: 'Unexplored', color: colors.unexplored },
        { text: 'Player', color: colors.player }
    ];

    for (let i = 0; i < legendItems.length; i++) {
        const yPos = legendY + 20 + i * 20;

        // Draw color sample
        ctx.fillStyle = legendItems[i].color;
        ctx.fillRect(legendX, yPos, 15, 15);

        // Draw text
        ctx.fillStyle = colors.text;
        ctx.fillText(legendItems[i].text, legendX + 22, yPos + 12);
    }

    // Draw instructions at bottom right
    ctx.textAlign = 'right';
    const instructions = [
        "Press 'M' or LB to close map",
        "Explore the world by crossing",
        "the borders of each area"
    ];

    for (let i = 0; i < instructions.length; i++) {
        const yPos = game.height - 70 + i * 18;
        ctx.fillText(instructions[i], game.width - 20, yPos);
    }

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
+ - Add XP (+5 for testing)
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
