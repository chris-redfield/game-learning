
# Dynamic World Game

A 2D action-adventure game with procedural world generation, RPG-inspired character progression, and dynamic combat mechanics.

<img src="assets/game-screenshot.png" alt="Screenshot" width="600"/>

## Key Features

### Player System
- **Attribute System**: Level up to increase STR, CON, DEX, and INT stats that affect combat and movement
- **Ability Progression**:
  - **Level 1**: Basic movement and sword attack
  - **Level 2**: Dash ability (temporary speed boost)
  - **Level 3**: Extended sword reach
  - **Level 4**: Blink ability (short-range teleportation)
- **Character Screen**: View and upgrade character attributes
- **Inventory System**: Collect and use items throughout your adventure
- **Particle Effects**: Blood splatters and visual feedback enhance combat immersion
<br>

### Experience System
- **Progressive Difficulty**: XP requirements scale exponentially, creating natural progression barriers
- **Dynamic XP Tables**: Find special items to modify XP scaling:
  - **Ancient Scroll**: Reduces XP scaling from 1.5x to 1.3x
  - **Dragon Heart**: Further reduces scaling to 1.2x, enabling higher level progression
- **Soul Collection**: Defeat enemies to collect souls that provide XP
<br>

### Enemy System
- **Attribute-Based Enemies**: Enemies with their own STR, CON, DEX, and INT attributes
- **Enemy Types**: Different enemy behaviors and statistics:
  - **Normal**: Balanced attributes
  - **Fast**: High DEX, quick movement
  - **Brute**: High STR, powerful attacks
  - **Magic**: INT-based abilities (when implemented)
- **Difficulty Scaling**: Enemies become progressively harder based on distance from origin
- **AI Behaviors**: Enemies with randomized movement, detection radii, and attack patterns
- **Visual Feedback**: Hit animations, knockback effects, and death particles
<br>

### World System
- **Infinite Procedural Generation**: The world expands as you explore by crossing area boundaries
- **Block Persistence**: Each block maintains its state (entities, items, etc.) when revisited
- **Safe Spawning**: Areas around entry points are cleared of dangerous obstacles
- **Difficulty Progression**: Areas further from origin have tougher enemies
- **Transition Effects**: Smooth fading transitions when moving between world blocks
- **Environment Objects**: Grass, bonfires, and other interactive elements

<img src="assets/world-map-visualization.svg" alt="world" width="600"/>
<br>

### Combat System
- **Directional Attacks**: Sword swings with actual hitboxes
- **Knockback Physics**: Enemies and player react physically to attacks
- **Damage Calculation**: Based on attacker's strength and defender's constitution
- **Recovery System**: Enemies temporarily recover after taking damage
- **Invulnerability Frames**: Brief invulnerability after taking damage
- **Special Abilities**: Dash and blink abilities to enhance combat options
<br>

### Collision System
- **Rectangle-based Collision**: Precise collision detection between entities
- **Layered Collisions**: Player-enemy, player-item, weapon-enemy and environmental collisions
- **Knockback Physics**: Push effects from collisions with damage
- **Debug Visualization**: Optional rendering of collision boundaries and detection radii
<br>

### Visual Systems
- **Sprite-based Animation**: Character and enemy animations for different states
- **Particle Effects**: Blood splatter, death particles, XP collection effects
- **Map Visualization**: Toggle-able overhead map showing explored and unexplored areas
- **HUD Elements**: Health/mana bars, level display, ability status indicators
- **Debug Overlays**: Optional display of enemy stats, collision boxes, and detection radii
<br>

### Build System
- **Cross-platform Building**: Easily build executables for Windows, macOS, and Linux
- **Asset Management**: Proper handling of game resources during build
- **One-command Building**: Simple script to package the game for distribution
<br>

## Controls

- **Movement**: WASD or Arrow Keys
- **Attack**: SPACE
- **Interact**: E
- **Dash**: SHIFT (Level 2+)
- **Blink**: B (Level 4+)
- **Character Screen**: ENTER
- **Map Toggle**: M
- **Debug Collision Boxes**: C (hold to display)
- **Enemy Debug Info**: F3
<br>

## Technical Details

- **Built with Pygame**: Using Python's popular game development library
- **Entity-Component Architecture**: Modular code organization
- **State Management**: For persistent world and entity states
- **Procedural Generation**: For world blocks and enemy placement
- **Event-Driven Input Handling**: For keyboard, mouse, and controller input
- **Controller Support**: Play with gamepad or keyboard
<br>

## Getting Started

### Prerequisites
* Python 3.x
* Dependencies: pygame, pillow, pyinstaller (for game build)
<br>

### Installation
1. Clone the repository
```console
git clone https://github.com/yourusername/DynamicWorldGame.git
cd DynamicWorldGame
```
<br>

2. Install requirements
```console
pip install -r requirements.txt
```
<br>

3. Run the game
```console
python main.py
```
<br>

### Building Executables
To build a standalone executable for your platform:
```console
python build.py
```
This will create an executable in the `dist` directory.

## Development Roadmap

- [ ] Additional enemy types
- [ ] Save/load functionality
- [ ] More world environment variety
- [ ] Skill Tree
- [ ] Boss encounters
- [ ] Quest system
- [ ] Equipment and weapon system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.