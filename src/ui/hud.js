/**
 * HUD - Heads Up Display for game status
 * Mirrors Python hud.py
 */
class HUD {
    constructor(player, screenWidth, screenHeight) {
        this.player = player;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;

        // Colors (matching Python)
        this.colors = {
            border: 'rgb(30, 30, 30)',        // Dark border
            health: 'rgb(220, 50, 50)',       // Red for health
            mana: 'rgb(50, 50, 220)',         // Blue for mana
            bg: 'rgb(60, 60, 60)',            // Dark gray background
            text: 'rgb(255, 255, 255)',       // White text
            xp: 'rgb(255, 255, 255)'          // White for XP text
        };

        // Bar scaling parameters (matching Python)
        this.healthBaseWidth = 30;     // Base width for initial health (6)
        this.healthScaling = 7;        // Width increase per health point
        this.manaBaseWidth = 10;       // Base width for initial mana (2)
        this.manaScaling = 6;          // Width increase per mana point

        // Fonts
        this.font = '16px Arial';
        this.smallFont = '14px Arial';
    }

    /**
     * Draw status bars (health and mana)
     */
    drawStatusBars(ctx) {
        const player = this.player;
        const attrs = player.attributes;

        // Measurements
        const margin = 10;
        const barSpacing = 5;
        const barHeight = 15;
        const iconSize = 40;
        const maxBarWidth = 300;

        // Draw the octagonal icon placeholder
        const iconX = margin;
        const iconY = margin;

        // Outer border
        ctx.fillStyle = this.colors.border;
        ctx.fillRect(iconX, iconY, iconSize, iconSize);

        // Inner fill
        ctx.fillStyle = 'rgb(30, 30, 40)';
        ctx.fillRect(iconX + 2, iconY + 2, iconSize - 4, iconSize - 4);

        // Calculate health bar width - scales linearly with max health
        const healthWidth = Math.min(
            maxBarWidth,
            this.healthBaseWidth + (attrs.maxHealth - 5) * this.healthScaling
        );

        // Calculate mana bar width - scales linearly with max mana
        const manaWidth = Math.min(
            maxBarWidth,
            this.manaBaseWidth + (attrs.maxMana - 1) * this.manaScaling
        );

        // Bar positions
        const healthX = iconX + iconSize + 10;
        const healthY = iconY;
        const manaX = healthX;
        const manaY = healthY + barHeight + barSpacing;

        // Calculate fill percentages
        const healthPercent = attrs.currentHealth / attrs.maxHealth;
        const healthFillWidth = Math.floor(healthWidth * healthPercent);

        const manaPercent = attrs.currentMana / attrs.maxMana;
        const manaFillWidth = Math.floor(manaWidth * manaPercent);

        // Draw health bar
        // Background
        ctx.fillStyle = this.colors.bg;
        ctx.fillRect(healthX, healthY, healthWidth, barHeight);
        // Border
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(healthX, healthY, healthWidth, barHeight);
        // Fill
        ctx.fillStyle = this.colors.health;
        ctx.fillRect(healthX, healthY, healthFillWidth, barHeight);

        // Draw mana bar
        // Background
        ctx.fillStyle = this.colors.bg;
        ctx.fillRect(manaX, manaY, manaWidth, barHeight);
        // Border
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(manaX, manaY, manaWidth, barHeight);
        // Fill
        ctx.fillStyle = this.colors.mana;
        ctx.fillRect(manaX, manaY, manaFillWidth, barHeight);

        // Display XP text underneath the icon
        ctx.font = this.font;
        ctx.fillStyle = this.colors.xp;
        const xpText = `XP: ${Math.floor(attrs.xp)}/${Math.floor(attrs.xpNeeded)}`;
        const textX = iconX;
        const textY = iconY + iconSize + 17; // 5px padding + font size
        ctx.fillText(xpText, textX, textY);

        // Display values on bars
        ctx.fillStyle = this.colors.text;
        ctx.fillText(`${attrs.currentHealth}/${attrs.maxHealth}`, healthX + 5, healthY + 12);
        ctx.fillText(`${attrs.currentMana}/${attrs.maxMana}`, manaX + 5, manaY + 12);
    }

    /**
     * Display ability status information
     */
    renderAbilityInfo(ctx) {
        const player = this.player;

        // Position below status bars with extra space for XP text
        let x = 10;
        let y = 85;

        ctx.font = this.font;

        // Dash ability (check player.dashing and player.dashTimer)
        if (player.skillTree && player.skillTree.isSkillUnlocked('dash')) {
            let dashStatus, color;

            if (player.dashing) {
                dashStatus = 'ACTIVE';
                color = 'rgb(0, 255, 0)'; // Green when active
            } else if (player.dashTimer === 0) {
                dashStatus = 'Ready';
                color = 'rgb(255, 255, 255)'; // White when ready
            } else {
                dashStatus = 'Cooling Down';
                color = 'rgb(255, 165, 0)'; // Orange when on cooldown
            }

            ctx.fillStyle = color;
            ctx.fillText(`Dash: ${dashStatus}`, x, y);
            y += 25;
        }

        // Extended Sword ability
        if (player.skillTree && player.skillTree.isSkillUnlocked('extended_sword')) {
            ctx.fillStyle = this.colors.text;
            ctx.fillText('Extended Sword: Active', x, y);
            y += 25;
        }

        // Blink ability (check player.blinkTimer)
        if (player.skillTree && player.skillTree.isSkillUnlocked('blink')) {
            let blinkStatus, blinkColor;

            if (player.blinkTimer === 0) {
                blinkStatus = 'Ready';
                blinkColor = this.colors.text;
            } else {
                blinkStatus = 'Cooling Down';
                blinkColor = 'rgb(255, 165, 0)'; // Orange
            }

            ctx.fillStyle = blinkColor;
            ctx.fillText(`Blink: ${blinkStatus}`, x, y);
        }
    }

    /**
     * Display information about the current world block
     */
    displayWorldInfo(ctx, blockInfo) {
        ctx.font = this.font;
        ctx.fillStyle = this.colors.text;
        ctx.fillText(`Current: ${blockInfo}`, this.screenWidth - 150, 25);
    }

    /**
     * Display game controls
     */
    displayControls(ctx, showDebug = false) {
        ctx.font = this.font;
        ctx.fillStyle = this.colors.text;

        if (showDebug) {
            const controlsY = this.screenHeight - 165;
            const controls = [
                'Controls:',
                'WASD or Arrow Keys: Move',
                'SPACE: Swing Sword',
                'F: Firebolt',
                'E: Interact',
                'SHIFT: Dash (if unlocked)',
                'B: Blink (if unlocked)',
                'C: Show Collision Boxes',
                'M: Toggle Map',
                'ENTER: Character Screen'
            ];

            for (let i = 0; i < controls.length; i++) {
                ctx.fillText(controls[i], 10, controlsY + i * 15);
            }
        } else {
            ctx.fillText('Hold C for debug and control keys', 10, this.screenHeight - 20);
        }
    }

    /**
     * Draw transition effect between blocks
     */
    drawTransitionEffect(ctx, fadeAlpha, transitionDirection) {
        // Draw fade overlay
        ctx.fillStyle = `rgba(0, 0, 0, ${fadeAlpha / 255})`;
        ctx.fillRect(0, 0, this.screenWidth, this.screenHeight);

        // Show transition text during fade
        if (fadeAlpha > 50 && transitionDirection) {
            ctx.font = this.font;
            ctx.fillStyle = this.colors.text;
            ctx.textAlign = 'center';
            ctx.fillText(
                `Moving ${transitionDirection.toUpperCase()}`,
                this.screenWidth / 2,
                this.screenHeight / 2
            );
            ctx.textAlign = 'left';
        }
    }

    /**
     * Display debug info for each enemy
     */
    displayEnemyDebug(ctx, entities) {
        let x = this.screenWidth - 450;
        let y = 40;
        const lineGap = 20;

        ctx.font = this.font;
        let anyFound = false;

        for (const entity of entities) {
            // Check if it's an enemy (has attributes and speed)
            if (entity.attributes && entity.speed !== undefined && entity.state !== undefined) {
                anyFound = true;

                const name = entity.name || entity.constructor.name;
                const level = entity.attributes.level || 1;
                const speed = entity.speed.toFixed(3);
                const difficulty = entity.difficulty || 'normal';
                const state = entity.state || 'unknown';

                const maxHealth = entity.attributes.maxHealth || 0;
                const currentHealth = entity.attributes.currentHealth || 0;
                const attack = (entity.attributes.attackPower || 0).toFixed(3);
                const defense = (entity.attributes.defense || 0).toFixed(3);

                // Choose color based on difficulty
                const colorMap = {
                    'normal': 'rgb(200, 200, 200)',
                    'fast': 'rgb(0, 255, 0)',
                    'strong': 'rgb(255, 0, 0)'
                };
                const color = colorMap[difficulty] || 'rgb(255, 255, 255)';

                ctx.fillStyle = color;
                const text = `${name} (Lvl ${level}, ${difficulty}) HP ${currentHealth}/${maxHealth} ATK ${attack} DEF ${defense} SPEED: ${speed} State: ${state}`;
                ctx.fillText(text, x, y);
                y += lineGap;
            }
        }

        if (!anyFound) {
            ctx.fillStyle = 'rgb(255, 255, 0)';
            ctx.fillText('No enemy debug info available.', x, y);
        }
    }

    /**
     * Draw all HUD elements
     */
    draw(ctx, world, options = {}) {
        const {
            fadeAlpha = 0,
            transitionDirection = null,
            transitionInProgress = false,
            entities = [],
            showEnemyDebug = false
        } = options;

        // Draw status bars
        this.drawStatusBars(ctx);

        // Display ability info
        this.renderAbilityInfo(ctx);

        // Display world info
        if (world && world.getBlockDescription) {
            const blockInfo = world.getBlockDescription();
            this.displayWorldInfo(ctx, blockInfo);
        }

        // Display controls
        this.displayControls(ctx, showEnemyDebug);

        // Enemy debug info in upper right removed - info now shown above each enemy

        // Draw transition effect if in progress
        if (transitionInProgress && fadeAlpha > 0) {
            this.drawTransitionEffect(ctx, fadeAlpha, transitionDirection);
        }
    }
}

// Export
window.HUD = HUD;
