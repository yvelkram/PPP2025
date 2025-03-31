
def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text} \033[38;2;255;255;255m"


def minmax(nums_raw):
    nums = [int(x) for x in nums_raw.split(", ")]

    largest_num = nums[0]
    smolest_num = nums[0]
    for i in nums:
        if i > largest_num:
            largest_num = i
        if i < smolest_num:
            smolest_num = i

    return largest_num, smolest_num


def main():
    a = "1, 20, 3, 40, 5, 6, 9, 13, -20, 0, 5, 41"
    maximum, minimum = minmax(a)
    print(f"가장 큰 수는 {maximum} 이고, 가장 작은 수는 {minimum} 입니다!")


if __name__ == '__main__':
    main()
