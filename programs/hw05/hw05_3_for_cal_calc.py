
# 3. 칼로리 계산 프로그램(과제#04-03)를 수정하여, 총 칼로리를 계산하시오.
# (반복문, 사전 활용)

calories = {"한라봉": 50 / 100, "딸기": 34 / 100, "바나나": 77 / 100}

eat = {}
total_gram = 0
for name in calories:
    gram = int(input(f"다음 과일을 얼만큼 드셨습니까? [{name}]  (g) : "))
    total_gram += gram
    eat[name] = gram

total_calorie = 0
for cal in calories:
    total_calorie += calories[cal] * eat[cal]

print(f"과일을 총 {total_gram}g 드셨으며, 칼로리는 총 {total_calorie}kcal 입니다.")

