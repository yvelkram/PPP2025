
# 2. 1-n까지 리스트를 돌려주는 함수를 만드시오. 함수는 get_range_list(n)


def get_range_list(n):
    result = []
    for i in range(1, n+1, 1):
        result.append(i)
    return result


def main():
    a = get_range_list(10)[:]
    print(a)


if __name__ == '__main__':
    main()
