
# 2. 숫자를 입력받아, 해당하는 구구단을 출력하는 함수 gugudan(dan)를 만드시오.


def gugudan(dan):
    print(f"{dan}단 입니다.")
    for i in range(1, 10):
        print(f"{dan} x {i} = {dan * i}")


def main():
    gugudan(250)


if __name__ == '__main__':
    main()
