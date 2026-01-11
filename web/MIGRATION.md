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
| 10 | Inventory System | COMPLETED |
| 11 | Items (Dragon Heart, Ancient Scroll, Health Potion) | COMPLETED |
| 12 | Bonfire & Rest Menu | COMPLETED |
| 13 | Save/Load System | COMPLETED |
| 14 | NPCs & Dialog | NOT STARTED |
| 15 | Death Logic | COMPLETED |

---

## Completed Phases (1-10)

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

### Phase 10: Inventory System - COMPLETED
- Inventory class with add/remove items and stackable item support
- Inventory grid (6x4) displayed on Attributes tab below portrait
- TAB key switches between stats and inventory sections
- Arrow key navigation within inventory grid
- E key / Space to use selected items
- Mouse hover and click support for inventory items
- Item tooltips on hover/selection
- Feedback messages when items can't be used

**Key Files:**
- `web/src/entities/inventory.js` - Inventory class
- `web/src/ui/character-screen.js` - Inventory grid UI

---

## Completed Phases (11-13)

### Phase 11: Items - COMPLETED
- Dragon Heart, Ancient Scroll, Health Potion items
- Item pickup with collision detection
- Bobbing animation effect
- Sprite loading from assets
- Special items placed at specific block coordinates

**Key Files:**
- `web/src/entities/items.js` - Item classes
- `web/src/world/world.js` - Item spawning

### Phase 12: Bonfire & Rest Menu - COMPLETED

**Description:** Bonfire rest points with menu system - exactly like Python implementation.

**Features Implemented:**
- Bonfire entity with animated flames (4-frame animation)
- Bonfire collision (player cannot walk through)
- Interact with E key when near bonfire
- Heals player to full HP and MP
- Origin bonfire shows Save/Load menu
- Debug collision box visible when C held

**Key Files:**
- `web/src/entities/bonfire.js` - Bonfire entity class
- `web/src/ui/bonfire-menu.js` - Dialog and menu classes

### Phase 13: Save/Load System - COMPLETED

**Description:** Game state persistence using localStorage - exactly like Python implementation.

**Features Implemented:**
- SaveLoadManager class for save/load operations
- Save game with file selection dialog
- Create new save with custom filename
- Overwrite existing saves
- Load game from file list
- Success/error message dialogs
- Saves player position, stats, skills, progression items

**Data Saved:**
- Player position (x, y, current block)
- Player attributes (level, XP, stats, stat/skill points)
- Unlocked skills
- Progression items (Ancient Scroll, Dragon Heart flags)

**Key Files:**
- `web/src/ui/bonfire-menu.js` - SaveLoadManager, dialogs

### Phase 15: Death Logic - COMPLETED

**Description:** Player death handling and respawn system - exactly like Python implementation.

**Features Implemented:**
- Death detection when player HP reaches 0
- "YOU DIED" death screen overlay with semi-transparent background
- Two options: Restart (reinitialize game) and Load Save
- Keyboard and mouse navigation for death screen options
- Restart functionality recreates world and player from scratch
- Load Save shows file dialog to load a previous save
- HUD hidden when death screen is active
- Death screen integrates with save/load system

**Key Files:**
- `web/src/ui/death-screen.js` - DeathScreen class
- `web/src/main.js` - Death detection, restartGame function

---

## Remaining Phase (14)

### Phase 14: NPCs & Dialog - NOT STARTED - exactly like it was implemented at the python code

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
- Hold `C` to show debug collision boxes (not a toggle)
- Press `E` near bonfire to interact and access save/load
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
│   ├── bonfire-sprites.png
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
    │   ├── soul.js               # XP soul pickup
    │   ├── bonfire.js            # Bonfire rest point
    │   ├── items.js              # Item classes
    │   └── inventory.js          # Inventory system
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
        ├── character-screen.js   # Character/Skill screen
        ├── bonfire-menu.js       # Save/Load dialogs
        └── death-screen.js       # Death overlay
```

---

## Next Session Priorities

1. **Phase 14: NPCs** - Add NPC system with test character - exactly like it was implemented at the python code

**Note:** Phase 15 (Death Logic) has been completed. Only Phase 14 remains.

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
