
# // 몫 - % 나머지

temp_c = int(input("온도를 입력하시오."))
temp_f = (temp_c * 1.8) + 32
print(f"{temp_c} C => {temp_f} F")


weight = int(input("몸무게는? : "))
height = int(input("키는? : "))

BMI = weight / ((height / 100) ** 2)

print(f"키 {height}cm에 몸무게 {weight}kg이면 BMI 지수는 {BMI} 입니다.")
