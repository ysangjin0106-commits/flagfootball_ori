# Flag Football Manager - 메인 진입점
import pygame
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Flag Football Manager")
    clock = pygame.time.Clock()

    game = Game(screen)
    game.run(clock)

    pygame.quit()

if __name__ == "__main__":
    main()
