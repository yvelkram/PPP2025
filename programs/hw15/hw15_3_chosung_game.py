# 3) 초성 게임을 완성하시오.
# 유니코드를 이용하여, 주어진 단어 뭉치에서 단어를 하나 선택하고, 초성을 제시한다.
# 사용자는 주어진 초성을 보고 주어진 단어를 맞추는 게임을 구현한다.

import random

game_text = "사과, 망고, 바나나, 수박, 자두, 복숭아, 딸기, 토마토, 자몽, 블루베리, 산딸기, 포도, 청포도,   ,    참외"
chosung_list = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"


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


def chosunglize(word: str) -> str:
    result = ""
    for i in word:
        result += str(chosung_list[(ord(i) - 44032) // 588])
    return result


def game_stage(words: list[str]) -> int:
    score = 10
    solution = random.choice(words)
    question = chosunglize(solution)

    print(f"문제 : [ {question} ]\n\t원래의 단어는 무엇입니까?")
    while 1:
        answer = input("> ")

        if answer == solution:
            print("정답입니다!")
            break
        else:
            print("오답입니다!")
            score -= 1

        if score <= 0:
            print(f"정답을 맞추지 못했습니다. 정답은 {solution} 입니다.")

    return score


def game_main(words: list[str]) -> None:
    score = 0
    count = 0

    while 1:
        if not count:
            print("시작(s) 를 입력하여 초성퀴즈를 시작하세요!")
        else:
            print(f"현재스코어 : {score}점 | 정답률 : {(score / count) * 10:0.2f}%")

        print(f"퇴장(q) / 초기화(r) / 시작하려면 엔터를 누르세요")
        command = input(">> ")
        if command in ["q", "퇴장", "ㅌㅈ", "ㅌ"]:
            break
        elif command in [""]:
            score += game_stage(words)
            count += 1
        elif command in ["r", "초기화", "리셋", "ㅊㄱㅎ", "ㅊ"]:
            score = 0
            count = 0
        else:
            continue


def main():
    game_main(setup(game_text))


if __name__ == '__main__':
    main()
