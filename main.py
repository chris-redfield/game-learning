import pygame
import sys
import random
from player import Player
from grass import Grass
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREEN

# Initialize pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

# Create player
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create grass patches randomly placed around the map
grass_patches = []
min_distance_between_grass = 64  # Minimum distance between grass patches
min_distance_from_player = 100   # Minimum distance from player start position

player_rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 35, 41)  # Player's initial position and size

def is_valid_position(x, y, existing_grass):
    """Check if a position is valid for a new grass patch"""
    new_rect = pygame.Rect(x, y, 32, 32)
    
    # Check if too close to player start position
    if new_rect.colliderect(player_rect) or pygame.math.Vector2(new_rect.center).distance_to(pygame.math.Vector2(player_rect.center)) < min_distance_from_player:
        return False
    
    # Check distance from other grass patches
    for grass in existing_grass:
        grass_rect = grass.get_rect()
        if new_rect.colliderect(grass_rect) or pygame.math.Vector2(new_rect.center).distance_to(pygame.math.Vector2(grass_rect.center)) < min_distance_between_grass:
            return False
    
    return True

# Attempt to place grass in valid positions
attempts = 0
while len(grass_patches) < 15 and attempts < 100:  # Reduced from 25 to 15 to avoid overcrowding
    x = random.randint(0, SCREEN_WIDTH - 32)
    y = random.randint(0, SCREEN_HEIGHT - 32)
    
    if is_valid_position(x, y, grass_patches):
        grass_patches.append(Grass(x, y))
    
    attempts += 1

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for space key press to trigger sword swing
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.start_swing()
                
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
    
    # Debug key for sprite testing
    if keys[pygame.K_p]:
        # Try different coordinates here to find the correct left-facing sprites
        x_pos = 2
        y_pos = 137  # Adjust this value to find the correct row
        player.load_specific_sprite(x_pos, y_pos)
    
    # Debug key to show collision boxes
    if keys[pygame.K_c]:
        show_collision_boxes = True
    else:
        show_collision_boxes = False
    
    # Process events
        
    player.move(dx, dy, grass_patches)
    player.update()
    
    # Draw everything
    screen.fill(GREEN)  # Green background for grass
    
    # Draw grass patches
    for grass in grass_patches:
        grass.draw(screen)
    
    # Draw player
    player.draw(screen)
    
    # Draw collision boxes for debugging if C key is pressed
    if show_collision_boxes:
        for grass in grass_patches:
            rect = grass.get_rect()
            pygame.draw.rect(screen, (255, 0, 0), rect, 1)
        
        player_rect = player.get_rect()
        pygame.draw.rect(screen, (0, 0, 255), player_rect, 1)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()