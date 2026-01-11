/**
 * DialogBalloon - Speech bubble system for NPCs and entities
 * Mirrors Python entities/npc/dialog_balloon.py
 */
class DialogBalloon {
    constructor() {
        this.activeBalloons = [];

        // Styling
        this.padding = 12;
        this.margin = 5;
        this.maxWidth = 600;
        this.lineHeight = 22;
        this.displayDuration = 4000;
        this.fadeDuration = 300;

        // Colors
        this.bgColor = { r: 30, g: 33, b: 41, a: 230 };
        this.textColor = { r: 255, g: 255, b: 255 };
        this.borderColor = { r: 180, g: 180, b: 200 };

        // Font settings
        this.fontSize = 15;
        this.fontFamily = 'Arial';

        // Tail properties for speech bubble
        this.tailHeight = 12;
        this.tailWidth = 18;
    }

    /**
     * Calculate appropriate width based on text length
     */
    getDynamicMaxWidth(text, screenWidth = 1280) {
        const textLength = text.length;

        let desiredWidth;
        if (textLength > 100) {
            desiredWidth = Math.min(800, Math.floor(screenWidth * 0.8));
        } else if (textLength > 60) {
            desiredWidth = Math.min(600, Math.floor(screenWidth * 0.7));
        } else if (textLength > 30) {
            desiredWidth = Math.min(450, Math.floor(screenWidth * 0.6));
        } else {
            desiredWidth = Math.min(350, Math.floor(screenWidth * 0.5));
        }

        return Math.max(300, desiredWidth);
    }

    /**
     * Add a new dialog balloon
     */
    addDialog(text, x, y, entityWidth = 35, entityHeight = 41) {
        // Get dynamic width
        const dynamicWidth = this.getDynamicMaxWidth(text);

        // Wrap text
        const wrappedLines = this.wrapText(text, dynamicWidth);

        // Calculate dimensions
        const ctx = document.createElement('canvas').getContext('2d');
        ctx.font = `${this.fontSize}px ${this.fontFamily}`;

        let textWidth = 0;
        for (const line of wrappedLines) {
            const lineWidth = ctx.measureText(line).width;
            if (lineWidth > textWidth) textWidth = lineWidth;
        }

        const textHeight = wrappedLines.length * this.lineHeight;
        const balloonWidth = textWidth + this.padding * 2;
        const balloonHeight = textHeight + this.padding * 2;

        // Position balloon above entity
        let balloonX = x + entityWidth / 2 - balloonWidth / 2;
        let balloonY = y - balloonHeight - this.tailHeight - 10;

        // Keep on screen
        const screenWidth = 1280;
        const screenHeight = 720;
        balloonX = Math.max(10, Math.min(balloonX, screenWidth - balloonWidth - 10));
        balloonY = Math.max(10, Math.min(balloonY, screenHeight - balloonHeight - 10));

        const balloon = {
            text: text,
            lines: wrappedLines,
            x: balloonX,
            y: balloonY,
            width: balloonWidth,
            height: balloonHeight,
            entityX: x + entityWidth / 2,
            entityY: y,
            createdTime: performance.now(),
            alpha: 1.0
        };

        this.activeBalloons.push(balloon);
    }

    /**
     * Wrap text to fit within max width
     */
    wrapText(text, maxWidth) {
        const ctx = document.createElement('canvas').getContext('2d');
        ctx.font = `${this.fontSize}px ${this.fontFamily}`;

        // Check if entire text fits
        if (ctx.measureText(text).width <= maxWidth) {
            return [text];
        }

        const words = text.split(' ');
        const lines = [];
        let currentLine = [];

        for (const word of words) {
            const testLine = [...currentLine, word].join(' ');
            const width = ctx.measureText(testLine).width;

            if (width <= maxWidth) {
                currentLine.push(word);
            } else {
                if (currentLine.length > 0) {
                    lines.push(currentLine.join(' '));
                    currentLine = [word];
                } else {
                    lines.push(word);
                }
            }
        }

        if (currentLine.length > 0) {
            lines.push(currentLine.join(' '));
        }

        return lines.length > 0 ? lines : [text];
    }

    /**
     * Update all active dialog balloons
     */
    update(currentTime) {
        this.activeBalloons = this.activeBalloons.filter(balloon => {
            const elapsed = currentTime - balloon.createdTime;

            if (elapsed > this.displayDuration + this.fadeDuration) {
                return false; // Remove
            } else if (elapsed > this.displayDuration) {
                // Fade out
                const fadeProgress = (elapsed - this.displayDuration) / this.fadeDuration;
                balloon.alpha = 1 - fadeProgress;
            }

            return true;
        });
    }

    /**
     * Draw all active dialog balloons
     */
    draw(ctx) {
        for (const balloon of this.activeBalloons) {
            const alpha = balloon.alpha;

            // Draw balloon background with rounded corners
            ctx.fillStyle = `rgba(${this.bgColor.r}, ${this.bgColor.g}, ${this.bgColor.b}, ${(this.bgColor.a / 255) * alpha})`;
            this.drawRoundedRect(ctx, balloon.x, balloon.y, balloon.width, balloon.height, 10);
            ctx.fill();

            // Draw border
            ctx.strokeStyle = `rgba(${this.borderColor.r}, ${this.borderColor.g}, ${this.borderColor.b}, ${alpha})`;
            ctx.lineWidth = 2;
            this.drawRoundedRect(ctx, balloon.x, balloon.y, balloon.width, balloon.height, 10);
            ctx.stroke();

            // Draw tail
            const tailCenterX = balloon.x + balloon.width / 2;
            const tailTopY = balloon.y + balloon.height;

            ctx.fillStyle = `rgba(${this.bgColor.r}, ${this.bgColor.g}, ${this.bgColor.b}, ${(this.bgColor.a / 255) * alpha})`;
            ctx.beginPath();
            ctx.moveTo(tailCenterX - this.tailWidth / 2, tailTopY);
            ctx.lineTo(tailCenterX + this.tailWidth / 2, tailTopY);
            ctx.lineTo(tailCenterX, tailTopY + this.tailHeight);
            ctx.closePath();
            ctx.fill();

            // Draw tail border
            ctx.strokeStyle = `rgba(${this.borderColor.r}, ${this.borderColor.g}, ${this.borderColor.b}, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(tailCenterX - this.tailWidth / 2, tailTopY);
            ctx.lineTo(tailCenterX, tailTopY + this.tailHeight);
            ctx.lineTo(tailCenterX + this.tailWidth / 2, tailTopY);
            ctx.stroke();

            // Draw text
            ctx.font = `${this.fontSize}px ${this.fontFamily}`;
            ctx.fillStyle = `rgba(${this.textColor.r}, ${this.textColor.g}, ${this.textColor.b}, ${alpha})`;
            ctx.textAlign = 'center';

            let yOffset = balloon.y + this.padding + this.fontSize;
            for (const line of balloon.lines) {
                ctx.fillText(line, balloon.x + balloon.width / 2, yOffset);
                yOffset += this.lineHeight;
            }

            ctx.textAlign = 'left';
        }
    }

    /**
     * Draw rounded rectangle path
     */
    drawRoundedRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
    }

    /**
     * Clear all dialog balloons
     */
    clear() {
        this.activeBalloons = [];
    }

    /**
     * Check if there are active dialogs
     */
    hasActiveDialog() {
        return this.activeBalloons.length > 0;
    }
}

// Singleton instance
window.dialogBalloonSystem = new DialogBalloon();
