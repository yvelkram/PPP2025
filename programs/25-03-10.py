# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255
# break, continue


def gugudan(dan = 5):
    for i in range(1, 10):
        print(f"{dan} * {i} = {dan * i}")


def main():
    gugudan()


if __name__ == '__main__':
    main()
