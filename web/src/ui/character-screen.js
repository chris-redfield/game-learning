/**
 * CharacterScreen - Full screen character management UI
 * Mirrors Python character_screen.py
 */
class CharacterScreen {
    constructor(player, screenWidth, screenHeight) {
        this.player = player;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.visible = false;

        // Colors (matching Python)
        this.colors = {
            background: 'rgba(30, 33, 41, 0.9)',
            text: 'rgb(255, 255, 255)',
            title: 'rgb(255, 215, 0)',       // Gold for titles
            statText: 'rgb(0, 255, 0)',       // Green for stat values
            button: 'rgb(100, 100, 120)',
            buttonHover: 'rgb(130, 130, 150)',
            buttonDisabled: 'rgb(70, 70, 80)',
            border: 'rgb(180, 180, 200)',
            health: 'rgb(220, 50, 50)',
            mana: 'rgb(50, 50, 220)',
            portraitBg: 'rgb(30, 30, 40)',
            cursor: 'rgb(255, 255, 0)',
            skillUnlocked: 'rgb(0, 150, 0)',
            skillAvailable: 'rgb(150, 150, 0)',
            skillUnavailable: 'rgb(100, 100, 100)',
            // Inventory colors
            gridBg: 'rgb(40, 40, 50)',
            gridBorder: 'rgb(100, 100, 120)',
            itemHover: 'rgb(80, 80, 100)',
            itemSelected: 'rgb(100, 100, 150)',
            usable: 'rgb(100, 180, 100)',
            unusable: 'rgb(180, 100, 100)',
            feedbackBg: 'rgba(0, 0, 0, 0.7)',
            feedbackText: 'rgb(255, 220, 100)'
        };

        // Fonts
        this.titleFont = 'bold 26px Arial';
        this.statFont = 'bold 22px Arial';
        this.textFont = '18px Arial';
        this.buttonFont = '16px Arial';

        // Current tab and selection
        this.currentTab = 'attributes';
        this.selectedIndex = 0;
        // Button order includes stat buttons AND tab buttons for full navigation
        this.buttonOrder = ['inc_str', 'inc_con', 'inc_dex', 'inc_int', 'tab_attributes', 'tab_skills'];

        // Button rectangles for mouse interaction
        this.buttons = {};
        this.tabRects = {};

        // Skill selection
        this.skillSelected = null;
        this.skillRects = {};
        this.unlockButtonRect = null;

        // Item grid configuration (matching Python)
        this.gridCols = 6;
        this.gridRows = 4;
        this.cellSize = 50;
        this.gridPadding = 5;

        // Item selection variables
        this.selectedItemIndex = -1;  // No item selected initially
        this.hoveredItemIndex = -1;   // No item hovered initially
        this.tooltipVisible = false;
        this.tooltipItem = null;

        // Navigation mode
        this.currentSection = 'stats';  // Can be 'stats' or 'inventory'
        this.gridSelectedRow = 0;
        this.gridSelectedCol = 0;

        // Cursor position for tooltip rendering
        this.cursorPos = { x: 0, y: 0 };

        // Item feedback message
        this.itemFeedbackMessage = null;
        this.itemFeedbackTimer = 0;

        // Mouse state
        this.mouseX = 0;
        this.mouseY = 0;
        this.hoveredButton = null;

        // Portrait (will load async)
        this.portrait = null;
        this.portraitSize = 150;
        this.loadPortrait();

        // Setup mouse listeners
        this.setupMouseListeners();
    }

    setupMouseListeners() {
        const canvas = document.getElementById('game-canvas');
        if (canvas) {
            canvas.addEventListener('mousemove', (e) => {
                if (!this.visible) return;
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                this.mouseX = (e.clientX - rect.left) * scaleX;
                this.mouseY = (e.clientY - rect.top) * scaleY;
                this.updateHover();
            });

            canvas.addEventListener('click', (e) => {
                if (!this.visible) return;
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const clickX = (e.clientX - rect.left) * scaleX;
                const clickY = (e.clientY - rect.top) * scaleY;
                this.handleClick(clickX, clickY);
            });
        }
    }

    updateHover() {
        this.hoveredButton = null;

        // Check stat buttons
        for (const [buttonId, rect] of Object.entries(this.buttons)) {
            if (this.pointInRect(this.mouseX, this.mouseY, rect)) {
                this.hoveredButton = buttonId;
                return;
            }
        }

        // Check tab buttons
        for (const [tabId, rect] of Object.entries(this.tabRects)) {
            if (this.pointInRect(this.mouseX, this.mouseY, rect)) {
                this.hoveredButton = `tab_${tabId}`;
                return;
            }
        }

        // Check skill nodes (in skills tab)
        if (this.currentTab === 'skills') {
            // Check unlock button first
            if (this.unlockButtonRect && this.pointInRect(this.mouseX, this.mouseY, this.unlockButtonRect)) {
                this.hoveredButton = 'unlock_button';
                return;
            }

            for (const [skillId, rect] of Object.entries(this.skillRects)) {
                if (this.pointInRect(this.mouseX, this.mouseY, rect)) {
                    this.hoveredButton = `skill_${skillId}`;
                    return;
                }
            }
        }

        // Check inventory items hover (in attributes tab)
        if (this.currentTab === 'attributes' && this.player.inventory) {
            this.hoveredItemIndex = -1;

            const inventoryItems = this.player.inventory.getItemsAndCounts();
            const margin = 30;
            const portraitX = margin + 50;
            const portraitY = margin + 80;
            const gridStartY = portraitY + this.portraitSize + 30 + 35;

            for (let idx = 0; idx < inventoryItems.length; idx++) {
                const row = Math.floor(idx / this.gridCols);
                const col = idx % this.gridCols;

                const cellX = portraitX + col * (this.cellSize + this.gridPadding) + this.gridPadding;
                const cellY = gridStartY + row * (this.cellSize + this.gridPadding) + this.gridPadding;
                const cellRect = { x: cellX, y: cellY, width: this.cellSize, height: this.cellSize };

                if (this.pointInRect(this.mouseX, this.mouseY, cellRect)) {
                    this.hoveredItemIndex = idx;
                    break;
                }
            }
        }
    }

    handleClick(x, y) {
        // Check tab clicks
        for (const [tabId, rect] of Object.entries(this.tabRects)) {
            if (this.pointInRect(x, y, rect)) {
                this.currentTab = tabId;
                this.skillSelected = null;
                // Update selection to the clicked tab
                this.selectedIndex = this.buttonOrder.indexOf(`tab_${tabId}`);
                return true;
            }
        }

        if (this.currentTab === 'attributes') {
            // Check stat button clicks
            for (const [buttonId, rect] of Object.entries(this.buttons)) {
                if (this.pointInRect(x, y, rect)) {
                    if (this.player.attributes.statPoints > 0) {
                        const stat = buttonId.replace('inc_', '');
                        this.player.attributes.increaseStat(stat);
                        return true;
                    }
                }
            }

            // Check inventory item clicks
            if (this.player.inventory) {
                const inventoryItems = this.player.inventory.getItemsAndCounts();
                const margin = 30;
                const portraitX = margin + 50;
                const portraitY = margin + 80;
                const gridStartY = portraitY + this.portraitSize + 30 + 35;

                for (let idx = 0; idx < inventoryItems.length; idx++) {
                    const row = Math.floor(idx / this.gridCols);
                    const col = idx % this.gridCols;

                    const cellX = portraitX + col * (this.cellSize + this.gridPadding) + this.gridPadding;
                    const cellY = gridStartY + row * (this.cellSize + this.gridPadding) + this.gridPadding;
                    const cellRect = { x: cellX, y: cellY, width: this.cellSize, height: this.cellSize };

                    if (this.pointInRect(x, y, cellRect)) {
                        const item = inventoryItems[idx].item;

                        // Toggle selection of this item
                        if (this.selectedItemIndex === idx) {
                            // If already selected, use the item
                            if (item && typeof item.use === 'function') {
                                const useResult = item.use(this.player);
                                if (typeof useResult === 'string') {
                                    this.itemFeedbackMessage = useResult;
                                    this.itemFeedbackTimer = 120;
                                } else if (useResult === true) {
                                    const actualIndex = this.player.inventory.items.indexOf(item);
                                    this.player.inventory.removeItem(actualIndex);
                                }
                            }
                        } else {
                            // Select this item
                            this.selectedItemIndex = idx;
                            this.gridSelectedRow = row;
                            this.gridSelectedCol = col;
                            this.currentSection = 'inventory';
                            this.updateSelectedItemPosition();
                        }
                        return true;
                    }
                }
            }
        } else if (this.currentTab === 'skills') {
            // Check unlock button click first
            if (this.unlockButtonRect && this.pointInRect(x, y, this.unlockButtonRect)) {
                if (this.skillSelected) {
                    this.player.skillTree.unlockSkill(this.skillSelected);
                    return true;
                }
            }

            // Check skill node clicks
            for (const [skillId, rect] of Object.entries(this.skillRects)) {
                if (this.pointInRect(x, y, rect)) {
                    this.skillSelected = skillId;
                    return true;
                }
            }
        }

        return false;
    }

    pointInRect(x, y, rect) {
        return x >= rect.x && x <= rect.x + rect.width &&
               y >= rect.y && y <= rect.y + rect.height;
    }

    async loadPortrait() {
        try {
            const img = new Image();
            img.src = 'assets/portrait-pixel-art.png';
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });
            this.portrait = img;
            console.log('Portrait loaded successfully');
        } catch (e) {
            console.log('Could not load portrait, using placeholder');
            this.portrait = null;
        }
    }

    toggle() {
        this.visible = !this.visible;
        if (this.visible) {
            this.selectedIndex = 0;
            this.currentTab = 'attributes';
            this.skillSelected = null;
            this.currentSection = 'stats';
            this.selectedItemIndex = -1;
            this.gridSelectedRow = 0;
            this.gridSelectedCol = 0;
        }
        return this.visible;
    }

    isVisible() {
        return this.visible;
    }

    // Navigation methods
    selectNext() {
        if (this.currentTab === 'attributes') {
            // Navigate through stat buttons and tab buttons
            this.selectedIndex = (this.selectedIndex + 1) % this.buttonOrder.length;
        }
    }

    selectPrev() {
        if (this.currentTab === 'attributes') {
            this.selectedIndex = (this.selectedIndex - 1 + this.buttonOrder.length) % this.buttonOrder.length;
        }
    }

    activateSelected() {
        const buttonId = this.buttonOrder[this.selectedIndex];

        // Handle tab button activation
        if (buttonId === 'tab_attributes') {
            this.currentTab = 'attributes';
            this.skillSelected = null;
            return true;
        }
        if (buttonId === 'tab_skills') {
            this.currentTab = 'skills';
            this.skillSelected = null;
            return true;
        }

        // Handle stat button activation
        if (this.currentTab === 'attributes' && buttonId.startsWith('inc_')) {
            const stat = buttonId.replace('inc_', '');
            if (this.player.attributes.statPoints > 0) {
                this.player.attributes.increaseStat(stat);
                return true;
            }
        }

        // Handle skill unlock
        if (this.currentTab === 'skills' && this.skillSelected) {
            if (this.player.skillTree.unlockSkill(this.skillSelected)) {
                return true;
            }
        }

        return false;
    }

    switchTab() {
        this.currentTab = this.currentTab === 'attributes' ? 'skills' : 'attributes';
        this.skillSelected = null;
    }

    // Skill navigation
    navigateSkills(direction) {
        const skills = Object.keys(this.player.skillTree.skills);
        if (skills.length === 0) return;

        if (!this.skillSelected) {
            this.skillSelected = skills[0];
            return;
        }

        const currentIndex = skills.indexOf(this.skillSelected);
        if (direction === 'down' || direction === 'right') {
            this.skillSelected = skills[(currentIndex + 1) % skills.length];
        } else if (direction === 'up' || direction === 'left') {
            this.skillSelected = skills[(currentIndex - 1 + skills.length) % skills.length];
        }
    }

    // Switch between stats and inventory sections
    switchSection() {
        if (this.currentSection === 'stats') {
            this.currentSection = 'inventory';
            // Initialize inventory selection
            if (this.player.inventory && this.player.inventory.getItemsAndCounts().length > 0) {
                this.selectedItemIndex = 0;
                this.gridSelectedRow = 0;
                this.gridSelectedCol = 0;
            } else {
                this.selectedItemIndex = -1;
            }
        } else {
            this.currentSection = 'stats';
            this.selectedItemIndex = -1;
        }

        // Update cursor position if we switched to inventory
        if (this.currentSection === 'inventory' && this.selectedItemIndex >= 0) {
            this.updateSelectedItemPosition();
        }
    }

    // Navigate inventory grid up
    selectInventoryUp() {
        if (this.currentSection !== 'inventory') return;

        const inventorySize = this.player.inventory ? this.player.inventory.getItemsAndCounts().length : 0;
        if (inventorySize === 0) return;

        // Move to previous row or wrap to bottom
        this.gridSelectedRow = (this.gridSelectedRow - 1 + this.gridRows) % this.gridRows;
        this.selectedItemIndex = this.gridSelectedRow * this.gridCols + this.gridSelectedCol;

        // Validate selection is within inventory bounds
        if (this.selectedItemIndex >= inventorySize) {
            // Wrap to bottom row
            this.gridSelectedRow = Math.floor((inventorySize - 1) / this.gridCols);
            const maxCol = Math.min(this.gridCols - 1, inventorySize - 1 - (this.gridSelectedRow * this.gridCols));
            if (this.gridSelectedCol > maxCol) {
                this.gridSelectedCol = maxCol;
            }
            this.selectedItemIndex = this.gridSelectedRow * this.gridCols + this.gridSelectedCol;
        }

        this.updateSelectedItemPosition();
    }

    // Navigate inventory grid down
    selectInventoryDown() {
        if (this.currentSection !== 'inventory') return;

        const inventorySize = this.player.inventory ? this.player.inventory.getItemsAndCounts().length : 0;
        if (inventorySize === 0) return;

        // Move to next row or wrap to top
        this.gridSelectedRow = (this.gridSelectedRow + 1) % this.gridRows;
        this.selectedItemIndex = this.gridSelectedRow * this.gridCols + this.gridSelectedCol;

        // Validate selection is within inventory bounds
        if (this.selectedItemIndex >= inventorySize) {
            // Wrap to first row
            this.gridSelectedRow = 0;
            this.selectedItemIndex = this.gridSelectedCol;
        }

        this.updateSelectedItemPosition();
    }

    // Navigate inventory grid left
    selectInventoryLeft() {
        if (this.currentSection !== 'inventory') return;

        const inventorySize = this.player.inventory ? this.player.inventory.getItemsAndCounts().length : 0;
        if (inventorySize === 0) return;

        // Move to previous column or wrap to last column
        this.gridSelectedCol = (this.gridSelectedCol - 1 + this.gridCols) % this.gridCols;
        this.selectedItemIndex = this.gridSelectedRow * this.gridCols + this.gridSelectedCol;

        // Validate selection is within inventory bounds
        if (this.selectedItemIndex >= inventorySize) {
            this.selectedItemIndex = inventorySize - 1;
            this.gridSelectedRow = Math.floor(this.selectedItemIndex / this.gridCols);
            this.gridSelectedCol = this.selectedItemIndex % this.gridCols;
        }

        this.updateSelectedItemPosition();
    }

    // Navigate inventory grid right
    selectInventoryRight() {
        if (this.currentSection !== 'inventory') return;

        const inventorySize = this.player.inventory ? this.player.inventory.getItemsAndCounts().length : 0;
        if (inventorySize === 0) return;

        // Move to next column or wrap to first column
        this.gridSelectedCol = (this.gridSelectedCol + 1) % this.gridCols;
        this.selectedItemIndex = this.gridSelectedRow * this.gridCols + this.gridSelectedCol;

        // Validate selection is within inventory bounds
        if (this.selectedItemIndex >= inventorySize) {
            this.gridSelectedCol = 0;
            this.gridSelectedRow = (this.gridSelectedRow + 1) % this.gridRows;
            this.selectedItemIndex = this.gridSelectedRow * this.gridCols;

            if (this.selectedItemIndex >= inventorySize) {
                this.gridSelectedRow = 0;
                this.gridSelectedCol = 0;
                this.selectedItemIndex = 0;
            }
        }

        this.updateSelectedItemPosition();
    }

    // Update cursor position for the currently selected inventory item
    updateSelectedItemPosition() {
        if (this.currentSection !== 'inventory' || this.selectedItemIndex < 0) return;

        const row = Math.floor(this.selectedItemIndex / this.gridCols);
        const col = this.selectedItemIndex % this.gridCols;

        // Calculate grid starting position (must match drawItemsGrid)
        const margin = 30;
        const portraitX = margin + 50;
        const portraitY = margin + 80;
        const gridStartY = portraitY + this.portraitSize + 30 + 35;

        const cellX = portraitX + col * (this.cellSize + this.gridPadding) + this.gridPadding;
        const cellY = gridStartY + row * (this.cellSize + this.gridPadding) + this.gridPadding;

        this.cursorPos = { x: cellX + this.cellSize + 10, y: cellY };
    }

    // Use the currently selected inventory item
    useSelectedItem() {
        if (this.currentSection !== 'inventory' || this.selectedItemIndex < 0) return false;
        if (!this.player.inventory) return false;

        const inventoryItems = this.player.inventory.getItemsAndCounts();
        if (this.selectedItemIndex >= inventoryItems.length) return false;

        const itemData = inventoryItems[this.selectedItemIndex];
        const item = itemData.item;

        if (item && typeof item.use === 'function') {
            // Try to use the item
            const useResult = item.use(this.player);

            // If useResult is a string, it's a message to display
            if (typeof useResult === 'string') {
                this.itemFeedbackMessage = useResult;
                this.itemFeedbackTimer = 120;
                return false;
            }
            // If useResult is true, item was used successfully
            else if (useResult === true) {
                // Item was used successfully, remove from inventory
                const actualIndex = this.player.inventory.items.indexOf(item);
                this.player.inventory.removeItem(actualIndex);

                // If inventory is now empty, reset selection
                if (this.player.inventory.getItemsAndCounts().length === 0) {
                    this.selectedItemIndex = -1;
                }
                // Otherwise adjust selection if it's now invalid
                else if (this.selectedItemIndex >= this.player.inventory.getItemsAndCounts().length) {
                    this.selectedItemIndex = this.player.inventory.getItemsAndCounts().length - 1;
                    this.gridSelectedRow = Math.floor(this.selectedItemIndex / this.gridCols);
                    this.gridSelectedCol = this.selectedItemIndex % this.gridCols;
                }
                return true;
            }
        }
        return false;
    }

    handleInput(input) {
        if (!this.visible) return false;

        // ESC to close character screen
        if (input.isKeyJustPressed('pause')) {
            this.visible = false;
            return true;
        }

        // Tab switching with 1/2 keys (matching Python)
        if (input.isKeyJustPressed('tabAttributes')) {
            this.currentTab = 'attributes';
            this.skillSelected = null;
            this.selectedIndex = this.buttonOrder.indexOf('tab_attributes');
            return true;
        }
        if (input.isKeyJustPressed('tabSkills')) {
            this.currentTab = 'skills';
            this.skillSelected = null;
            return true;
        }

        if (this.currentTab === 'attributes') {
            // TAB key to switch between stats and inventory sections
            if (input.isKeyJustPressed('inventory')) {
                this.switchSection();
                return true;
            }

            if (this.currentSection === 'stats') {
                // Navigation with up/down arrows for stats
                if (input.isKeyJustPressed('up')) {
                    this.selectPrev();
                    return true;
                }
                if (input.isKeyJustPressed('down')) {
                    this.selectNext();
                    return true;
                }
                // Left/right navigation between tab buttons
                const currentButton = this.buttonOrder[this.selectedIndex];
                if (input.isKeyJustPressed('left')) {
                    if (currentButton === 'tab_skills') {
                        this.selectedIndex = this.buttonOrder.indexOf('tab_attributes');
                        return true;
                    }
                }
                if (input.isKeyJustPressed('right')) {
                    if (currentButton === 'tab_attributes') {
                        this.selectedIndex = this.buttonOrder.indexOf('tab_skills');
                        return true;
                    }
                }
                // Activation with E or Space
                if (input.isKeyJustPressed('interact') || input.isKeyJustPressed('attack')) {
                    this.activateSelected();
                    return true;
                }
            } else if (this.currentSection === 'inventory') {
                // Inventory navigation
                if (input.isKeyJustPressed('up')) {
                    this.selectInventoryUp();
                    return true;
                }
                if (input.isKeyJustPressed('down')) {
                    this.selectInventoryDown();
                    return true;
                }
                if (input.isKeyJustPressed('left')) {
                    this.selectInventoryLeft();
                    return true;
                }
                if (input.isKeyJustPressed('right')) {
                    this.selectInventoryRight();
                    return true;
                }
                // Use item with E or Space
                if (input.isKeyJustPressed('interact') || input.isKeyJustPressed('attack')) {
                    this.useSelectedItem();
                    return true;
                }
            }
        } else if (this.currentTab === 'skills') {
            // Skill navigation
            if (input.isKeyJustPressed('up')) {
                this.navigateSkills('up');
                return true;
            }
            if (input.isKeyJustPressed('down')) {
                this.navigateSkills('down');
                return true;
            }
            if (input.isKeyJustPressed('left')) {
                this.navigateSkills('left');
                return true;
            }
            if (input.isKeyJustPressed('right')) {
                this.navigateSkills('right');
                return true;
            }
            // Unlock skill with E
            if (input.isKeyJustPressed('interact') || input.isKeyJustPressed('attack')) {
                this.activateSelected();
                return true;
            }
        }

        return false;
    }

    draw(ctx) {
        if (!this.visible) return;

        const margin = 30;

        // Draw semi-transparent overlay
        ctx.fillStyle = this.colors.background;
        ctx.fillRect(0, 0, this.screenWidth, this.screenHeight);

        // Draw border
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 4;
        ctx.strokeRect(margin, margin, this.screenWidth - margin * 2, this.screenHeight - margin * 2);

        // Draw title
        ctx.font = this.titleFont;
        ctx.fillStyle = this.colors.title;
        ctx.textAlign = 'center';
        ctx.fillText('CHARACTER SHEET', this.screenWidth / 2, margin + 40);

        // Draw close instructions
        ctx.font = this.textFont;
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'right';
        ctx.fillText('Press ENTER to close', this.screenWidth - margin - 10, margin + 40);
        ctx.textAlign = 'left';

        // Draw tabs
        this.drawTabs(ctx, margin);

        // Draw content based on current tab
        if (this.currentTab === 'attributes') {
            this.drawAttributesTab(ctx, margin);
        } else {
            this.drawSkillsTab(ctx, margin);
        }
    }

    drawTabs(ctx, margin) {
        const tabWidth = 150;
        const tabHeight = 30;
        const tabY = this.screenHeight - margin - tabHeight - 10;

        // Attributes tab
        const attrTabX = this.screenWidth / 2 - tabWidth - 5;
        const isAttrSelected = this.buttonOrder[this.selectedIndex] === 'tab_attributes';
        const isAttrHovered = this.hoveredButton === 'tab_attributes';
        let attrColor = this.currentTab === 'attributes' ? this.colors.buttonHover : this.colors.button;
        if (isAttrHovered) attrColor = this.colors.buttonHover;

        // Draw selection cursor for attributes tab
        if (isAttrSelected) {
            ctx.strokeStyle = this.colors.cursor;
            ctx.lineWidth = 3;
            ctx.strokeRect(attrTabX - 3, tabY - 3, tabWidth + 6, tabHeight + 6);
        }

        ctx.fillStyle = attrColor;
        ctx.fillRect(attrTabX, tabY, tabWidth, tabHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(attrTabX, tabY, tabWidth, tabHeight);

        ctx.font = this.buttonFont;
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'center';
        ctx.fillText('ATTRIBUTES', attrTabX + tabWidth / 2, tabY + tabHeight / 2 + 5);

        // Skills tab
        const skillsTabX = this.screenWidth / 2 + 5;
        const isSkillsSelected = this.buttonOrder[this.selectedIndex] === 'tab_skills';
        const isSkillsHovered = this.hoveredButton === 'tab_skills';
        let skillsColor = this.currentTab === 'skills' ? this.colors.buttonHover : this.colors.button;
        if (isSkillsHovered) skillsColor = this.colors.buttonHover;

        // Draw selection cursor for skills tab
        if (isSkillsSelected) {
            ctx.strokeStyle = this.colors.cursor;
            ctx.lineWidth = 3;
            ctx.strokeRect(skillsTabX - 3, tabY - 3, tabWidth + 6, tabHeight + 6);
        }

        ctx.fillStyle = skillsColor;
        ctx.fillRect(skillsTabX, tabY, tabWidth, tabHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(skillsTabX, tabY, tabWidth, tabHeight);

        ctx.fillStyle = this.colors.text;
        ctx.fillText('SKILLS', skillsTabX + tabWidth / 2, tabY + tabHeight / 2 + 5);

        ctx.textAlign = 'left';

        // Store tab rects for click detection
        this.tabRects = {
            attributes: { x: attrTabX, y: tabY, width: tabWidth, height: tabHeight },
            skills: { x: skillsTabX, y: tabY, width: tabWidth, height: tabHeight }
        };

        // Draw separator line
        ctx.strokeStyle = this.colors.border;
        ctx.beginPath();
        ctx.moveTo(margin + 10, tabY - 10);
        ctx.lineTo(this.screenWidth - margin - 10, tabY - 10);
        ctx.stroke();

        // Tab switch hint
        ctx.font = '14px Arial';
        ctx.fillStyle = 'rgb(150, 150, 150)';
        ctx.textAlign = 'center';
        ctx.fillText('Press 1/2 or click to switch tabs', this.screenWidth / 2, tabY + tabHeight + 20);
        ctx.textAlign = 'left';
    }

    drawAttributesTab(ctx, margin) {
        const player = this.player;
        const attrs = player.attributes;

        // Portrait section
        const portraitX = margin + 50;
        const portraitY = margin + 80;

        // Draw portrait background
        ctx.fillStyle = this.colors.portraitBg;
        ctx.fillRect(portraitX, portraitY, this.portraitSize, this.portraitSize);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 3;
        ctx.strokeRect(portraitX, portraitY, this.portraitSize, this.portraitSize);

        // Draw portrait image if loaded
        if (this.portrait) {
            const scale = Math.min(this.portraitSize / this.portrait.width, this.portraitSize / this.portrait.height);
            const w = this.portrait.width * scale;
            const h = this.portrait.height * scale;
            const px = portraitX + (this.portraitSize - w) / 2;
            const py = portraitY + (this.portraitSize - h) / 2;
            ctx.drawImage(this.portrait, px, py, w, h);
        } else {
            // Placeholder
            ctx.fillStyle = 'rgb(200, 180, 150)';
            ctx.beginPath();
            ctx.arc(portraitX + this.portraitSize / 2, portraitY + this.portraitSize / 2, this.portraitSize / 3, 0, Math.PI * 2);
            ctx.fill();
        }

        // Stats next to portrait
        const statsX = portraitX + this.portraitSize + 30;
        let statsY = portraitY;

        // Level
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.statText;
        ctx.fillText(`Level: ${attrs.level}`, statsX, statsY + 20);

        // Stat points
        ctx.fillStyle = this.colors.title;
        ctx.fillText(`Stat Points: ${attrs.statPoints}`, statsX, statsY + 50);

        // XP bar
        ctx.font = this.textFont;
        ctx.fillStyle = this.colors.text;
        ctx.fillText(`XP: ${attrs.xp} / ${attrs.xpNeeded}`, statsX, statsY + 80);

        // XP progress bar
        const xpBarWidth = 180;
        const xpBarHeight = 15;
        const xpBarX = statsX;
        const xpBarY = statsY + 90;
        ctx.fillStyle = 'rgb(50, 50, 50)';
        ctx.fillRect(xpBarX, xpBarY, xpBarWidth, xpBarHeight);
        const xpFill = attrs.xpNeeded > 0 ? (attrs.xp / attrs.xpNeeded) * xpBarWidth : xpBarWidth;
        ctx.fillStyle = 'rgb(100, 200, 100)';
        ctx.fillRect(xpBarX, xpBarY, xpFill, xpBarHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(xpBarX, xpBarY, xpBarWidth, xpBarHeight);

        // Resource bars
        this.drawResourceBars(ctx, statsX, statsY + 130);

        // Attributes section (right side)
        const attributesX = this.screenWidth / 2;
        let attributesY = 90;

        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText('ATTRIBUTES', attributesX, attributesY);

        // Attribute list with + buttons
        const attributeData = [
            { name: 'Strength', key: 'str', desc: `Attack Power: ${attrs.getAttackPower()}` },
            { name: 'Constitution', key: 'con', desc: `Max HP: ${attrs.maxHealth}` },
            { name: 'Dexterity', key: 'dex', desc: `Speed: ${player.baseSpeed.toFixed(2)}` },
            { name: 'Intelligence', key: 'int', desc: `Max MP: ${attrs.maxMana}` }
        ];

        ctx.font = this.textFont;
        for (let i = 0; i < attributeData.length; i++) {
            const attr = attributeData[i];
            const yPos = attributesY + 40 + i * 50;

            // Attribute name and value
            ctx.fillStyle = this.colors.text;
            ctx.fillText(attr.name, attributesX, yPos);

            ctx.fillStyle = this.colors.statText;
            ctx.fillText(`${attrs[attr.key]}`, attributesX + 130, yPos);

            // Description
            ctx.fillStyle = 'rgb(150, 150, 150)';
            ctx.fillText(attr.desc, attributesX + 160, yPos);

            // + button
            const buttonId = `inc_${attr.key}`;
            const buttonX = attributesX + 350;
            const buttonY = yPos - 18;
            const buttonSize = 30;

            this.buttons[buttonId] = { x: buttonX, y: buttonY, width: buttonSize, height: buttonSize };

            // Button color based on state
            let buttonColor = this.colors.buttonDisabled;
            if (attrs.statPoints > 0) {
                buttonColor = this.colors.button;
                // Check if hovered
                if (this.hoveredButton === buttonId) {
                    buttonColor = this.colors.buttonHover;
                }
            }

            // Check if selected with controller/keyboard
            const isSelected = this.buttonOrder[this.selectedIndex] === buttonId;
            if (isSelected) {
                ctx.strokeStyle = this.colors.cursor;
                ctx.lineWidth = 3;
                ctx.strokeRect(buttonX - 3, buttonY - 3, buttonSize + 6, buttonSize + 6);
            }

            ctx.fillStyle = buttonColor;
            ctx.fillRect(buttonX, buttonY, buttonSize, buttonSize);
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 1;
            ctx.strokeRect(buttonX, buttonY, buttonSize, buttonSize);

            ctx.fillStyle = this.colors.text;
            ctx.font = this.buttonFont;
            ctx.textAlign = 'center';
            ctx.fillText('+', buttonX + buttonSize / 2, buttonY + buttonSize / 2 + 5);
            ctx.textAlign = 'left';
            ctx.font = this.textFont;
        }

        // Abilities section
        this.drawAbilitiesSection(ctx, attributesX, attributesY + 260);

        // Items grid below portrait
        this.drawItemsGrid(ctx, portraitX, portraitY + this.portraitSize + 30);

        // Draw item tooltip if needed
        if (this.tooltipVisible && this.tooltipItem) {
            const tooltipPos = this.hoveredItemIndex >= 0
                ? { x: this.mouseX, y: this.mouseY }
                : this.cursorPos;
            this.drawItemTooltip(ctx, this.tooltipItem, tooltipPos);
        }
    }

    drawResourceBars(ctx, x, y) {
        const attrs = this.player.attributes;
        const barWidth = 180;
        const barHeight = 20;

        // Health bar
        const healthPercent = attrs.currentHealth / attrs.maxHealth;
        ctx.fillStyle = 'rgb(60, 20, 20)';
        ctx.fillRect(x, y, barWidth, barHeight);
        ctx.fillStyle = this.colors.health;
        ctx.fillRect(x, y, barWidth * healthPercent, barHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, barWidth, barHeight);

        ctx.font = this.textFont;
        ctx.fillStyle = this.colors.text;
        ctx.fillText(`HP: ${attrs.currentHealth}/${attrs.maxHealth}`, x + 10, y + 15);

        // Mana bar
        const manaPercent = attrs.currentMana / attrs.maxMana;
        ctx.fillStyle = 'rgb(20, 20, 60)';
        ctx.fillRect(x, y + 30, barWidth, barHeight);
        ctx.fillStyle = this.colors.mana;
        ctx.fillRect(x, y + 30, barWidth * manaPercent, barHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.strokeRect(x, y + 30, barWidth, barHeight);

        ctx.fillStyle = this.colors.text;
        ctx.fillText(`MP: ${attrs.currentMana}/${attrs.maxMana}`, x + 10, y + 45);
    }

    drawAbilitiesSection(ctx, x, y) {
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText('ABILITIES', x, y);

        const abilities = [
            { id: 'basic_sword', name: 'Sword Attack', desc: 'SPACE' },
            { id: 'dash', name: 'Dash', desc: 'SHIFT' },
            { id: 'extended_sword', name: 'Extended Sword', desc: 'Increased reach' },
            { id: 'blink', name: 'Blink', desc: 'B key' },
            { id: 'firebolt', name: 'Firebolt', desc: 'F key' }
        ];

        ctx.font = this.textFont;
        let abilityY = y + 30;
        let hasAbilities = false;

        for (const ability of abilities) {
            if (this.player.skillTree.isSkillUnlocked(ability.id)) {
                hasAbilities = true;
                ctx.fillStyle = this.colors.statText;
                ctx.fillText(ability.name, x, abilityY);
                ctx.fillStyle = 'rgb(150, 150, 150)';
                ctx.fillText(ability.desc, x + 150, abilityY);
                abilityY += 25;
            }
        }

        if (!hasAbilities) {
            ctx.fillStyle = 'rgb(150, 150, 150)';
            ctx.fillText('No abilities unlocked yet', x, abilityY);
        }
    }

    drawItemsGrid(ctx, x, y) {
        // Title for items section
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText('ITEMS', x, y);

        // Draw control instructions
        if (this.currentSection === 'inventory' && this.player.inventory &&
            this.player.inventory.getItemsAndCounts().length > 0) {
            ctx.font = this.textFont;
            ctx.fillStyle = this.colors.text;
            ctx.fillText('Press E to use selected item', x + 100, y);
        }

        // Calculate grid dimensions
        const gridWidth = this.cellSize * this.gridCols + this.gridPadding * (this.gridCols + 1);
        const gridHeight = this.cellSize * this.gridRows + this.gridPadding * (this.gridRows + 1);

        // Draw grid background
        ctx.fillStyle = this.colors.gridBg;
        ctx.fillRect(x, y + 35, gridWidth, gridHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y + 35, gridWidth, gridHeight);

        // Get player inventory items
        const inventoryItems = this.player.inventory ? this.player.inventory.getItemsAndCounts() : [];

        // Reset tooltip state (will be set if item is hovered/selected)
        this.tooltipVisible = false;
        this.tooltipItem = null;

        // Draw grid cells
        for (let row = 0; row < this.gridRows; row++) {
            for (let col = 0; col < this.gridCols; col++) {
                const cellX = x + col * (this.cellSize + this.gridPadding) + this.gridPadding;
                const cellY = y + 35 + row * (this.cellSize + this.gridPadding) + this.gridPadding;

                // Get item index
                const itemIdx = row * this.gridCols + col;

                // Determine cell background color based on selection status
                let cellColor = this.colors.gridBorder;

                // Check if this is the selected cell
                const isSelected = itemIdx === this.selectedItemIndex;
                const isHovered = itemIdx === this.hoveredItemIndex;

                // Draw selected or hovered item with different background
                if (isSelected && this.currentSection === 'inventory') {
                    cellColor = this.colors.itemSelected;
                } else if (isHovered) {
                    cellColor = this.colors.itemHover;
                }

                // Draw cell background
                ctx.fillStyle = cellColor;
                ctx.fillRect(cellX, cellY, this.cellSize, this.cellSize);
                ctx.strokeStyle = this.colors.gridBorder;
                ctx.lineWidth = 1;
                ctx.strokeRect(cellX, cellY, this.cellSize, this.cellSize);

                // Draw item if it exists in inventory
                if (itemIdx < inventoryItems.length) {
                    const itemData = inventoryItems[itemIdx];
                    const item = itemData.item;
                    const count = itemData.count;

                    if (item) {
                        // Get item icon if available
                        if (item.icon) {
                            // Center the icon in the cell
                            const iconX = cellX + (this.cellSize - item.icon.width) / 2;
                            const iconY = cellY + (this.cellSize - item.icon.height) / 2;
                            ctx.drawImage(item.icon, iconX, iconY);
                        } else {
                            // Fallback to a colored rectangle
                            ctx.fillStyle = 'rgb(150, 150, 150)';
                            ctx.fillRect(cellX + 5, cellY + 5, this.cellSize - 10, this.cellSize - 10);

                            // Draw item name initial
                            ctx.font = 'bold 16px Arial';
                            ctx.fillStyle = this.colors.text;
                            ctx.textAlign = 'center';
                            ctx.fillText(item.name.charAt(0).toUpperCase(), cellX + this.cellSize / 2, cellY + this.cellSize / 2 + 5);
                            ctx.textAlign = 'left';
                        }

                        // Draw item count if more than 1
                        if (count > 1) {
                            ctx.font = this.textFont;
                            ctx.fillStyle = this.colors.text;
                            const countText = `${count}`;
                            ctx.fillText(countText, cellX + this.cellSize - 15, cellY + this.cellSize - 5);
                        }

                        // Add visual indication if item is usable
                        if (typeof item.use === 'function' && !item.oneTimeUse) {
                            // Small green indicator in the corner
                            ctx.fillStyle = this.colors.usable;
                            ctx.fillRect(cellX + 2, cellY + 2, 6, 6);
                        }

                        // Draw selection outline
                        if (isSelected && this.currentSection === 'inventory') {
                            // Draw a bright border around the selected item
                            ctx.strokeStyle = this.colors.cursor;
                            ctx.lineWidth = 3;
                            ctx.strokeRect(cellX - 2, cellY - 2, this.cellSize + 4, this.cellSize + 4);

                            // Show button prompt
                            ctx.font = this.buttonFont;
                            ctx.fillStyle = this.colors.cursor;
                            ctx.fillText('E', cellX + this.cellSize - 12, cellY + 12);

                            // Store selected item for tooltip rendering
                            if (this.hoveredItemIndex !== itemIdx) {
                                this.tooltipVisible = true;
                                this.tooltipItem = item;
                            }
                        }

                        // Set tooltip for hovered items
                        if (isHovered) {
                            this.tooltipVisible = true;
                            this.tooltipItem = item;
                        }
                    }
                }
            }
        }

        // Draw feedback message below the grid if active
        if (this.itemFeedbackMessage && this.itemFeedbackTimer > 0) {
            this.itemFeedbackTimer--;
            this.drawItemFeedback(ctx, x + 100, y + 35 + gridHeight + 10);
        }
    }

    drawItemFeedback(ctx, x, y) {
        if (!this.itemFeedbackMessage) return;

        // Calculate message position - center horizontally
        const padding = 8;
        ctx.font = this.statFont;
        const textWidth = ctx.measureText(this.itemFeedbackMessage).width;

        const msgX = x + (this.gridCols * (this.cellSize + this.gridPadding)) / 2 - textWidth / 2;
        const msgY = y;

        // Draw message background
        ctx.fillStyle = this.colors.feedbackBg;
        ctx.fillRect(msgX - padding, msgY - padding - 15, textWidth + padding * 2, 30 + padding * 2);

        // Draw border
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 2;
        ctx.strokeRect(msgX - padding, msgY - padding - 15, textWidth + padding * 2, 30 + padding * 2);

        // Draw message text
        ctx.fillStyle = this.colors.feedbackText;
        ctx.fillText(this.itemFeedbackMessage, msgX, msgY);

        // Clear message when timer expires
        if (this.itemFeedbackTimer <= 0) {
            this.itemFeedbackMessage = null;
        }
    }

    drawItemTooltip(ctx, item, mousePos) {
        if (!item) return;

        // Get item information
        const name = item.name || 'Unknown Item';
        let description = item.description || 'No description available.';

        // Add usage hint if applicable
        const usable = typeof item.use === 'function' && !item.oneTimeUse;
        if (usable) {
            description += ' (Press E to use)';
        }

        // Calculate tooltip dimensions
        const padding = 10;
        const maxWidth = 250;

        // Render text dimensions
        ctx.font = this.statFont;
        const nameWidth = ctx.measureText(name).width;

        // Word wrap description
        ctx.font = '14px Arial';
        const words = description.split(' ');
        const wrappedDesc = [];
        let currentLine = '';

        for (const word of words) {
            const testLine = currentLine ? currentLine + ' ' + word : word;
            const testWidth = ctx.measureText(testLine).width;

            if (testWidth < maxWidth) {
                currentLine = testLine;
            } else {
                wrappedDesc.push(currentLine);
                currentLine = word;
            }
        }
        if (currentLine) {
            wrappedDesc.push(currentLine);
        }

        // Calculate tooltip size
        const tooltipWidth = Math.max(maxWidth, nameWidth) + padding * 2;
        const lineHeight = 18;
        const tooltipHeight = padding * 2 + 25 + wrappedDesc.length * lineHeight + 5;

        // Position tooltip near mouse but ensure it stays on screen
        let tooltipX = Math.min(mousePos.x + 15, this.screenWidth - tooltipWidth - 10);
        let tooltipY = Math.min(mousePos.y + 15, this.screenHeight - tooltipHeight - 10);

        // Draw tooltip background
        ctx.fillStyle = this.colors.background;
        ctx.fillRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.lineWidth = 2;
        ctx.strokeRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight);

        // Draw name
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText(name, tooltipX + padding, tooltipY + padding + 15);

        // Draw description
        ctx.font = '14px Arial';
        ctx.fillStyle = this.colors.text;
        let yOffset = tooltipY + padding + 25 + 15;
        for (const line of wrappedDesc) {
            ctx.fillText(line, tooltipX + padding, yOffset);
            yOffset += lineHeight;
        }
    }

    drawSkillsTab(ctx, margin) {
        const player = this.player;
        const attrs = player.attributes;

        // Header and skill points display
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText(`Skill Points: ${attrs.skillPoints}`, margin + 50, margin + 90);

        // Instructions
        ctx.font = this.textFont;
        ctx.fillStyle = this.colors.text;
        ctx.fillText('Click on a skill to view details and unlock it', margin + 50, margin + 120);

        // Get skill data organized by branch
        const branches = this.player.skillTree.getSkillsByBranch();
        const branchNames = ['Mind', 'Body', 'Magic Sword'];
        const branchIds = ['mind', 'body', 'magic_sword'];

        const screenWidth = this.screenWidth - margin * 2 - 100;
        const branchWidth = screenWidth / 3;
        const startY = margin + 150;
        const diamondSize = 17;       // 15% smaller
        const levelSpacing = 94;      // 15% smaller
        const skillSpacing = 119;     // 15% smaller

        this.skillRects = {};
        const skillPositions = {};

        // Draw branch headers (diamond shapes with names)
        for (let i = 0; i < branchNames.length; i++) {
            const branchX = margin + 50 + i * branchWidth + branchWidth / 2;

            // Draw diamond for branch header
            ctx.fillStyle = 'rgb(100, 200, 100)';
            ctx.beginPath();
            ctx.moveTo(branchX, startY);
            ctx.lineTo(branchX + diamondSize, startY + diamondSize);
            ctx.lineTo(branchX, startY + diamondSize * 2);
            ctx.lineTo(branchX - diamondSize, startY + diamondSize);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw branch name above diamond
            ctx.font = this.textFont;
            ctx.fillStyle = this.colors.text;
            ctx.textAlign = 'center';
            ctx.fillText(branchNames[i], branchX, startY - 10);
        }

        // Draw skills for each branch
        for (let branchIdx = 0; branchIdx < branchIds.length; branchIdx++) {
            const branchId = branchIds[branchIdx];
            const skills = branches[branchId];
            const branchX = margin + 50 + branchIdx * branchWidth + branchWidth / 2;

            // Get first level skills (no parent in this branch)
            const firstLevelSkills = skills.filter(skill => !skill.parent);

            // Draw first level skills
            for (let i = 0; i < firstLevelSkills.length; i++) {
                const skill = firstLevelSkills[i];
                let skillX = branchX;
                if (firstLevelSkills.length > 1) {
                    const offset = (i - (firstLevelSkills.length - 1) / 2) * skillSpacing;
                    skillX += offset;
                }
                const skillY = startY + 80;

                // Draw connection from branch header to skill
                ctx.strokeStyle = this.colors.border;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(branchX, startY + diamondSize * 2);
                ctx.lineTo(skillX, skillY - 15);
                ctx.stroke();

                // Draw the skill node
                this.drawSkillNode(ctx, skill, skillX, skillY);
                skillPositions[skill.id] = { x: skillX, y: skillY };
            }

            // Draw child skills (recursive levels)
            let processedParents = new Set();
            let currentLevelSkills = [...firstLevelSkills];

            while (currentLevelSkills.length > 0) {
                const nextLevelSkills = [];

                for (const parentSkill of currentLevelSkills) {
                    if (processedParents.has(parentSkill.id)) continue;
                    processedParents.add(parentSkill.id);

                    const parentPos = skillPositions[parentSkill.id];
                    if (!parentPos) continue;

                    // Find children of this parent
                    const children = skills.filter(s => s.parent === parentSkill.id);

                    for (let i = 0; i < children.length; i++) {
                        const child = children[i];
                        let childX = parentPos.x;
                        if (children.length > 1) {
                            const offset = (i - (children.length - 1) / 2) * skillSpacing;
                            childX += offset;
                        }
                        const childY = parentPos.y + levelSpacing;

                        // Draw connection from parent to child
                        ctx.strokeStyle = this.colors.border;
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.moveTo(parentPos.x, parentPos.y + 15);
                        ctx.lineTo(childX, childY - 15);
                        ctx.stroke();

                        // Draw the skill node
                        this.drawSkillNode(ctx, child, childX, childY);
                        skillPositions[child.id] = { x: childX, y: childY };
                        nextLevelSkills.push(child);
                    }
                }

                currentLevelSkills = nextLevelSkills;
            }
        }

        ctx.textAlign = 'left';

        // Draw selected skill details panel
        if (this.skillSelected && this.player.skillTree.skills[this.skillSelected]) {
            const skill = this.player.skillTree.skills[this.skillSelected];
            const tabHeight = 30;
            const tabMargin = 20;
            const detailY = this.screenHeight - margin - 150 - tabHeight - tabMargin;
            const detailWidth = this.screenWidth - margin * 2 - 100;
            const detailHeight = 120;

            ctx.fillStyle = 'rgba(30, 33, 41, 0.95)';
            ctx.fillRect(margin + 50, detailY, detailWidth, detailHeight);
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 2;
            ctx.strokeRect(margin + 50, detailY, detailWidth, detailHeight);

            // Skill name
            ctx.font = this.statFont;
            ctx.fillStyle = this.colors.title;
            ctx.fillText(skill.name, margin + 70, detailY + 30);

            // Skill description
            ctx.font = this.textFont;
            ctx.fillStyle = this.colors.text;
            ctx.fillText(skill.description, margin + 70, detailY + 55);

            // Draw unlock button or status
            const canUnlock = !skill.unlocked && skill.canUnlock(this.player) && attrs.skillPoints > 0;

            if (canUnlock) {
                // Draw unlock button
                const buttonX = margin + 50 + detailWidth - 120;
                const buttonY = detailY + detailHeight - 45;
                const buttonW = 100;
                const buttonH = 30;

                this.unlockButtonRect = { x: buttonX, y: buttonY, width: buttonW, height: buttonH };

                const isHovered = this.hoveredButton === 'unlock_button';
                ctx.fillStyle = isHovered ? this.colors.buttonHover : this.colors.button;
                ctx.fillRect(buttonX, buttonY, buttonW, buttonH);
                ctx.strokeStyle = this.colors.border;
                ctx.lineWidth = 1;
                ctx.strokeRect(buttonX, buttonY, buttonW, buttonH);

                ctx.font = this.buttonFont;
                ctx.fillStyle = this.colors.text;
                ctx.textAlign = 'center';
                ctx.fillText('Unlock', buttonX + buttonW / 2, buttonY + buttonH / 2 + 5);
                ctx.textAlign = 'left';
            } else {
                this.unlockButtonRect = null;

                // Show status message
                let statusText, statusColor;
                if (skill.unlocked) {
                    statusText = 'Skill Unlocked';
                    statusColor = 'rgb(0, 150, 0)';
                } else if (!skill.implemented) {
                    statusText = 'Not Yet Implemented';
                    statusColor = 'rgb(150, 0, 0)';
                } else if (attrs.level < skill.levelRequired) {
                    statusText = `Requires Level ${skill.levelRequired}`;
                    statusColor = 'rgb(150, 0, 0)';
                } else if (skill.parent && !this.player.skillTree.isSkillUnlocked(skill.parent)) {
                    const parentSkill = this.player.skillTree.skills[skill.parent];
                    statusText = `Requires ${parentSkill.name} Skill`;
                    statusColor = 'rgb(150, 0, 0)';
                } else if (attrs.skillPoints <= 0) {
                    statusText = 'No Skill Points Available';
                    statusColor = 'rgb(150, 0, 0)';
                } else {
                    statusText = 'Cannot Unlock Now';
                    statusColor = 'rgb(150, 0, 0)';
                }

                ctx.font = this.textFont;
                ctx.fillStyle = statusColor;
                ctx.textAlign = 'right';
                ctx.fillText(statusText, margin + 50 + detailWidth - 10, detailY + detailHeight - 20);
                ctx.textAlign = 'left';
            }
        }
    }

    drawSkillNode(ctx, skill, x, y) {
        const attrs = this.player.attributes;
        const nodeSize = 15;  // 15% smaller

        // Determine skill color based on state
        let nodeColor;
        if (skill.unlocked) {
            nodeColor = this.colors.skillUnlocked;  // Green
        } else if (skill.canUnlock(this.player) && attrs.skillPoints > 0) {
            nodeColor = this.colors.skillAvailable;  // Yellow
        } else {
            nodeColor = this.colors.skillUnavailable;  // Gray
        }

        // Check if hovered
        const isHovered = this.hoveredButton === `skill_${skill.id}`;
        if (isHovered && !skill.unlocked) {
            nodeColor = this.colors.buttonHover;
        }

        // Draw diamond shape
        ctx.fillStyle = nodeColor;
        ctx.beginPath();
        ctx.moveTo(x, y - nodeSize);
        ctx.lineTo(x + nodeSize, y);
        ctx.lineTo(x, y + nodeSize);
        ctx.lineTo(x - nodeSize, y);
        ctx.closePath();
        ctx.fill();

        // Highlight selected skill
        if (this.skillSelected === skill.id) {
            ctx.strokeStyle = this.colors.cursor;
            ctx.lineWidth = 3;
        } else {
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 1;
        }
        ctx.stroke();

        // Draw skill name above diamond
        ctx.font = '12px Arial';  // Slightly smaller font
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'center';
        ctx.fillText(skill.name, x, y - nodeSize - 6);

        // Draw level requirement below diamond
        ctx.fillText(`Level ${skill.levelRequired}+`, x, y + nodeSize + 15);

        // Store rect for mouse interaction (larger hitbox)
        const hitboxSize = 50;
        this.skillRects[skill.id] = {
            x: x - hitboxSize / 2,
            y: y - hitboxSize / 2,
            width: hitboxSize,
            height: hitboxSize
        };
    }

    navigateSkills(direction) {
        const branches = this.player.skillTree.getSkillsByBranch();
        const branchIds = ['mind', 'body', 'magic_sword'];

        // If no skill selected, select first available
        if (!this.skillSelected) {
            for (const branchId of branchIds) {
                if (branches[branchId].length > 0) {
                    this.skillSelected = branches[branchId][0].id;
                    return true;
                }
            }
            return false;
        }

        // Find current branch and index
        let currentBranch = null;
        let currentIndex = -1;

        for (const branchId of branchIds) {
            for (let i = 0; i < branches[branchId].length; i++) {
                if (branches[branchId][i].id === this.skillSelected) {
                    currentBranch = branchId;
                    currentIndex = i;
                    break;
                }
            }
            if (currentBranch) break;
        }

        if (!currentBranch) return false;

        const branchIndex = branchIds.indexOf(currentBranch);

        if (direction === 'up') {
            if (currentIndex > 0) {
                this.skillSelected = branches[currentBranch][currentIndex - 1].id;
                return true;
            }
        } else if (direction === 'down') {
            if (currentIndex < branches[currentBranch].length - 1) {
                this.skillSelected = branches[currentBranch][currentIndex + 1].id;
                return true;
            }
        } else if (direction === 'left') {
            if (branchIndex > 0) {
                const newBranch = branchIds[branchIndex - 1];
                if (branches[newBranch].length > 0) {
                    const newIndex = Math.min(currentIndex, branches[newBranch].length - 1);
                    this.skillSelected = branches[newBranch][newIndex].id;
                    return true;
                }
            }
        } else if (direction === 'right') {
            if (branchIndex < branchIds.length - 1) {
                const newBranch = branchIds[branchIndex + 1];
                if (branches[newBranch].length > 0) {
                    const newIndex = Math.min(currentIndex, branches[newBranch].length - 1);
                    this.skillSelected = branches[newBranch][newIndex].id;
                    return true;
                }
            }
        }

        return false;
    }
}

// Export
window.CharacterScreen = CharacterScreen;
