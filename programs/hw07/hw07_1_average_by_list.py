
# 1. 숫자 리스트를 매개변수로 받아서 평균을 구하는 함수를 완성하시오. 함수는 average(nums)


def average(nums):
    total = 0
    for i in nums:
        total += int(i)
    return total / len(nums)


def main():
    x = [1, 2, 3, 4, 5]
    mean = average(x)

    print(f"모든 숫자의 평균은 {mean:0.2f} 입니다.")


if __name__ == '__main__':
    main()
