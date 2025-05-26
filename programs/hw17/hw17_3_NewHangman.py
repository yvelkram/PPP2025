import random
import hw17_1_NewCountDown


game_words = "apple, banana, grape, mango, strawberry, eggplant, potato, watermelon, melon, egg"


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


def print_words(data: list, lives: int) -> None:
    print(f"LIVE {lives}", end="")
    print(" "*5, end="")
    for token in data:
        print(" ", end="")
        if token[0] == 0:
            print(token[1], end="")
        else:
            print("_", end="")
    print("\n")


def print_hangman(lives: int) -> None:
    match lives:
        case 0:
            print(" " * 15 + " \\ o /\n",
                  " " * 15 + " \\|/\n",
                  " " * 15 + "  |\n",
                  " " * 15 + " / \\\n",
                  " " * 15 + "/   \\\n")
        case 1:
            print(" " * 15 + " \\ o /\n",
                  " " * 15 + " \\|/\n",
                  " " * 15 + "  |\n",
                  " " * 15 + " /\n",
                  " " * 15 + "/\n")
        case 2:
            print(" " * 15 + " \\ o /\n",
                  " " * 15 + " \\|/\n",
                  " " * 15 + "  |\n\n\n")
        case 3:
            print(" " * 15 + " \\ o /\n",
                  " " * 15 + " \\|/\n\n\n\n",)
        case 4:
            print(" " * 15 + " \\ o\n",
                  " " * 15 + " \\|\n\n\n\n",)
        case 5:
            print(" " * 15 + "   o\n",
                  " " * 15 + "  |\n\n\n\n", )
        case _:
            print(" " * 15 + "   o\n\n\n\n\n\n")


def check_trial(data: list) -> bool:
    trial = input(" > ")[0]

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
        print_hangman(lives)
        print_words(data, lives)

        if lives <= 0:
            print("정답을 맞추지 못했습니다!")
            return False

        if not check_trial(data):
            lives -= 1

        if check_game_end(data):
            print_words(data, lives)
            return True


def main() -> None:
    words = setup(game_words)
    game(words)



if __name__ == '__main__':
    main()
