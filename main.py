import pygame
import sys

from entities.player import Player

from world import World
from map import Map
from entities.enemy import Enemy

from character_screen import CharacterScreen
from death_screen import DeathScreen

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREEN, DESERT
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Initialize pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic World Game")
clock = pygame.time.Clock()

# Create font for display
font = pygame.font.SysFont('Arial', 16)

# Game state variables
player = None
game_world = None
initial_block = None
game_map = None
character_screen = None

# Create death screen (only created once)
death_screen = DeathScreen()

# Transition effects
fade_alpha = 0
fading_in = False
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))
fade_duration = 500  # ms
fade_start_time = 0
transition_direction = None

# Game loop
running = True
show_collision_boxes = False
transition_in_progress = False

def initialize_game():
    """Initialize or reinitialize all game objects"""
    global player, game_world, initial_block, game_map, character_screen
    
    # Create player at the center of the screen
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # Create world
    game_world = World()
    
    # Generate the first block (at 0,0)
    initial_block = game_world.generate_block(0, 0)
    
    # Create map
    game_map = Map(game_world)
    
    # Create character screen
    character_screen = CharacterScreen(player)

def restart_game():
    """Restart the game by reinitializing everything"""
    initialize_game()
    print("Game restarted!")

def start_transition(direction):
    """Start a transition effect when moving between blocks"""
    global fading_in, fade_alpha, fade_start_time, transition_in_progress
    
    fading_in = True
    fade_alpha = 0
    fade_start_time = pygame.time.get_ticks()
    transition_in_progress = True

# Initial game setup
initialize_game()

while running:
    current_time = pygame.time.get_ticks()
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Check if death screen is active and handle its events first
        if death_screen.is_active():
            result = death_screen.handle_event(event)
            if result == "restart":
                restart_game()
                continue
        # Check for key presses
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.start_swing()
            # Level up when '+' key is pressed
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                player.level_up()
            # Toggle map when 'M' key is pressed
            elif event.key == pygame.K_m:
                # Only toggle map if character screen is not visible and death screen is not active
                if not character_screen.is_visible() and not death_screen.is_active():
                    map_visible = game_map.toggle()
                    print(f"DEBUG: Map toggled - visible: {map_visible}")
            # Toggle character screen when 'ENTER' key is pressed
            elif event.key == pygame.K_RETURN:
                # Only toggle character screen if map is not visible and death screen is not active
                if not game_map.is_visible() and not death_screen.is_active():
                    character_screen_visible = character_screen.toggle()
                    print(f"DEBUG: Character screen toggled - visible: {character_screen_visible}")
        
        # Handle character screen events
        if character_screen.is_visible():
            character_screen.handle_event(event)
    
    # Handle transition effect
    if transition_in_progress:
        elapsed = current_time - fade_start_time
        
        if fading_in:
            # Fade to black
            fade_alpha = min(255, int(255 * elapsed / fade_duration))
            
            if fade_alpha >= 255:
                # Transition complete, now fade out
                fading_in = False
                fade_start_time = current_time
        else:
            # Fade from black
            fade_alpha = max(0, 255 - int(255 * elapsed / fade_duration))
            
            if fade_alpha <= 0:
                # Transition fully complete
                transition_in_progress = False

    # Only process input if not transitioning, map is not visible, character screen is not visible, and death screen is not active
    if (not transition_in_progress or not fading_in) and not game_map.is_visible() and not character_screen.is_visible() and not death_screen.is_active():
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player.speed
        
        # Handle dash ability (Level 2)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and player.level >= 2:
            player.dash(current_time)
            
        # Handle blink ability (Level 4)
        if keys[pygame.K_b] and player.level >= 4:
            # Get current obstacles
            obstacles = game_world.get_current_entities()
            player.blink(obstacles, current_time)
        
        # Debug key for collision boxes and all debug visuals
        if keys[pygame.K_c]:
            show_collision_boxes = True
            # Enable sword hitbox visualization
            if hasattr(player, 'debug_sword_rect'):
                player.debug_sword_rect = True
            else:
                player.debug_sword_rect = True
            
            # Enable soul attraction radius visualization
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'collect'):  # Identify souls
                    if hasattr(entity, 'debug_show_radius'):
                        entity.debug_show_radius = True
                    else:
                        entity.debug_show_radius = True
        else:
            show_collision_boxes = False
            # Disable sword hitbox visualization
            if hasattr(player, 'debug_sword_rect'):
                player.debug_sword_rect = False
                
            # Disable soul attraction radius visualization
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'collect') and hasattr(entity, 'debug_show_radius'):
                    entity.debug_show_radius = False
        
        # Get current entities from world
        current_entities = game_world.get_current_entities()

        # Move player
        player.move(dx, dy, current_entities)

        # Additional check for player-initiated collisions
        player_rect = player.get_rect()
        for entity in current_entities:
            if isinstance(entity, Enemy) and player_rect.colliderect(entity.get_rect()):
                entity.handle_player_collision(player)
                break  # Only handle one collision per frame to prevent multiple damage

        # Update enemies
        for entity in current_entities:
            if isinstance(entity, Enemy):
                entity.update(player, current_entities)

        # Check for enemies that need to be removed and handle soul drops
        entities_to_remove = []
        souls_to_add = []

        for entity in current_entities:
            if isinstance(entity, Enemy) and hasattr(entity, 'should_remove') and entity.should_remove:
                entities_to_remove.append(entity)
                
                # Check if this enemy should drop a soul
                if hasattr(entity, 'will_drop_soul') and entity.will_drop_soul:
                    # Get the soul from the enemy and add it to the souls to add list
                    soul = entity.drop_soul()
                    if soul:
                        souls_to_add.append(soul)
                        print(f"Soul dropped at ({soul.x}, {soul.y})")

        # Remove dead enemies from current block
        for entity in entities_to_remove:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.remove_entity(entity)
                print(f"Removed dead {entity.__class__.__name__} from the world")

        # Add souls to the current block
        for soul in souls_to_add:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.add_entity(soul)
                print(f"Added soul to the world at ({soul.x}, {soul.y})")

        # Update souls and check for collection
        souls_to_remove = []
        for entity in current_entities:
            if hasattr(entity, 'collect'):  # Identify souls by their collect method
                # Update the soul and check if it was collected
                if entity.update(player):
                    # If collected, add to souls to remove list
                    souls_to_remove.append(entity)

        # Remove collected souls
        for entity in souls_to_remove:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.remove_entity(entity)
                print(f"Removed collected soul from the world")

        # Always update player with obstacles to prevent knockback collisions
        player.update(current_time, current_entities)
        
        # Check for sword collisions with enemies
        if player.swinging:
            player.check_sword_collisions(current_entities)
        
        # Check if player has changed blocks
        if not transition_in_progress:
            block_changed, direction = game_world.check_player_block_transition(player)
            if block_changed:
                transition_direction = direction
                start_transition(direction)
                print(f"DEBUG: Block transition triggered! Moving {direction}")
    
    # Check if player is dead
    if player.current_health <= 0 and not death_screen.is_active():
        death_screen.activate()
        print("Player died! Death screen activated.")
    
    # Draw everything
    if game_map.is_visible() and not death_screen.is_active():
        # Draw the map screen
        game_map.draw(screen)
    elif character_screen.is_visible() and not death_screen.is_active():
        # First draw the game behind the character screen
        screen.fill(GREEN)  # Green background for grass
        
        # Draw entities in current block
        for entity in game_world.get_current_entities():
            entity.draw(screen)
        
        # Draw player
        player.draw(screen)
        
        # Draw the character screen on top
        character_screen.draw(screen)
    else:
        # Draw normal game screen
        screen.fill(GREEN)  # Green background for grass
        
        # First draw stuck blood particles in the background
        player.draw_stuck_blood(screen)
        
        # Then draw entities in current block
        for entity in game_world.get_current_entities():
            entity.draw(screen)
        
        # Finally draw player and active particles
        player.draw(screen)
        
        # Draw collision boxes for debugging if C key is pressed
        if show_collision_boxes:
            for entity in game_world.get_current_entities():
                rect = entity.get_rect()
                pygame.draw.rect(screen, (255, 0, 0), rect, 1)
            
            player_rect = player.get_rect()
            pygame.draw.rect(screen, (0, 0, 255), player_rect, 1)
        
        # Only show game UI if death screen is not active
        if not death_screen.is_active():
            # Display world info
            block_info = game_world.get_block_description()
            block_text = font.render(f"Current: {block_info}", True, (255, 255, 255))
            screen.blit(block_text, (SCREEN_WIDTH - 150, 10))
            
            # Display control info
            controls_y = SCREEN_HEIGHT - 150  # Adjusted for removed control
            controls_text = [
                "Controls:",
                "WASD or Arrow Keys: Move",
                "SPACE: Swing Sword",
                "SHIFT: Dash (Level 2+)",
                "B: Blink (Level 4+)",
                "+: Level Up",
                "C: Show Collision Boxes",
                "M: Toggle Map",
                "ENTER: Character Screen"
            ]
            
            for i, text in enumerate(controls_text):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, controls_y + i * 15))
            
            # Display player level info
            player.render_level_info(screen, font, 10, 10)
            
            # Draw transition effect if in progress
            if transition_in_progress:
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))
                
                # Show transition text during fade
                if fade_alpha > 50:
                    if transition_direction:
                        direction_text = font.render(f"Moving {transition_direction.upper()}", True, (255, 255, 255))
                        text_rect = direction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                        screen.blit(direction_text, text_rect)

        # Draw death screen on top of everything if active
        if death_screen.is_active():
            death_screen.draw(screen, player.get_rect())
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()