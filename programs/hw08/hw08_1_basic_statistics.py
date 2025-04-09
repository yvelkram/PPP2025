#수업시간에 같이 한 예제처럼, 숫자가 여러 줄에 걸쳐서 저장되어 있는 경우, 각 숫자를 읽어와서,
# 1) 총 숫자의 개수,
# 2) 주어진 숫자의 평균,
# 3) 주어진 숫자의 최댓값,
# 4) 주어진 숫자의 최솟값,
# 5) 중앙값을 출력하시오.


def read_text(filename):
    lines = open(filename).readlines()
    result = ""
    for ln in lines:
        ln = ln.replace("\n", " ")
        result += ln

    return result


def text2list(t):
    if t == "" or t.strip() == "":
        print("empty text input!")
        return []

    result = []
    for i in t.split(" "):
        if i == "":
            continue
        result.append(int(i))

    if len(result) == 0:
        print("invalid text input!")
        return []
    return result


def average(n_list):
    if len(n_list) == 0:
        print("empty list input!")
        return 0

    return sum(n_list) / len(n_list)


def median(n_list):
    if len(n_list) == 0:
        print("empty list input!")
        return 0
    elif len(n_list) <= 1:
        print("list is too short!")
        return n_list[0]

    sorted_list = sorted(n_list)

    # 짝수일때 : 가운데 2개 평균
    if len(sorted_list) % 2 == 0:
        a = sorted_list[int(len(sorted_list) / 2) - 1]
        b = sorted_list[int(len(sorted_list) / 2)]
        return (a + b) / 2
    # 홀수일때 : 그냥 가운데값
    else:
        return sorted_list[int(len(sorted_list) / 2)]


def maximum(n_list):
    if len(n_list) == 0:
        print("empty list input!")
        return 0

    a = n_list[0]
    for i in n_list:
        if a < i:
            a = i
    return a


def minimum(n_list):
    if len(n_list) == 0:
        print("empty list input!")
        return 0

    a = n_list[0]
    for i in n_list:
        if a > i:
            a = i
    return a


def main():
    nums = text2list(read_text("../../data/hw08/numbers0.txt"))

    print(f"총 숫자의 개수 : {len(nums)}")
    print(f"주어진 숫자의 평균 : {average(nums):0.1f}")
    print(f"주어진 숫자의 최댓값 : {maximum(nums)}")
    print(f"주어진 숫자의 최솟값 : {minimum(nums)}")
    print(f"주어진 숫자의 중앙값 : {median(nums)}")


if __name__ == '__main__':
    main()
