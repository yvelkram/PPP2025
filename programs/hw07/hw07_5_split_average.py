
# 5. 1번과제에서 만든 함수를 이용하며, 메인에서 split()함수를 이용하여 여러 값을 한줄로 입력 받아
# 평균을 출력할 수 있는 프로그램을 완성하시오.


import hw07_1_average_by_list


def main():
    a = "1 2 3 4 5"
    mean = hw07_1_average_by_list.average(a.split(" "))

    print(f"모든 숫자의 평균은 {mean:0.2f} 입니다.")


if __name__ == '__main__':
    main()
