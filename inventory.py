import pygame
from typing import Dict, List, Optional, Type

class Inventory:
    """Manages the player's collected items"""
    
    def __init__(self, max_slots=24):
        self.max_slots = max_slots
        self.items = []  # List of items
        self.item_counts = {}  # Dictionary to track quantities of stackable items
    
    def add_item(self, item) -> bool:
        """
        Add an item to the inventory
        
        Args:
            item: The item object to add
            
        Returns:
            bool: True if successfully added, False if inventory is full
        """
        # Check if inventory is full
        if len(self.items) >= self.max_slots and item.name not in self.item_counts:
            print(f"Inventory full, cannot add {item.name}")
            return False
        
        # Check if the item is stackable and we already have one
        if hasattr(item, 'stackable') and item.stackable and item.name in self.item_counts:
            # Increase count for existing item
            self.item_counts[item.name] += 1
            print(f"Added {item.name} to stack (now have {self.item_counts[item.name]})")
            return True
        
        # Add as new item
        self.items.append(item)
        # Initialize count for stackable items
        if hasattr(item, 'stackable') and item.stackable:
            self.item_counts[item.name] = 1
        
        print(f"Added {item.name} to inventory (slot {len(self.items)-1})")
        return True
    
    def remove_item(self, item_index) -> Optional[object]:
        """
        Remove an item from inventory by index
        
        Args:
            item_index: Index of item to remove
            
        Returns:
            The removed item or None if index is invalid
        """
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            
            # Check if it's a stacked item
            if hasattr(item, 'stackable') and item.stackable and item.name in self.item_counts:
                if self.item_counts[item.name] > 1:
                    # Reduce stack count
                    self.item_counts[item.name] -= 1
                    print(f"Removed one {item.name} from stack (remaining: {self.item_counts[item.name]})")
                    return item
                else:
                    # Remove last item from stack
                    del self.item_counts[item.name]
            
            # Remove item from inventory
            self.items.pop(item_index)
            print(f"Removed {item.name} from inventory")
            return item
        
        return None
    
    def get_item_by_name(self, item_name) -> Optional[object]:
        """
        Find the first item with the given name
        
        Args:
            item_name: Name of the item to find
            
        Returns:
            The found item or None if not found
        """
        for item in self.items:
            if item.name == item_name:
                return item
        return None
    
    def get_item_count(self, item_name) -> int:
        """
        Get the count of a specific item
        
        Args:
            item_name: Name of the item to count
            
        Returns:
            int: The count of the item (0 if none found)
        """
        return self.item_counts.get(item_name, 0)
    
    def get_all_items(self) -> List:
        """
        Get all items in the inventory
        
        Returns:
            List of all items
        """
        return self.items.copy()
    
    def get_items_and_counts(self) -> List[Dict]:
        """
        Get all items with their counts
        
        Returns:
            List of dictionaries with item and count information
        """
        result = []
        for item in self.items:
            count = 1
            if hasattr(item, 'stackable') and item.stackable and item.name in self.item_counts:
                count = self.item_counts[item.name]
            
            result.append({
                'item': item,
                'count': count
            })
        
        return result
    
    def clear(self):
        """Clear the entire inventory"""
        self.items = []
        self.item_counts = {}
        print("Inventory cleared")
    
    def is_full(self) -> bool:
        """Check if inventory is full"""
        return len(self.items) >= self.max_slots
    
    def get_empty_slots(self) -> int:
        """Get number of empty slots"""
        return max(0, self.max_slots - len(self.items))