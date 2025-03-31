
# 4. 숫자 n이 주어졌을 때, 1부터 n까지의 합을 구하시오. 함수명은 sum_n(n)


def sum_n(n):
    total = 0
    for i in range(1, n + 1):
        total += i

    print(f"{1} 부터 {n} 까지의 합은 {total} 입니다.")
    return total


def main():
    sum_n(100)


if __name__ == '__main__':
    main()
