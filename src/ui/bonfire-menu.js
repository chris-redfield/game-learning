/**
 * Dialog system for bonfire save/load functionality
 * Exactly like it was implemented at the python code (dialog.py)
 */

// Base Dialog class
class Dialog {
    constructor(title, options = [], callback = null) {
        this.title = title;
        this.options = options;
        this.callback = callback;
        this.visible = false;
        this.selectedOption = 0;
        this.justShown = false; // Prevent input on same frame as show()

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
        this.width = 500;
        this.optionHeight = 30;
        this.padding = 20;
    }

    show() {
        this.visible = true;
        this.selectedOption = 0;
        this.justShown = true; // Will be cleared after first input check
    }

    hide() {
        this.visible = false;
    }

    isVisible() {
        return this.visible;
    }

    selectNext() {
        if (this.options.length > 0) {
            this.selectedOption = (this.selectedOption + 1) % this.options.length;
        }
    }

    selectPrev() {
        if (this.options.length > 0) {
            this.selectedOption = (this.selectedOption - 1 + this.options.length) % this.options.length;
        }
    }

    selectOption() {
        if (this.callback && this.options.length > 0) {
            this.callback(this.selectedOption);
        }
    }

    handleInput(input) {
        if (!this.visible) return false;

        // Skip input on the same frame the dialog was shown
        // This prevents the key that opened this dialog from also selecting an option
        if (this.justShown) {
            this.justShown = false;
            return true; // Block input but don't process
        }

        if (input.isKeyJustPressed('up')) {
            this.selectPrev();
            return true;
        }
        if (input.isKeyJustPressed('down')) {
            this.selectNext();
            return true;
        }
        if (input.isKeyJustPressed('confirm') || input.isKeyJustPressed('interact')) {
            this.selectOption();
            return true;
        }
        if (input.isKeyJustPressed('escape') || input.isKeyJustPressed('back')) {
            this.hide();
            return true;
        }

        return true; // Block other input
    }

    render(ctx, screenWidth, screenHeight) {
        if (!this.visible) return;

        const height = 100 + this.options.length * this.optionHeight;
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
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.fillText(this.title, x + this.width / 2, y + this.padding + 20);

        // Draw options
        ctx.font = '20px Arial';
        for (let i = 0; i < this.options.length; i++) {
            const optionY = y + this.padding + 60 + i * this.optionHeight;

            if (i === this.selectedOption) {
                ctx.fillStyle = this.colors.selected;
                ctx.textAlign = 'left';
                ctx.fillText('>', x + this.padding, optionY);
            } else {
                ctx.fillStyle = this.colors.option;
            }

            ctx.textAlign = 'left';
            ctx.fillText(this.options[i], x + this.padding + 20, optionY);
        }

        ctx.textAlign = 'left';
    }
}

// BonfireMenu - Main menu with Save/Load/Cancel
class BonfireMenu extends Dialog {
    constructor(onSaveCallback, onLoadCallback) {
        super('Bonfire', ['Save Game', 'Load Game', 'Cancel'], null);
        this.onSaveCallback = onSaveCallback;
        this.onLoadCallback = onLoadCallback;
        this.width = 300;
    }

    selectOption() {
        const selected = this.options[this.selectedOption];
        this.hide();

        if (selected === 'Save Game' && this.onSaveCallback) {
            this.onSaveCallback();
        } else if (selected === 'Load Game' && this.onLoadCallback) {
            this.onLoadCallback();
        }
    }
}

// FileDialog - Base for save/load file selection
class FileDialog extends Dialog {
    constructor(title, message = '', callback = null) {
        super(title, [], callback);
        this.message = message;
        this.files = [];
    }

    setFiles(files) {
        this.files = files;
        this.options = [...files];
        this.selectedOption = 0;
    }

    render(ctx, screenWidth, screenHeight) {
        if (!this.visible) return;

        const messageHeight = this.message ? 30 : 0;
        const height = 100 + messageHeight + this.options.length * this.optionHeight;
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
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.fillText(this.title, x + this.width / 2, y + this.padding + 20);

        // Draw message
        let currentY = y + this.padding + 50;
        if (this.message) {
            ctx.font = '16px Arial';
            ctx.fillStyle = this.colors.text;
            ctx.textAlign = 'left';
            ctx.fillText(this.message, x + this.padding, currentY);
            currentY += 30;
        }

        // Draw options
        ctx.font = '20px Arial';
        for (let i = 0; i < this.options.length; i++) {
            const optionY = currentY + i * this.optionHeight;

            if (i === this.selectedOption) {
                ctx.fillStyle = this.colors.selected;
                ctx.textAlign = 'left';
                ctx.fillText('>', x + this.padding, optionY);
            } else {
                ctx.fillStyle = this.colors.option;
            }

            ctx.textAlign = 'left';
            ctx.fillText(this.options[i], x + this.padding + 20, optionY);
        }

        ctx.textAlign = 'left';
    }
}

// SaveOverwriteDialog - For save game with file creation
class SaveOverwriteDialog extends FileDialog {
    constructor(saveManager, onSaveComplete) {
        super('Save Game', 'Choose a save file to overwrite, or create a new one:');
        this.saveManager = saveManager;
        this.onSaveComplete = onSaveComplete;
        this.editingName = false;
        this.enteredName = '';
        this.defaultName = this.generateDefaultName();
    }

    generateDefaultName() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hour = String(now.getHours()).padStart(2, '0');
        const minute = String(now.getMinutes()).padStart(2, '0');
        const second = String(now.getSeconds()).padStart(2, '0');
        return `${year}${month}${day}_${hour}${minute}${second}.sav`;
    }

    show() {
        super.show();
        this.editingName = false;
        this.enteredName = '';
        this.defaultName = this.generateDefaultName();
        this.refreshFiles();
    }

    refreshFiles() {
        const files = this.saveManager.getSaveFiles();
        this.setFiles([...files, '<Create New Save>']);
    }

    selectOption() {
        const selected = this.options[this.selectedOption];

        if (selected === '<Create New Save>') {
            this.editingName = true;
            this.enteredName = '';
        } else {
            // Overwrite existing file
            this.saveToFile(selected);
        }
    }

    saveToFile(filename) {
        this.saveManager.saveGameToFile(filename);
        this.hide();
        if (this.onSaveComplete) {
            this.onSaveComplete(filename);
        }
    }

    handleInput(input) {
        if (!this.visible) return false;

        if (this.editingName) {
            // Handle text input for filename
            return true; // Let keyboard events pass through
        }

        return super.handleInput(input);
    }

    handleKeyDown(event) {
        if (!this.visible || !this.editingName) return false;

        if (event.key === 'Enter') {
            let finalName = this.enteredName || this.defaultName;
            if (!finalName.endsWith('.sav')) {
                finalName += '.sav';
            }
            this.saveToFile(finalName);
            return true;
        } else if (event.key === 'Escape') {
            this.editingName = false;
            return true;
        } else if (event.key === 'Backspace') {
            this.enteredName = this.enteredName.slice(0, -1);
            return true;
        } else if (event.key.length === 1 && !event.ctrlKey && !event.altKey) {
            // Only add printable characters
            this.enteredName += event.key;
            return true;
        }

        return false;
    }

    render(ctx, screenWidth, screenHeight) {
        super.render(ctx, screenWidth, screenHeight);

        if (this.editingName && this.visible) {
            // Draw filename entry prompt
            const text = `Enter filename: ${this.enteredName || this.defaultName}`;
            ctx.font = '18px Arial';
            ctx.fillStyle = this.colors.text;
            ctx.textAlign = 'center';
            ctx.fillText(text, screenWidth / 2, screenHeight / 2 + 150);
            ctx.textAlign = 'left';
        }
    }
}

// LoadFileDialog - For load game file selection
class LoadFileDialog extends FileDialog {
    constructor(saveManager, onLoadComplete) {
        super('Load Game', 'Select a save file to load:');
        this.saveManager = saveManager;
        this.onLoadComplete = onLoadComplete;
        this.noSaves = false;
    }

    show() {
        super.show();
        this.refreshFiles();
    }

    refreshFiles() {
        const files = this.saveManager.getSaveFiles();
        if (files.length === 0) {
            this.noSaves = true;
            this.message = 'There are no save files.';
            this.setFiles(['Back']);
        } else {
            this.noSaves = false;
            this.message = 'Select a save file to load:';
            // Add Back option at the end of file list
            this.setFiles([...files, 'Back']);
        }
    }

    selectOption() {
        const selected = this.options[this.selectedOption];

        // Back option - just hide the dialog
        if (selected === 'Back') {
            this.hide();
            return;
        }

        // Load the selected save file
        const success = this.saveManager.loadGameFromFile(selected);
        this.hide();

        if (this.onLoadComplete) {
            this.onLoadComplete(selected, success);
        }
    }
}

// SaveLoadManager - Handles saving and loading game state
class SaveLoadManager {
    constructor(player, world) {
        this.player = player;
        this.world = world;
        this.saveKeyPrefix = 'dark_garden_';
    }

    setGameState(player, world) {
        this.player = player;
        this.world = world;
    }

    getSaveFiles() {
        const files = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(this.saveKeyPrefix)) {
                const filename = key.replace(this.saveKeyPrefix, '');
                files.push(filename);
            }
        }
        // Sort by filename (which includes timestamp)
        files.sort().reverse();
        return files;
    }

    saveGameToFile(filename) {
        if (!this.player || !this.world) {
            console.error('SaveLoadManager: player or world not set');
            return false;
        }

        const saveData = {
            timestamp: new Date().toISOString(),
            // Player position
            playerX: this.player.x,
            playerY: this.player.y,
            // Block position
            blockX: this.world.currentBlockCoords.x,
            blockY: this.world.currentBlockCoords.y,
            // Player attributes
            level: this.player.attributes.level,
            xp: this.player.attributes.xp,
            currentHealth: this.player.attributes.currentHealth,
            maxHealth: this.player.attributes.maxHealth,
            currentMana: this.player.attributes.currentMana,
            maxMana: this.player.attributes.maxMana,
            // Stats
            str: this.player.attributes.str,
            con: this.player.attributes.con,
            dex: this.player.attributes.dex,
            int: this.player.attributes.int,
            statPoints: this.player.attributes.statPoints,
            skillPoints: this.player.attributes.skillPoints,
            // Progression items
            foundAncientScroll: this.player.attributes.foundAncientScroll,
            foundDragonHeart: this.player.attributes.foundDragonHeart,
            // Skills
            unlockedSkills: this.getUnlockedSkills()
        };

        const key = this.saveKeyPrefix + filename;
        localStorage.setItem(key, JSON.stringify(saveData));
        console.log(`Game saved to ${filename}`);
        return true;
    }

    loadGameFromFile(filename) {
        if (!this.player || !this.world) {
            console.error('SaveLoadManager: player or world not set');
            return false;
        }

        const key = this.saveKeyPrefix + filename;
        const data = localStorage.getItem(key);

        if (!data) {
            console.log(`No save data for ${filename}`);
            return false;
        }

        try {
            const saveData = JSON.parse(data);

            // Restore player position
            this.player.x = saveData.playerX;
            this.player.y = saveData.playerY;

            // Restore block position
            this.world.currentBlockCoords.x = saveData.blockX;
            this.world.currentBlockCoords.y = saveData.blockY;

            // Ensure the block is generated
            this.world.getBlockAt(saveData.blockX, saveData.blockY);

            // Restore attributes
            this.player.attributes.level = saveData.level;
            this.player.attributes.xp = saveData.xp;
            this.player.attributes.currentHealth = saveData.currentHealth;
            this.player.attributes.maxHealth = saveData.maxHealth;
            this.player.attributes.currentMana = saveData.currentMana;
            this.player.attributes.maxMana = saveData.maxMana;

            // Restore stats
            this.player.attributes.str = saveData.str;
            this.player.attributes.con = saveData.con;
            this.player.attributes.dex = saveData.dex;
            this.player.attributes.int = saveData.int;
            this.player.attributes.statPoints = saveData.statPoints;
            this.player.attributes.skillPoints = saveData.skillPoints;

            // Restore progression items
            this.player.attributes.foundAncientScroll = saveData.foundAncientScroll || false;
            this.player.attributes.foundDragonHeart = saveData.foundDragonHeart || false;

            // Restore skills
            if (saveData.unlockedSkills) {
                this.restoreUnlockedSkills(saveData.unlockedSkills);
            }

            // Recalculate XP needed
            this.player.attributes.xpNeeded = this.player.attributes.getXpNeeded();

            console.log(`Game loaded from ${filename}`);
            return true;
        } catch (e) {
            console.error('Error loading save:', e);
            return false;
        }
    }

    getUnlockedSkills() {
        const unlocked = [];
        for (const [skillId, skill] of Object.entries(this.player.skillTree.skills)) {
            if (skill.unlocked) {
                unlocked.push(skillId);
            }
        }
        return unlocked;
    }

    restoreUnlockedSkills(unlockedSkills) {
        // Reset all skills first
        for (const skill of Object.values(this.player.skillTree.skills)) {
            skill.unlocked = false;
        }

        // Unlock saved skills
        for (const skillId of unlockedSkills) {
            if (this.player.skillTree.skills[skillId]) {
                this.player.skillTree.skills[skillId].unlocked = true;

                // Apply skill effects
                if (skillId === 'sprint') {
                    this.player.attributes.canSprint = true;
                } else if (skillId === 'dash') {
                    this.player.attributes.canDash = true;
                } else if (skillId === 'dash_cooldown1') {
                    this.player.attributes.dashCooldown = 1800;
                } else if (skillId === 'dash_cooldown2') {
                    this.player.attributes.dashCooldown = 900;
                } else if (skillId === 'extended_sword') {
                    this.player.attributes.swordLength = Math.floor(this.player.attributes.baseSwordLength * 1.5);
                } else if (skillId === 'blink') {
                    this.player.attributes.canBlink = true;
                }
            }
        }
    }

    deleteSave(filename) {
        const key = this.saveKeyPrefix + filename;
        localStorage.removeItem(key);
        console.log(`Save ${filename} deleted`);
    }
}

// MessageDialog - Simple message with OK button
class MessageDialog extends Dialog {
    constructor(title = 'Message', message = '') {
        super(title, ['OK'], null);
        this.message = message;
        this.width = 400;
    }

    setMessage(title, message) {
        this.title = title;
        this.message = message;
    }

    selectOption() {
        this.hide();
    }

    render(ctx, screenWidth, screenHeight) {
        if (!this.visible) return;

        const messageHeight = this.message ? 40 : 0;
        const height = 120 + messageHeight;
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
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.fillText(this.title, x + this.width / 2, y + this.padding + 20);

        // Draw message
        if (this.message) {
            ctx.font = '18px Arial';
            ctx.fillStyle = this.colors.text;
            ctx.fillText(this.message, x + this.width / 2, y + this.padding + 55);
        }

        // Draw OK button
        const buttonY = y + height - 45;
        ctx.font = '20px Arial';
        ctx.fillStyle = this.colors.selected;
        ctx.fillText('> OK', x + this.width / 2 - 20, buttonY);

        ctx.textAlign = 'left';
    }
}

// Export
window.Dialog = Dialog;
window.BonfireMenu = BonfireMenu;
window.FileDialog = FileDialog;
window.SaveOverwriteDialog = SaveOverwriteDialog;
window.LoadFileDialog = LoadFileDialog;
window.MessageDialog = MessageDialog;
window.SaveLoadManager = SaveLoadManager;
