
chosung_list = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"


def print_code(ch):
    print(f"{ch} => {ord(ch)}")


def print_char(code):
    print(f"{code} => {chr(code)}")


def chosunglize(word: str) -> str:
    result = ""
    for i in word:
        result += str(chosung_list[(ord(i) - 44032) // 588])
    return result


def main():
    print(chosunglize("가나다라마바사아자차카타파하"))


if __name__ == '__main__':
    main()
