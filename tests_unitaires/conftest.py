from gamers import Gamer, Element
import pytest
import pygame

@pytest.fixture
def gamer_factory():
    def make_gamer(x, y, id, player_name, personnage):
        gamer = Gamer(x, y, id, player_name, personnage) 
        return gamer
    return make_gamer

@pytest.fixture
def camembert_factory():
    def make_camembert(x, y, name_element, color):
        camembert = Element(x, y, name_element, color)
        return camembert
    return make_camembert

@pytest.fixture
def fall_factory():
    def make_fall(x, y, name_element):
        fall = Element(x, y, name_element)
        return fall
    return make_fall

@pytest.fixture(scope='module', autouse=True)
def pygame_setup():
    pygame.init()
    pygame.mixer.init()
    yield
    pygame.quit()