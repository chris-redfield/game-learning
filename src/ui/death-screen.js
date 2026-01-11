/**
 * Death Screen - Shown when player dies
 * Exactly like it was implemented at the Python code (death_screen.py)
 */
class DeathScreen {
    constructor() {
        // State
        this.active = false;
        this.selectedOption = 0;
        this.options = ['Restart', 'Load Save'];

        // Colors
        this.colors = {
            overlay: 'rgba(0, 0, 0, 0.7)',
            title: '#ffffff',
            option: '#ffffff',
            selected: '#ffff00',
            highlight: 'rgba(80, 80, 80, 0.8)'
        };

        // Callbacks
        this.onRestart = null;
        this.onLoadSave = null;
    }

    /**
     * Activate the death screen
     */
    activate() {
        this.active = true;
        this.selectedOption = 0; // Default to Restart
        console.log('Death screen activated');
    }

    /**
     * Check if death screen is active
     */
    isActive() {
        return this.active;
    }

    /**
     * Deactivate the death screen
     */
    deactivate() {
        this.active = false;
    }

    /**
     * Handle input for the death screen
     */
    handleInput(input) {
        if (!this.active) return false;

        // Navigate up
        if (input.isKeyJustPressed('up')) {
            this.selectedOption = (this.selectedOption - 1 + this.options.length) % this.options.length;
            return true;
        }

        // Navigate down
        if (input.isKeyJustPressed('down')) {
            this.selectedOption = (this.selectedOption + 1) % this.options.length;
            return true;
        }

        // Select option (Enter, Space, or E)
        if (input.isKeyJustPressed('confirm') || input.isKeyJustPressed('character')) {
            this.selectOption();
            return true;
        }

        return true; // Block all other input
    }

    /**
     * Handle mouse input
     */
    handleMouse(mouseX, mouseY, clicked, screenWidth, screenHeight) {
        if (!this.active) return false;

        const centerX = screenWidth / 2;
        const centerY = screenHeight / 2;

        // Option rectangles
        const optionWidth = 200;
        const optionHeight = 40;
        const restartY = centerY + 20;
        const loadSaveY = centerY + 70;

        // Check hover
        if (mouseX >= centerX - optionWidth / 2 && mouseX <= centerX + optionWidth / 2) {
            if (mouseY >= restartY - optionHeight / 2 && mouseY <= restartY + optionHeight / 2) {
                this.selectedOption = 0;
                if (clicked) {
                    this.selectOption();
                    return true;
                }
            } else if (mouseY >= loadSaveY - optionHeight / 2 && mouseY <= loadSaveY + optionHeight / 2) {
                this.selectedOption = 1;
                if (clicked) {
                    this.selectOption();
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Select the current option
     */
    selectOption() {
        if (this.selectedOption === 0) {
            // Restart
            console.log('Death screen: Restart selected');
            this.active = false;
            if (this.onRestart) {
                this.onRestart();
            }
        } else if (this.selectedOption === 1) {
            // Load Save
            console.log('Death screen: Load Save selected');
            if (this.onLoadSave) {
                this.onLoadSave();
            }
            // Keep death screen active until game is loaded
        }
    }

    /**
     * Render the death screen
     */
    render(ctx, screenWidth, screenHeight) {
        if (!this.active) return;

        // Draw semi-transparent overlay
        // (game world and player are already rendered underneath)
        ctx.fillStyle = this.colors.overlay;
        ctx.fillRect(0, 0, screenWidth, screenHeight);

        const centerX = screenWidth / 2;
        const centerY = screenHeight / 2;

        // Draw "YOU DIED" title
        ctx.font = 'bold 72px Arial';
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('YOU DIED', centerX, centerY - 60);

        // Draw menu options
        const optionY = [centerY + 20, centerY + 70];
        const optionWidth = 200;
        const optionHeight = 40;

        ctx.font = '28px Arial';

        for (let i = 0; i < this.options.length; i++) {
            const y = optionY[i];

            // Draw highlight background for selected option
            if (i === this.selectedOption) {
                ctx.fillStyle = this.colors.highlight;
                ctx.beginPath();
                ctx.roundRect(centerX - optionWidth / 2, y - optionHeight / 2, optionWidth, optionHeight, 5);
                ctx.fill();

                // Draw "press A" or "press Space" hint
                ctx.font = '16px Arial';
                ctx.fillStyle = this.colors.selected;
                ctx.textAlign = 'left';
                ctx.fillText('press Space', centerX + optionWidth / 2 + 20, y);
                ctx.textAlign = 'center';
                ctx.font = '28px Arial';
            }

            // Draw option text
            ctx.fillStyle = i === this.selectedOption ? this.colors.selected : this.colors.option;
            ctx.fillText(this.options[i], centerX, y);
        }

        ctx.textAlign = 'left';
        ctx.textBaseline = 'alphabetic';
    }
}

// Export
window.DeathScreen = DeathScreen;
