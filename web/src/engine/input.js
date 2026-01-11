/**
 * Input Handler - Manages keyboard, mouse, and gamepad input
 */
class InputHandler {
    constructor() {
        // Keyboard state
        this.keys = {};
        this.keysJustPressed = {};
        this.keysJustReleased = {};

        // Mouse state
        this.mouse = {
            x: 0,
            y: 0,
            buttons: {},
            buttonsJustPressed: {},
            buttonsJustReleased: {}
        };

        // Gamepad state
        this.gamepad = null;
        this.gamepadButtons = {};
        this.gamepadButtonsJustPressed = {};
        this.gamepadAxes = { x: 0, y: 0 };
        this.deadzone = 0.45;

        // Key mappings (matching Pygame version)
        this.keyMap = {
            // Movement
            'KeyW': 'up',
            'ArrowUp': 'up',
            'KeyS': 'down',
            'ArrowDown': 'down',
            'KeyA': 'left',
            'ArrowLeft': 'left',
            'KeyD': 'right',
            'ArrowRight': 'right',

            // Actions
            'Space': 'attack',
            'KeyE': 'interact',
            'KeyF': 'firebolt',
            'KeyB': 'blink',
            'ShiftLeft': 'dash',
            'ShiftRight': 'dash',

            // UI
            'KeyM': 'map',
            'Enter': 'character',
            'Escape': 'pause',
            'KeyC': 'debug',
            'Tab': 'inventory',
            'Digit1': 'tabAttributes',
            'Digit2': 'tabSkills'
        };

        // Gamepad button mappings (standard gamepad layout)
        this.gamepadMap = {
            0: 'attack',      // A button
            1: 'blink',       // B button
            2: 'firebolt',    // X button
            3: 'interact',    // Y button
            4: 'dash',        // Left bumper
            5: 'dash',        // Right bumper
            8: 'pause',       // Select
            9: 'character',   // Start
            12: 'up',         // D-pad up
            13: 'down',       // D-pad down
            14: 'left',       // D-pad left
            15: 'right'       // D-pad right
        };

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Keyboard events
        window.addEventListener('keydown', (e) => this.onKeyDown(e));
        window.addEventListener('keyup', (e) => this.onKeyUp(e));

        // Mouse events
        window.addEventListener('mousemove', (e) => this.onMouseMove(e));
        window.addEventListener('mousedown', (e) => this.onMouseDown(e));
        window.addEventListener('mouseup', (e) => this.onMouseUp(e));

        // Gamepad events
        window.addEventListener('gamepadconnected', (e) => this.onGamepadConnected(e));
        window.addEventListener('gamepaddisconnected', (e) => this.onGamepadDisconnected(e));
    }

    // Keyboard handlers
    onKeyDown(event) {
        // Prevent default for game keys
        if (this.keyMap[event.code]) {
            event.preventDefault();
        }

        if (!this.keys[event.code]) {
            this.keysJustPressed[event.code] = true;
        }
        this.keys[event.code] = true;
    }

    onKeyUp(event) {
        this.keys[event.code] = false;
        this.keysJustReleased[event.code] = true;
    }

    // Mouse handlers
    onMouseMove(event) {
        const canvas = document.getElementById('game-canvas');
        if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            this.mouse.x = (event.clientX - rect.left) * scaleX;
            this.mouse.y = (event.clientY - rect.top) * scaleY;
        }
    }

    onMouseDown(event) {
        if (!this.mouse.buttons[event.button]) {
            this.mouse.buttonsJustPressed[event.button] = true;
        }
        this.mouse.buttons[event.button] = true;
    }

    onMouseUp(event) {
        this.mouse.buttons[event.button] = false;
        this.mouse.buttonsJustReleased[event.button] = true;
    }

    // Gamepad handlers
    onGamepadConnected(event) {
        console.log('Gamepad connected:', event.gamepad.id);
        this.gamepad = event.gamepad;
    }

    onGamepadDisconnected(event) {
        console.log('Gamepad disconnected');
        this.gamepad = null;
        this.gamepadButtons = {};
        this.gamepadAxes = { x: 0, y: 0 };
    }

    // Update gamepad state (must be called each frame)
    updateGamepad() {
        // Get fresh gamepad state
        const gamepads = navigator.getGamepads();
        if (!gamepads) return;

        // Find first connected gamepad
        for (const gp of gamepads) {
            if (gp) {
                this.gamepad = gp;
                break;
            }
        }

        if (!this.gamepad) return;

        // Update axes with deadzone
        const rawX = this.gamepad.axes[0] || 0;
        const rawY = this.gamepad.axes[1] || 0;

        this.gamepadAxes.x = Math.abs(rawX) > this.deadzone ? rawX : 0;
        this.gamepadAxes.y = Math.abs(rawY) > this.deadzone ? rawY : 0;

        // Update buttons
        const previousButtons = { ...this.gamepadButtons };
        this.gamepadButtonsJustPressed = {};

        this.gamepad.buttons.forEach((button, index) => {
            const pressed = button.pressed;
            if (pressed && !previousButtons[index]) {
                this.gamepadButtonsJustPressed[index] = true;
            }
            this.gamepadButtons[index] = pressed;
        });
    }

    // Clear per-frame state (call at end of frame)
    clearFrameState() {
        this.keysJustPressed = {};
        this.keysJustReleased = {};
        this.mouse.buttonsJustPressed = {};
        this.mouse.buttonsJustReleased = {};
        this.gamepadButtonsJustPressed = {};
    }

    // Helper methods for checking input
    isKeyDown(action) {
        // Check keyboard
        for (const [code, mappedAction] of Object.entries(this.keyMap)) {
            if (mappedAction === action && this.keys[code]) {
                return true;
            }
        }

        // Check gamepad buttons
        for (const [button, mappedAction] of Object.entries(this.gamepadMap)) {
            if (mappedAction === action && this.gamepadButtons[button]) {
                return true;
            }
        }

        return false;
    }

    isKeyJustPressed(action) {
        // Check keyboard
        for (const [code, mappedAction] of Object.entries(this.keyMap)) {
            if (mappedAction === action && this.keysJustPressed[code]) {
                return true;
            }
        }

        // Check gamepad buttons
        for (const [button, mappedAction] of Object.entries(this.gamepadMap)) {
            if (mappedAction === action && this.gamepadButtonsJustPressed[button]) {
                return true;
            }
        }

        return false;
    }

    // Get movement vector (keyboard + gamepad combined)
    getMovementVector() {
        let x = 0;
        let y = 0;

        // Keyboard input
        if (this.isKeyDown('left')) x -= 1;
        if (this.isKeyDown('right')) x += 1;
        if (this.isKeyDown('up')) y -= 1;
        if (this.isKeyDown('down')) y += 1;

        // Gamepad analog stick (overrides keyboard if being used)
        if (this.gamepadAxes.x !== 0 || this.gamepadAxes.y !== 0) {
            x = this.gamepadAxes.x;
            y = this.gamepadAxes.y;
        }

        // Normalize diagonal movement
        const magnitude = Math.sqrt(x * x + y * y);
        if (magnitude > 1) {
            x /= magnitude;
            y /= magnitude;
        }

        return { x, y };
    }

    // Get facing direction from movement or input
    getFacingDirection() {
        const movement = this.getMovementVector();

        if (Math.abs(movement.x) > Math.abs(movement.y)) {
            return movement.x > 0 ? 'right' : 'left';
        } else if (movement.y !== 0) {
            return movement.y > 0 ? 'down' : 'up';
        }

        return null; // No direction pressed
    }

    // Check if gamepad is connected
    hasGamepad() {
        return this.gamepad !== null;
    }

    // Get debug info
    getDebugInfo() {
        const movement = this.getMovementVector();
        let info = `Movement: (${movement.x.toFixed(2)}, ${movement.y.toFixed(2)})`;

        if (this.hasGamepad()) {
            info += ` | Gamepad: ${this.gamepad.id.substring(0, 20)}...`;
        }

        return info;
    }
}

// Export for use in other modules
window.InputHandler = InputHandler;
