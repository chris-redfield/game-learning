/**
 * GIF Frame Loader - Extracts frames from animated GIFs for canvas rendering
 * Uses the gifuct-js approach to parse GIF files
 */

class GifLoader {
    constructor() {
        this.cache = new Map();
    }

    /**
     * Load a GIF and extract all frames as canvas-ready images
     * @param {string} url - URL to the GIF file
     * @returns {Promise<{frames: ImageData[], delays: number[]}>}
     */
    async loadGif(url) {
        // Check cache first
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }

        try {
            // Fetch the GIF as binary data
            console.log(`Fetching GIF from: ${url}`);
            const response = await fetch(url);
            console.log(`Response status: ${response.status}, content-type: ${response.headers.get('content-type')}`);
            const arrayBuffer = await response.arrayBuffer();
            const data = new Uint8Array(arrayBuffer);
            console.log(`Received ${data.length} bytes`);

            // Parse the GIF
            const gif = this.parseGif(data);

            // Cache and return
            this.cache.set(url, gif);
            return gif;
        } catch (error) {
            console.error(`Error loading GIF ${url}:`, error);
            return { frames: [], delays: [], width: 32, height: 24 };
        }
    }

    /**
     * Parse GIF binary data and extract frames
     */
    parseGif(data) {
        const frames = [];
        const delays = [];

        // GIF header check
        const header = String.fromCharCode(...data.slice(0, 6));
        console.log(`GIF header received: "${header}" (bytes: ${data.slice(0, 10).join(', ')})`);
        if (header !== 'GIF87a' && header !== 'GIF89a') {
            console.error('Invalid GIF header:', header);
            return { frames: [], delays: [], width: 0, height: 0 };
        }

        // Logical screen descriptor
        const width = data[6] | (data[7] << 8);
        const height = data[8] | (data[9] << 8);
        const packed = data[10];
        const hasGlobalColorTable = (packed & 0x80) !== 0;
        const globalColorTableSize = 1 << ((packed & 0x07) + 1);

        let pos = 13; // Start after header

        // Global color table
        let globalColorTable = null;
        if (hasGlobalColorTable) {
            globalColorTable = [];
            for (let i = 0; i < globalColorTableSize; i++) {
                globalColorTable.push([data[pos++], data[pos++], data[pos++]]);
            }
        }

        // Create a canvas for compositing frames
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');

        // Previous frame data for disposal
        let previousImageData = null;
        let disposalMethod = 0;
        let transparentIndex = -1;
        let delayTime = 100; // Default delay in ms

        // Parse blocks
        while (pos < data.length) {
            const blockType = data[pos++];

            if (blockType === 0x21) { // Extension block
                const extType = data[pos++];

                if (extType === 0xF9) { // Graphics Control Extension
                    pos++; // Block size (always 4)
                    const gcPacked = data[pos++];
                    disposalMethod = (gcPacked >> 2) & 0x07;
                    const hasTransparency = (gcPacked & 0x01) !== 0;
                    delayTime = (data[pos++] | (data[pos++] << 8)) * 10; // Convert to ms
                    if (delayTime === 0) delayTime = 100; // Default if 0
                    transparentIndex = hasTransparency ? data[pos++] : -1;
                    if (!hasTransparency) pos++;
                    pos++; // Block terminator
                } else {
                    // Skip other extension blocks
                    while (data[pos] !== 0) {
                        pos += data[pos] + 1;
                    }
                    pos++; // Block terminator
                }
            } else if (blockType === 0x2C) { // Image descriptor
                const frameLeft = data[pos++] | (data[pos++] << 8);
                const frameTop = data[pos++] | (data[pos++] << 8);
                const frameWidth = data[pos++] | (data[pos++] << 8);
                const frameHeight = data[pos++] | (data[pos++] << 8);
                const framePacked = data[pos++];

                const hasLocalColorTable = (framePacked & 0x80) !== 0;
                const interlaced = (framePacked & 0x40) !== 0;
                const localColorTableSize = 1 << ((framePacked & 0x07) + 1);

                // Local color table
                let colorTable = globalColorTable;
                if (hasLocalColorTable) {
                    colorTable = [];
                    for (let i = 0; i < localColorTableSize; i++) {
                        colorTable.push([data[pos++], data[pos++], data[pos++]]);
                    }
                }

                // LZW decode
                const minCodeSize = data[pos++];
                const imageData = this.decodeLZW(data, pos, minCodeSize, frameWidth * frameHeight);

                // Skip to end of image data blocks
                while (data[pos] !== 0) {
                    pos += data[pos] + 1;
                }
                pos++; // Block terminator

                // Handle disposal
                if (disposalMethod === 2) {
                    // Restore to background
                    ctx.clearRect(0, 0, width, height);
                } else if (disposalMethod === 3 && previousImageData) {
                    // Restore to previous
                    ctx.putImageData(previousImageData, 0, 0);
                }

                // Save current state before drawing if needed
                if (disposalMethod === 3) {
                    previousImageData = ctx.getImageData(0, 0, width, height);
                }

                // Draw frame pixels
                const frameImageData = ctx.getImageData(frameLeft, frameTop, frameWidth, frameHeight);
                let pixelIndex = 0;

                for (let y = 0; y < frameHeight; y++) {
                    const row = interlaced ? this.getInterlacedRow(y, frameHeight) : y;
                    for (let x = 0; x < frameWidth; x++) {
                        const colorIndex = imageData[pixelIndex++];
                        if (colorIndex !== transparentIndex && colorTable && colorTable[colorIndex]) {
                            const color = colorTable[colorIndex];
                            const idx = (row * frameWidth + x) * 4;
                            frameImageData.data[idx] = color[0];
                            frameImageData.data[idx + 1] = color[1];
                            frameImageData.data[idx + 2] = color[2];
                            frameImageData.data[idx + 3] = 255;
                        }
                    }
                }

                ctx.putImageData(frameImageData, frameLeft, frameTop);

                // Create an image from the current canvas state
                const frameCanvas = document.createElement('canvas');
                frameCanvas.width = width;
                frameCanvas.height = height;
                const frameCtx = frameCanvas.getContext('2d');
                frameCtx.drawImage(canvas, 0, 0);

                frames.push(frameCanvas);
                delays.push(delayTime);

                // Reset for next frame
                transparentIndex = -1;

            } else if (blockType === 0x3B) { // Trailer
                break;
            } else {
                // Unknown block, try to skip
                if (data[pos]) {
                    while (data[pos] !== 0 && pos < data.length) {
                        pos += data[pos] + 1;
                    }
                    pos++;
                }
            }
        }

        return { frames, delays, width, height };
    }

    /**
     * LZW decoder for GIF image data
     */
    decodeLZW(data, startPos, minCodeSize, pixelCount) {
        const clearCode = 1 << minCodeSize;
        const eofCode = clearCode + 1;

        let codeSize = minCodeSize + 1;
        let nextCode = eofCode + 1;
        let maxCode = 1 << codeSize;

        // Initialize code table
        const codeTable = [];
        for (let i = 0; i < clearCode; i++) {
            codeTable[i] = [i];
        }

        const output = [];
        let pos = startPos;
        let bitBuffer = 0;
        let bitCount = 0;
        let blockSize = data[pos++];
        let blockPos = 0;

        const readCode = () => {
            while (bitCount < codeSize) {
                if (blockPos >= blockSize) {
                    blockSize = data[pos++];
                    if (blockSize === 0) return -1;
                    blockPos = 0;
                }
                bitBuffer |= data[pos++] << bitCount;
                bitCount += 8;
                blockPos++;
            }
            const code = bitBuffer & ((1 << codeSize) - 1);
            bitBuffer >>= codeSize;
            bitCount -= codeSize;
            return code;
        };

        let prevCode = -1;

        while (output.length < pixelCount) {
            const code = readCode();
            if (code === -1 || code === eofCode) break;

            if (code === clearCode) {
                codeSize = minCodeSize + 1;
                maxCode = 1 << codeSize;
                nextCode = eofCode + 1;
                codeTable.length = clearCode;
                for (let i = 0; i < clearCode; i++) {
                    codeTable[i] = [i];
                }
                prevCode = -1;
                continue;
            }

            let entry;
            if (code < nextCode) {
                entry = codeTable[code];
            } else if (code === nextCode && prevCode >= 0) {
                entry = [...codeTable[prevCode], codeTable[prevCode][0]];
            } else {
                break; // Invalid code
            }

            if (entry) {
                output.push(...entry);

                if (prevCode >= 0 && nextCode < 4096) {
                    codeTable[nextCode++] = [...codeTable[prevCode], entry[0]];
                    if (nextCode >= maxCode && codeSize < 12) {
                        codeSize++;
                        maxCode = 1 << codeSize;
                    }
                }
            }

            prevCode = code;
        }

        return output;
    }

    /**
     * Get interlaced row index
     */
    getInterlacedRow(y, height) {
        const pass1 = Math.floor((height + 7) / 8);
        const pass2 = Math.floor((height + 3) / 8);
        const pass3 = Math.floor((height + 1) / 4);

        if (y < pass1) return y * 8;
        if (y < pass1 + pass2) return (y - pass1) * 8 + 4;
        if (y < pass1 + pass2 + pass3) return (y - pass1 - pass2) * 4 + 2;
        return (y - pass1 - pass2 - pass3) * 2 + 1;
    }
}

// Global instance
window.gifLoader = new GifLoader();
