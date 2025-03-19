
# 1) 과제#03의 BMI 계산결과에 따라 아래 텍스트를 참고하여, 비만 정도를 표시하시오.
# 2020년 비만 진료지침에서는 체질량지수(BMI)
# △23~24.9kg/㎡를 비만 전단계
# △25~29.9kg/㎡를 1단계 비만
# △30~34.9kg/㎡를 2단계 비만
# △35kg/㎡ 이상을 3단계 비만으로 정의했다.

import math

weight = int(input("몸무게는? (kg) : "))
height = int(input("키는? (cm) : "))

bmi = weight / math.pow(height / 100, 2)

if bmi < 23:
    print("비만이 아닙니다.")
elif bmi < 25:
    print("비만 전단계 입니다.")
elif bmi < 30:
    print("1단계 비만입니다.")
elif bmi < 35:
    print("2단계 비만입니다.")
else:
    print("3단계 비만입니다.")
