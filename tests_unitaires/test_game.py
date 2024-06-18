import pytest 
import datetime
from gamers import Gamer
from unittest.mock import patch, MagicMock
import pygame



def test_creation_personnage(gamer_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    pnj = gamer_factory(x=0, y=0, id=2, player_name="PNJ", personnage=1)

    assert gamer is not None
    assert gamer.id == 1
    assert gamer.player_name == "Player1"
    assert gamer.x == 0
    assert gamer.y == 0
    assert gamer.personnage == 2
    assert pnj is not None
    assert pnj.id == 2
    assert pnj.player_name == "PNJ"
    assert pnj.x == 0
    assert pnj.y == 0
    assert pnj.personnage == 1


@patch('pygame.mixer.Sound', autospec=True)
def test_move_gamer(mock_sound, gamer_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    game_mock = MagicMock()
    game_mock.board_game_height = 10
    game_mock.board_game_width = 10
    game_mock.gamers = [gamer]

    # Move right
    gamer.move("right", 10, 10, game_mock)
    assert gamer.x == 1 and gamer.y == 0

    # Move down
    gamer.move("down", 10, 10, game_mock)
    assert gamer.x == 1 and gamer.y == 1

    # Move left
    gamer.move("left", 10, 10, game_mock)
    assert gamer.x == 0 and gamer.y == 1

    # Move up
    gamer.move("up", 10, 10, game_mock)
    assert gamer.x == 0 and gamer.y == 0


@patch('pygame.mixer.Sound', autospec=True)
def test_gamer_yell(mock_sound, gamer_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    gamer.yell()
    mock_sound.assert_called_once()

def test_check_camembert_false(gamer_factory, camembert_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    camembert = camembert_factory(x=0, y=0,name_element="camembert", color="blue")

    camembert_sprites = pygame.sprite.Group()
    camembert_sprites.add(camembert)

    assert gamer.check_camembert(camembert_sprites) == True

    camembert.rect.x = 100  # Move camembert out of collision
    camembert.rect.y = 100
    assert gamer.check_camembert(camembert_sprites) == False


def test_check_camembert_true(gamer_factory, camembert_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    camembert = camembert_factory(x=0, y=0,name_element="camembert", color="blue")

    camembert_sprites = pygame.sprite.Group()
    camembert_sprites.add(camembert)

    assert gamer.check_camembert(camembert_sprites) == True
    assert gamer.check_camembert(camembert_sprites) == True


@patch('pygame.mixer.Sound', autospec=True)
def test_take_camembert(mock_sound, gamer_factory, camembert_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    camembert = camembert_factory(x=0, y=0,name_element= "camembert", color="blue")
    
    # Mock the color_question attribute
    camembert.color_question = "blue"

    camembert_sprites = pygame.sprite.Group()
    camembert_sprites.add(camembert)

    game_mock = MagicMock()
    game_mock.camembert_question_points = 50
    game_mock.board_game_height = 10
    game_mock.board_game_width = 10
    game_board = [["blue"] * 10] * 10

    gamer.take_camembert(camembert_sprites, 10, 10, game_mock, game_board)

    assert gamer.score == 50
    assert "blue" in gamer.camembert_part
    assert camembert not in camembert_sprites

    # Check that a new camembert is created
    assert len(camembert_sprites) == 1
    new_camembert = camembert_sprites.sprites()[0]
    assert new_camembert.color == "blue"

@patch('pygame.mixer.Sound', autospec=True)
def test_check_fall(mock_sound, gamer_factory, fall_factory):
    gamer = gamer_factory(x=0, y=0, id=1, player_name="Player1", personnage=2)
    fall_element = fall_factory(x=0, y=0, name_element="fall")

    fall_sprites = pygame.sprite.Group()
    fall_sprites.add(fall_element)

    gamers_sprite = pygame.sprite.Group()
    gamers_sprite.add(gamer)

    game_mock = MagicMock()
    game_mock.board_game_height = 10
    game_mock.board_game_width = 10
    game_mock.hole_points = -10

    gamer.check_fall(fall_sprites, gamers_sprite, 10, 10, game_mock)

    assert gamer.score == -10
    mock_sound.assert_called()
    # Check if the gamer is repositioned on the board
    assert not (gamer.x == 0 and gamer.y == 0)  # Ensure gamer has moved




    