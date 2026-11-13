"""Classic Snake game built with pygame.

Move with the arrow keys or WASD, eat the red food to grow, and avoid walls and
your own tail. Press R to restart after a game over, or ESC to quit.
"""

import random
import sys

import pygame

# Grid and window settings. Each grid cell is CELL pixels square.
CELL = 20
COLS = 30
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
# Starting game speed in frames per second. Speed increases as the score rises.
FPS_START = 8

# Colors as (red, green, blue) tuples.
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 40, 40)
WHITE = (255, 255, 255)
GREY = (40, 40, 40)

# Movement directions as (column change, row change).
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def random_food(snake):
    """Pick a random grid cell for food that is not occupied by the snake."""
    while True:
        pos = (random.randrange(COLS), random.randrange(ROWS))
        if pos not in snake:
            return pos


def new_game():
    """Create the starting game state: a 3-cell snake in the middle, moving right."""
    start_x, start_y = COLS // 2, ROWS // 2
    # The head is the first element of the list.
    snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    return {
        "snake": snake,
        "direction": RIGHT,
        # Direction queued from key presses; applied at the next game step.
        "next_direction": RIGHT,
        "food": random_food(snake),
        "score": 0,
        "game_over": False,
    }


def draw_text(screen, font, text, center, color=WHITE):
    """Draw `text` centered on `center` (x, y) of the screen."""
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


def main():
    """Set up the window and run the main game loop until the player quits."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    # Clock limits how fast the loop runs, which sets the snake's speed.
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 64)

    game = new_game()

    # Keys mapped to directions. WASD and arrow keys both work.
    key_map = {
        pygame.K_UP: UP, pygame.K_w: UP,
        pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
        pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
        pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
    }

    while True:
        # 1. Handle input events (window close, key presses).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game["game_over"]:
                    game = new_game()
                elif event.key in key_map and not game["game_over"]:
                    new_dir = key_map[event.key]
                    cur = game["direction"]
                    # Prevent reversing directly into yourself
                    if (new_dir[0] + cur[0], new_dir[1] + cur[1]) != (0, 0):
                        game["next_direction"] = new_dir

        # 2. Advance the game by one step if it is still running.
        if not game["game_over"]:
            game["direction"] = game["next_direction"]
            head_x, head_y = game["snake"][0]
            dx, dy = game["direction"]
            new_head = (head_x + dx, head_y + dy)

            # The game ends if the head leaves the grid or runs into the body.
            # The tail is excluded from the check because it moves away this step.
            hit_wall = not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS)
            hit_self = new_head in game["snake"][:-1]
            if hit_wall or hit_self:
                game["game_over"] = True
            else:
                # Add the new head. If it landed on food, keep the tail (the snake grows).
                # Otherwise remove the tail so the length stays the same.
                game["snake"].insert(0, new_head)
                if new_head == game["food"]:
                    game["score"] += 1
                    game["food"] = random_food(game["snake"])
                else:
                    game["snake"].pop()

        # 3. Draw the frame: background, grid lines, food, snake, score, and game-over text.
        screen.fill(BLACK)
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, GREY, (0, y), (WIDTH, y))

        fx, fy = game["food"]
        pygame.draw.rect(screen, RED, (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4))

        # Draw the head in bright green and the body in dark green.
        for i, (x, y) in enumerate(game["snake"]):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2))

        draw_text(screen, font, f"Score: {game['score']}", (70, 20))

        if game["game_over"]:
            draw_text(screen, big_font, "GAME OVER", (WIDTH // 2, HEIGHT // 2 - 20))
            draw_text(screen, font, "Press R to restart or ESC to quit", (WIDTH // 2, HEIGHT // 2 + 30))

        # Show the finished frame, then wait so the loop runs at the target speed.
        pygame.display.flip()
        # Speed rises by 1 FPS for every 3 points, capped at 20 FPS.
        speed = FPS_START + game["score"] // 3
        clock.tick(min(speed, 20))


if __name__ == "__main__":
    main()
