import sys
import pygame
vdisplay = Xvfb()
vdisplay.start()


pygame.init()
# pygame.mixer.init()

WINDOW_SIZE = [500, 500]
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

pygame.display.set_caption("Sänka skepp")


BACKGROUND_COLOR = (255, 255, 255)

# bestämmer storleken på rutnätet
CELL_SIZE = 50
MARGIN = 0
# dimensionerna av spelnätet
ROWS = 10
COLUMNS = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

player1_ships = []
player2_ships = []

player1_ships_destroyed = []
player2_ships_destroyed = []

# Antal skepp för varje spelare
NUM_SHIPS = 5

# ljudfiler init
# intro_sound = pygame.mixer.Sound('intro.wav')
# start_sound = pygame.mixer.Sound('start.wav')
# ship_sound = pygame.mixer.Sound('ship.wav')
# shoot_sound = pygame.mixer.Sound('shoot.wav')
# sink_sound = pygame.mixer.Sound('sink.wav')
# splash_sound = pygame.mixer.Sound('splash.wav')
# win_sound = pygame.mixer.Sound('win.wav')

# intro_sound.play()


def draw_grid():
    # horisontella linjerna
    for row in range(ROWS):
        pygame.draw.line(screen, BLACK, (0, row*CELL_SIZE+MARGIN),
                         (COLUMNS*CELL_SIZE+MARGIN, row*CELL_SIZE+MARGIN))

    # verticala linjer
    for column in range(COLUMNS):
        pygame.draw.line(screen, BLACK, (column*CELL_SIZE+MARGIN, 0),
                         (column*CELL_SIZE+MARGIN, ROWS*CELL_SIZE+MARGIN))


def draw_ship(row, column, player):
    # beräkna vänstra hörnet av cellen
    x = column * (CELL_SIZE + MARGIN) + MARGIN
    y = row * (CELL_SIZE + MARGIN) + MARGIN

    if player == 1:
        color = BLUE
    else:
        color = RED
    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))


def place_ships():
    # spelaren som kör just nu, 1 är spelare 1 osv.
    current_player = 1

    # Set the ship placement mode
    placing_ships = True

    while placing_ships:
        # pygame event för att fånga mus händelser
        for event in pygame.event.get():
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ship_sound.play()
                # beräkna cellen som musen klickade
                column = mouse_x // (CELL_SIZE + MARGIN)
                row = mouse_y // (CELL_SIZE + MARGIN)

                x = column * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN

                # placera skepperna
                if current_player == 1:
                    player1_ships.append((row, column))
                else:
                    player2_ships.append((row, column))

                # byt till nästa spelare
                current_player = 3 - current_player

            # om båda spelare har placerad alla sina skepp, avsluta förbredningsperioden och starta spelet
            if len(player1_ships) == NUM_SHIPS and len(player2_ships) == NUM_SHIPS:
                placing_ships = False
                start_sound.play()

        screen.fill(WHITE)
        draw_grid()

        # Vi behöver rita om skepperna för varje spelomgång så att endast kvarliggande skepper visas
        for ship in player1_ships:
            draw_ship(ship[0], ship[1], 1)
        for ship in player2_ships:
            draw_ship(ship[0], ship[1], 2)

        # updtaera skärmen efter varje omritning
        pygame.display.update()
        # spelets 'timeframe'
        clock.tick(60)


place_ships()

font = pygame.font.Font(None, 24)
text = font.render(
    "Ship placement phase finished, game starting!", True, BLACK)
screen.blit(text, (10, 10))
pygame.display.update()

current_player = 1
playing = True

game_state = [[0 for column in range(COLUMNS)] for row in range(ROWS)]


def attack_cell(game_state, player, row, column):
    player1_ships_destroyed = []
    player2_ships_destroyed = []
    # kontrollera om cellen har redan varit attackerad
    if game_state[row][column] != 0:
        return "invalid"

    # Kontrollera om ett skepp har slagits
    if player == 1 and (row, column) in player2_ships:
        player2_ships.remove((row, column))
        player2_ships_destroyed.append((row, column))
        # cellen som blir attackerad ges värdet 1
        game_state[row][column] = 1
        return "hit"
    elif player == 2 and (row, column) in player1_ships:
        player1_ships.remove((row, column))
        player1_ships_destroyed.append((row, column))
        game_state[row][column] = 1
        return "hit"
    # ff dvs. friendly fire
    elif player == 1 and (row, column) in player1_ships:
        return "ff"
    elif player == 2 and (row, column) in player2_ships:
        return "ff"
    else:
        game_state[row][column] = -1
        return "miss"


def check_win(game_state, current_player):
    # Kontrollera om spelare 1 inte har några skepp kvar på rutnätet
    if not player1_ships:
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

    # Kontrollera för spelare 2
    elif not player2_ships:
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            shoot_sound.play()
            # mus position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            column = mouse_x // (CELL_SIZE + MARGIN)
            row = mouse_y // (CELL_SIZE + MARGIN)

            # Attackera cellen
            attack_result = attack_cell(
                game_state, current_player, row, column)

            # Rita om efter attacken
            screen.fill(WHITE)
            draw_grid()

            for ship in player1_ships:
                draw_ship(ship[0], ship[1], 1)
            for ship in player2_ships:
                draw_ship(ship[0], ship[1], 2)

            # Visa spelarnas namn, färg och information om spelet
            font = pygame.font.Font(None, 16)
            # Spelare 1
            current_player_color = RED if current_player == 1 else BLUE
            text = font.render(
                f"player {3 - current_player}'s turn", True, current_player_color)
            screen.blit(text, (WINDOW_SIZE[0] - 70, 10))

            text = font.render("Player 1", True, BLUE)  # Blue
            screen.blit(text, (10, WINDOW_SIZE[1] - 50))
            text = font.render(
                f"Ships remaining: {NUM_SHIPS - len(player1_ships_destroyed)}", True, BLUE)
            screen.blit(text, (10, WINDOW_SIZE[1] - 25))
            text = font.render(
                f"Ships destroyed: {len(player2_ships_destroyed)}", True, BLUE)
            screen.blit(text, (10, WINDOW_SIZE[1] - 10))

            # Spelare 2
            text = font.render("Player 2", True, RED)  # Red
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 50))
            text = font.render(
                f"Ships remaining: {NUM_SHIPS - len(player2_ships_destroyed)}", True, RED)
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 25))
            text = font.render(
                f"Ships destroyed: {len(player1_ships_destroyed)}", True, RED)
            screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 10))

            # Notera resultatet av attacken
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

            pygame.display.update()

            current_player = 3 - current_player

            # Kontrollera om någon har vunnit
            check_win(game_state, current_player)

        # Slutligen kontrollera om någon spelare har förlorat
        keys = pygame.key.get_pressed()
        if any(keys):
            # If any key is being pressed, exit the program
            pygame.quit()
            sys.exit()

place_ships()
