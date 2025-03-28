import pygame
import random
import math
from PIL import Image, ImageSequence
from entities.enemy import Enemy

class Slime(Enemy):
    def __init__(self, x, y):
        # Define slime-specific dimensions
        width = 32
        height = 24
        
        # Call parent constructor with SLOWER speed (skeletons use 1.0)
        super().__init__(x, y, width, height, speed=0.5)
        
        # Slime-specific properties
        self.health = 5  # Slimes have less health than skeletons
        self.attack_power = 1
        self.defense = 0  # Slimes have no defense
        
        # SLOWER animation speed (reduced from the default 0.1)
        self.animation_speed = 0.03  # Half the default animation speed
        
        # Load slime sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load slime sprites from GIF files"""
        self.sprites = {
            'idle': [],
            'moving': []
        }
        
        try:
            # Load idle animation from GIF
            self.load_animation_from_gif('assets/slime_idle.gif', 'idle')
            
            # Load moving animation from GIF
            self.load_animation_from_gif('assets/slime_move.gif', 'moving')
                
        except Exception as e:
            print(f"Error loading slime sprites: {e}")
            # Create colored rectangle placeholders
            for _ in range(4):
                idle_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                idle_placeholder.fill((0, 200, 0))  # Green for slime
                self.sprites['idle'].append(idle_placeholder)
            
            for _ in range(6):
                move_placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                move_placeholder.fill((0, 180, 0))  # Slightly darker green
                self.sprites['moving'].append(move_placeholder)
    
    def load_animation_from_gif(self, gif_path, animation_key):
        """Load frames from a GIF file and add them to sprites dictionary"""
        try:
            # Open the GIF file using PIL
            gif = Image.open(gif_path)
            
            # Process each frame in the GIF
            frames = []
            for frame in ImageSequence.Iterator(gif):
                # Convert PIL image to pygame surface
                frame_rgba = frame.convert("RGBA")
                frame_data = frame_rgba.tobytes()
                size = frame_rgba.size
                mode = frame_rgba.mode
                
                # Create pygame surface from the frame data
                py_frame = pygame.image.fromstring(frame_data, size, mode)
                
                # Scale the frame to match the slime's dimensions
                scaled_frame = pygame.transform.scale(py_frame, (self.width, self.height))
                frames.append(scaled_frame)
            
            # Add the frames to the sprites dictionary
            self.sprites[animation_key] = frames
            
        except Exception as e:
            print(f"Error loading animation from {gif_path}: {e}")
            raise
    
    def get_animation_frames(self):
        """Get animation frames based on state - stick to simplest approach"""
        if self.state == "moving" and len(self.sprites["moving"]) > 0:
            return self.sprites["moving"]
        elif self.state == "idle" and len(self.sprites["idle"]) > 0:
            return self.sprites["idle"]
        
        # Fallback to any available animation
        for key in self.sprites:
            if len(self.sprites[key]) > 0:
                return self.sprites[key]
        
        # Default to empty list if no suitable animation found
        return []
    
    def handle_player_collision(self, player):
        """Slimes attack on contact but don't stop moving"""
        # Don't call super() here as it would stop movement
        
        # Attack the player but keep moving
        # Pass position for knockback calculation
        enemy_center_x = self.x + (self.width / 2)
        enemy_center_y = self.y + (self.height / 2)
        player.take_damage(self.attack_power, enemy_center_x, enemy_center_y)
    
    def update(self, player=None, obstacles=None):
        """Override update method to properly handle death state for slimes"""
        # If in dying state, update death animation
        if self.state == "dying":
            self.death_timer += 16.67  # Approximate milliseconds per frame at 60 FPS
            
            # Update death particles
            if hasattr(self, 'death_particles') and self.death_particles:
                self.update_death_particles()
            
            # Check if it's time to remove the entity
            if self.death_timer >= self.death_duration:
                self.should_remove = True
                
                # If we should drop a soul, prepare it
                if not hasattr(self, 'will_drop_soul'):
                    self.will_drop_soul = True
            
            return  # Skip regular updates when dying
        
        # Call the parent update method for regular behavior
        super().update(player, obstacles)
    
    def die(self):
        """Override die method to ensure proper death animation for slimes"""
        # Set dying state
        self.state = "dying"
        self.animation_counter = 0
        
        # Force creation of death particles 
        self.create_death_particles()
        
        # Set a timer for removing the entity
        self.death_timer = 0
        self.death_duration = 500  # ms before removing entity
        self.should_remove = False  # Will be set to True when death animation completes
        
        # Prepare to drop a soul
        self.will_drop_soul = True
        
        print(f"Slime is dying!")
    
    def create_death_particles(self):
        """Create particles for slime death animation - with green tint"""
        self.death_particles = []
        
        # Create more particles for slimes
        particle_count = random.randint(20, 25)
        
        # Enemy center coordinates
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        for _ in range(particle_count):
            # Random angle for 360-degree spread
            angle = random.uniform(0, 2 * math.pi)
            
            # Direction vector from angle
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            # Random distance from center
            distance = random.uniform(0, self.width / 2)
            
            # Starting position with some randomness
            start_x = center_x + dir_x * distance
            start_y = center_y + dir_y * distance
            
            # Random size
            size = random.randint(4, 10)
            
            # Greenish colors for slime particles
            green = random.randint(150, 250)
            red = random.randint(30, 100)
            blue = random.randint(30, 100)
            color = (red, green, blue)
            
            # Create particle with higher velocity for slimes
            self.death_particles.append({
                'x': start_x,
                'y': start_y,
                'vel_x': dir_x * random.uniform(0.8, 2.5),
                'vel_y': dir_y * random.uniform(0.8, 2.5),
                'size': size,
                'color': color,
                'life': random.randint(15, 30),
                'max_life': 30
            })
    
    def draw(self, surface):
        """Override draw method to handle death animation properly for slimes"""
        # If dying, only draw death particles
        if self.state == "dying":
            self.draw_death_particles(surface)
            return
        
        # Regular drawing code for non-dying states
        animation_frames = self.get_animation_frames()
        
        if len(animation_frames) > 0 and self.frame < len(animation_frames):
            sprite = animation_frames[self.frame]
            
            # Handle hit animation for slimes (flashing instead of tinting)
            if self.hit:
                # Only draw the slime on even frames during hit animation
                if (self.hit_timer // 40) % 2 == 0:
                    surface.blit(sprite, (self.x, self.y))
            else:
                # Normal drawing (no hit effect)
                surface.blit(sprite, (self.x, self.y))
            
            # Draw blood particles
            if hasattr(self, 'blood_particles'):
                for particle in self.blood_particles:
                    if particle:  # Make sure particle is not None
                        particle.draw(surface)