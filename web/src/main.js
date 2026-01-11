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
    bonfireMenu: null, // Bonfire save/load menu
    saveDialog: null, // Save file dialog
    loadDialog: null, // Load file dialog
    messageDialog: null, // Message dialog for confirmations
    saveLoadManager: null, // Save/Load manager
    deathScreen: null, // Death screen overlay
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

    // Create Save/Load Manager
    gameState.saveLoadManager = new SaveLoadManager(gameState.player, gameState.world);

    // Create Message Dialog for confirmations
    gameState.messageDialog = new MessageDialog();

    // Create Death Screen
    gameState.deathScreen = new DeathScreen();
    gameState.deathScreen.onRestart = restartGame;
    gameState.deathScreen.onLoadSave = () => {
        // Show load dialog when "Load Save" is selected from death screen
        gameState.loadDialog.show();
    };

    // Create Save and Load file dialogs
    gameState.saveDialog = new SaveOverwriteDialog(gameState.saveLoadManager, (filename) => {
        console.log(`Game saved to ${filename}`);
        // Show success message
        gameState.messageDialog.setMessage('Save Game', `Game saved successfully to ${filename}`);
        gameState.messageDialog.show();
    });
    gameState.loadDialog = new LoadFileDialog(gameState.saveLoadManager, (filename, success) => {
        if (success) {
            console.log(`Game loaded from ${filename}`);
            // Deactivate death screen if active (like Python)
            if (gameState.deathScreen && gameState.deathScreen.isActive()) {
                gameState.deathScreen.deactivate();
            }
            // Re-set bonfire callback after loading
            setBonfireCallback();
            gameState.messageDialog.setMessage('Load Game', `Game loaded successfully from ${filename}`);
            gameState.messageDialog.show();
        } else {
            console.log('Failed to load game');
            gameState.messageDialog.setMessage('Load Game', 'Failed to load game');
            gameState.messageDialog.show();
        }
    });

    // Create Bonfire Menu (shows Save/Load/Cancel options)
    gameState.bonfireMenu = new BonfireMenu(
        () => gameState.saveDialog.show(),  // On Save
        () => gameState.loadDialog.show()   // On Load
    );

    // Add keyboard listener for filename entry in save dialog
    // This must run BEFORE the input system processes the key
    document.addEventListener('keydown', (event) => {
        // Block all key events when in filename editing mode
        if (gameState.saveDialog && gameState.saveDialog.editingName && gameState.saveDialog.visible) {
            gameState.saveDialog.handleKeyDown(event);
            event.preventDefault();
            event.stopPropagation();
            return;
        }
    }, true); // Use capture phase to run before other handlers

    // Set bonfire callback for origin bonfire
    setBonfireCallback();

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

/**
 * Restart the game - reinitialize everything
 * Exactly like Python restart_game() function
 */
function restartGame() {
    console.log('Restarting game...');

    // Clear current game state
    gameState.souls = [];
    gameState.projectiles = [];
    if (window.particleSystem) {
        window.particleSystem.clear();
        window.particleSystem.setCurrentBlock(0, 0);
    }

    // Recreate world
    gameState.world = new World(game);
    gameState.world.generateBlock(0, 0, { x: game.width / 2, y: game.height / 2 });

    // Recreate player at center
    const centerX = game.width / 2 - 17;
    const centerY = game.height / 2 - 20;
    gameState.player = new Player(game, centerX, centerY, 'link');

    // Update references
    gameState.hud = new HUD(gameState.player, game.width, game.height);
    gameState.characterScreen = new CharacterScreen(gameState.player, game.width, game.height);
    gameState.saveLoadManager.setGameState(gameState.player, gameState.world);

    // Set bonfire callback
    setBonfireCallback();

    // Close any open menus
    if (gameState.characterScreen.isVisible()) {
        gameState.characterScreen.toggle();
    }
    game.showMap = false;

    console.log('Game restarted!');
}

// Game update logic
function updateGame(dt) {
    // Don't update during transitions
    if (gameState.transitioning) {
        return;
    }

    // Handle death screen input when active (highest priority after transitions)
    if (gameState.deathScreen && gameState.deathScreen.isActive()) {
        gameState.deathScreen.handleInput(game.input);
        // Still allow load dialog to be used from death screen
        if (gameState.loadDialog && gameState.loadDialog.isVisible()) {
            gameState.loadDialog.handleInput(game.input);
        }
        return;
    }

    // Handle message dialog input when visible (highest priority)
    if (gameState.messageDialog && gameState.messageDialog.isVisible()) {
        gameState.messageDialog.handleInput(game.input);
        return;
    }

    // Handle save dialog input when visible
    if (gameState.saveDialog && gameState.saveDialog.isVisible()) {
        if (!gameState.saveDialog.editingName) {
            gameState.saveDialog.handleInput(game.input);
        }
        return;
    }

    // Handle load dialog input when visible
    if (gameState.loadDialog && gameState.loadDialog.isVisible()) {
        gameState.loadDialog.handleInput(game.input);
        return;
    }

    // Handle bonfire menu input when visible
    if (gameState.bonfireMenu && gameState.bonfireMenu.isVisible()) {
        gameState.bonfireMenu.handleInput(game.input);
        return;
    }

    // Toggle character screen (must work even when paused)
    if (game.input.isKeyJustPressed('character')) {
        gameState.characterScreen.toggle();
        // Close map if opening character screen
        if (gameState.characterScreen.isVisible()) {
            game.showMap = false;
        }
    }

    // Toggle map (must work even when paused)
    if (game.input.isKeyJustPressed('map')) {
        game.showMap = !game.showMap;
        // Close character screen if opening map
        if (game.showMap && gameState.characterScreen.isVisible()) {
            gameState.characterScreen.toggle();
        }
    }

    // Handle character screen input when visible (before pause check)
    if (gameState.characterScreen && gameState.characterScreen.isVisible()) {
        gameState.characterScreen.handleInput(game.input);
        // Pause game when character screen is open
        return;
    }

    // Pause game when map is open
    if (game.showMap) {
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

    // Handle interact (E key) - for bonfires and NPCs
    if (game.input.isKeyJustPressed('interact')) {
        checkEntityInteraction(player, world, currentTime);
    }

    // Handle add XP (+ key for testing, matching Python)
    if (game.input.isKeyJustPressed('addXp')) {
        player.gainXp(5);
        console.log(`XP: ${player.attributes.xp}/${player.attributes.xpNeeded} | Level: ${player.attributes.level}`);
    }

    // Get all obstacles (for collision)
    const allObstacles = [...obstacles];

    // Update player (pass obstacles for knockback collision)
    player.update(dt, game, allObstacles);

    // Update enemies
    const enemies = world.getEnemies();
    for (const enemy of enemies) {
        enemy.update(dt, player, allObstacles);
    }

    // Update items (for bobbing animation and pickup detection)
    const items = world.getItems();
    for (const item of items) {
        if (item.update(player)) {
            // Item was collected, remove from block
            const currentBlock = world.getCurrentBlock();
            if (currentBlock) {
                currentBlock.removeEntity(item);
            }
        }
    }

    // Update bonfires
    const bonfires = world.getBonfires();
    for (const bonfire of bonfires) {
        bonfire.update(dt, currentTime);
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

    // Check for player death (exactly like Python)
    if (player.attributes.currentHealth <= 0 && !gameState.deathScreen.isActive()) {
        console.log('Player died!');
        gameState.deathScreen.activate();
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

    // Draw HUD (not when death screen is active, like Python)
    if (!gameState.deathScreen || !gameState.deathScreen.isActive()) {
        const enemies = world.getEnemies();
        gameState.hud.draw(ctx, world, {
            entities: enemies,
            showEnemyDebug: game.showDebug
        });
    }

    // Draw overlays
    if (game.showMap) {
        drawMapOverlay(ctx, world);
    }

    if (gameState.characterScreen.isVisible()) {
        gameState.characterScreen.draw(ctx);
    }

    // Draw bonfire menu on top
    if (gameState.bonfireMenu && gameState.bonfireMenu.isVisible()) {
        gameState.bonfireMenu.render(ctx, game.width, game.height);
    }

    // Draw save dialog on top of bonfire menu
    if (gameState.saveDialog && gameState.saveDialog.isVisible()) {
        gameState.saveDialog.render(ctx, game.width, game.height);
    }

    // Draw load dialog on top of everything
    if (gameState.loadDialog && gameState.loadDialog.isVisible()) {
        gameState.loadDialog.render(ctx, game.width, game.height);
    }

    // Draw message dialog on top of everything (success/error messages)
    if (gameState.messageDialog && gameState.messageDialog.isVisible()) {
        gameState.messageDialog.render(ctx, game.width, game.height);
    }

    // Draw death screen on top of everything (when player dies)
    if (gameState.deathScreen && gameState.deathScreen.isActive()) {
        gameState.deathScreen.render(ctx, game.width, game.height, gameState.player);
        // Draw load dialog on top of death screen if visible
        if (gameState.loadDialog && gameState.loadDialog.isVisible()) {
            gameState.loadDialog.render(ctx, game.width, game.height);
        }
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
E - Interact (bonfires, NPCs)
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

// Check if player can interact with any entities nearby (E key)
// Exactly like Python main.py check_entity_interaction function
function checkEntityInteraction(player, world, currentTime) {
    const entities = world.getCurrentEntities();
    const playerRect = player.getRect();
    const playerCenterX = playerRect.x + playerRect.width / 2;
    const playerCenterY = playerRect.y + playerRect.height / 2;

    // Check each entity for interaction
    for (const entity of entities) {
        if (!entity.interact) continue;

        const entityRect = entity.getRect();
        const entityCenterX = entityRect.x + entityRect.width / 2;
        const entityCenterY = entityRect.y + entityRect.height / 2;

        // Calculate distance between centers
        const dx = playerCenterX - entityCenterX;
        const dy = playerCenterY - entityCenterY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // If within 60 pixels, allow interaction
        if (distance < 60) {
            entity.interact(player, currentTime);
            return true;
        }
    }

    return false;
}

// Set the save/load callback for the origin bonfire
// Exactly like Python main.py set_bonfire_callback function
function setBonfireCallback() {
    const world = gameState.world;
    if (!world) return;

    // Get the origin block
    const originBlock = world.getBlockAt(0, 0);
    if (!originBlock) return;

    // Find the bonfire entity
    const entities = originBlock.getEntities();
    for (const entity of entities) {
        if (entity instanceof Bonfire && entity.isOriginBonfire()) {
            // Set the callback to show bonfire menu
            entity.saveLoadCallback = () => {
                if (gameState.bonfireMenu) {
                    gameState.bonfireMenu.show();
                }
            };
            console.log('Set save/load callback for origin bonfire');
            return;
        }
    }

    console.warn('Could not find origin bonfire to set callback');
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
