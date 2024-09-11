import random

from pyglet.window import key
import pyglet

FPS = 10  # frames per second (aka speed of the game)
WINDOW_BLOCK_WIDTH = 15  # number of blocks (aka size of the screen)
BLOCK_WIDTH = 50  # size of squares in pixels
FOOD_SCORE = 5  # points by food

# direction vectors
LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, 1)
DOWN = (0, -1)

# Create a window
window = pyglet.window.Window(WINDOW_BLOCK_WIDTH * BLOCK_WIDTH, WINDOW_BLOCK_WIDTH * BLOCK_WIDTH, caption="A python is a snake")
batch = pyglet.graphics.Batch()

def draw_grid():
    """Draw the grid lines of the board"""
    for i in range(WINDOW_BLOCK_WIDTH + 1):
        pyglet.shapes.Line(i * BLOCK_WIDTH, 0, i * BLOCK_WIDTH, WINDOW_BLOCK_WIDTH * BLOCK_WIDTH, width=1, color=(58, 58, 58), batch=batch).draw()
        pyglet.shapes.Line(0, i * BLOCK_WIDTH, WINDOW_BLOCK_WIDTH * BLOCK_WIDTH, i * BLOCK_WIDTH, width=1, color=(58, 58, 58), batch=batch).draw()

def draw_rectangle(xywh, color=(0, 0, 0)):
    """draw a filled rectangle

    Args:
        xywh (tuple): x, y, width, height
        color (tuple): (red, green, blue)

    Returns:
        None: draws a rectangle on the screen
    """
    x, y, dx, dy = xywh
    pyglet.shapes.Rectangle(x, y, dx, dy, color=color, batch=batch).draw()

def get_random_position():
    """get a random block position within the window

    Returns:
        int: lower bound
        int: upper bound
    """
    return (
        random.randrange(1, WINDOW_BLOCK_WIDTH),
        random.randrange(1, WINDOW_BLOCK_WIDTH),
    )

def get_block_xywh(position):
    """Returns the x, y, width, and height for a position

    Args:
        position (tuple): (int, int) a position within the window

    Returns:
        float: x pixel
        float: y pixel
        float: pixel width
        float: pixel height
    """
    return (
        position[0] * BLOCK_WIDTH,
        position[1] * BLOCK_WIDTH,
        BLOCK_WIDTH,
        BLOCK_WIDTH,
    )

def render_text(text, color=(128, 58, 58), **kwargs):
    """Display the text onto the screen

    Args:
        text (str): text to display

    Returns:
        None: displays text to surface
    """
    xpct = kwargs.pop("xpct", 0.02)
    ypct = kwargs.pop("ypct", 0.92)

    kwargs.setdefault("x", int(xpct * window.width))
    kwargs.setdefault("y", int(ypct * window.height))
    kwargs.setdefault("font_size", 26)
    kwargs.setdefault("font_name", "Times New Roman")

    pyglet.text.Label(text, color=color + (255,), **kwargs).draw()

def get_food_position(food_pos=None, occupied_positions=None):
    """Return the current or new food position

    Args:
        food_pos (tuple): If None then a new food_pos will be returned
            otherwise the food_position is unchanged
        occupied_positions (list): a list of positions, if provided new food will
            not occupy these positions

    """
    occupied_positions = occupied_positions or []
    if food_pos is None:
        while True:
            food_pos = get_random_position()
            if not food_pos in occupied_positions:
                break
    return food_pos

def create_obstacles(difficulty=25, snake_pos=None):
    """Create the obstacles

    Args:
        difficulty (int): number of blocks - 5 easy 20 medium 50 hard

    Returns:
        list: of (i, j) positions for obstacles
    """
    if snake_pos is None:
        snake_pos = []
    obstacles = []
    for i in range(1, difficulty):
        lo = get_random_position()
        obstacles.append(lo)

        max_j = random.randint(1, int(difficulty / 2))

        for j in range(1, max_j):

            if random.randint(1, 2) == 1:
                lo = (lo[0] + 1, lo[1])

            else:
                lo = (lo[0], lo[1] + 1)

            within_x_bounds = 0 < lo[0] <= WINDOW_BLOCK_WIDTH
            within_y_bounds = 0 < lo[1] <= WINDOW_BLOCK_WIDTH
            if within_x_bounds and within_y_bounds:
                close_to_snake = False
                for pos in snake_pos:
                    close_to_snake = (pos[0] - 1 < lo[0] < pos[0] + 1) and (
                        pos[1] - 1 < lo[1] < pos[1] + 1
                    )
                    if close_to_snake:
                        break

                if not close_to_snake:
                    obstacles.append(lo)

    return obstacles

def on_draw():
    """update the objects on screen"""
    global objects, score, game_is_active
    window.clear()

    draw_grid()

    food = objects["food"]
    if food["pos"] is not None:
        food_xywh = get_block_xywh(food["pos"])
        draw_rectangle(food_xywh, food["color"])

    obstacles = objects["obstacles"]
    for block_pos in obstacles["pos"]:
        block_xywh = get_block_xywh(block_pos)
        draw_rectangle(block_xywh, obstacles["color"])

    snake = objects["snake"]
    for block_pos in snake["pos"]:
        block_xywh = get_block_xywh(block_pos)
        draw_rectangle(block_xywh, snake["color"])

    render_text("Score : {}".format(score))
    if not game_is_active:
        render_text(
            "GAME OVER",
            font_size=40,
            xpct=0.5,
            ypct=0.5,
            anchor_x="center",
        )

def on_key_press(symbol, modifiers):
    global objects

    direction = objects["snake"]["direction"]

    if symbol == key.UP:
        if direction != DOWN:
            direction = UP

    elif symbol == key.DOWN:
        if direction != UP:
            direction = DOWN

    elif symbol == key.LEFT:
        if direction != RIGHT:
            direction = LEFT

    elif symbol == key.RIGHT:
        if direction != LEFT:
            direction = RIGHT

    objects["snake"]["direction"] = direction

def update_game(dt):
    """update the game

    In this function the snake position is updated, checks
    for collisions and game scoring. Updates appropriately

    """
    global objects, score, game_is_active

    if not game_is_active:
        return

    snake_pos = objects["snake"]["pos"]
    direction = objects["snake"]["direction"]
    obstacles_pos = objects["obstacles"]["pos"]
    food_pos = objects["food"]["pos"]

    occupied_pos = snake_pos + obstacles_pos
    head_pos = snake_pos[0]
    head_pos = (
        (head_pos[0] + direction[0]) % WINDOW_BLOCK_WIDTH,
        (head_pos[1] + direction[1]) % WINDOW_BLOCK_WIDTH,
    )

    collide_with_self = head_pos in snake_pos
    collide_with_obstacle = head_pos in obstacles_pos

    # move the snake
    snake_pos.insert(0, head_pos)
    tail_pos = snake_pos.pop(-1)

    if collide_with_obstacle or collide_with_self:
        stop_game()
        return

    elif head_pos == food_pos:
        score += FOOD_SCORE
        food_pos = None
        snake_pos.append(tail_pos)

    food_pos = get_food_position(food_pos=food_pos, occupied_positions=occupied_pos)
    objects["food"]["pos"] = food_pos

def start_game(difficulty=10):
    """start game"""
    global objects, snake_direction, score, game_is_active
    game_is_active = True

    half_width = int(WINDOW_BLOCK_WIDTH / 2.0)
    snake_pos = [
        (half_width, half_width),
        (half_width, half_width + 1),
        (half_width, half_width + 2),
    ]

    objects = {
        "snake": {
            "pos": snake_pos,
            "color": (100, 200, 150),
            "direction": RIGHT,
        },
        "obstacles": {
            "pos": create_obstacles(snake_pos=snake_pos, difficulty=difficulty),
            "color": (200, 23, 23),
        },
        "food": {
            "pos": None,
            "color": (23, 23, 200),
        },
    }

    snake_direction = RIGHT
    score = 0

    window.push_handlers(
        on_key_press=on_key_press,
        on_draw=on_draw,
    )

def stop_game():
    """stop the game play"""
    global game_is_active, window, score

    game_is_active = False
    pyglet.clock.unschedule(update_game)
    window.remove_handlers()

if __name__ == "__main__":
    objects = {}
    score = 0
    game_is_active = True

    start_game()

    pyglet.clock.schedule_interval(update_game, 1.0 / FPS)
    pyglet.app.run()
