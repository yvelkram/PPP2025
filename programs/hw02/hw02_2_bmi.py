
# 2) 키와 몸무게가 임의로 주어졌을 때 BMI를 구하시오.

weight = 60
height = 170
BMI = weight / ((height / 100) ** 2)
print("키 {}cm에 몸무게 {}kg이면 BMI 지수는 {} 입니다.".format(height, weight, BMI))
