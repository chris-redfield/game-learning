import pygame
import sys
import math
import os
import datetime

from entities.player.player import Player
from world import World
from map import Map
from entities.enemy.enemy import Enemy
from entities.projectile.firebolt import Firebolt
from character_screen import CharacterScreen
from death_screen import DeathScreen
from hud import HUD
from dialog import Dialog, FileDialog
from dialog import SaveOverwriteDialog
from save_manager import SaveManager

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREEN, DESERT

# Set working directory to script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Initialize pygame
pygame.init()
font = pygame.font.SysFont(None, 24)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Dark Garden of Z")
clock = pygame.time.Clock()

# Initialize joysticks
pygame.joystick.init()
joysticks = []


def initialize_controllers():
    """Detect and initialize connected controllers"""
    global joysticks
    joysticks = []
    joystick_count = pygame.joystick.get_count()
    
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Detected controller: {joystick.get_name()}")

def check_entity_interaction(player):
    """Check if the player can interact with any entities they're near"""
    entities = game_world.get_current_entities()
    player_rect = player.get_rect()
    
    # First pass: check for direct collisions
    for entity in entities:
        if hasattr(entity, 'interact'):
            if player_rect.colliderect(entity.get_rect()):
                entity.interact(player)
                return True
    
    # Second pass: check for nearby interactive entities
    for entity in entities:
        if hasattr(entity, 'interact'):
            # Get center points
            player_center = player_rect.center
            entity_rect = entity.get_rect()
            entity_center = entity_rect.center
            
            # Calculate distance between centers
            distance = math.sqrt((player_center[0] - entity_center[0])**2 + 
                                (player_center[1] - entity_center[1])**2)
            
            # If within 50 pixels, consider it close enough to interact
            if distance < 50:
                entity.interact(player)
                return True
    
    return False

# Game state variables
player = None
game_world = None
initial_block = None
game_map = None
character_screen = None
game_hud = None
show_enemy_debug = False
projectiles = []

# Create death screen (only created once)
death_screen = DeathScreen()

# Save/Load system variables
save_manager = None
save_load_dialog = None
file_dialog = None
message_dialog = None
save_overwrite_dialog = None

# Transition effects
fade_alpha = 0
fading_in = False
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))
fade_duration = 500  # ms
fade_start_time = 0
transition_direction = None

# Game loop control
running = True
show_collision_boxes = False
transition_in_progress = False

def initialize_game():
    global player, game_world, initial_block, game_map, character_screen, game_hud
    global save_manager, save_load_dialog, file_dialog, message_dialog, save_overwrite_dialog

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    game_world = World()
    initial_block = game_world.generate_block(0, 0)
    set_bonfire_callback()
    game_world.place_special_items("ancient_scroll", [-4, 3])
    game_world.place_special_items("dragon_heart", [8,-9])

    game_map = Map(game_world)
    character_screen = CharacterScreen(player)
    game_hud = HUD(player)

    save_load_dialog = Dialog("Bonfire", ["Save Game", "Load Game", "Cancel"], on_save_load_option)
    file_dialog = FileDialog("Load Game", "Select a save file to load:")
    message_dialog = Dialog("Message", ["OK"], lambda _: message_dialog.hide())
    

    save_load_dialog.set_fonts()
    file_dialog.set_fonts()
    message_dialog.set_fonts()
    
    save_manager = SaveManager(game_world, player)
    save_overwrite_dialog = SaveOverwriteDialog(save_manager, on_save_overwrite)
    save_overwrite_dialog.set_fonts()

    initialize_controllers()

def on_save_overwrite(saved_path):
    show_message(f"Game saved to {os.path.basename(saved_path)}")

    if save_overwrite_dialog and save_overwrite_dialog.is_visible():
        save_overwrite_dialog.draw(screen)

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

# Save/Load system functions
def show_save_load_dialog():
    """Display the save/load dialog"""
    global save_load_dialog
    save_load_dialog.show()

def on_save_load_option(option_index):
    global save_load_dialog, save_manager, save_overwrite_dialog

    if option_index == 0:  # Save Game
        save_overwrite_dialog.files = save_overwrite_dialog.get_save_files() + ["<Create New Save>"]
        save_overwrite_dialog.options = save_overwrite_dialog.files
        save_overwrite_dialog.reset()
        save_overwrite_dialog.show()
    
    elif option_index == 1:  # Load Game
        show_load_dialog()

    save_load_dialog.hide()


def show_load_dialog():
    """Show the file selection dialog"""
    global file_dialog, save_manager
    
    # Get the save files
    save_dir = save_manager.save_directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    save_files = [f for f in os.listdir(save_dir) if f.endswith('.sav')]
    
    if not save_files:
        show_message("No save files found")
        return
    
    # Configure and show the dialog
    file_dialog.options = save_files
    file_dialog.file_callback = on_file_selected
    file_dialog.show()

def on_file_selected(file_index, files):
    """Handle save file selection"""
    global file_dialog, save_manager, death_screen
    
    file_dialog.hide()
    
    if file_index < 0 or file_index >= len(files):
        return
    
    # Load the selected file
    file_path = os.path.join(save_manager.save_directory, files[file_index])
    success = save_manager.load_game(file_path)
    
    if success:
        # Re-set the bonfire callback after loading the game
        set_bonfire_callback()
        # Deactivate the death screen if it's active
        if death_screen.is_active():
            death_screen.active = False
        show_message(f"Game loaded from {files[file_index]}")
    else:
        show_message("Failed to load game")

def show_message(message):
    """Show a message dialog"""
    global message_dialog
    
    message_dialog.title = "Message"
    message_dialog.options = [message, "OK"]
    message_dialog.show()

def set_bonfire_callback():
    """Set the save/load callback for the origin bonfire"""
    global game_world
    
    # Make sure we have the origin block (regardless of current player position)
    origin_block = game_world.get_or_generate_block(0, 0)
    
    # Find the bonfire entity
    bonfire_found = False
    for entity in origin_block.entities:
        if hasattr(entity, 'is_origin_bonfire') and entity.is_origin_bonfire():
            # Set the callback
            entity.save_load_callback = show_save_load_dialog
            print("DEBUG: Set save/load callback for origin bonfire")
            bonfire_found = True
            break
    
    if not bonfire_found:
        print("WARNING: Could not find origin bonfire to set callback")

# Initial game setup
initialize_game()

# Main game loop
while running:
    current_time = pygame.time.get_ticks()
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Check dialogs first (they have priority)
        if save_load_dialog and save_load_dialog.is_visible():
            if save_load_dialog.handle_event(event):
                continue
        
        if file_dialog and file_dialog.is_visible():
            if file_dialog.handle_event(event):
                continue
        
        if message_dialog and message_dialog.is_visible():
            if message_dialog.handle_event(event):
                continue

        if save_overwrite_dialog and save_overwrite_dialog.is_visible():
            if save_overwrite_dialog.handle_event(event):
                continue

        # Handle death screen events
        if death_screen.is_active():
            result = death_screen.handle_event(event)
            if result == "restart":
                restart_game()
                continue
            elif result == "load":
                # Show the load game dialog when "Load Save" is selected
                show_load_dialog()
                # Keep the death screen active until a game is successfully loaded
                continue
                
        # Handle keyboard inputs
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.start_swing()
            elif event.key == pygame.K_e:
                check_entity_interaction(player)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                player.gain_xp(50)
            elif event.key == pygame.K_m:
                if not character_screen.is_visible() and not death_screen.is_active():
                    game_map.toggle()
            elif event.key == pygame.K_RETURN:
                if not game_map.is_visible() and not death_screen.is_active():
                    character_screen.toggle()
            elif event.key == pygame.K_F3:
                show_enemy_debug = not show_enemy_debug
                print(f"Enemy debug info: {'ON' if show_enemy_debug else 'OFF'}")
            elif event.key == pygame.K_f:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                firebolt = Firebolt(
                    player,
                    player.particles
                )
                projectiles.append(firebolt)
        
        # Handle controller inputs
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 2:  # Attack
                player.start_swing()
            elif event.button == 0:  # Interact
                check_entity_interaction(player)
            elif event.button == 7:  # Character screen
                if not game_map.is_visible() and not death_screen.is_active():
                    character_screen.toggle()
            elif event.button == 6:  # Map toggle
                if not character_screen.is_visible() and not death_screen.is_active():
                    game_map.toggle()
            elif event.button == 1 and player.skill_tree.is_skill_unlocked("blink"):  # Blink
                obstacles = game_world.get_current_entities()
                player.blink(obstacles, current_time)
        
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

    # Skip gameplay updates if UI elements are active
    if (
        not transition_in_progress or not fading_in) and not game_map.is_visible() and not character_screen.is_visible() and not death_screen.is_active() and not save_load_dialog.is_visible() and not file_dialog.is_visible() and not message_dialog.is_visible() and not save_overwrite_dialog.is_visible():
        # Initialize movement variables
        dx, dy = 0, 0
        
        # Handle controller movement
        if joysticks and len(joysticks) > 0:
            joystick = joysticks[0]
            
            # Left stick for movement
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            
            # Add deadzone to prevent drift
            deadzone = 0.45
            
            # Only update movement and direction when outside deadzone
            if abs(x_axis) > deadzone:
                dx = x_axis * player.speed
                # Update horizontal facing
                if x_axis > 0:
                    player.facing = "right"
                else:
                    player.facing = "left"
            
            if abs(y_axis) > deadzone:
                dy = y_axis * player.speed
                # Only update vertical facing if horizontal movement isn't happening
                if abs(x_axis) <= deadzone:
                    if y_axis > 0:
                        player.facing = "down"
                    else:
                        player.facing = "up"
            
            # Dash ability (controller)
            if joystick.get_button(4) and player.skill_tree.is_skill_unlocked("dash"):
                player.dash(current_time)
        
        # Handle keyboard movement
        keys = pygame.key.get_pressed()
        
        # Only use keyboard if no controller movement
        if dx == 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = player.speed
        
        if dy == 0:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = player.speed
        
        # Dash ability (keyboard)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and player.skill_tree.is_skill_unlocked("dash"):
            player.dash(current_time)
            
        # Blink ability
        if keys[pygame.K_b] and player.skill_tree.is_skill_unlocked("blink"):
            obstacles = game_world.get_current_entities()
            player.blink(obstacles, current_time)
        
        # Debug visuals
        if keys[pygame.K_c]:
            show_collision_boxes = True
            # Enable sword hitbox visualization
            if hasattr(player, 'debug_sword_rect'):
                player.debug_sword_rect = True
            else:
                player.debug_sword_rect = True
            
            # Enable soul attraction radius visualization
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'collect'):
                    if hasattr(entity, 'debug_show_radius'):
                        entity.debug_show_radius = True
                    else:
                        entity.debug_show_radius = True
                        
            # Add this new code to enable skeleton detection radius visualization
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'show_detection_radius'):
                    entity.show_detection_radius = True

        else:
            show_collision_boxes = False
            if hasattr(player, 'debug_sword_rect'):
                player.debug_sword_rect = False
                
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'collect') and hasattr(entity, 'debug_show_radius'):
                    entity.debug_show_radius = False
                    
            # Add this new code to disable skeleton detection radius visualization
            for entity in game_world.get_current_entities():
                if hasattr(entity, 'show_detection_radius'):
                    entity.show_detection_radius = False
        
        # Get current entities from world
        current_entities = game_world.get_current_entities()

        # Move player
        player.move(dx, dy, current_entities)

        # Handle player-enemy collisions
        player_rect = player.get_rect()
        for entity in current_entities:
            if isinstance(entity, Enemy) and player_rect.colliderect(entity.get_rect()):
                entity.handle_player_collision(player)
                break

        # Update enemies
        for entity in current_entities:
            if isinstance(entity, Enemy):
                entity.update(player, current_entities)

        # Process enemy deaths and soul drops
        entities_to_remove = []
        souls_to_add = []

        for entity in current_entities:
            if isinstance(entity, Enemy) and hasattr(entity, 'should_remove') and entity.should_remove:
                entities_to_remove.append(entity)
                
                if hasattr(entity, 'will_drop_soul') and entity.will_drop_soul:
                    soul = entity.drop_soul()
                    if soul:
                        souls_to_add.append(soul)

        # Remove dead enemies
        for entity in entities_to_remove:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.remove_entity(entity)

        # Add souls to the world
        for soul in souls_to_add:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.add_entity(soul)

        # Update and collect souls
        souls_to_remove = []
        for entity in current_entities:
            if hasattr(entity, 'collect'):
                if entity.update(player):
                    souls_to_remove.append(entity)

        # Remove collected souls
        for entity in souls_to_remove:
            current_block = game_world.get_current_block()
            if current_block:
                current_block.remove_entity(entity)

        # Update other entities (like bonfire)
        for entity in current_entities:
            if (hasattr(entity, 'update') and 
                not isinstance(entity, Enemy) and 
                not hasattr(entity, 'collect')):
                entity.update()

        # Update player
        player.update(current_time, current_entities)
        
        for projectile in projectiles[:]:
            projectile.update(current_time, current_entities)
            if not projectile.alive:
                projectiles.remove(projectile)

        # Check sword collisions
        if player.swinging:
            player.check_sword_collisions(current_entities)
        
        # Check for block transitions
        if not transition_in_progress:
            block_changed, direction = game_world.check_player_block_transition(player)
            if block_changed:
                transition_direction = direction
                start_transition(direction)

    # Check for player death
    if player.attributes.current_health <= 0 and not death_screen.is_active():
        death_screen.activate()
    
    # Draw the game world
    if game_map.is_visible() and not death_screen.is_active():
        # Draw the map screen
        game_map.draw(screen)
    elif character_screen.is_visible() and not death_screen.is_active():
        # Draw the character screen with game background
        screen.fill(GREEN)
        
        # Draw entities and player
        for entity in game_world.get_current_entities():
            entity.draw(screen)
        player.draw(screen)
        
        for projectile in projectiles:
            projectile.draw(screen)

        # Draw character screen overlay
        character_screen.draw(screen)
    else:
        # Draw normal game screen
        screen.fill(GREEN)
        
        # Draw background blood splatters
        player.particles.draw_stuck_blood(screen)
        
        # Draw world entities
        for entity in game_world.get_current_entities():
            entity.draw(screen)

        # Draw player
        player.draw(screen)

        for projectile in projectiles:
            projectile.draw(screen)

        # Draw collision boxes for debugging
        if show_collision_boxes:
            for entity in game_world.get_current_entities():
                rect = entity.get_rect()
                pygame.draw.rect(screen, (255, 0, 0), rect, 1)
            
            player_rect = player.get_rect()
            pygame.draw.rect(screen, (0, 0, 255), player_rect, 1)
        
            for projectile in projectiles:
                projectile_rect = projectile.rect
                pygame.draw.rect(screen, (255, 165, 0), projectile_rect, 1)  # Orange color for projectiles

        # Draw HUD if not in death screen
        if not death_screen.is_active():
            game_hud.draw(
                surface=screen,
                game_world=game_world,
                fade_surface=fade_surface,
                fade_alpha=fade_alpha,
                transition_direction=transition_direction,
                transition_in_progress=transition_in_progress,
                entities=game_world.get_current_entities(),
                show_enemy_debug=show_enemy_debug
            )

        # Draw death screen if active
        if death_screen.is_active():
            death_screen.draw(screen, player)
    
    # Draw dialogs on top if visible
    if save_load_dialog and save_load_dialog.is_visible():
        save_load_dialog.draw(screen)

    if file_dialog and file_dialog.is_visible():
        file_dialog.draw(screen)

    if message_dialog and message_dialog.is_visible():
        message_dialog.draw(screen)

    if save_overwrite_dialog and save_overwrite_dialog.is_visible():
        save_overwrite_dialog.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()