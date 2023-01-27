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
player_1_ship_type = [4, 3, 3, 1]
player2_ships = []
player_2_ship_type = [4, 3, 3, 1]

# antal skepp man har förlorat
player1_ships_destroyed = 0
player2_ships_destroyed = 0

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


def draw_ship(coordinates, player, shaded):
    # En loop för varje koordinat i skeppet.'
    for coordinate in coordinates:
        row, column = coordinate[0], coordinate[1]
        # beräkna vänstra hörnet av cellen
        x = column * (CELL_SIZE + MARGIN) + MARGIN
        y = row * (CELL_SIZE + MARGIN) + MARGIN 

        if player == 1:
            color = BLUE
        else:
            color = RED
        ship_part = pygame.Surface((CELL_SIZE, CELL_SIZE))
        ship_part.fill(color)
        if shaded == True:
            ship_part.set_alpha(60)
        screen.blit(ship_part, (x, y))
        if shaded == False:
            for i in range(1, 4):
                pygame.draw.rect(screen, BLACK, (x-i, y-i, CELL_SIZE+1, CELL_SIZE+1), 1)


def check_coordinate(player_ships, unit):
    occupied = False
    for ship in player_ships:
        for coord in ship:
            if coord in unit:
                occupied = True
            else:
                occupied = False
    return occupied

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
    
    # Lägger ut datorns skeppar innan spelet börjar
    for i in range(sum(player_2_ship_type)):
        rotation = random.choice([0,90])
        unit = []
        if rotation == 0:
            row = random.randint(0, ROWS - 1)
            column = random.randint(0, COLUMNS - 1 - SHIP_SIZE)
            for _ in range(SHIP_SIZE):
                unit.append([row+_, column])
        else:
            row = random.randint(0, ROWS - -1 - SHIP_SIZE)
            column = random.randint(0, COLUMNS - 1)
            for _ in range(SHIP_SIZE):
                unit.append([row, column+_])
        occupied = False
        if len(player2_ships) != 0:
            occupied = check_coordinate(player2_ships, unit)
        if occupied == False:
            player2_ships.append(unit)
            player_2_ship_type[len(unit)-2] -= 1
            #Kontrollerar om alla skepp av typen har lagts ut, om ja byt till nästa skepp typ
            if player_2_ship_type[len(unit)-2] == 0:
                SHIP_SIZE += 1
           
    # återgå till start skepp        
    SHIP_SIZE = 2
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
        cube_image.fill(BLUE)
        cube_image.set_alpha(cube_alpha)

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
                            SHIP_SIZE = i + 2  # The index of the option selected
                            dropdown_open = False
                            print(f'Selected ship size: {SHIP_SIZE}')
                            break
                        else:
                            shoot_sound.play()

                elif (row, column) not in player1_ships and (row, column) not in player2_ships:
                    place = True
                    # placera skepperna, unit är en tillfällig lista för att samla alla skepp delar i en och samma
                    unit = []
                    if rotation == 0:
                        if row + SHIP_SIZE <= ROWS and column + 1 <= COLUMNS:
                            for _ in range(SHIP_SIZE):
                                unit.append([row+_, column])
                        else:
                            place = False
                            print("invalid placment")
                            shoot_sound.play()
                    else:
                        if column + SHIP_SIZE <= COLUMNS and row + 1 <= ROWS:
                            for _ in range(SHIP_SIZE):
                                unit.append([row, column+_])
                        else:
                            place = False
                            print("invalid placement")
                            shoot_sound.play()
                            
                    occupied = check_coordinate(player1_ships, unit)
                    print(occupied)
                    if occupied == True:
                        print("ya")
                        place == False

                    if place == True and player_1_ship_type[len(unit)-2] != 0:
                        player1_ships.append(unit)
                        player_1_ship_type[len(unit)-2] -= 1
                        ship_sound.play()
                else:
                    shoot_sound.play()
                    print("invalid placement")
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rotation = rotate(rotation)

            # om båda spelare har placerad alla sina skepp, avsluta förbredningsperioden och starta spelet
            if sum(player_1_ship_type) == 0 and sum(player_2_ship_type) == 0:
                placing_ships = False
                start_sound.play()

        screen.fill(WHITE)
        draw_grid()
        # lite genomskinliga skeppet för att visa visuellt vart man kommer att placera
        screen.blit(cube_image, (cube_x, cube_y))
        # Vi behöver rita om skepperna för varje spelomgång så att endast kvarliggande skepper visas
        for ship in player1_ships:
            draw_ship(ship, 1, False)

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
                name = f"{option} {player_1_ship_type[i]}x" if current_player == 1 else f"{option} {player_2_ship_type[i]}x"
                text = font.render(name, True, BLACK)
                screen.blit(text, (rect.x + 5, rect.y+7))
        else:
            text = font.render(
                dropdown_options[SHIP_SIZE - 2] + " \u2193", True, BLACK)
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
        draw_ship(ship, 1, True)

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
        f"Ships remaining: {sum(player_1_ship_type) - player1_ships_destroyed}", True, BLUE)
    screen.blit(text, (10, WINDOW_SIZE[1] - 25))
    text = font.render(
        f"Ships destroyed: {player2_ships_destroyed}", True, BLUE)
    screen.blit(text, (10, WINDOW_SIZE[1] - 10))

    # Spelare 2
    text = font.render("Computer", True, RED)  # Red
    screen.blit(text, (WINDOW_SIZE[0] - 200, WINDOW_SIZE[1] - 50))
    text = font.render(
        f"Ships remaining: {sum(player_2_ship_type) - player2_ships_destroyed}", True, RED)
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
            draw_ship(ship, 1, False)
        for ship in player2_ships:
            draw_ship(ship, 2, False)
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
