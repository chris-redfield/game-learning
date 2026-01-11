/**
 * Inventory - Manages the player's collected items
 * Mirrors Python inventory.py
 */
class Inventory {
    constructor(maxSlots = 24) {
        this.maxSlots = maxSlots;
        this.items = [];  // List of items
        this.itemCounts = {};  // Dictionary to track quantities of stackable items
    }

    /**
     * Add an item to the inventory
     * @param {Object} item - The item object to add
     * @returns {boolean} True if successfully added, False if inventory is full
     */
    addItem(item) {
        // Check if inventory is full
        if (this.items.length >= this.maxSlots && !this.itemCounts[item.name]) {
            console.log(`Inventory full, cannot add ${item.name}`);
            return false;
        }

        // Check if the item is stackable and we already have one
        if (item.stackable && this.itemCounts[item.name]) {
            // Increase count for existing item
            this.itemCounts[item.name]++;
            console.log(`Added ${item.name} to stack (now have ${this.itemCounts[item.name]})`);
            return true;
        }

        // Add as new item
        this.items.push(item);
        // Initialize count for stackable items
        if (item.stackable) {
            this.itemCounts[item.name] = 1;
        }

        console.log(`Added ${item.name} to inventory (slot ${this.items.length - 1})`);
        return true;
    }

    /**
     * Remove an item from inventory by index
     * @param {number} itemIndex - Index of item to remove
     * @returns {Object|null} The removed item or null if index is invalid
     */
    removeItem(itemIndex) {
        if (itemIndex >= 0 && itemIndex < this.items.length) {
            const item = this.items[itemIndex];

            // Check if it's a stacked item
            if (item.stackable && this.itemCounts[item.name]) {
                if (this.itemCounts[item.name] > 1) {
                    // Reduce stack count
                    this.itemCounts[item.name]--;
                    console.log(`Removed one ${item.name} from stack (remaining: ${this.itemCounts[item.name]})`);
                    return item;
                } else {
                    // Remove last item from stack
                    delete this.itemCounts[item.name];
                }
            }

            // Remove item from inventory
            this.items.splice(itemIndex, 1);
            console.log(`Removed ${item.name} from inventory`);
            return item;
        }

        return null;
    }

    /**
     * Find the first item with the given name
     * @param {string} itemName - Name of the item to find
     * @returns {Object|null} The found item or null if not found
     */
    getItemByName(itemName) {
        for (const item of this.items) {
            if (item.name === itemName) {
                return item;
            }
        }
        return null;
    }

    /**
     * Get the count of a specific item
     * @param {string} itemName - Name of the item to count
     * @returns {number} The count of the item (0 if none found)
     */
    getItemCount(itemName) {
        return this.itemCounts[itemName] || 0;
    }

    /**
     * Get all items in the inventory
     * @returns {Array} List of all items
     */
    getAllItems() {
        return [...this.items];
    }

    /**
     * Get all items with their counts
     * @returns {Array} List of objects with item and count information
     */
    getItemsAndCounts() {
        const result = [];
        for (const item of this.items) {
            let count = 1;
            if (item.stackable && this.itemCounts[item.name]) {
                count = this.itemCounts[item.name];
            }

            result.push({
                item: item,
                count: count
            });
        }
        return result;
    }

    /**
     * Clear the entire inventory
     */
    clear() {
        this.items = [];
        this.itemCounts = {};
        console.log('Inventory cleared');
    }

    /**
     * Check if inventory is full
     * @returns {boolean}
     */
    isFull() {
        return this.items.length >= this.maxSlots;
    }

    /**
     * Get number of empty slots
     * @returns {number}
     */
    getEmptySlots() {
        return Math.max(0, this.maxSlots - this.items.length);
    }
}

// Export
window.Inventory = Inventory;
