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
    // Handle input for testing
    const movement = game.input.getMovementVector();
    const direction = game.input.getFacingDirection();

    // Test attack
    if (game.input.isKeyJustPressed('attack')) {
        console.log('Attack pressed!');
    }

    // Test interact
    if (game.input.isKeyJustPressed('interact')) {
        console.log('Interact pressed!');
    }

    // Test firebolt
    if (game.input.isKeyJustPressed('firebolt')) {
        console.log('Firebolt pressed!');
    }

    // Test blink
    if (game.input.isKeyJustPressed('blink')) {
        console.log('Blink pressed!');
    }

    // Test dash
    if (game.input.isKeyJustPressed('dash')) {
        console.log('Dash pressed!');
    }

    // Test map toggle
    if (game.input.isKeyJustPressed('map')) {
        game.showMap = !game.showMap;
        console.log('Map toggled:', game.showMap);
    }

    // Test character screen toggle
    if (game.input.isKeyJustPressed('character')) {
        game.showCharacterScreen = !game.showCharacterScreen;
        console.log('Character screen toggled:', game.showCharacterScreen);
    }

    // Update debug info display
    updateDebugInfo(movement, direction);
}

// Game render logic
function renderGame(ctx) {
    // Draw test grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
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

    // Draw center crosshair
    const centerX = game.width / 2;
    const centerY = game.height / 2;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(centerX - 20, centerY);
    ctx.lineTo(centerX + 20, centerY);
    ctx.moveTo(centerX, centerY - 20);
    ctx.lineTo(centerX, centerY + 20);
    ctx.stroke();

    // Draw movement indicator
    const movement = game.input.getMovementVector();
    if (movement.x !== 0 || movement.y !== 0) {
        const indicatorLength = 50;
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(
            centerX + movement.x * indicatorLength,
            centerY + movement.y * indicatorLength
        );
        ctx.stroke();

        // Draw arrow head
        const angle = Math.atan2(movement.y, movement.x);
        const headLength = 15;
        ctx.beginPath();
        ctx.moveTo(
            centerX + movement.x * indicatorLength,
            centerY + movement.y * indicatorLength
        );
        ctx.lineTo(
            centerX + movement.x * indicatorLength - headLength * Math.cos(angle - Math.PI / 6),
            centerY + movement.y * indicatorLength - headLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(
            centerX + movement.x * indicatorLength,
            centerY + movement.y * indicatorLength
        );
        ctx.lineTo(
            centerX + movement.x * indicatorLength - headLength * Math.cos(angle + Math.PI / 6),
            centerY + movement.y * indicatorLength - headLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.stroke();
    }

    // Draw test sprite if loaded
    const sprites = game.getImage('sprites');
    if (sprites) {
        // Draw Link sprite from spritesheet at center
        game.drawSprite(sprites, 1, 3, 16, 24, centerX - 35, centerY + 50, 70, 96);
    }

    // Draw info text
    ctx.fillStyle = 'white';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Phase 1: Core Engine Test', centerX, 50);

    ctx.font = '16px Arial';
    ctx.fillText('Use WASD/Arrow keys or Gamepad to move', centerX, 80);
    ctx.fillText('Press C to toggle debug mode', centerX, 100);

    // Draw state indicators
    if (game.showMap) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(0, 0, game.width, game.height);
        ctx.fillStyle = 'white';
        ctx.font = '32px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('MAP SCREEN (Press M to close)', centerX, centerY);
    }

    if (game.showCharacterScreen) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(100, 100, game.width - 200, game.height - 200);
        ctx.fillStyle = 'white';
        ctx.font = '32px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('CHARACTER SCREEN (Press Enter to close)', centerX, centerY);
    }

    ctx.textAlign = 'left';
}

// Update debug info element
function updateDebugInfo(movement, direction) {
    const debugElement = document.getElementById('debug-info');
    if (debugElement && game.showDebug) {
        debugElement.innerHTML = `
            Movement: (${movement.x.toFixed(2)}, ${movement.y.toFixed(2)})<br>
            Direction: ${direction || 'none'}<br>
            Gamepad: ${game.input.hasGamepad() ? 'Connected' : 'None'}
        `;
        debugElement.style.display = 'block';
    } else if (debugElement) {
        debugElement.style.display = 'none';
    }
}

// Show controls info
function showControlsInfo() {
    console.log(`
=== The Dark Garden of Z - Controls ===
WASD / Arrow Keys - Move
Space - Attack
E - Interact
F - Firebolt
B - Blink
Shift - Dash
M - Map
Enter - Character Screen
C - Debug Mode
Escape - Pause

Gamepad:
Left Stick - Move
A - Attack
B - Blink
X - Firebolt
Y - Interact
LB/RB - Dash
Start - Character Screen
Select - Pause
===================================
    `);
}

// Start the game when page loads
window.addEventListener('load', init);
