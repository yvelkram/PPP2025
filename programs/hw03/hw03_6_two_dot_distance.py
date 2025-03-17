
# 6) 두 지점 사이 거리 구하기
# x1, y1, x2, y2를 각각 입력 받아서 두 지점의 거리를 출력하기

import math

x1 = int(input("x1 : "))
y1 = int(input("y1 : "))
x2 = int(input("x2 : "))
y2 = int(input("y2 : "))

d = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

print(f"두 점, P1({x1, y1}) 과 P2({x2, y2}) 사이의 거리는 {d} 입니다.")
