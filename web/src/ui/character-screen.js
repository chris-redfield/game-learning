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
        this.buttonOrder = ['inc_str', 'inc_con', 'inc_dex', 'inc_int'];

        // Button rectangles for mouse interaction
        this.buttons = {};
        this.tabRects = {};

        // Skill selection
        this.skillSelected = null;
        this.skillRects = {};

        // Portrait (will load async)
        this.portrait = null;
        this.portraitSize = 150;
        this.loadPortrait();
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
        this.selectedIndex = (this.selectedIndex + 1) % this.buttonOrder.length;
    }

    selectPrev() {
        this.selectedIndex = (this.selectedIndex - 1 + this.buttonOrder.length) % this.buttonOrder.length;
    }

    activateSelected() {
        if (this.currentTab === 'attributes') {
            const buttonId = this.buttonOrder[this.selectedIndex];
            const stat = buttonId.replace('inc_', '');
            if (this.player.attributes.statPoints > 0) {
                this.player.attributes.increaseStat(stat);
                return true;
            }
        } else if (this.currentTab === 'skills' && this.skillSelected) {
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

        // Tab switching
        if (input.isKeyJustPressed('tab') || input.isKeyJustPressed('skillTab')) {
            this.switchTab();
            return true;
        }

        if (this.currentTab === 'attributes') {
            // Navigation
            if (input.isKeyJustPressed('up')) {
                this.selectPrev();
                return true;
            }
            if (input.isKeyJustPressed('down')) {
                this.selectNext();
                return true;
            }
            // Activation
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
            // Unlock skill
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
        const attrColor = this.currentTab === 'attributes' ? this.colors.buttonHover : this.colors.button;
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
        const skillsColor = this.currentTab === 'skills' ? this.colors.buttonHover : this.colors.button;
        ctx.fillStyle = skillsColor;
        ctx.fillRect(skillsTabX, tabY, tabWidth, tabHeight);
        ctx.strokeStyle = this.colors.border;
        ctx.strokeRect(skillsTabX, tabY, tabWidth, tabHeight);

        ctx.fillStyle = this.colors.text;
        ctx.fillText('SKILLS', skillsTabX + tabWidth / 2, tabY + tabHeight / 2 + 5);

        ctx.textAlign = 'left';

        // Store tab rects
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
        ctx.fillText('Press TAB to switch', this.screenWidth / 2, tabY + tabHeight + 20);
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
            }

            // Check if selected
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

        // Skill points display
        ctx.font = this.statFont;
        ctx.fillStyle = this.colors.title;
        ctx.fillText(`Skill Points: ${attrs.skillPoints}`, margin + 50, margin + 100);

        // Instructions
        ctx.font = this.textFont;
        ctx.fillStyle = this.colors.text;
        ctx.fillText('Use arrow keys to select, E to unlock', margin + 50, margin + 130);

        // Draw skill tree
        const skills = this.player.skillTree.skills;
        const skillIds = Object.keys(skills);

        const startX = margin + 100;
        const startY = margin + 180;
        const spacing = 120;
        const nodeSize = 40;

        this.skillRects = {};

        let col = 0;
        let row = 0;
        const cols = 4;

        for (const skillId of skillIds) {
            const skill = skills[skillId];
            const x = startX + col * spacing;
            const y = startY + row * 100;

            // Determine color
            let nodeColor;
            if (skill.unlocked) {
                nodeColor = this.colors.skillUnlocked;
            } else if (attrs.level >= skill.levelRequired && attrs.skillPoints > 0) {
                nodeColor = this.colors.skillAvailable;
            } else {
                nodeColor = this.colors.skillUnavailable;
            }

            // Draw diamond shape
            ctx.fillStyle = nodeColor;
            ctx.beginPath();
            ctx.moveTo(x, y - nodeSize / 2);
            ctx.lineTo(x + nodeSize / 2, y);
            ctx.lineTo(x, y + nodeSize / 2);
            ctx.lineTo(x - nodeSize / 2, y);
            ctx.closePath();
            ctx.fill();

            // Selection highlight
            if (this.skillSelected === skillId) {
                ctx.strokeStyle = this.colors.cursor;
                ctx.lineWidth = 3;
                ctx.stroke();
            } else {
                ctx.strokeStyle = this.colors.border;
                ctx.lineWidth = 1;
                ctx.stroke();
            }

            // Skill name
            ctx.font = '14px Arial';
            ctx.fillStyle = this.colors.text;
            ctx.textAlign = 'center';
            ctx.fillText(skill.unlocked ? skill.levelRequired : `Lvl ${skill.levelRequired}`, x, y + nodeSize / 2 + 20);
            ctx.textAlign = 'left';

            // Store rect for mouse interaction
            this.skillRects[skillId] = {
                x: x - nodeSize / 2,
                y: y - nodeSize / 2,
                width: nodeSize,
                height: nodeSize
            };

            col++;
            if (col >= cols) {
                col = 0;
                row++;
            }
        }

        // Draw selected skill details
        if (this.skillSelected && skills[this.skillSelected]) {
            const skill = skills[this.skillSelected];
            const detailY = this.screenHeight - margin - 180;

            ctx.fillStyle = 'rgba(30, 33, 41, 0.95)';
            ctx.fillRect(margin + 50, detailY, this.screenWidth - margin * 2 - 100, 100);
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 2;
            ctx.strokeRect(margin + 50, detailY, this.screenWidth - margin * 2 - 100, 100);

            ctx.font = this.statFont;
            ctx.fillStyle = this.colors.title;

            // Capitalize skill name
            const skillName = this.skillSelected.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            ctx.fillText(skillName, margin + 70, detailY + 30);

            ctx.font = this.textFont;
            ctx.fillStyle = this.colors.text;
            ctx.fillText(`Level Required: ${skill.levelRequired}`, margin + 70, detailY + 55);

            // Status
            let statusText, statusColor;
            if (skill.unlocked) {
                statusText = 'UNLOCKED';
                statusColor = this.colors.skillUnlocked;
            } else if (attrs.level >= skill.levelRequired && attrs.skillPoints > 0) {
                statusText = 'Press E to Unlock';
                statusColor = this.colors.skillAvailable;
            } else if (attrs.level < skill.levelRequired) {
                statusText = `Requires Level ${skill.levelRequired}`;
                statusColor = 'rgb(150, 0, 0)';
            } else {
                statusText = 'No skill points';
                statusColor = 'rgb(150, 0, 0)';
            }

            ctx.fillStyle = statusColor;
            ctx.fillText(statusText, margin + 70, detailY + 80);
        }
    }
}

// Export
window.CharacterScreen = CharacterScreen;
