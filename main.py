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
for _ in range(25):  # Create 25 grass patches
    x = random.randint(0, SCREEN_WIDTH - 32)
    y = random.randint(0, SCREEN_HEIGHT - 32)
    grass_patches.append(Grass(x, y))

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
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
        
    player.move(dx, dy)
    player.update()
    
    # Draw everything
    screen.fill(GREEN)  # Green background for grass
    
    # Draw grass patches
    for grass in grass_patches:
        grass.draw(screen)
    
    # Draw player
    player.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()