
# 2) 실습02/실습03 완성하기 – BMI를 구하기 (input 이용, math 이용)

import math

weight = int(input("몸무게는? : "))
height = int(input("키는? : "))

BMI = weight / math.pow(height / 100, 2)

print(f"키 {height}cm에 몸무게 {weight}kg이면 BMI 지수는 {BMI} 입니다.")
