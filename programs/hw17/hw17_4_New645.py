import random
import hw17_2_NewGugudanExam


def extract_number(number_list: list[int]) -> None:
    if len(number_list) >= 45:
        print("이미 모든 숫자를 추출했습니다.")
        return

    while 1:
        new_number = random.randint(1, 45)
        if not new_number in number_list:
            number_list.append(new_number)
            break


def make_numbers(size = 7) -> list[int]:
    number_list = []

    for i in range(size):
        extract_number(number_list)

    return number_list


def main() -> None:
    n = hw17_2_NewGugudanExam.input_vaildator("int", "몇회 추출하실겁니까? > ")

    for i in range(n):
        nums = make_numbers()
        print(f"{i+1:3}회차 예상번호 : [{nums[0]:2} {nums[1]:2} {nums[2]:2} {nums[3]:2} {nums[4]:2} {nums[5]:2}], ", end="")
        print(f"보너스 번호는 [{nums[6]:2}]")


if __name__ == '__main__':
    main()
