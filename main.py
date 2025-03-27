import pygame
import sys

from entities.player import Player

from world import World
from map import Map
from entities.skeleton import Skeleton

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREEN
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

# Create player at the center of the screen
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create world
game_world = World()

# Generate the first block (at 0,0)
initial_block = game_world.generate_block(0, 0)

# Create map
game_map = Map(game_world)

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

def start_transition(direction):
    """Start a transition effect when moving between blocks"""
    global fading_in, fade_alpha, fade_start_time, transition_in_progress
    
    fading_in = True
    fade_alpha = 0
    fade_start_time = pygame.time.get_ticks()
    transition_in_progress = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for space key press to trigger sword swing
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.start_swing()
            # Level up when '+' key is pressed
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                player.level_up()
            # Toggle map when 'M' key is pressed
            elif event.key == pygame.K_m:
                map_visible = game_map.toggle()
                print(f"DEBUG: Map toggled - visible: {map_visible}")
                
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
    
    # Only process input if not transitioning and map is not visible
    if (not transition_in_progress or not fading_in) and not game_map.is_visible():
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
        
        # Debug key for collision boxes
        if keys[pygame.K_c]:
            show_collision_boxes = True
        else:
            show_collision_boxes = False
        
        # Get current entities from world
        current_entities = game_world.get_current_entities()
        
        # Update enemies
        for entity in current_entities:
            if isinstance(entity, Skeleton):
                entity.update(player)
        
        # Move player
        player.move(dx, dy, current_entities)
        player.update(current_time)
        
        # Check if player has changed blocks
        if not transition_in_progress:
            block_changed, direction = game_world.check_player_block_transition(player)
            if block_changed:
                transition_direction = direction
                start_transition(direction)
                print(f"DEBUG: Block transition triggered! Moving {direction}")
    
    # Draw everything
    if game_map.is_visible():
        # Draw the map screen
        game_map.draw(screen)
    else:
        # Draw normal game screen
        screen.fill(GREEN)  # Green background for grass
        
        # Draw entities in current block
        for entity in game_world.get_current_entities():
            entity.draw(screen)
        
        # Draw player
        player.draw(screen)
        
        # Draw collision boxes for debugging if C key is pressed
        if show_collision_boxes:
            for entity in game_world.get_current_entities():
                rect = entity.get_rect()
                pygame.draw.rect(screen, (255, 0, 0), rect, 1)
            
            player_rect = player.get_rect()
            pygame.draw.rect(screen, (0, 0, 255), player_rect, 1)
        
        # Display world info
        block_info = game_world.get_block_description()
        block_text = font.render(f"Current: {block_info}", True, (255, 255, 255))
        screen.blit(block_text, (SCREEN_WIDTH - 150, 10))
        
        # Display control info
        controls_y = SCREEN_HEIGHT - 120
        controls_text = [
            "Controls:",
            "WASD or Arrow Keys: Move",
            "SPACE: Swing Sword",
            "SHIFT: Dash (Level 2+)",
            "B: Blink (Level 4+)",
            "+: Level Up",
            "C: Show Collision Boxes",
            "M: Toggle Map"
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
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()