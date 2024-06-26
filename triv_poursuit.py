import pygame
import numpy as np
from gamers import *
import random
import main
import sql_game
import os
import openai
from dotenv import load_dotenv



# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer les valeurs des variables d'environnement
api_key = os.getenv('openai_api_key')
api_base = os.getenv('openai_api_key_base')
api_deployment = os.getenv('openai_api_deployment')
api_version = os.getenv('openai_api_version')

# Configurer l'API OpenAI avec les informations d'Azure
openai.api_key = api_key
openai.api_base = api_base
openai.api_type = 'azure'
openai.api_version = api_version

global etape_jeu
etape_jeu = 0

def set_music(etape_jeu, volume):
    if etape_jeu == 0:
        file_name = 'song_day.wav'
    elif etape_jeu == 1:
        file_name = 'night_song.wav'
    music = pygame.mixer.music.load(f"sounds/{file_name}")
    pygame.mixer.music.set_volume(volume)  # 1.0 volume max
    pygame.mixer.music.play(-1)


def set_image(etape_jeu):
    if etape_jeu == 0:
        file_name = 'day_img.webp'
    elif etape_jeu == 1:
        file_name = 'night_img.webp'
    background_img = pygame.image.load(f'img/{file_name}')
    background_img = pygame.transform.scale(background_img, (game_board_width, height))
    return background_img

# Initialisation de l'historique des conversations
conversation_history = []

# Liste globale pour stocker les dialogues
dialogues = []

def get_response(prompt, conversation_partner, player):
    global conversation_history, dialogues, etape_jeu
    
    character = conversation_partner.caracter
    lore = conversation_partner.lore
    partner_score = conversation_partner.score
    

    if partner_score <= -500:
            character = "Tu es très en colère car je t'ai fait du mal en te faisant tomber dans des trous. Si jamais je te donne un camembert ou un fromage, tu acceptes de faire la paix avec moi et potentiellement me donner une récompense à l'avenir"

    if etape_jeu == 0:
        if ('camembert' in prompt or 'fromage' in prompt) and player.camembert_part:
            conversation_partner.score += 250
            player.camembert_part.pop()
            sound_eat = pygame.mixer.Sound('sounds/eat.wav')
            sound_eat.set_volume(0.2)
            sound_eat.play()
            
        if player.arme == None and partner_score >= 250:
            character = "Tu es très heureux car tu as le ventre rempli avec tous les camemberts que je t'ai donnés. Si jamais je te dis 'donne-moi une récompense' ou quelque chose dans le genre, tu me donneras une hache en guise de remerciement."
   
    if etape_jeu ==1:
        character = "Tu es effrayé car tu vois plein d'orc autour de toi !! Si on te parle tu cries !! tu oublis tout le reste sur les camemberts et tout ce qui te preoccupe en ce moment meme sont les orcs a côté de toi"
    preprompt = f"Tu incarnes un personnage avec les traits de caractères suivants:\n {character}\nHistoire: {lore}\n. Tu dois répondre en tant que ce personnage."

    # Ajouter le nouveau message à l'historique
    conversation_history.append({"role": "user", "content": prompt})
    dialogues.append((player.player_name, prompt))

    # Limiter la taille de l'historique pour éviter des appels trop longs à l'API
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    messages = [{"role": "system", "content": preprompt}] + conversation_history

    response = openai.ChatCompletion.create(
        engine=api_deployment,
        messages=messages,
        max_tokens=100
    )

    print("Réponse brute de l'API:", response)
    
    try:
        response_text = response['choices'][0]['message']['content'].strip()
        response_text = response['choices'][0]['message']['content'].strip()
    except KeyError:
        response_text = response['choices'][0].get('text', '').strip()

    # Ajouter la réponse de l'IA à l'historique
    conversation_history.append({"role": "assistant", "content": response_text})
    dialogues.append((conversation_partner.player_name, response_text))

    # Vérifier si la réponse contient "hache"
    if 'hache' in response_text and etape_jeu == 0:
        player.additem('hache')
        
        #passe etape_jeu a 1
        etape_jeu = 1
        set_music(etape_jeu, 0.3)

        #ajout des orcs
        for x in range(3):
            pnj= Gamer(0, 0, 4+x, "Brute", 3)
            gamer_sprites.add(pnj)
            pnj.set_position(5+x, 12+x, cell_width, cell_height)
        
    return response_text

def draw_button(screen, text, x, y, width, height, active_color, inactive_color, font_size):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    
    font = pygame.font.SysFont(None, font_size)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (width / 2)), (y + (height / 2)))
    screen.blit(text_surf, text_rect)
    return False

def auto_wrap(text: str, font, max_width: int) -> list:
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line)
            current_line = word + ' '

    wrapped_lines.append(current_line)
    return wrapped_lines

def are_players_adjacent(player1, player2):
    return abs(player1.x - player2.x) <= 1 and abs(player1.y - player2.y) <= 1

def draw_dialogues(screen, dialogues, x, y, width, height, color, scroll_offset):
    font = pygame.font.SysFont(None, 25)
    pygame.draw.rect(screen, color, (x, y, width, height))
    dialogue_y = y + 10 - scroll_offset  # Start position for the dialogue text with scroll offset
    for speaker, message in dialogues:
        wrapped_lines = auto_wrap(f"{speaker}: {message}", font, width - 20)
        for line in wrapped_lines:
            if dialogue_y + 20 < y + height and dialogue_y >= y:  # Check if line is within the visible area
                text_surf = font.render(line, True, (0, 0, 0))
                screen.blit(text_surf, (x + 10, dialogue_y))
            dialogue_y += 20

def draw_input_box(screen, input_text, x, y, width, height, color):
    font = pygame.font.SysFont(None, 25)
    pygame.draw.rect(screen, color, (x, y, width, height))
    wrapped_lines = auto_wrap(input_text, font, width - 20)
    input_y = y + 10  # Start position for the input text
    for line in wrapped_lines:
        text_surf = font.render(line, True, (0, 0, 0))
        screen.blit(text_surf, (x + 10, input_y))
        input_y += 20

pygame.init()
pygame.mixer.init() 

#reglage de la musique
set_music(etape_jeu, 0.3)

width, height = 1800, 1000
screen = pygame.display.set_mode((width, height))

interface_width = 500  
interface_height = height
interface_x = width - interface_width
interface_y = 0

interface_bg_color = (255, 255, 255)
interface_image = pygame.image.load('img/interface_img.png')  
interface_image = pygame.transform.scale(interface_image, (interface_width, interface_height))

button_x = interface_x + 50
button_y = 100
button_width = 400
button_height = 50
active_color = (255, 105, 180)
inactive_color = (10, 210, 255)
answer_active_color = (255, 180, 105)
answer_inactive_color = (10, 255, 210)

cat_id = []
colors = {}
for categorie in sql_game.categories():
    cat_id.append(categorie[0])
    colors[categorie[0]] = (categorie[1], categorie[2], categorie[3])

np.random.seed(5)
game_board = np.random.choice(cat_id, size=(main.board_game_height, main.board_game_width))

game = main.new_game()

game_board_width = width - interface_width
cell_width = game_board_width  // game.board_game_width
cell_height = height // game.board_game_height


gamer_sprites = pygame.sprite.Group()
joueurs = []
game_gamers_sprite = game.gamers_sprite()
for gamer in game_gamers_sprite:
    joueurs.append(gamer)
    gamer_sprites.add(gamer)
    gamer.set_position(gamer.y, gamer.x, cell_width, cell_height)
    gamer.set_params(gamer.personnage)

camembert_pink = Element(0, 0, "camembert", "pink")
camembert_green = Element(0, 0, "camembert", "green")
camembert_blue = Element(0, 0, "camembert", "blue")
camembert_yellow = Element(0, 0, "camembert", "yellow")
camembert_purple = Element(0, 0, "camembert", "purple")
camembert_orange = Element(0, 0, "camembert", "orange")

camembert_sprites = pygame.sprite.Group()
camembert_sprites.add(camembert_pink)
camembert_sprites.add(camembert_green)
camembert_sprites.add(camembert_blue)
camembert_sprites.add(camembert_yellow)
camembert_sprites.add(camembert_purple)
camembert_sprites.add(camembert_orange)

fall_one = Element(0, 0, "fall")
fall_two = Element(0, 0, "fall")

fall_sprites = pygame.sprite.Group()
fall_sprites.add(fall_one)
fall_sprites.add(fall_two)

camembert_pink.set_position(2, 11, cell_width, cell_height)
camembert_pink.set_image()

camembert_green.set_position(11, 21, cell_width, cell_height)
camembert_green.set_image()

camembert_blue.set_position(10, 5, cell_width, cell_height)
camembert_blue.set_image()

camembert_yellow.set_position(2, 1, cell_width, cell_height)
camembert_yellow.set_image()

camembert_purple.set_position(7, 12, cell_width, cell_height)
camembert_purple.set_image()

camembert_orange.set_position(2, 20, cell_width, cell_height)
camembert_orange.set_image()

fall_one.set_position(10, 13, cell_width, cell_height)
fall_one.set_image()

fall_two.set_position(3, 13, cell_width, cell_height)
fall_two.set_image()


current_player_index = 0
conversation_open = False
input_text = ""
chat_history_ids = None
conversation_partner = None

# Variables de défilement
scroll_offset = 0
scroll_speed = 20

running = True
while running:
    
    screen.blit(set_image(etape_jeu), (0, 0))
  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN and not conversation_open:
            if event.key == pygame.K_LEFT:
                joueurs[current_player_index].move("left", cell_height, cell_width, game)
            elif event.key == pygame.K_RIGHT:
                joueurs[current_player_index].move("right", cell_height, cell_width, game)
            elif event.key == pygame.K_UP:
                joueurs[current_player_index].move("up", cell_height, cell_width, game)
            elif event.key == pygame.K_DOWN:
                joueurs[current_player_index].move("down", cell_height, cell_width, game)
            joueurs[current_player_index].check_camembert(camembert_sprites)
            joueurs[current_player_index].take_camembert(camembert_sprites, cell_width, cell_height, game, game_board)
            joueurs[current_player_index].check_fall(fall_sprites, gamer_sprites, cell_width, cell_height, game)

    

            if event.key == pygame.K_SPACE:
                current_player_index = (current_player_index + 1) % main.nb_gamers
                joueurs[current_player_index].yell()
                print(f"Passage au joueur {current_player_index + 1}")
        
        for gamer in gamer_sprites:
            if joueurs[current_player_index].id != gamer.id and gamer.id != 2:
                pnj = gamer
                if joueurs[current_player_index].rect.colliderect(pnj.rect):
                    sound_orc = pygame.mixer.Sound('sounds/orc.wav')
                    sound_orc.set_volume(0.2)
                    sound_orc.play()
                    pnj.move("up", cell_height, cell_width, game)
                    print(etape_jeu)

        if event.type == pygame.KEYDOWN and conversation_open:
            if event.key == pygame.K_RETURN:
                response = get_response(input_text, conversation_partner, joueurs[current_player_index])
                conversation_partner.yell()
                input_text = ""
                print(f"{conversation_partner.player_name}: {response}")

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette vers le haut
                scroll_offset = max(scroll_offset - scroll_speed, 0)
            elif event.button == 5:  # Molette vers le bas
                scroll_offset += scroll_speed

    interface_rect = pygame.Rect(interface_x, interface_y, interface_width, interface_height)
    pygame.draw.rect(screen, interface_bg_color, interface_rect)
    screen.blit(interface_image, (interface_x, interface_y))

    button_start_x = 1300  
    button_start_y = 800   
    button_x_ = button_start_x
    button_y_ = button_start_y

    max_buttons_per_row = 4  
    button_count = 0  

    for gamer in gamer_sprites:
        draw_button(screen, gamer.player_name, button_x_, button_y_, 150, button_height, active_color, inactive_color, 25)
        draw_button(screen, f"{gamer.score}    {len(gamer.camembert_part)}/{game.end_game_max_camembert}", button_x_, button_y_ + 50, 150, button_height, active_color, inactive_color, 25)

        button_x_ += 130
        button_count += 1

        if button_count >= max_buttons_per_row:
            button_x_ = button_start_x
            button_y_ += 100  
            button_count = 0
    
    texte_bouton = f"{joueurs[current_player_index].player_name} : Déplacez-vous"
    draw_button(screen, texte_bouton, button_x, button_y, button_width, button_height, active_color, inactive_color, 40)
        
    category_button_y = 550
    category_button_x = 1450
    category_button_width = 200
    category_button_height = 40
    incr_y = 40
    for categorie in sql_game.categories():
        category_color = (categorie[1], categorie[2], categorie[3])
        draw_button(screen, categorie[0], category_button_x, category_button_y, category_button_width, category_button_height, category_color, category_color, 25)
        category_button_y += incr_y

    gamer_sprites.draw(screen)
    gamer_sprites.update()
    
    camembert_sprites.draw(screen)
    camembert_sprites.update()
    
    fall_sprites.draw(screen)
    fall_sprites.update()

    if not conversation_open:
        for i, gamer1 in enumerate(joueurs):
            for j, gamer2 in enumerate(joueurs):
                if i != j and are_players_adjacent(gamer1, gamer2):
                    if draw_button(screen, "Dialoguer", 50, 850, 200, 50, active_color, inactive_color, 30):
                        conversation_open = True
                        conversation_partner = gamer2 if current_player_index == i else gamer1

    if conversation_open:
        draw_dialogues(screen, dialogues, 400, 400, 1000, 200, (255, 255, 255), scroll_offset)
        draw_input_box(screen, input_text, 400, 620, 1000, 50, (200, 200, 200))
        if draw_button(screen, "Fermer", 1300, 550, 100, 50, active_color, inactive_color, 30):
            conversation_open = False
    
    # winner = game.victory()

    # if winner is not None:
    #     win_text = f"Le gagnant est {winner.player_name} avec un score de {winner.score}"
    #     print(win_text)
    #     draw_button(screen, win_text, 200, 200, 900, 500, inactive_color, inactive_color, 50)
    #     screen.blit(winner.image, (620, 500))
    #     music = pygame.mixer.music.load('sounds/Benny_Hill_Theme.wav')
    #     pygame.mixer.music.set_volume(0.5)
    #     pygame.mixer.music.play(-1)
    #     pygame.display.flip()
    #     pygame.time.delay(10000)
    #     running = False
    
    pygame.display.flip()

sql_game.end_game(game.id)
for gamer in gamer_sprites:
    sql_game.gamer_end_game(game.id, gamer.id, gamer.score, len(gamer.camembert_part))
import last_game
pygame.quit()
