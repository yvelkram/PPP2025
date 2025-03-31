
# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255
# break, continue

def gugudan(dan):
    print(f"{dan}단 입니다.")
    for i in range(1, 10):
        print(f"{dan} x {i} = {dan * i}")


def largest(a, b, c, d):
    if a > b:
        if a > c:
            if a > d:
                return a
            return d
        else:
            if c > d:
                return c
            return d
    else:
        if b > c:
            if b > d:
                return b
            return d
        else:
            if c > d:
                return c
            return d



def main():
    x1 = 4
    x2 = 5
    x3 = 6
    x4 = 7
    largest_num = largest(x1, x2, x3, x4)
    print(f"가장 큰 수는 {largest_num}입니다.")


if __name__ == '__main__':
    main()
