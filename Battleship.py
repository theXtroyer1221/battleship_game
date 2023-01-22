import sys
import pygame
import random
import time

pygame.init()

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

# antal skepp man har förlorat
player1_ships_destroyed = 0
player2_ships_destroyed = 0

# Antal skepp för varje spelare
NUM_SHIPS = 2
SHIP_SIZE = 2

dropdown = pygame.Rect(10, 10, 100, 20)  # x, y, width, height
dropdown_options = ['jollar', 'briggar', 'galärer', 'fullriggare']
font = pygame.font.Font(pygame.font.match_font('bitstreamverasans'), 16)


# bilder init
fire = pygame.transform.scale(
    pygame.image.load("fireball.gif"), (CELL_SIZE, CELL_SIZE))

# ljudfiler init
intro_sound = pygame.mixer.Sound('intro.wav')
start_sound = pygame.mixer.Sound('start.wav')
ship_sound = pygame.mixer.Sound('ship.wav')
shoot_sound = pygame.mixer.Sound('shoot.wav')
sink_sound = pygame.mixer.Sound('sink.wav')
splash_sound = pygame.mixer.Sound('splash.wav')
win_sound = pygame.mixer.Sound('win.wav')

intro_sound.play()


def draw_grid():
    # horisontella linjerna
    for row in range(ROWS):
        pygame.draw.line(screen, BLACK, (0, row*CELL_SIZE+MARGIN),
                         (COLUMNS*CELL_SIZE+MARGIN, row*CELL_SIZE+MARGIN))

    # verticala linjer
    for column in range(COLUMNS):
        pygame.draw.line(screen, BLACK, (column*CELL_SIZE+MARGIN, 0),
                         (column*CELL_SIZE+MARGIN, ROWS*CELL_SIZE+MARGIN))


def draw_ship(coordinates, player):
    # En loop för varje koordinat i skeppet.
    for coordinate in coordinates:
        row, column = coordinate[0], coordinate[1]
        # beräkna vänstra hörnet av cellen
        x = column * (CELL_SIZE + MARGIN) + MARGIN
        y = row * (CELL_SIZE + MARGIN) + MARGIN

        if player == 1:
            color = BLUE
        else:
            color = RED
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))


def place_ships():
    global SHIP_SIZE
    cube_image = None  # The image of the cube
    cube_x = None  # The x-coordinate of the cube
    cube_y = None  # The y-coordinate of the cube
    cube_alpha = 80  # The transparency of the cube (0-255)
    # spelaren som kör just nu, 1 är spelare 1 osv.
    current_player = 1

    # Set the ship placement mode
    placing_ships = True
    dropdown_open = False

    # Anger om skeppet är horisontell eller vertikal, spelaren kan vända på skeppet genom att variabeln ändras med en inline funktion eller lambda som ändrar värdet på variabeln från  till 90 och vice versa
    rotation = 0
    def rotate(r): return 0 if r == 90 else r + 90

    while placing_ships:
        # beräkna cellen som musen klickade
        mouse_x, mouse_y = pygame.mouse.get_pos()
        column = mouse_x // (CELL_SIZE + MARGIN)
        row = mouse_y // (CELL_SIZE + MARGIN)

        x = column * (CELL_SIZE + MARGIN) + MARGIN
        y = row * (CELL_SIZE + MARGIN) + MARGIN

        # Delen av kode om cube_image är för att skapa en "ghost" som visar visuellt vart skeppet kommer att placeras"
        if rotation == 0:
            cube_image = pygame.Surface((CELL_SIZE, CELL_SIZE*SHIP_SIZE))
        else:
            cube_image = pygame.Surface((CELL_SIZE*SHIP_SIZE, CELL_SIZE))
        if current_player == 1:
            cube_image.fill(BLUE)
        else:
            cube_image.fill(RED)
        cube_image.set_alpha(cube_alpha)
        # if column * CELL_SIZE < column * CELL_SIZE * 10:
        cube_x, cube_y = column * CELL_SIZE, row * CELL_SIZE

        # pygame event för att fånga mus händelser
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if dropdown.collidepoint(event.pos):
                    # Open the dropdown menu
                    dropdown_open = True
                elif dropdown_open:
                    # Check if user clicked on an option in the dropdown menu
                    for i, option in enumerate(dropdown_options):
                        rect = pygame.Rect(dropdown.x, dropdown.y +
                                           ((i + 1) * 30), dropdown.width, 30)
                        if rect.collidepoint(event.pos):
                            SHIP_SIZE = i + 1  # The index of the option selected
                            dropdown_open = False
                            print(f'Selected ship size: {SHIP_SIZE}')
                            break

                elif (row, column) not in player1_ships and (row, column) not in player2_ships:
                    ship_sound.play()
                    # placera skepperna, unit är en tillfällig lista för att samla alla skepp delar i en och samma
                    unit = []
                    if rotation == 0:
                        for _ in range(SHIP_SIZE):
                            unit.append([row+_, column])
                    else:
                        for _ in range(SHIP_SIZE):
                            unit.append([row, column+_])

                    if current_player == 1:
                        player1_ships.append(unit)
                    else:
                        player2_ships.append(unit)

                    # byt till nästa spelare
                    current_player = 3 - current_player
                else:
                    shoot_sound.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rotation = rotate(rotation)

            # om båda spelare har placerad alla sina skepp, avsluta förbredningsperioden och starta spelet
            if len(player1_ships) == NUM_SHIPS and len(player2_ships) == NUM_SHIPS:
                placing_ships = False
                start_sound.play()

        screen.fill(WHITE)
        draw_grid()
        # lite genomskinliga skeppet för att visa visuellt vart man kommer att placera
        screen.blit(cube_image, (cube_x, cube_y))
        # Vi behöver rita om skepperna för varje spelomgång så att endast kvarliggande skepper visas
        for ship in player1_ships:
            draw_ship(ship, 1)
        for ship in player2_ships:
            draw_ship(ship, 2)
        # Rita dropdown för att välja skepp typ
        pygame.draw.rect(screen, WHITE, dropdown)
        pygame.draw.rect(screen, BLACK, dropdown,
                         1)  # svart ram
        if dropdown_open:
            for i, option in enumerate(dropdown_options):
                rect = pygame.Rect(dropdown.x, dropdown.y +
                                   ((i + 1) * 30), dropdown.width, 30)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                text = font.render(option, True, BLACK)
                screen.blit(text, (rect.x + 5, rect.y+7))
        else:
            text = font.render(
                dropdown_options[SHIP_SIZE - 1] + " \u2193", True, BLACK)
            screen.blit(text, (dropdown.x + 5, dropdown.y))
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


def attack_cell(current_player, game_state, ships, row, column):
    global player1_ships_destroyed, player2_ships_destroyed
    # kontrollera om cellen har redan varit attackerad
    if game_state[row][column] != 0:
        return "invalid"

    result = "miss"
    for ship in ships:
        if [row, column] in ship:
            ship.remove([row, column])
            game_state[row][column] = 1
            result = "hit"
            if current_player == 1 and not ship:
                player2_ships_destroyed += 1
                ships.remove(ship)
            elif current_player == 2 and not ship:
                player1_ships_destroyed += 1
                ships.remove(ship)
            break

    screen.fill(WHITE)
    draw_grid()

    # Rita eld för att indikera en attackerad cell från föregående turer
    # variablerna i (column) och j(row) talar om vilken ruta som trycks, men för att uttrycka det i pygames koordinatsystem gångrar vi med rutstorleken. Ex. om explosionen är vid rad 4, då är det  y koordinaten 4 * 50 = 200
    for i in range(COLUMNS):
        for j in range(ROWS):
            if game_state[i][j] == 1:
                screen.blit(
                    fire, (j * CELL_SIZE, i * CELL_SIZE))

    for ship in player1_ships:
        draw_ship(ship, 1)
    for ship in player2_ships:
        draw_ship(ship, 2)

    # Visa spelarnas namn, färg och information om spelet, samt nästa spelares tur
    font = pygame.font.Font(None, 16)
    if current_player == 1:
        text = font.render(
            f"Computers's turn", True, RED)
        screen.blit(text, (WINDOW_SIZE[0] - 120, 10))
    else:
        text = font.render(
            f"player 1's turn", True, BLUE)
        screen.blit(text, (WINDOW_SIZE[0] - 80, 10))

    text = font.render("Player", True, BLUE)  # Blue
    screen.blit(text, (10, WINDOW_SIZE[1] - 50))
    text = font.render(
        f"Ships remaining: {NUM_SHIPS - player1_ships_destroyed}", True, BLUE)
    screen.blit(text, (10, WINDOW_SIZE[1] - 25))
    text = font.render(
        f"Ships destroyed: {player2_ships_destroyed}", True, BLUE)
    screen.blit(text, (10, WINDOW_SIZE[1] - 10))

    # Spelare 2
    text = font.render("Computer", True, RED)  # Red
    screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 50))
    text = font.render(
        f"Ships remaining: {NUM_SHIPS - player2_ships_destroyed}", True, RED)
    screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 25))
    text = font.render(
        f"Ships destroyed: {player1_ships_destroyed}", True, RED)
    screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 10))

    # Notera resultatet av attacken
    font = pygame.font.Font(None, 36)
    if result == "hit":
        text = font.render(
            f"Player {current_player} hits a ship!", True, BLACK)
        sink_sound.play()
    elif result == "miss":
        text = font.render(
            f"Player {current_player} misses!", True, BLACK)
        splash_sound.play()
    elif result == "invalid":
        text = font.render(
            f"Player {current_player}, Invalid attack!", True, BLACK)
    screen.blit(text, (10, 10))

    pygame.display.update()


def check_win(game_state, current_player):
    # Kontrollera om spelare 1 inte har några skepp kvar på rutnätet
    if not player1_ships:
        screen.fill(WHITE)
        draw_grid()

        for ship in player1_ships:
            draw_ship(ship, 1)
        for ship in player2_ships:
            draw_ship(ship, 2)
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
            draw_ship(ship, 1)
        for ship in player2_ships:
            draw_ship(ship, 2)
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
            attack_result = attack_cell(current_player,
                                        game_state, player2_ships, row, column)

            current_player = 3 - current_player

            # Datorns tur att köra, använd random för att slumpmässsigt välja attack koordinat
            font = pygame.font.Font(None, 24)
            text = font.render(
                "Computer player's turn, please wait...", True, BLACK)
            screen.blit(text, (10, WINDOW_SIZE[1]))
            pygame.display.update()
            pygame.time.wait(1200)

            row = random.randint(0, ROWS - 1)
            column = random.randint(0, COLUMNS - 1)
            attack_result = attack_cell(
                current_player, game_state, player1_ships, row, column)
            print(attack_result, [row, column])

            # Kontrollera om någon har vunnit
            check_win(game_state, current_player)

        # Slutligen kontrollera om någon spelare har förlorat
        keys = pygame.key.get_pressed()
        if any(keys):
            # If any key is being pressed, exit the program
            pygame.quit()
            sys.exit()

place_ships()
