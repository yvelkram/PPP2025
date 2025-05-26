import tkinter
from tkinter import simpledialog
from tkinter import messagebox
import random


game_words = "apple, banana, grape, mango, strawberry, eggplant, potato, watermelon, melon, egg"
title = "Hangman Game"


def setup(words: str) -> list[str]:
    result = []
    word = ""
    for char in words:
        if char not in [",", " ", "\n"]:
            word += char
        elif word != "":
            result.append(word)
            word = ""
    result.append(word)

    return result


def print_words(data: list, lives: int) -> str:
    s = ""

    s += f"LIVE {lives}"
    s += " "*5

    for token in data:
        s += " "
        if token[0] == 0:
            s += str(token[1])
        else:
            s += "_"
    s += "\n"

    return s


def print_hangman(lives: int, offset=15) -> str:
    s = ""
    match lives:
        case 0:
            s += " " * offset + "\\ o /\n"
            s += " " * offset + " \\|/\n"
            s += " " * offset + "  |\n"
            s += " " * offset + " / \\\n"
            s += " " * offset + "/   \\\n"
        case 1:
            s += " " * offset + "\\ o /\n"
            s += " " * offset + " \\|/\n"
            s += " " * offset + "  |\n"
            s += " " * offset + " /\n"
            s += " " * offset + "/\n"
        case 2:
            s += " " * offset + "\\ o /\n"
            s += " " * offset + " \\|/\n"
            s += " " * offset + "  |\n\n\n"
        case 3:
            s += " " * offset + "\\ o /\n"
            s += " " * offset + " \\|/\n\n\n\n"
        case 4:
            s += " " * offset + "\\ o\n"
            s += " " * offset + " \\|\n\n\n\n"
        case 5:
            s += " " * offset + "   o\n"
            s += " " * offset + "  |\n\n\n\n"
        case _:
            s += " " * offset + "   o\n\n\n\n\n\n"

    return s


def check_trial(data: list, lives: int) -> bool:
    trial = simpledialog.askstring(title=title,
                                   prompt=print_hangman(lives) + print_words(data, lives))

    answer = []
    for n, i in enumerate(data):
        if trial == i[1]:
            answer.append(n)

    if len(answer) == 0:
        return False

    for i in answer:
        data[i][0] = 0

    return True


def check_game_end(data: list) -> bool:
    test = 0
    for token in data:
        test += token[0]

    if test == 0:
        return True
    else:
        return False


def game(words: list[str]) -> bool:
    data = []
    lives = 5

    for i in random.choice(words):
        data.append([1, i])

    while 1:
        if lives <= 0:
            messagebox.showinfo(title=title,
                                message="정답을 맞추지 못했습니다!\n" + print_hangman(lives) + print_words(data, lives))
            return False

        if not check_trial(data, lives):
            lives -= 1

        if check_game_end(data):
            messagebox.showinfo(title=title,
                                message=print_hangman(lives) + print_words(data, lives))
            return True


def main() -> None:
    words = setup(game_words)
    game(words)


if __name__ == '__main__':
    main()
