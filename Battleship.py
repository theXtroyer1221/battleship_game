import pygame
import sys

# Initialize Pygame
pygame.init()

# Set the window size
WINDOW_SIZE = [500, 500]

# Create the window
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# Set the window title
pygame.display.set_caption("Battleship")

# Set the background color
BACKGROUND_COLOR = (255, 255, 255)

# Set the cell size and margin
CELL_SIZE = 50
MARGIN = 0

# Set the grid dimensions
ROWS = 10
COLUMNS = 10

# Set the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Set up the player's ships
player1_ships = []
player2_ships = []

player1_ships_destroyed = []
player2_ships_destroyed = []

# Set the number of ships for each player
NUM_SHIPS = 5

# Load the audio files
intro_sound = pygame.mixer.Sound('intro.wav')
start_sound = pygame.mixer.Sound('start.wav')
ship_sound = pygame.mixer.Sound('ship.wav')
shoot_sound = pygame.mixer.Sound('shoot.wav')
sink_sound = pygame.mixer.Sound('sink.wav')
splash_sound = pygame.mixer.Sound('splash.wav')
win_sound = pygame.mixer.Sound('win.wav')

intro_sound.play()


def draw_grid():
    # Draw the horizontal lines
    for row in range(ROWS):
        pygame.draw.line(screen, BLACK, (0, row*CELL_SIZE+MARGIN),
                         (COLUMNS*CELL_SIZE+MARGIN, row*CELL_SIZE+MARGIN))

    # Draw the vertical lines
    for column in range(COLUMNS):
        pygame.draw.line(screen, BLACK, (column*CELL_SIZE+MARGIN, 0),
                         (column*CELL_SIZE+MARGIN, ROWS*CELL_SIZE+MARGIN))


def draw_ship(row, column, player):
    # Calculate the top-left corner of the cell
    x = column * (CELL_SIZE + MARGIN) + MARGIN
    y = row * (CELL_SIZE + MARGIN) + MARGIN

    # Draw the ship
    if player == 1:
        color = BLUE
    else:
        color = RED
    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))


def place_ships():
    # Set the current player
    current_player = 1

    # Set the ship placement mode
    placing_ships = True

    while placing_ships:
        # Handle events
        for event in pygame.event.get():
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ship_sound.play()
                # Calculate the row and column that was clicked
                column = mouse_x // (CELL_SIZE + MARGIN)
                row = mouse_y // (CELL_SIZE + MARGIN)

                x = column * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN

                # Place the ship for the current player
                if current_player == 1:
                    player1_ships.append((row, column))
                else:
                    player2_ships.append((row, column))

                # Switch to the other player
                current_player = 3 - current_player

            # If both players have placed all of their ships, end ship placement mode
            if len(player1_ships) == NUM_SHIPS and len(player2_ships) == NUM_SHIPS:
                placing_ships = False
                start_sound.play()

        # Clear the screen
        screen.fill(WHITE)

        # Draw the grid
        draw_grid()

        # Draw the ships for each player
        for ship in player1_ships:
            draw_ship(ship[0], ship[1], 1)
        for ship in player2_ships:
            draw_ship(ship[0], ship[1], 2)

        # Update the display
        pygame.display.update()

        # Limit the frame rate
        clock.tick(60)


place_ships()

# Display a message to let the players know that the ship placement phase is finished
font = pygame.font.Font(None, 24)
text = font.render(
    "Ship placement phase finished, game starting!", True, BLACK)
screen.blit(text, (10, 10))
pygame.display.update()

# Set the current player to player 1
current_player = 1

# Set the game mode
playing = True

# Set the game state
game_state = [[0 for column in range(COLUMNS)] for row in range(ROWS)]


def attack_cell(game_state, player, row, column):
    player1_ships_destroyed = []
    player2_ships_destroyed = []
    # Check if the cell has already been attacked
    if game_state[row][column] != 0:
        return "invalid"

    # Check if the player hit a ship
    if player == 1 and (row, column) in player2_ships:
        player2_ships.remove((row, column))
        player2_ships_destroyed.append((row, column))
        # Set the cell to 1 to indicate it has been attack
        game_state[row][column] = 1
        return "hit"
    elif player == 2 and (row, column) in player1_ships:
        player1_ships.remove((row, column))
        player1_ships_destroyed.append((row, column))
        # Set the cell to 1 to indicate it has been attacked
        game_state[row][column] = 1
        return "hit"
    elif player == 1 and (row, column) in player1_ships:
        return "ff"
    elif player == 2 and (row, column) in player2_ships:
        return "ff"
    else:
        # Set the cell to -1 to indicate it has been attack
        game_state[row][column] = -1
        return "miss"


def check_win(game_state, current_player):
    # Check if player 1 has no more ships
    if not player1_ships:
        # Display a message to the players indicating that player 2 has won
        screen.fill(WHITE)

        draw_grid()

        for ship in player1_ships:
            draw_ship(ship[0], ship[1], 1)
        for ship in player2_ships:
            draw_ship(ship[0], ship[1], 2)
        font = pygame.font.Font(None, 36)
        text = font.render(
            "Player 2 wins! Press any key to exit...", True, BLACK)
        win_sound.play()
        screen.blit(text, (10, 10))
        pygame.display.update()

    # Check if player 2 has no more ships
    elif not player2_ships:
        # Display a message to the players indicating that player 1 has won
        screen.fill(WHITE)

        draw_grid()

        for ship in player1_ships:
            draw_ship(ship[0], ship[1], 1)
        for ship in player2_ships:
            draw_ship(ship[0], ship[1], 2)
        font = pygame.font.Font(None, 36)
        text = font.render(
            "Player 1 wins! Press any key to exit...", True, BLACK)
        win_sound.play()
        screen.blit(text, (10, 10))
        pygame.display.update()


while playing:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            shoot_sound.play()
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Calculate the row and column that was clicked
            column = mouse_x // (CELL_SIZE + MARGIN)
            row = mouse_y // (CELL_SIZE + MARGIN)

            # Attack the selected cell for the current player
            attack_result = attack_cell(
                game_state, current_player, row, column)

            # Clear the screen
            screen.fill(WHITE)

            # Draw the grid
            draw_grid()

            # Draw the ships for each player
            for ship in player1_ships:
                draw_ship(ship[0], ship[1], 1)
            for ship in player2_ships:
                draw_ship(ship[0], ship[1], 2)

            # Display the player's name, color, and ship count at the bottom of the screen
            font = pygame.font.Font(None, 16)
            # Display player 1's information
            current_player_color = RED if current_player == 1 else BLUE
            text = font.render(
                f"player {3 - current_player}'s turn", True, current_player_color)
            screen.blit(text, (WINDOW_SIZE[0] - 70, 10))
            # Display player 1's information
            text = font.render("Player 1", True, BLUE)  # Blue
            screen.blit(text, (10, WINDOW_SIZE[1] - 50))
            text = font.render(
                f"Ships remaining: {NUM_SHIPS - len(player1_ships_destroyed)}", True, BLUE)
            screen.blit(text, (10, WINDOW_SIZE[1] - 25))
            text = font.render(
                f"Ships destroyed: {len(player2_ships_destroyed)}", True, BLUE)
            screen.blit(text, (10, WINDOW_SIZE[1] - 10))

            # Display player 2's information
            text = font.render("Player 2", True, RED)  # Red
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 50))
            text = font.render(
                f"Ships remaining: {NUM_SHIPS - len(player2_ships_destroyed)}", True, RED)
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 25))
            text = font.render(
                f"Ships destroyed: {len(player1_ships_destroyed)}", True, RED)
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 10))

            # Display a message to the players indicating the result of the attack
            font = pygame.font.Font(None, 36)
            if attack_result == "hit":
                text = font.render(
                    f"Player {current_player} hits a ship!", True, BLACK)
                sink_sound.play()
            elif attack_result == "miss":
                text = font.render(
                    f"Player {current_player} misses!", True, BLACK)
                splash_sound.play()
            elif attack_result == "ff":
                text = font.render(
                    f"Player {current_player}, friendly fire!", True, BLACK)
            screen.blit(text, (10, 10))

            # Update the display
            pygame.display.update()

            # Switch to the other player
            current_player = 3 - current_player

            # Check if the game has been won
            check_win(game_state, current_player)

        # Check if any key is being pressed
        keys = pygame.key.get_pressed()
        if any(keys):
            # If any key is being pressed, exit the program
            pygame.quit()
            sys.exit()

place_ships()
