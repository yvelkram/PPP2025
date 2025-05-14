# 1) ASCII 코드를 이용하여 입력받은 문자열을 대문자는 소문자로, 소문자는 대문자로 바꾸시오.


def toggle_text(text: str) -> str:
    code = ord(text)
    if 65 <= code <= 90:
        return chr(code + 32)
    elif 97 <= code <= 122:
        return chr(code - 32)
    else:
        print(f"Not a togglable text : {text}")
        return ""


def main():
    print(toggle_text("x"))


if __name__ == '__main__':
    main()
