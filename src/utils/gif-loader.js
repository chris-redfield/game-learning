/**
 * Animation Frame Loader - Extracts frames from animated GIFs and APNGs for canvas rendering
 * Mimics Python PIL's ImageSequence.Iterator behavior
 * Handles both GIF and APNG (Animated PNG) formats
 */

class GifLoader {
    constructor() {
        this.cache = new Map();
    }

    /**
     * Load an animated image and extract all frames as canvas-ready images
     * Supports both GIF and APNG formats
     */
    async loadGif(url) {
        // Check cache first
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }

        try {
            console.log(`Loading animation from: ${url}`);
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            const data = new Uint8Array(arrayBuffer);

            // Check file signature
            const signature = String.fromCharCode(...data.slice(0, 4));

            let result;

            if (signature === 'GIF8') {
                // It's a GIF file
                console.log('Detected GIF format');
                result = this.parseGif(data);
            } else if (data[0] === 0x89 && data[1] === 0x50 && data[2] === 0x4E && data[3] === 0x47) {
                // It's a PNG file - check if it's animated (APNG)
                console.log('Detected PNG format, checking for animation...');
                result = await this.parseApng(data, url);
            } else {
                // Try to load as image anyway
                console.log('Unknown format, attempting to load as image');
                result = await this.loadAsSingleFrame(url);
            }

            this.cache.set(url, result);
            return result;
        } catch (error) {
            console.error(`Error loading animation ${url}:`, error);
            return { frames: [], delays: [], width: 32, height: 24 };
        }
    }

    /**
     * Parse APNG (Animated PNG) file
     */
    async parseApng(data, url) {
        // Read PNG chunks
        const chunks = this.readPngChunks(data);

        // Find acTL chunk (animation control)
        const acTL = chunks.find(c => c.type === 'acTL');

        if (!acTL) {
            // Not animated, load as single frame
            console.log('No acTL chunk found, loading as single frame PNG');
            return await this.loadAsSingleFrame(url);
        }

        // Get animation info from acTL
        const numFrames = this.readUint32(acTL.data, 0);
        const numPlays = this.readUint32(acTL.data, 4);
        console.log(`APNG: ${numFrames} frames, ${numPlays} loops`);

        // Get image dimensions from IHDR
        const ihdr = chunks.find(c => c.type === 'IHDR');
        const width = this.readUint32(ihdr.data, 0);
        const height = this.readUint32(ihdr.data, 4);
        const bitDepth = ihdr.data[8];
        const colorType = ihdr.data[9];

        console.log(`APNG dimensions: ${width}x${height}, bitDepth: ${bitDepth}, colorType: ${colorType}`);

        // Get palette if present
        const plte = chunks.find(c => c.type === 'PLTE');
        let palette = null;
        if (plte) {
            palette = [];
            for (let i = 0; i < plte.data.length; i += 3) {
                palette.push([plte.data[i], plte.data[i + 1], plte.data[i + 2]]);
            }
        }

        // Get transparency info
        const trns = chunks.find(c => c.type === 'tRNS');
        let transparency = null;
        if (trns) {
            transparency = Array.from(trns.data);
        }

        // Collect frame control and data chunks
        const frameControls = [];
        const frameDataChunks = [];
        let currentFrameData = [];
        let idatData = [];

        for (const chunk of chunks) {
            if (chunk.type === 'fcTL') {
                // Frame control chunk
                const fc = {
                    sequenceNumber: this.readUint32(chunk.data, 0),
                    width: this.readUint32(chunk.data, 4),
                    height: this.readUint32(chunk.data, 8),
                    xOffset: this.readUint32(chunk.data, 12),
                    yOffset: this.readUint32(chunk.data, 16),
                    delayNum: this.readUint16(chunk.data, 20),
                    delayDen: this.readUint16(chunk.data, 22),
                    disposeOp: chunk.data[24],
                    blendOp: chunk.data[25]
                };
                frameControls.push(fc);

                // Save previous frame data
                if (currentFrameData.length > 0) {
                    frameDataChunks.push(this.concatArrays(currentFrameData));
                    currentFrameData = [];
                }
            } else if (chunk.type === 'IDAT') {
                idatData.push(chunk.data);
            } else if (chunk.type === 'fdAT') {
                // Frame data chunk (skip first 4 bytes - sequence number)
                currentFrameData.push(chunk.data.slice(4));
            }
        }

        // Don't forget the last frame data
        if (currentFrameData.length > 0) {
            frameDataChunks.push(this.concatArrays(currentFrameData));
        }

        // If IDAT data exists and first fcTL references the default image
        if (idatData.length > 0 && frameControls.length > 0) {
            const firstFc = frameControls[0];
            if (firstFc.xOffset === 0 && firstFc.yOffset === 0 &&
                firstFc.width === width && firstFc.height === height) {
                // First frame uses IDAT
                frameDataChunks.unshift(this.concatArrays(idatData));
            }
        }

        // Decompress and render each frame
        const frames = [];
        const delays = [];

        // Create a canvas for compositing
        const compositeCanvas = document.createElement('canvas');
        compositeCanvas.width = width;
        compositeCanvas.height = height;
        const compositeCtx = compositeCanvas.getContext('2d');

        for (let i = 0; i < Math.min(frameControls.length, frameDataChunks.length); i++) {
            const fc = frameControls[i];
            const compressedData = frameDataChunks[i];

            try {
                // Decompress the frame data
                const rawData = await this.inflateData(compressedData);

                // Create frame image data
                const frameCanvas = document.createElement('canvas');
                frameCanvas.width = fc.width;
                frameCanvas.height = fc.height;
                const frameCtx = frameCanvas.getContext('2d');
                const imageData = frameCtx.createImageData(fc.width, fc.height);

                // Decode PNG filter and convert to pixels
                this.decodePngData(rawData, imageData.data, fc.width, fc.height,
                    colorType, bitDepth, palette, transparency);

                frameCtx.putImageData(imageData, 0, 0);

                // Handle dispose operation for previous frame
                if (i > 0) {
                    const prevFc = frameControls[i - 1];
                    if (prevFc.disposeOp === 1) {
                        // APNG_DISPOSE_OP_BACKGROUND - clear previous frame region
                        compositeCtx.clearRect(prevFc.xOffset, prevFc.yOffset, prevFc.width, prevFc.height);
                    }
                    // disposeOp 2 (PREVIOUS) would restore to before previous frame - complex, skip for now
                }

                // Handle blend operation
                if (fc.blendOp === 0) {
                    // APNG_BLEND_OP_SOURCE - replace
                    compositeCtx.clearRect(fc.xOffset, fc.yOffset, fc.width, fc.height);
                }
                // blendOp 1 is OVER (alpha composite) which is default canvas behavior

                // Draw frame onto composite
                compositeCtx.drawImage(frameCanvas, fc.xOffset, fc.yOffset);

                // Create a copy of the current composite for this frame
                const resultCanvas = document.createElement('canvas');
                resultCanvas.width = width;
                resultCanvas.height = height;
                const resultCtx = resultCanvas.getContext('2d');
                resultCtx.drawImage(compositeCanvas, 0, 0);

                frames.push(resultCanvas);

                // Calculate delay in milliseconds
                let delayMs = 100; // Default
                if (fc.delayDen > 0) {
                    delayMs = (fc.delayNum / fc.delayDen) * 1000;
                } else if (fc.delayNum > 0) {
                    delayMs = fc.delayNum * 10; // Assume 100ths of a second
                }
                if (delayMs < 10) delayMs = 100; // Minimum delay
                delays.push(delayMs);

            } catch (err) {
                console.error(`Error decoding frame ${i}:`, err);
            }
        }

        console.log(`Parsed APNG: ${frames.length} frames, ${width}x${height}`);
        return { frames, delays, width, height };
    }

    /**
     * Read PNG chunks from data
     */
    readPngChunks(data) {
        const chunks = [];
        let pos = 8; // Skip PNG signature

        while (pos < data.length) {
            const length = this.readUint32(data, pos);
            const type = String.fromCharCode(data[pos + 4], data[pos + 5], data[pos + 6], data[pos + 7]);
            const chunkData = data.slice(pos + 8, pos + 8 + length);

            chunks.push({ type, data: chunkData, length });

            pos += 12 + length; // 4 (length) + 4 (type) + length + 4 (CRC)

            if (type === 'IEND') break;
        }

        return chunks;
    }

    /**
     * Inflate (decompress) zlib data using pako
     */
    async inflateData(compressedData) {
        // Use pako for reliable zlib decompression
        if (typeof pako !== 'undefined') {
            try {
                return pako.inflate(compressedData);
            } catch (e) {
                console.warn('pako.inflate failed, trying raw inflate:', e.message);
                try {
                    // Try raw inflate (without zlib header)
                    return pako.inflateRaw(compressedData);
                } catch (e2) {
                    console.error('pako.inflateRaw also failed:', e2.message);
                }
            }
        }

        // Fallback to DecompressionStream if pako not available
        if (typeof DecompressionStream !== 'undefined') {
            try {
                // Strip zlib header and trailer for deflate-raw
                let dataToDecompress = compressedData;
                if (compressedData[0] === 0x78) {
                    dataToDecompress = compressedData.slice(2, compressedData.length - 4);
                }

                const ds = new DecompressionStream('deflate-raw');
                const writer = ds.writable.getWriter();
                writer.write(dataToDecompress);
                writer.close();

                const reader = ds.readable.getReader();
                const chunks = [];

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    chunks.push(value);
                }

                return this.concatArrays(chunks);
            } catch (e) {
                console.error('DecompressionStream failed:', e.message);
            }
        }

        throw new Error('No decompression method available');
    }

    /**
     * Decode PNG filtered data to RGBA pixels
     */
    decodePngData(rawData, pixels, width, height, colorType, bitDepth, palette, transparency) {
        let bytesPerPixel;
        switch (colorType) {
            case 0: bytesPerPixel = 1; break; // Grayscale
            case 2: bytesPerPixel = 3; break; // RGB
            case 3: bytesPerPixel = 1; break; // Indexed
            case 4: bytesPerPixel = 2; break; // Grayscale + Alpha
            case 6: bytesPerPixel = 4; break; // RGBA
            default: bytesPerPixel = 4;
        }

        const scanlineLength = width * bytesPerPixel + 1; // +1 for filter byte
        let prevScanline = new Uint8Array(width * bytesPerPixel);

        for (let y = 0; y < height; y++) {
            const scanlineStart = y * scanlineLength;
            if (scanlineStart >= rawData.length) break;

            const filterType = rawData[scanlineStart];
            const scanline = new Uint8Array(width * bytesPerPixel);

            // Apply PNG filter
            for (let x = 0; x < width * bytesPerPixel; x++) {
                const raw = rawData[scanlineStart + 1 + x] || 0;
                const a = x >= bytesPerPixel ? scanline[x - bytesPerPixel] : 0;
                const b = prevScanline[x];
                const c = x >= bytesPerPixel ? prevScanline[x - bytesPerPixel] : 0;

                let value;
                switch (filterType) {
                    case 0: value = raw; break; // None
                    case 1: value = (raw + a) & 0xFF; break; // Sub
                    case 2: value = (raw + b) & 0xFF; break; // Up
                    case 3: value = (raw + Math.floor((a + b) / 2)) & 0xFF; break; // Average
                    case 4: value = (raw + this.paethPredictor(a, b, c)) & 0xFF; break; // Paeth
                    default: value = raw;
                }
                scanline[x] = value;
            }

            // Convert to RGBA
            for (let x = 0; x < width; x++) {
                const pixelIndex = (y * width + x) * 4;

                if (colorType === 3 && palette) {
                    // Indexed color
                    const colorIndex = scanline[x];
                    if (palette[colorIndex]) {
                        pixels[pixelIndex] = palette[colorIndex][0];
                        pixels[pixelIndex + 1] = palette[colorIndex][1];
                        pixels[pixelIndex + 2] = palette[colorIndex][2];
                        pixels[pixelIndex + 3] = transparency && transparency[colorIndex] !== undefined
                            ? transparency[colorIndex] : 255;
                    }
                } else if (colorType === 2) {
                    // RGB
                    const srcIndex = x * 3;
                    pixels[pixelIndex] = scanline[srcIndex];
                    pixels[pixelIndex + 1] = scanline[srcIndex + 1];
                    pixels[pixelIndex + 2] = scanline[srcIndex + 2];
                    pixels[pixelIndex + 3] = 255;
                } else if (colorType === 6) {
                    // RGBA
                    const srcIndex = x * 4;
                    pixels[pixelIndex] = scanline[srcIndex];
                    pixels[pixelIndex + 1] = scanline[srcIndex + 1];
                    pixels[pixelIndex + 2] = scanline[srcIndex + 2];
                    pixels[pixelIndex + 3] = scanline[srcIndex + 3];
                } else if (colorType === 0) {
                    // Grayscale
                    pixels[pixelIndex] = scanline[x];
                    pixels[pixelIndex + 1] = scanline[x];
                    pixels[pixelIndex + 2] = scanline[x];
                    pixels[pixelIndex + 3] = 255;
                } else if (colorType === 4) {
                    // Grayscale + Alpha
                    const srcIndex = x * 2;
                    pixels[pixelIndex] = scanline[srcIndex];
                    pixels[pixelIndex + 1] = scanline[srcIndex];
                    pixels[pixelIndex + 2] = scanline[srcIndex];
                    pixels[pixelIndex + 3] = scanline[srcIndex + 1];
                }
            }

            prevScanline = scanline;
        }
    }

    /**
     * Paeth predictor for PNG filtering
     */
    paethPredictor(a, b, c) {
        const p = a + b - c;
        const pa = Math.abs(p - a);
        const pb = Math.abs(p - b);
        const pc = Math.abs(p - c);
        if (pa <= pb && pa <= pc) return a;
        if (pb <= pc) return b;
        return c;
    }

    /**
     * Read unsigned 32-bit big-endian integer
     */
    readUint32(data, offset) {
        return (data[offset] << 24) | (data[offset + 1] << 16) |
               (data[offset + 2] << 8) | data[offset + 3];
    }

    /**
     * Read unsigned 16-bit big-endian integer
     */
    readUint16(data, offset) {
        return (data[offset] << 8) | data[offset + 1];
    }

    /**
     * Concatenate multiple Uint8Arrays
     */
    concatArrays(arrays) {
        const totalLength = arrays.reduce((sum, arr) => sum + arr.length, 0);
        const result = new Uint8Array(totalLength);
        let offset = 0;
        for (const arr of arrays) {
            result.set(arr, offset);
            offset += arr.length;
        }
        return result;
    }

    /**
     * Load an image file as a single frame (fallback)
     */
    async loadAsSingleFrame(url) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);

                resolve({
                    frames: [canvas],
                    delays: [100],
                    width: img.width,
                    height: img.height
                });
            };
            img.onerror = () => {
                resolve({ frames: [], delays: [], width: 0, height: 0 });
            };
            img.src = url;
        });
    }

    /**
     * Parse GIF binary data and extract frames
     */
    parseGif(data) {
        const frames = [];
        const delays = [];

        // GIF header check
        const header = String.fromCharCode(...data.slice(0, 6));
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

        console.log(`Parsed GIF: ${frames.length} frames, ${width}x${height}`);
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
