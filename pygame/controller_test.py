import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the display (needed for pygame to capture events)
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Controller Input Test")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Font setup
font = pygame.font.Font(None, 36)

# Initialize joysticks
pygame.joystick.init()
joysticks = []

# Function to get connected joysticks
def initialize_joysticks():
    global joysticks
    joysticks = []
    
    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    
    # Initialize each joystick
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Detected controller: {joystick.get_name()}")
        print(f"Number of axes: {joystick.get_numaxes()}")
        print(f"Number of buttons: {joystick.get_numbuttons()}")
        print(f"Number of hats: {joystick.get_numhats()}")

# Initialize connected joysticks
initialize_joysticks()

# Logs for storing events
button_log = []
axis_log = []
hat_log = []

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Controller connected or disconnected
        elif event.type == pygame.JOYDEVICEADDED:
            print("Controller connected!")
            initialize_joysticks()
        
        elif event.type == pygame.JOYDEVICEREMOVED:
            print("Controller disconnected!")
            initialize_joysticks()
        
        # Button events
        elif event.type == pygame.JOYBUTTONDOWN:
            log_entry = f"Button {event.button} pressed on controller {event.joy}"
            print(log_entry)
            button_log.append(log_entry)
            
        elif event.type == pygame.JOYBUTTONUP:
            log_entry = f"Button {event.button} released on controller {event.joy}"
            print(log_entry)
            button_log.append(log_entry)
        
        # Axis movement events
        elif event.type == pygame.JOYAXISMOTION:
            # Only log significant movements (beyond deadzone)
            if abs(event.value) > 0.2:
                log_entry = f"Axis {event.axis} moved to {event.value:.2f} on controller {event.joy}"
                print(log_entry)
                axis_log.append(log_entry)
        
        # Hat movement events (D-pad)
        elif event.type == pygame.JOYHATMOTION:
            log_entry = f"Hat {event.hat} moved to {event.value} on controller {event.joy}"
            print(log_entry)
            hat_log.append(log_entry)
        
        # Keyboard events (for quitting)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Clear the screen
    screen.fill(BLACK)
    
    # Render controller status
    y_pos = 20
    if len(joysticks) == 0:
        text = font.render("No controller detected. Please connect a controller.", True, WHITE)
        screen.blit(text, (20, y_pos))
    else:
        for i, joystick in enumerate(joysticks):
            text = font.render(f"Controller {i}: {joystick.get_name()}", True, WHITE)
            screen.blit(text, (20, y_pos))
            y_pos += 40
            
            # Show current button states
            button_text = "Buttons pressed: "
            any_pressed = False
            for b in range(joystick.get_numbuttons()):
                if joystick.get_button(b):
                    button_text += f"{b}, "
                    any_pressed = True
            
            if any_pressed:
                text = font.render(button_text[:-2], True, WHITE)
            else:
                text = font.render("No buttons pressed", True, WHITE)
            
            screen.blit(text, (40, y_pos))
            y_pos += 40
            
            # Show current axis values
            for a in range(joystick.get_numaxes()):
                value = joystick.get_axis(a)
                if abs(value) > 0.1:  # Only show non-zero axes
                    text = font.render(f"Axis {a}: {value:.2f}", True, WHITE)
                    screen.blit(text, (40, y_pos))
                    y_pos += 30
            
            # Show current hat values
            for h in range(joystick.get_numhats()):
                value = joystick.get_hat(h)
                if value != (0, 0):  # Only show non-zero hats
                    text = font.render(f"Hat {h}: {value}", True, WHITE)
                    screen.blit(text, (40, y_pos))
                    y_pos += 30
    
    # Display instructions
    y_pos += 20
    text = font.render("Press buttons on your controller to see their IDs", True, BLUE)
    screen.blit(text, (20, y_pos))
    y_pos += 30
    text = font.render("Press ESC to quit", True, BLUE)
    screen.blit(text, (20, y_pos))
    
    # Display recent logs (last 5 entries)
    y_pos += 40
    text = font.render("Recent Events:", True, WHITE)
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    # Combine all logs and show the most recent ones
    all_logs = button_log + axis_log + hat_log
    recent_logs = all_logs[-5:] if all_logs else ["No events logged yet"]
    
    for log in recent_logs:
        text = font.render(log, True, WHITE)
        screen.blit(text, (20, y_pos))
        y_pos += 25
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()