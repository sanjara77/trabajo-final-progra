
from interfaz_usuario import DotsAndBoxesController


def main():
    game = DotsAndBoxesController(size=4, player_time=60)
    game.start()


if __name__ == "__main__":
    main()
