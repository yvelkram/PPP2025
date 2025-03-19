
# 3) 과제#03에서 칼로리 계산 프로그램을 사전형(딕셔너리)를 이용하여 구현하시오

calories = {"한라봉": 50, "딸기": 34, "바나나": 77}

eat_hallabong = int(input("한라봉을 얼만큼 드셨습니까? (g) : "))
eat_strawberry = int(input("딸기를 얼만큼 드셨습니까? (g) : "))
eat_banana = int(input("바나나를 얼만큼 드셨습니까? (g) : "))

total_gram = eat_hallabong + eat_strawberry + eat_banana
calorie = (eat_hallabong * calories["한라봉"] / 100
           + eat_strawberry * calories["딸기"] / 100
           + eat_banana * calories["바나나"] / 100)

print(f"과일을 총 {total_gram}g 드셨으며, 칼로리는 총 {calorie}kcal 입니다.")
