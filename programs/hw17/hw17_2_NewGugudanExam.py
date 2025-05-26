import tkinter
from tkinter import simpledialog
from tkinter import messagebox
import random


def problem(n: int) -> bool:
    a = random.randint(1, 9)
    b = random.randint(1, 9)

    answer = simpledialog.askinteger(title=str(n), prompt=f"Q{n} : {a} x {b} = ")

    if answer == a * b:
        return True
    else:
        return False


def main() -> None:
    title = "Gugudan Exam"

    score = 0
    total_questions_number = 5

    messagebox.showinfo(title=title,
                        message=f"총 {total_questions_number}개의 문제가 출제됩니다!")

    for i in range(total_questions_number):
        is_correct = problem(i + 1)
        if is_correct:
            score += 1

    messagebox.showinfo(title=title,
                        message=f"맞힌 문제는 {score}개이고, 점수는 {(score / total_questions_number) * 100:0.0f}점 입니다.")


if __name__ == '__main__':
    main()
