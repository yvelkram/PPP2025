# 2)
# 구구단 문제를 제출하고, 정답 개수를 체크해서 점수를 출력하시오.
import random


def input_vaildator(expected_type: str, input_string="") -> int or float:
    while 1:
        a = input(input_string)

        if expected_type == "int":
            try:
                int(a)
            except ValueError:
                pass
            else:
                return int(a)
        elif expected_type == "float":
            try:
                float(a)
            except ValueError:
                pass
            else:
                return float(a)
        else:
            print(f"not a implemented type! : {expected_type}")


def problem(n: int) -> bool:
    a = random.randint(1, 9)
    b = random.randint(1, 9)

    print(f"Q{n} : {a} x {b} = ", end="")
    answer = input_vaildator("int")

    if answer == a * b:
        return True
    else:
        return False


def main() -> None:
    score = 0
    total_questions_number = 5

    print(f"총 {total_questions_number}개의 문제가 출제됩니다!")

    for i in range(total_questions_number):
        is_correct = problem(i + 1)
        if is_correct:
            score += 1

    print(f"맞힌 문제는 {score}개이고, 점수는 {(score / total_questions_number) * 100:0.0f}점 입니다.")


if __name__ == '__main__':
    main()
