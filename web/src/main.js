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
    currentBlock: { x: 0, y: 0 }
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

    // Create player at center of screen
    const centerX = game.width / 2 - 17; // Half player width
    const centerY = game.height / 2 - 20; // Half player height
    gameState.player = new Player(game, centerX, centerY, 'link');

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
    const player = gameState.player;
    const currentTime = performance.now();

    // Handle movement
    const movement = game.input.getMovementVector();
    const dx = movement.x * player.speed;
    const dy = movement.y * player.speed;
    player.move(dx, dy, []);

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
        if (player.blink([], currentTime)) {
            console.log('Blink!');
        }
    }

    // Handle firebolt (placeholder)
    if (game.input.isKeyJustPressed('firebolt')) {
        console.log('Firebolt! (Coming in Phase 6)');
    }

    // Handle interact
    if (game.input.isKeyJustPressed('interact')) {
        console.log('Interact pressed!');
    }

    // Toggle map
    if (game.input.isKeyJustPressed('map')) {
        game.showMap = !game.showMap;
    }

    // Toggle character screen
    if (game.input.isKeyJustPressed('character')) {
        game.showCharacterScreen = !game.showCharacterScreen;
    }

    // Update player
    player.update(dt, game);

    // Keep player in bounds (temporary - will be replaced by world transitions)
    player.x = Math.max(0, Math.min(game.width - player.width, player.x));
    player.y = Math.max(0, Math.min(game.height - player.height, player.y));

    // Debug: gain XP on interact (for testing)
    if (game.input.isKeyJustPressed('interact')) {
        player.gainXp(5);
        console.log(`XP: ${player.attributes.xp}/${player.attributes.xpNeeded} | Level: ${player.attributes.level}`);
    }
}

// Game render logic
function renderGame(ctx) {
    const player = gameState.player;

    // Draw ground pattern
    drawGroundPattern(ctx);

    // Render player
    if (player) {
        player.render(ctx, game);
    }

    // Draw HUD (temporary until Phase 7)
    drawTemporaryHUD(ctx, player);

    // Draw overlays
    if (game.showMap) {
        drawMapOverlay(ctx);
    }

    if (game.showCharacterScreen) {
        drawCharacterOverlay(ctx, player);
    }
}

// Draw a simple ground pattern
function drawGroundPattern(ctx) {
    // Draw subtle grid pattern
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    const gridSize = 50;

    for (let x = 0; x < game.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, game.height);
        ctx.stroke();
    }

    for (let y = 0; y < game.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(game.width, y);
        ctx.stroke();
    }
}

// Temporary HUD until Phase 7
function drawTemporaryHUD(ctx, player) {
    if (!player) return;

    const attrs = player.attributes;

    // Background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(10, 10, 200, 100);

    ctx.font = '14px monospace';
    ctx.fillStyle = 'white';

    // Health
    ctx.fillStyle = '#ff4444';
    ctx.fillText(`HP: ${attrs.currentHealth}/${attrs.maxHealth}`, 20, 30);

    // Mana
    ctx.fillStyle = '#4444ff';
    ctx.fillText(`MP: ${attrs.currentMana}/${attrs.maxMana}`, 20, 50);

    // Level & XP
    ctx.fillStyle = '#ffff44';
    ctx.fillText(`Level: ${attrs.level}`, 20, 70);

    const xpPercent = attrs.xpNeeded > 0 ? ((attrs.xp / attrs.xpNeeded) * 100).toFixed(1) : 100;
    ctx.fillStyle = '#44ff44';
    ctx.fillText(`XP: ${attrs.xp}/${attrs.xpNeeded} (${xpPercent}%)`, 20, 90);

    // Controls hint
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '12px monospace';
    ctx.fillText('WASD: Move | SPACE: Attack | SHIFT: Dash | B: Blink', 10, game.height - 10);
}

// Map overlay
function drawMapOverlay(ctx) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(0, 0, game.width, game.height);

    ctx.fillStyle = 'white';
    ctx.font = '32px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('WORLD MAP', game.width / 2, 60);

    ctx.font = '18px Arial';
    ctx.fillText('(Coming in Phase 3 - World System)', game.width / 2, 100);

    // Draw a placeholder grid
    const gridSize = 60;
    const offsetX = game.width / 2 - gridSize * 2.5;
    const offsetY = game.height / 2 - gridSize * 2;

    for (let y = 0; y < 5; y++) {
        for (let x = 0; x < 5; x++) {
            const px = offsetX + x * gridSize;
            const py = offsetY + y * gridSize;

            ctx.strokeStyle = '#444';
            ctx.lineWidth = 1;
            ctx.strokeRect(px, py, gridSize - 2, gridSize - 2);

            // Current block indicator
            if (x === 2 && y === 2) {
                ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
                ctx.fillRect(px, py, gridSize - 2, gridSize - 2);
                ctx.fillStyle = 'lime';
                ctx.font = '12px Arial';
                ctx.fillText('YOU', px + gridSize / 2, py + gridSize / 2 + 4);
            }
        }
    }

    ctx.font = '16px Arial';
    ctx.fillStyle = '#888';
    ctx.fillText('Press M to close', game.width / 2, game.height - 40);
    ctx.textAlign = 'left';
}

// Character screen overlay
function drawCharacterOverlay(ctx, player) {
    if (!player) return;

    const attrs = player.attributes;

    // Background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
    ctx.fillRect(100, 80, game.width - 200, game.height - 160);

    // Border
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;
    ctx.strokeRect(100, 80, game.width - 200, game.height - 160);

    // Title
    ctx.fillStyle = 'white';
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('CHARACTER', game.width / 2, 130);

    ctx.textAlign = 'left';
    ctx.font = '18px monospace';

    const startX = 150;
    let y = 180;

    // Level info
    ctx.fillStyle = '#ffdd44';
    ctx.fillText(`Level: ${attrs.level} / ${attrs.maxLevel}`, startX, y);
    y += 30;

    // XP bar
    ctx.fillStyle = '#888';
    ctx.fillText(`XP: ${attrs.xp} / ${attrs.xpNeeded}`, startX, y);
    y += 20;

    // XP progress bar
    ctx.fillStyle = '#333';
    ctx.fillRect(startX, y, 300, 20);
    const xpWidth = attrs.xpNeeded > 0 ? (attrs.xp / attrs.xpNeeded) * 300 : 300;
    ctx.fillStyle = '#44aa44';
    ctx.fillRect(startX, y, xpWidth, 20);
    ctx.strokeStyle = '#666';
    ctx.strokeRect(startX, y, 300, 20);
    y += 50;

    // Stats
    ctx.fillStyle = '#ff6666';
    ctx.fillText(`STR: ${attrs.str}`, startX, y);
    ctx.fillStyle = '#aaa';
    ctx.fillText(`(Attack Power: ${attrs.getAttackPower()})`, startX + 100, y);
    y += 30;

    ctx.fillStyle = '#66ff66';
    ctx.fillText(`CON: ${attrs.con}`, startX, y);
    ctx.fillStyle = '#aaa';
    ctx.fillText(`(Max HP: ${attrs.maxHealth})`, startX + 100, y);
    y += 30;

    ctx.fillStyle = '#66ffff';
    ctx.fillText(`DEX: ${attrs.dex}`, startX, y);
    ctx.fillStyle = '#aaa';
    ctx.fillText(`(Speed: ${player.baseSpeed.toFixed(2)})`, startX + 100, y);
    y += 30;

    ctx.fillStyle = '#ff66ff';
    ctx.fillText(`INT: ${attrs.int}`, startX, y);
    ctx.fillStyle = '#aaa';
    ctx.fillText(`(Max MP: ${attrs.maxMana})`, startX + 100, y);
    y += 50;

    // Available points
    if (attrs.statPoints > 0) {
        ctx.fillStyle = '#ffff00';
        ctx.fillText(`Available Stat Points: ${attrs.statPoints}`, startX, y);
        y += 25;
        ctx.fillStyle = '#888';
        ctx.font = '14px monospace';
        ctx.fillText('(Stat allocation coming in Phase 8)', startX, y);
    }

    // Close hint
    ctx.fillStyle = '#888';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Press ENTER to close', game.width / 2, game.height - 100);
    ctx.textAlign = 'left';
}

// Show controls info
function showControlsInfo() {
    console.log(`
=== The Dark Garden of Z - Controls ===
WASD / Arrow Keys - Move
Space - Attack (Sword Swing)
E - Interact (also gives 5 XP for testing)
Shift - Dash (speed boost)
B - Blink (teleport forward)
F - Firebolt (Coming Phase 6)
M - Map
Enter - Character Screen
C - Debug Mode

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

// Start the game when page loads
window.addEventListener('load', init);
