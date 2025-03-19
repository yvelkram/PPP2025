
# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255

"""import math

x1 = int(input("x1 : "))
y1 = int(input("y1 : "))
x2 = int(input("x2 : "))
y2 = int(input("y2 : "))

d = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

if d <= 1:
    print("두 점이 너무 가깝습니다.")"""


a = int(input("> "))

if (a % 2) == 0:
    print(f"{a}는 짝수입니다.")
else:
    print(f"{a}는 홀수입니다.")

text = "Hello, World!"

print(len(text))
print(text.lower())
print(text.upper())
print("=" * 30)
print(text[0:3])
print(text[-2:])

te = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
print(te[2:6])
