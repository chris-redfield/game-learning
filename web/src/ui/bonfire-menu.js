/**
 * BonfireMenu - Dialog menu for bonfire interaction (Save/Load/Cancel)
 * Exactly like it was implemented at the python code (dialog.py)
 */
class BonfireMenu {
    constructor() {
        this.visible = false;
        this.selectedOption = 0;
        this.options = ['Save Game', 'Load Game', 'Cancel'];
        this.title = 'Bonfire';

        // Callbacks
        this.onSave = null;
        this.onLoad = null;

        // Colors matching Python
        this.colors = {
            background: 'rgba(30, 33, 41, 0.9)',
            text: '#ffffff',
            title: '#ffd700',
            option: '#c8c8c8',
            selected: '#ffff00',
            border: '#b4b4c8'
        };

        // Dialog dimensions
        this.width = 300;
        this.optionHeight = 30;
        this.padding = 20;
    }

    show() {
        this.visible = true;
        this.selectedOption = 0;
    }

    hide() {
        this.visible = false;
    }

    isVisible() {
        return this.visible;
    }

    selectNext() {
        this.selectedOption = (this.selectedOption + 1) % this.options.length;
    }

    selectPrev() {
        this.selectedOption = (this.selectedOption - 1 + this.options.length) % this.options.length;
    }

    selectOption() {
        const selected = this.options[this.selectedOption];

        if (selected === 'Save Game' && this.onSave) {
            this.onSave();
        } else if (selected === 'Load Game' && this.onLoad) {
            this.onLoad();
        }

        this.hide();
    }

    handleInput(input) {
        if (!this.visible) return false;

        // Check for up/down navigation
        if (input.isKeyJustPressed('up')) {
            this.selectPrev();
            return true;
        }
        if (input.isKeyJustPressed('down')) {
            this.selectNext();
            return true;
        }

        // Check for selection
        if (input.isKeyJustPressed('confirm') || input.isKeyJustPressed('interact')) {
            this.selectOption();
            return true;
        }

        // Check for cancel
        if (input.isKeyJustPressed('escape') || input.isKeyJustPressed('back')) {
            this.hide();
            return true;
        }

        return true; // Block other input while menu is visible
    }

    render(ctx, screenWidth, screenHeight) {
        if (!this.visible) return;

        // Calculate dialog height based on options
        const height = 80 + this.options.length * this.optionHeight;

        // Center dialog on screen
        const x = (screenWidth - this.width) / 2;
        const y = (screenHeight - height) / 2;

        // Draw background
        ctx.fillStyle = this.colors.background;
        ctx.fillRect(x, y, this.width, height);

        // Draw border
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, this.width, height);

        // Draw title
        ctx.font = 'bold 20px Arial';
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.fillText(this.title, x + this.width / 2, y + this.padding + 15);

        // Draw options
        ctx.font = '16px Arial';
        for (let i = 0; i < this.options.length; i++) {
            const optionY = y + this.padding + 50 + i * this.optionHeight;

            if (i === this.selectedOption) {
                ctx.fillStyle = this.colors.selected;
                // Draw cursor
                ctx.textAlign = 'left';
                ctx.fillText('>', x + this.padding, optionY);
            } else {
                ctx.fillStyle = this.colors.option;
            }

            ctx.textAlign = 'left';
            ctx.fillText(this.options[i], x + this.padding + 20, optionY);
        }

        // Reset text align
        ctx.textAlign = 'left';
    }
}

/**
 * SaveLoadManager - Handles saving and loading game state to localStorage
 * Exactly like it was implemented at the python code (save_manager.py)
 */
class SaveLoadManager {
    constructor() {
        this.saveKey = 'dark_garden_save';
        this.maxSlots = 3;
    }

    getSaveSlots() {
        const slots = [];
        for (let i = 1; i <= this.maxSlots; i++) {
            const key = `${this.saveKey}_${i}`;
            const data = localStorage.getItem(key);
            if (data) {
                try {
                    const parsed = JSON.parse(data);
                    slots.push({
                        slot: i,
                        exists: true,
                        timestamp: parsed.timestamp || 'Unknown',
                        level: parsed.level || 1
                    });
                } catch (e) {
                    slots.push({ slot: i, exists: false });
                }
            } else {
                slots.push({ slot: i, exists: false });
            }
        }
        return slots;
    }

    saveGame(slot, player, world) {
        const saveData = {
            timestamp: new Date().toISOString(),
            // Player position
            playerX: player.x,
            playerY: player.y,
            // Block position
            blockX: world.currentBlockCoords.x,
            blockY: world.currentBlockCoords.y,
            // Player attributes
            level: player.attributes.level,
            xp: player.attributes.xp,
            currentHealth: player.attributes.currentHealth,
            maxHealth: player.attributes.maxHealth,
            currentMana: player.attributes.currentMana,
            maxMana: player.attributes.maxMana,
            // Stats
            str: player.attributes.str,
            con: player.attributes.con,
            dex: player.attributes.dex,
            int: player.attributes.int,
            statPoints: player.attributes.statPoints,
            skillPoints: player.attributes.skillPoints,
            // Progression items
            foundAncientScroll: player.attributes.foundAncientScroll,
            foundDragonHeart: player.attributes.foundDragonHeart,
            // Skills
            unlockedSkills: this.getUnlockedSkills(player)
        };

        const key = `${this.saveKey}_${slot}`;
        localStorage.setItem(key, JSON.stringify(saveData));
        console.log(`Game saved to slot ${slot}`);
        return true;
    }

    loadGame(slot, player, world) {
        const key = `${this.saveKey}_${slot}`;
        const data = localStorage.getItem(key);

        if (!data) {
            console.log(`No save data in slot ${slot}`);
            return false;
        }

        try {
            const saveData = JSON.parse(data);

            // Restore player position
            player.x = saveData.playerX;
            player.y = saveData.playerY;

            // Restore block position
            world.currentBlockCoords.x = saveData.blockX;
            world.currentBlockCoords.y = saveData.blockY;

            // Ensure the block is generated
            world.getBlockAt(saveData.blockX, saveData.blockY);

            // Restore attributes
            player.attributes.level = saveData.level;
            player.attributes.xp = saveData.xp;
            player.attributes.currentHealth = saveData.currentHealth;
            player.attributes.maxHealth = saveData.maxHealth;
            player.attributes.currentMana = saveData.currentMana;
            player.attributes.maxMana = saveData.maxMana;

            // Restore stats
            player.attributes.str = saveData.str;
            player.attributes.con = saveData.con;
            player.attributes.dex = saveData.dex;
            player.attributes.int = saveData.int;
            player.attributes.statPoints = saveData.statPoints;
            player.attributes.skillPoints = saveData.skillPoints;

            // Restore progression items
            player.attributes.foundAncientScroll = saveData.foundAncientScroll || false;
            player.attributes.foundDragonHeart = saveData.foundDragonHeart || false;

            // Restore skills
            if (saveData.unlockedSkills) {
                this.restoreUnlockedSkills(player, saveData.unlockedSkills);
            }

            // Recalculate XP needed
            player.attributes.xpNeeded = player.attributes.getXpNeeded();

            console.log(`Game loaded from slot ${slot}`);
            return true;
        } catch (e) {
            console.error('Error loading save:', e);
            return false;
        }
    }

    getUnlockedSkills(player) {
        const unlocked = [];
        for (const [skillId, skill] of Object.entries(player.skillTree.skills)) {
            if (skill.unlocked) {
                unlocked.push(skillId);
            }
        }
        return unlocked;
    }

    restoreUnlockedSkills(player, unlockedSkills) {
        // Reset all skills first
        for (const skill of Object.values(player.skillTree.skills)) {
            skill.unlocked = false;
        }

        // Unlock saved skills
        for (const skillId of unlockedSkills) {
            if (player.skillTree.skills[skillId]) {
                player.skillTree.skills[skillId].unlocked = true;

                // Apply skill effects
                if (skillId === 'dash') {
                    player.attributes.canDash = true;
                } else if (skillId === 'extended_sword') {
                    player.attributes.swordLength = Math.floor(player.attributes.baseSwordLength * 1.5);
                } else if (skillId === 'blink') {
                    player.attributes.canBlink = true;
                }
            }
        }
    }

    deleteSave(slot) {
        const key = `${this.saveKey}_${slot}`;
        localStorage.removeItem(key);
        console.log(`Save slot ${slot} deleted`);
    }
}

// Export
window.BonfireMenu = BonfireMenu;
window.SaveLoadManager = SaveLoadManager;
