# The Dark Garden of Z - Pygame to JavaScript Migration Plan

## Overview
This document tracks the migration of "The Dark Garden of Z" from Python/Pygame to JavaScript/HTML5 Canvas.

**Branch:** `claude/port-pygame-to-javascript-cUeug`
**Last Updated:** 2026-01-11

---

## Phase Status Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Core Engine | COMPLETED |
| 2 | Player | COMPLETED |
| 3 | World Generation | COMPLETED |
| 4 | Combat System | COMPLETED |
| 5 | Enemies | COMPLETED |
| 6 | Projectiles & Particles | COMPLETED |
| 7 | HUD | COMPLETED |
| 8 | Character Screen | COMPLETED |
| 9 | Skill Tree | COMPLETED |
| 10 | Inventory System | NOT STARTED |
| 11 | Items (Dragon Heart, Ancient Scroll) | NOT STARTED |
| 12 | NPCs & Dialog | NOT STARTED |
| 13 | Bonfire & Rest Menu | NOT STARTED |
| 14 | Save/Load System | NOT STARTED |

---

## Completed Phases (1-9)

### Phase 1: Core Engine - COMPLETED
- HTML5 Canvas setup (1280x720)
- Game loop with delta time
- Input handling (keyboard + gamepad)
- Asset loading system
- Transition effects (fade in/out)

**Key Files:**
- `web/src/engine/game.js` - Main game class
- `web/src/engine/input.js` - Input handler with keyboard/gamepad support
- `web/index.html` - HTML entry point
- `web/css/style.css` - Styling

### Phase 2: Player - COMPLETED
- Player movement with collision detection
- Sprite animation (4 directions)
- Sword swing attack
- Dash ability (SHIFT key)
- Blink teleport (B key)
- Player attributes system

**Key Files:**
- `web/src/entities/player.js` - Player, PlayerAttributes, Skill, SkillTree classes

### Phase 3: World Generation - COMPLETED
- Procedural block generation
- Grass/bush obstacles
- Rock obstacles
- Difficulty scaling based on distance from origin
- Block transition with safe spawn positioning

**Key Files:**
- `web/src/world/world.js` - World class
- `web/src/world/block.js` - Block class
- `web/src/world/grass.js` - Grass obstacle
- `web/src/world/rock.js` - Rock obstacle

### Phase 4: Combat System - COMPLETED
- Sword attack hitbox detection
- Damage calculation with STR scaling
- Knockback on hit
- Defense calculation with CON scaling
- Enemy health bars

### Phase 5: Enemies - COMPLETED
- Slime enemy with AI
- Skeleton enemy with AI
- Enemy leveling system
- Difficulty-based spawning
- Blood particles on death
- Soul drops with XP

**Key Files:**
- `web/src/entities/slime.js`
- `web/src/entities/skeleton.js`
- `web/src/entities/soul.js`

### Phase 6: Projectiles & Particles - COMPLETED
- Firebolt spell (F key)
- Particle system for effects
- Blood particles
- XP gain particles
- Stuck blood on ground

**Key Files:**
- `web/src/combat/projectile.js`
- `web/src/effects/particles.js`

### Phase 7: HUD - COMPLETED
- Health bar (red)
- Mana bar (blue)
- XP display
- Ability status (Dash/Blink ready)
- Controls list
- Current block info
- FPS counter

**Key Files:**
- `web/src/ui/hud.js`

### Phase 8: Character Screen - COMPLETED
- Full-screen overlay (ENTER key)
- Attributes tab with stat allocation
- Portrait display
- Resource bars (HP/MP)
- Navigation with mouse and keyboard
- ESC to close

**Key Files:**
- `web/src/ui/character-screen.js`

### Phase 9: Skill Tree - COMPLETED
- Three branches: Mind, Body, Magic Sword
- Proper tree structure with parent/child relationships
- Visual tree with connecting lines
- Skill unlock system with skill points
- Skills start locked (except Basic Sword)
- Skill points gained every 3 levels starting at level 4
- Click to select, Unlock button to unlock

**Skills Implemented:**
- Mind: Heal*, Firebolt, Bless*, Fireball*
- Body: Dash, Blink, Increased Dash Speed*, Reduced Dash Cooldown*, Extended Blink*, Extended Blink II*, Ghost Blink*
- Magic Sword: Basic Sword, Throw Sword*, Extended Sword, Extended Sword II*, Extended Sword III*, Teleport Sword*

(*) = Not yet implemented in gameplay

---

## Remaining Phases (10-14)

### Phase 10: Inventory System - NOT STARTED

**Description:** Add inventory tab to character screen for managing items.

**Tasks:**
1. Add third tab "INVENTORY" to character screen
2. Create inventory grid UI (matching Python)
3. Add item slot system
4. Implement item selection and info display
5. Add keyboard navigation for inventory

**Python Reference Files:**
- `character_screen.py` - `draw_inventory_tab()` method
- `entities/player/inventory.py`

**Notes:**
- Inventory should be a new tab alongside ATTRIBUTES and SKILLS
- Grid-based layout for item slots
- Item info panel when hovering/selecting

---

### Phase 11: Items (Dragon Heart, Ancient Scroll) - NOT STARTED

**Description:** Add special progression items that affect XP gain.

**Items to Implement:**

#### Ancient Scroll
- Reduces XP multiplier from 1.5 to 1.3
- Found in the world (specific location or random drop)
- Stored in inventory

#### Dragon Heart
- Reduces XP multiplier from 1.3 to 1.2 (or 1.5 to 1.2 if no scroll)
- Found in the world (specific location or random drop)
- Stored in inventory

**Tasks:**
1. Create Item base class
2. Create AncientScroll item class
3. Create DragonHeart item class
4. Add item pickup logic
5. Modify XP calculation to check for items
6. Add visual representation in world

**Python Reference Files:**
- `entities/player/attributes.py` - XP multiplier logic
- `entities/items/` directory

**Notes:**
- `foundAncientScroll` and `foundDragonHeart` flags already exist in PlayerAttributes
- XP table generation already checks these flags

---

### Phase 12: NPCs & Dialog - NOT STARTED

**Description:** Add NPC system with dialog balloons.

**Tasks:**
1. Create NPC base class
2. Create dialog balloon UI component
3. Add interaction system (E key near NPC)
4. Create test NPC (Link character)
5. Add dialog text system
6. Implement dialog progression (multiple lines)

**Python Reference Files:**
- `entities/npc/npc.py`
- `entities/npc/link_npc.py`
- `ui/dialog_balloon.py`

**Notes:**
- NPCs should be non-hostile entities
- Dialog appears in speech balloon above NPC
- E key to advance dialog
- NPCs can give hints, quests, or items
- DO NOT implement LLM-based dialog (keep it simple static text)

---

### Phase 13: Bonfire & Rest Menu - NOT STARTED

**Description:** Add bonfire rest points with menu system.

**Features:**
- Bonfire entity in world
- Rest menu when interacting (E key)
- Options: Rest (heal), Save Game, Return to Game
- Visual bonfire effect (animated flames)

**Tasks:**
1. Create Bonfire entity class
2. Add bonfire sprite/animation
3. Create BonfireMenu UI class
4. Implement rest/heal functionality
5. Integrate with save system
6. Add bonfire spawning in world

**Python Reference Files:**
- `entities/bonfire.py`
- `ui/bonfire_menu.py`

**Notes:**
- Bonfires should be rare (maybe 1 per few blocks)
- Resting restores HP and MP to full
- Menu should pause game like character screen

---

### Phase 14: Save/Load System - NOT STARTED

**Description:** Implement game state persistence using localStorage.

**Data to Save:**
- Player position (x, y, current block)
- Player attributes (level, XP, stats, stat points, skill points)
- Unlocked skills
- Inventory items
- Visited blocks (for map)
- Found items (Ancient Scroll, Dragon Heart flags)

**Tasks:**
1. Create SaveManager class
2. Implement save data serialization
3. Implement save to localStorage
4. Implement load from localStorage
5. Add save slot system (optional, at least 1 slot)
6. Add save confirmation UI
7. Add load game option on start
8. Auto-save at bonfires

**Python Reference Files:**
- `save_manager.py`

**Notes:**
- Use JSON format for save data
- localStorage key: `dark_garden_save_1`
- Validate save data on load
- Handle corrupted save gracefully

---

## Important Observations

### Code Structure
- JavaScript files use class-based structure mirroring Python
- All classes exported via `window.ClassName`
- Game state managed in `gameState` object in main.js
- Rendering uses HTML5 Canvas 2D context

### Key Differences from Python
1. **Async Asset Loading:** JavaScript requires async/await for loading images
2. **No Pygame Rect:** Custom rectangle collision using `_rectsOverlap()` helper
3. **Input Handling:** Combined keyboard + gamepad in InputHandler class
4. **Font Rendering:** Canvas `fillText()` vs Pygame `font.render()`

### Known Issues to Address
- None currently blocking

### Testing Notes
- Use `+` key to add XP for testing skill unlocks
- Press `C` for debug mode (currently disabled)
- Gamepad support tested with standard layout

---

## File Structure

```
web/
├── index.html
├── css/
│   └── style.css
├── assets/
│   ├── link-spritesheet.png
│   ├── slime-spritesheet.png
│   ├── skeleton-spritesheet.png
│   ├── grass-spritesheet.png
│   ├── rock-spritesheet.png
│   ├── soul.png
│   └── portrait-pixel-art.png
└── src/
    ├── main.js                    # Game entry point
    ├── engine/
    │   ├── game.js               # Core game class
    │   └── input.js              # Input handling
    ├── entities/
    │   ├── player.js             # Player, Attributes, SkillTree
    │   ├── slime.js              # Slime enemy
    │   ├── skeleton.js           # Skeleton enemy
    │   └── soul.js               # XP soul pickup
    ├── world/
    │   ├── world.js              # World generation
    │   ├── block.js              # Block container
    │   ├── grass.js              # Grass obstacle
    │   └── rock.js               # Rock obstacle
    ├── combat/
    │   └── projectile.js         # Firebolt projectile
    ├── effects/
    │   └── particles.js          # Particle system
    └── ui/
        ├── hud.js                # HUD display
        └── character-screen.js   # Character/Skill screen
```

---

## Next Session Priorities

1. **Phase 10: Inventory System** - Add inventory tab to character screen
2. **Phase 11: Items** - Add Dragon Heart and Ancient Scroll
3. **Phase 12: NPCs** - Add NPC system with test character
4. **Phase 13: Bonfire** - Add rest points
5. **Phase 14: Save/Load** - Implement persistence

---

## Commands Reference

### Development
```bash
# Start local server (from web/ directory)
python -m http.server 8000

# Or use any static file server
npx serve .
```

### Git
```bash
# Current branch
git checkout claude/port-pygame-to-javascript-cUeug

# Commit changes
git add -A && git commit -m "message"

# Push to remote
git push -u origin claude/port-pygame-to-javascript-cUeug
```

---

## Contact / Notes

This migration is being done by Claude (AI assistant) based on the original Python/Pygame implementation. The goal is a 1:1 feature port to JavaScript for web browser compatibility.

**Original Game:** The Dark Garden of Z (Python/Pygame)
**Target Platform:** Modern web browsers (Chrome, Firefox, Safari, Edge)
