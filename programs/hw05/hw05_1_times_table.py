
# 1. 숫자를 입력받아, 입력받은 숫자의 구구단을 출력하시오.

n = int(input("몇단을 출력합니까? : "))

print(f"{n}단 입니다.")
for i in range(1, 10):
    print(f"{n} x {i} = {n * i}")
