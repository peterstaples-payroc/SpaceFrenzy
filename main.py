import os
from SpaceFrenzyEngine import SpaceFrenzyEngine


main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_game():
    engine = SpaceFrenzyEngine(main_dir)
    engine.start()


if __name__ == '__main__':
    load_game()
