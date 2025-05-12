
def int_append(x: any, data: list) -> str:
    try:
        data.append(int(x))
    except ValueError:
        return f"converting to int failed : {x}"
    return f"int(x) = {int(x)}"


def average(data: list) -> float:
    if not len(data):
        return 0

    total = 0
    for i in data:
        total += i

    return total / len(data)


def main() -> None:
    number_list = []

    while 1:
        x = input("X=? ")
        if x == "-1":
            break
        else:
            int_append(x, number_list)

    print(f"입력된 값은 {number_list} 입니다. ", end="")
    print(f"총 {len(number_list)}개의 자연수가 입력되었고, 평균은 {average(number_list):0.1f}입니다.")


if __name__ == '__main__':
    main()
