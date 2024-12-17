import pygame
import random
import os
import shutil
import sys
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import time
from automata import Automata
from difficulty import MAX_LEVEL, get_params_from_difficulty
from json_stuff import update_json, read_json
from colors import get_color_map
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

pygame.init()

# Sizes and dimensions
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Climbing Game")

PLAYER_RADIUS = 24
ICON_RADIUS = 18
HOLD_RADIUS = 32

# Load images
player_image = pygame.image.load("images/player_image.png")
player_image = pygame.transform.scale(player_image, (PLAYER_RADIUS * 2, PLAYER_RADIUS * 2))

icon_image = pygame.image.load("images/icon_image.png")
icon_image = pygame.transform.scale(icon_image, (ICON_RADIUS * 2, ICON_RADIUS * 2))

background_image = pygame.image.load("images/background_image.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Scale for death and erosion chances
scale = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)

COLORS = [RED, GREEN, BLUE]

def die():
    # Delete the entire game from your computer
    # print("GET FUCKED LMAOOOOOOO")
    current_dir = os.getcwd()

    try:
        shutil.rmtree(current_dir)
    except Exception as e:
        # print(f"WINDOWS OS DEBUG THINGY ARGHHHHHHHH: {e}")
        print(f"Encountered an error while dying. Lucky you.", file=sys.stderr)

    sys.exit(1)

def generate_holds(NUM_HOLDS, HOLD_RADIUS, WIDTH):
    holds = []
    previous_x = WIDTH // 2  # Start in screen middle
    x_variation = 100  
    for i in range(NUM_HOLDS):
        x = previous_x + random.randint(-x_variation, x_variation)
        # Keep x in screen boundaries
        x = max(HOLD_RADIUS, min(WIDTH - HOLD_RADIUS, x))
        color = random.choice(COLORS)
        holds.append((x, color))
        previous_x = x
    return holds

# Function for menu screen
def menu_screen(max_level_achieved, eroded_levels=[]):
    font = pygame.font.Font(None, 50)
    menu_running = True
    level_rects = []
    scroll_offset = 0  # Offset for scrolling
    viewport_height = 400  # Height of the visible area
    line_height = 50  # Height of each level entry (including spacing)

    while menu_running:
        screen.fill(WHITE)

        # Render title
        levels_text = "Select Level (1-{}):".format(max_level_achieved)
        levels_rendered = font.render(levels_text, True, BLACK)
        screen.blit(levels_rendered, (100, 50))

        # Create clipping area for scrolling list
        clip_rect = pygame.Rect(100, 150, 300, viewport_height)  # x, y, width, height
        pygame.draw.rect(screen, WHITE, clip_rect)
        pygame.draw.rect(screen, BLACK, clip_rect, 2)

        # Start rendering levels within clipping area
        level_rects.clear()
        start_y = 150 - scroll_offset
        for i in range(1, max_level_achieved + 1):
            y_position = start_y + (i - 1) * line_height
            if y_position < 150 or y_position > 150 + viewport_height - line_height:
                continue  # Skip rendering levels if they go off screen
            
            # Determine color based on erosion status
            level_color = RED if i in eroded_levels else BLACK
            level_text = "\tLevel {}".format(i)
            level_rendered = font.render(level_text, True, level_color)
            level_rect = level_rendered.get_rect(topleft=(clip_rect.left, y_position))
            level_rects.append((i, level_rect))
            screen.blit(level_rendered, level_rect.topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mouse_pos = event.pos
                    for level, rect in level_rects:
                        if rect.collidepoint(mouse_pos) and level not in eroded_levels:
                            menu_running = False
                            return level
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * line_height
                # Clamp scroll offset to valid range
                scroll_offset = max(0, min(scroll_offset, (max_level_achieved * line_height) - viewport_height))

def game_screen(difficulty):
    random.seed(difficulty)     # Keep seed constant so that levels are always the same
    np.random.seed(difficulty)

    # Make an automata to show, if user succeeds
    automata = Automata(n=max(64, difficulty*2), beauty_factor=difficulty/MAX_LEVEL)

    # Get level-specific parameters
    NUM_HOLDS, icon_direction, erosion_chance, death_chance = get_params_from_difficulty(difficulty)
    print(f"Holds: {NUM_HOLDS}, speed: {icon_direction}, erosion: {erosion_chance} death: {death_chance}")
    player_pos = 0
    icon_x = 0
    holds = generate_holds(NUM_HOLDS, HOLD_RADIUS, WIDTH)

    # Camera view
    top_index = 4
    bottom_index = 0
    visible_y_positions = [int(i * ((HEIGHT) / (top_index + 1)) - HOLD_RADIUS) for i in range(top_index + 2)]
    visible_y_positions = visible_y_positions[::-1]

    running = True 
    clock = pygame.time.Clock()
    finished = False 
    completed = False

    while running:
        screen.blit(background_image, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not finished:
                    # Check if the icon is over the next hold
                    next_hold_x, color = holds[player_pos + 1] if player_pos < len(holds) - 1 else (None, None)
                    if next_hold_x is not None and abs(icon_x - next_hold_x) <= HOLD_RADIUS:
                        # Move to the next hold
                        if player_pos < len(holds) - 1:
                            player_pos += 1
                    else:
                        # Re-seed to make death chance non-level dependent
                        random.seed(time.time()) 
                        # Die lol
                        if random.randint(0, 100) < death_chance * scale:
                            die()
                        # Slipping logic
                        if player_pos > 0:
                            player_pos -= 1

        # Update camera indices
        top_index = min(player_pos + 3, len(holds) - 1)
        bottom_index = max(player_pos - 1, 0)

        # Check end of route
        if player_pos == len(holds) - 1 and not finished:
            finished = True
            completed = True
            screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.wait(100) # Take a beat before playing the animation
            running = False

        # Update icon position
        if not finished:
            icon_x += icon_direction
            if icon_x <= 0 or icon_x >= WIDTH:
                icon_direction *= -1

        # Draw visible holds
        if not finished:
            visible_holds = holds[bottom_index:top_index + 1]
            for i, (hold_x, color) in enumerate(visible_holds):
                hold_y = visible_y_positions[i] 
                pygame.draw.circle(screen, color, (hold_x, hold_y), HOLD_RADIUS)

        # Draw player
        if not finished:
            player_x, _ = holds[player_pos]
            player_y = visible_y_positions[player_pos - bottom_index]
            player_rect = player_image.get_rect(center=(player_x, player_y))
            screen.blit(player_image, player_rect.topleft)

        # Draw moving icon
        if not finished:
            icon_y = (
                visible_y_positions[player_pos + 1 - bottom_index]
                if player_pos < len(holds) - 1
                else visible_y_positions[player_pos - bottom_index]
            )
            icon_rect = icon_image.get_rect(center=(icon_x, icon_y))
            screen.blit(icon_image, icon_rect.topleft)

        # Update display
        if not finished:
            pygame.display.flip()
        clock.tick(30)

    random.seed(difficulty) # Reseed with difficulty

    if finished:
        reward_screen(automata, num_frames=100 + (difficulty * 2), frame_rate=1<<12)

    eroded = False
    if completed:
        # Randomly erode some levels upon completion
        if random.randint(0, 100) < erosion_chance * scale:
            # print("EROSION CHANCE SUCCESS DEBUG THINGY", erosion_chance * scale, difficulty)
            eroded = True

    return completed, eroded

def reward_screen(automata, num_frames=20, frame_rate=10):
    fig, ax = plt.subplots(figsize=(5, 5))
    clock = pygame.time.Clock()

    cmap = get_color_map()

    for _ in range(num_frames):
        # Get a new grid
        array = automata.generate_frame()

        ax.clear()
        ax.imshow(array, cmap=cmap)  
        ax.axis('off') 
        
        ax.axhline(0, color='white', linestyle='--')
        ax.axvline(0, color='white', linestyle='--')
        ax.axhline(array.shape[0] - 1, color='white', linestyle='--')
        ax.axvline(array.shape[1] - 1, color='white', linestyle='--')

        canvas = FigureCanvas(fig)

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)

        # Load grid to Pygame
        image = pygame.image.load(buf, "image.png")
        buf.close()

        # Scale grid
        scaled_image = pygame.transform.scale(image, (screen.get_width(), screen.get_height()))

        # Display
        screen.fill((0, 0, 0)) 
        screen.blit(scaled_image, (0, 0))
        pygame.display.flip()
        clock.tick(frame_rate)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

def main():
    # Get level info
    max_level_achieved, eroded_levels = read_json()
    while True:
        difficulty = menu_screen(max_level_achieved, eroded_levels)
        completed, eroded = game_screen(difficulty)
        # Unlock next level upon completion
        if completed and max_level_achieved < MAX_LEVEL and difficulty == max_level_achieved:
            max_level_achieved += 1
            if eroded: 
                eroded_levels.append(difficulty)
        update_json(max_level_achieved, eroded_levels)

if __name__ == "__main__":
    main()
