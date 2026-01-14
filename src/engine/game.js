/**
 * Game Engine - Core game loop and rendering
 */
class Game {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Game configuration
        this.width = 1280;
        this.height = 720;
        this.targetFPS = 60;
        this.backgroundColor = '#004040'; // Teal green (0, 64, 64)

        // Set canvas size
        this.canvas.width = this.width;
        this.canvas.height = this.height;

        // Scale canvas to fit screen while maintaining aspect ratio
        this.scaleCanvas();
        window.addEventListener('resize', () => this.scaleCanvas());

        // Timing
        this.lastTime = 0;
        this.deltaTime = 0;
        this.frameTime = 1000 / this.targetFPS;
        this.accumulator = 0;

        // FPS tracking
        this.fps = 0;
        this.frameCount = 0;
        this.fpsTime = 0;
        this.fpsUpdateInterval = 500; // Update FPS display every 500ms

        // Performance metrics
        this.perfMetrics = {
            frameTime: 0,
            updateTime: 0,
            renderTime: 0,
            // Rolling averages
            avgFrameTime: 0,
            avgUpdateTime: 0,
            avgRenderTime: 0,
            samples: [],
            maxSamples: 60 // 1 second of data at 60fps
        };

        // Game state
        this.running = false;
        this.paused = false;

        // Input
        this.input = new InputHandler();

        // Entity lists
        this.entities = [];
        this.uiElements = [];

        // Game state flags
        this.showDebug = false;
        this.showMap = false;
        this.showCharacterScreen = false;
        this.showDeathScreen = false;

        // Transition effect
        this.transition = {
            active: false,
            alpha: 0,
            fadeIn: false,
            duration: 500,
            startTime: 0
        };

        // Asset loader
        this.assets = {
            images: {},
            loaded: false,
            toLoad: 0,
            loadedCount: 0
        };
    }

    scaleCanvas() {
        const maxWidth = window.innerWidth - 40;
        const maxHeight = window.innerHeight - 40;

        const scaleX = maxWidth / this.width;
        const scaleY = maxHeight / this.height;
        const scale = Math.min(scaleX, scaleY, 1); // Don't scale up

        this.canvas.style.width = `${this.width * scale}px`;
        this.canvas.style.height = `${this.height * scale}px`;
    }

    // Asset loading
    loadImage(key, src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.assets.images[key] = img;
                this.assets.loadedCount++;
                resolve(img);
            };
            img.onerror = () => {
                console.error(`Failed to load image: ${src}`);
                reject(new Error(`Failed to load: ${src}`));
            };
            img.src = src;
            this.assets.toLoad++;
        });
    }

    async loadAssets() {
        // Core assets to load
        const imagesToLoad = [
            ['sprites', 'assets/sprites.png'],
            ['bonfire', 'assets/bonfire-sprites.png'],
            ['skeleton_idle', 'assets/Skeleton_02_White_Idle.png'],
            ['skeleton_walk', 'assets/Skeleton_02_White_Walk.png'],
            ['slime_idle', 'assets/slime_idle.gif'],
            ['slime_move', 'assets/slime_move.gif'],
            ['health_potion', 'assets/health-potion.png'],
            ['ancient_scroll', 'assets/ancient_scroll.png'],
            ['portrait', 'assets/portrait-pixel-art.png'],
            // Ark character sprites
            ['ark_stand_down', 'assets/ark/ark_stand_down.png'],
            ['ark_stand_up', 'assets/ark/ark_stand_up.png'],
            ['ark_stand_left', 'assets/ark/ark_stand_left.png'],
            ['ark_stand_right', 'assets/ark/ark_stand_right.png'],
            ['ark_walk_down', 'assets/ark/ark_walk_down_speed-70.png'],
            ['ark_walk_up', 'assets/ark/ark_walk_up_speed-70.png'],
            ['ark_walk_left', 'assets/ark/ark_walk_left_speed-70.png'],
            ['ark_walk_right', 'assets/ark/ark_walk_right_speed-70.png'],
            // Environment
            ['bush1', 'assets/bush/bush1.png'],
            ['bush2', 'assets/bush/bush2.png'],
            ['bush3', 'assets/bush/bush3.png'],
            ['rock1', 'assets/rock/rock1.png'],
            ['rock2', 'assets/rock/rock2.png'],
            ['rock3', 'assets/rock/rock3.png']
        ];

        try {
            await Promise.all(imagesToLoad.map(([key, src]) => this.loadImage(key, src)));
            this.assets.loaded = true;
            console.log('All assets loaded successfully');
        } catch (error) {
            console.error('Error loading assets:', error);
            // Continue anyway with placeholder rendering
            this.assets.loaded = true;
        }
    }

    getImage(key) {
        return this.assets.images[key] || null;
    }

    // Entity management
    addEntity(entity) {
        this.entities.push(entity);
    }

    removeEntity(entity) {
        const index = this.entities.indexOf(entity);
        if (index > -1) {
            this.entities.splice(index, 1);
        }
    }

    // Main game loop
    start() {
        this.running = true;
        this.lastTime = performance.now();
        requestAnimationFrame((time) => this.gameLoop(time));
    }

    stop() {
        this.running = false;
    }

    gameLoop(currentTime) {
        if (!this.running) return;

        // Calculate delta time
        this.deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;

        // FPS calculation
        this.frameCount++;
        this.fpsTime += this.deltaTime;
        if (this.fpsTime >= this.fpsUpdateInterval) {
            this.fps = Math.round((this.frameCount * 1000) / this.fpsTime);
            this.frameCount = 0;
            this.fpsTime = 0;
            this.updateFPSDisplay();
        }

        // Update gamepad state
        this.input.updateGamepad();

        // Show debug only while C key is held down (not a toggle)
        this.showDebug = this.input.isKeyDown('debug');

        // Fixed timestep for physics/logic
        const updateStart = performance.now();
        this.accumulator += this.deltaTime;
        let didUpdate = false;
        while (this.accumulator >= this.frameTime) {
            if (!this.paused) {
                this.update(this.frameTime / 1000); // Convert to seconds
            }
            this.accumulator -= this.frameTime;
            didUpdate = true;
        }
        this.perfMetrics.updateTime = performance.now() - updateStart;

        // Clear per-frame input state only after an update ran
        // This prevents input loss on high refresh rate displays (120Hz+)
        // where render frames can occur faster than the fixed timestep
        if (didUpdate) {
            this.input.clearFrameState();
        }

        // Render
        const renderStart = performance.now();
        this.render();
        this.perfMetrics.renderTime = performance.now() - renderStart;

        // Update performance metrics
        this.updatePerfMetrics();

        // Next frame
        requestAnimationFrame((time) => this.gameLoop(time));
    }

    update(dt) {
        // Update transition effect
        this.updateTransition();

        // Update all entities
        for (const entity of this.entities) {
            if (entity.update) {
                entity.update(dt, this);
            }
        }

        // Override in subclass or main.js for game-specific logic
        if (this.onUpdate) {
            this.onUpdate(dt);
        }
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = this.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Draw all entities (sorted by y position for depth)
        const sortedEntities = [...this.entities].sort((a, b) => {
            const ay = a.y + (a.height || 0);
            const by = b.y + (b.height || 0);
            return ay - by;
        });

        for (const entity of sortedEntities) {
            if (entity.render) {
                entity.render(this.ctx, this);
            }
        }

        // Override in subclass or main.js for game-specific rendering
        if (this.onRender) {
            this.onRender(this.ctx);
        }

        // Draw transition overlay
        this.renderTransition();

        // Draw debug info
        if (this.showDebug) {
            this.renderDebug();
        }
    }

    // Transition effects
    startTransition(fadeIn = false, callback = null) {
        this.transition.active = true;
        this.transition.fadeIn = fadeIn;
        this.transition.startTime = performance.now();
        this.transition.alpha = fadeIn ? 1 : 0;
        this.transition.callback = callback;
    }

    updateTransition() {
        if (!this.transition.active) return;

        const elapsed = performance.now() - this.transition.startTime;
        const progress = Math.min(elapsed / this.transition.duration, 1);

        if (this.transition.fadeIn) {
            this.transition.alpha = 1 - progress;
        } else {
            this.transition.alpha = progress;
        }

        if (progress >= 1) {
            this.transition.active = false;
            if (this.transition.callback) {
                this.transition.callback();
            }
        }
    }

    renderTransition() {
        if (this.transition.alpha > 0) {
            this.ctx.fillStyle = `rgba(0, 0, 0, ${this.transition.alpha})`;
            this.ctx.fillRect(0, 0, this.width, this.height);
        }
    }

    // Debug rendering (disabled - no visual overlay)
    renderDebug() {
        // Debug overlay removed per user request
    }

    updateFPSDisplay() {
        const fpsElement = document.getElementById('fps-counter');
        if (fpsElement) {
            fpsElement.textContent = `FPS: ${this.fps}`;
        }
    }

    updatePerfMetrics() {
        const sample = {
            frame: this.deltaTime,
            update: this.perfMetrics.updateTime,
            render: this.perfMetrics.renderTime
        };

        this.perfMetrics.samples.push(sample);
        if (this.perfMetrics.samples.length > this.perfMetrics.maxSamples) {
            this.perfMetrics.samples.shift();
        }

        // Calculate rolling averages
        if (this.perfMetrics.samples.length > 0) {
            let totalFrame = 0, totalUpdate = 0, totalRender = 0;
            for (const s of this.perfMetrics.samples) {
                totalFrame += s.frame;
                totalUpdate += s.update;
                totalRender += s.render;
            }
            const count = this.perfMetrics.samples.length;
            this.perfMetrics.avgFrameTime = totalFrame / count;
            this.perfMetrics.avgUpdateTime = totalUpdate / count;
            this.perfMetrics.avgRenderTime = totalRender / count;
        }
    }

    getPerfMetrics() {
        return {
            fps: this.fps,
            frameTime: this.perfMetrics.avgFrameTime.toFixed(2),
            updateTime: this.perfMetrics.avgUpdateTime.toFixed(2),
            renderTime: this.perfMetrics.avgRenderTime.toFixed(2)
        };
    }

    // Utility methods
    isOffscreen(x, y, margin = 0) {
        return x < -margin || x > this.width + margin ||
               y < -margin || y > this.height + margin;
    }

    // Draw helpers
    drawRect(x, y, width, height, color, filled = true) {
        if (filled) {
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x, y, width, height);
        } else {
            this.ctx.strokeStyle = color;
            this.ctx.strokeRect(x, y, width, height);
        }
    }

    drawCircle(x, y, radius, color, filled = true) {
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, Math.PI * 2);
        if (filled) {
            this.ctx.fillStyle = color;
            this.ctx.fill();
        } else {
            this.ctx.strokeStyle = color;
            this.ctx.stroke();
        }
    }

    drawText(text, x, y, color = 'white', font = '16px Arial') {
        this.ctx.fillStyle = color;
        this.ctx.font = font;
        this.ctx.fillText(text, x, y);
    }

    // Image drawing with sprite sheet support
    drawImage(image, x, y, width = null, height = null) {
        if (!image) return;

        if (width && height) {
            this.ctx.drawImage(image, x, y, width, height);
        } else {
            this.ctx.drawImage(image, x, y);
        }
    }

    drawSprite(image, sx, sy, sw, sh, dx, dy, dw, dh) {
        if (!image) return;
        this.ctx.drawImage(image, sx, sy, sw, sh, dx, dy, dw, dh);
    }
}

// Export for use in other modules
window.Game = Game;
