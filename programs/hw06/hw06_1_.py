
# 1. 칼로리 계산 프로그램(과제#04-03)를 수정하여, 총 칼로리를 계산하시오.
# (반복문, 사전 활용)


def calc_cal(grams):
    calories = {"한라봉": 50 / 100, "딸기": 34 / 100, "바나나": 77 / 100}

    eat = {}
    total_gram = 0
    for name in calories:
        total_gram += grams[0]
        eat[name] = grams[0]

    total_calorie = 0
    for name in calories:
        total_calorie += calories[name] * eat[name]

    for name in eat:
        print(f"[{name}] : {eat[name]}g, {eat[name] * calories[name]:,.1f}kcal")
    print(f"과일을 총 {total_gram:,}g 드셨으며, 칼로리는 총 {total_calorie:,.1f}kcal 입니다.")


def main():
    calc_cal([150, 200, 100])


if __name__ == '__main__':
    main()
