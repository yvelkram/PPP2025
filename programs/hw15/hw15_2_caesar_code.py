# 2) ASCII 코드를 이용하여 카이사르 암호(Caesar cipher)를 구현하시오.
# 카이사르 암호는 그림과 같이 각 알파벳을 일정한 거리만큼 밀어서 다른 알파벳으로 대치 하는 방법으로 3칸을 옮겼을 때, 오른쪽 아래 그림과 같다.


def shift_char(char: str, shift: int) -> str:
    # single character convert

    code = ord(char)
    if 65 <= code <= 90:  # abcd case
        code += shift
        if code < 65:  # underflow
            code += 23
        elif code > 90:  # overflow
            code -= 23

    elif 97 <= code <= 122:  # ABCD case
        code += shift
        if code < 97:  # underflow
            code += 23
        elif code > 122:  # overflow
            code -= 23

    return chr(code)


def caesar_encode(text: str, shift: int = 3) -> str:
    result = ""

    # reconstruct encoded/decoded character
    for char in text:
        result += shift_char(char, shift)
    return result


def caesar_decode(text: str, shift: int = 3) -> str:
    return caesar_encode(text, -shift)


def main():
    print(caesar_encode("hello, world!"))
    print(caesar_encode("hello, world!", 10))
    print(caesar_decode("khoor, zruog!"))
    print(caesar_decode("rovvy, jyevn!", 10))


if __name__ == '__main__':
    main()
