# Dynamic World Game

A 2D adventure game with procedural world generation and a classic RPG-inspired character progression system.

## Key Features

### Dynamic World System
* **Infinite World**: The world expands as the player explores by crossing area boundaries
* **Block Persistence**: Each block maintains its state (entity positions, etc.) when revisited
* **Safe Spawning**: When generating new blocks, a safe area is created around player entry points
* **Transition Effects**: Smooth fading transitions when moving between world blocks

<img src="assets/world-map-visualization.svg" alt="world" width="600"/>

### Entity System

#### Player Character
* Animated character with directional movement
* Sword combat with swing animation
* Collision detection with obstacles and enemies
* Level progression system:
  * **Level 1**: Basic movement and sword attack
  * **Level 2**: Dash ability (temporary speed boost)
  * **Level 3**: Extended sword reach
  * **Level 4**: Blink ability (short-range teleportation)

#### Enemies
* **Skeleton**: Basic enemy with idle and movement animations
* Simple AI that alternates between idle and random movement
* Collision detection with player and obstacles
* Health system with damage handling

#### Environment
* **Grass**: Environmental obstacle with collision detection
* Procedurally placed in each world block

### World Map
* Toggle-able overhead map view (press 'M')
* Displays all visited and known areas
* Color-coded to show:
  * Current location
  * Visited areas
  * Unexplored but known areas
* Includes player position marker
* Coordinate display for navigation

### Collision System
* Rectangle-based collision detection between entities
* Prevents movement through obstacles
* Handles entity interactions
* Debug mode to visualize collision boundaries (press 'C')

## Controls

* **Movement**: WASD or Arrow Keys
* **Attack**: SPACE (sword swing)
* **Dash**: SHIFT (Level 2+)
* **Blink**: B (Level 4+)
* **Level Up**: + (for testing)
* **Map Toggle**: M
* **Collision Boxes**: C (hold to display)

## Technical Details

* Built with Pygame
* Entity-based architecture for game objects
* Sprite-based rendering with animation support
* Procedural content generation for world blocks
* State management for persistent world data

## Getting Started

### Prerequisites
* Python 3.x
* Pygame library

### Installation
1. Clone the repository
2. Install requirements: `pip install pygame`
3. Run the game: `python main.py`
