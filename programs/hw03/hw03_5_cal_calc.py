
# 5) 칼로리 구하기 (과일마다 섭취 g를 입력받아서 칼로리 출력하기)
# (https://various.foodsafetykorea.go.kr/nutrient/)
# 한라봉 50 kcal/100g
# 딸기(설향) 34 kcal/100g
# 바나나 77 kcal/100g

cal_hallabong = 50 / 100
cal_strawberry = 34 / 100
cal_banana = 77 / 100

eat_hallabong = int(input("한라봉을 얼만큼 드셨습니까? (g) : "))
eat_strawberry = int(input("딸기를 얼만큼 드셨습니까? (g) : "))
eat_banana = int(input("바나나를 얼만큼 드셨습니까? (g) : "))

total_gram = eat_hallabong + eat_strawberry + eat_banana
calorie = eat_hallabong * cal_hallabong + eat_strawberry * cal_strawberry + eat_banana * cal_banana

print(f"과일을 총 {total_gram}g 드셨으며, 칼로리는 총 {calorie}kcal 입니다.")
