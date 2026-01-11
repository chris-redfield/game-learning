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
            skillUnavailable: 'rgb(100, 100, 100)'
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
            // Navigation with up/down arrows
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
        const startY = margin + 170;
        const diamondSize = 20;
        const levelSpacing = 110;
        const skillSpacing = 140;

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
                ctx.lineTo(skillX, skillY - 18);
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
                        ctx.moveTo(parentPos.x, parentPos.y + 18);
                        ctx.lineTo(childX, childY - 18);
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
        const nodeSize = 18;

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
        ctx.font = '14px Arial';
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'center';
        ctx.fillText(skill.name, x, y - nodeSize - 8);

        // Draw level requirement below diamond
        ctx.fillText(`Level ${skill.levelRequired}+`, x, y + nodeSize + 18);

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
