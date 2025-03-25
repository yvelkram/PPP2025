
# 1부터 10까지 출력하시오.
for i in range(1, 11):
    print(i)
print("-" * 50)

# 1부터 10까지 합계를 구하시오.
total = 0
for i in range(1, 11):
    total += i
print(total)
print("-" * 50)

# 1부터 100까지 합계를 구하시오.
total = 0
for i in range(1, 101):
    total += i
print(total)
print("-" * 50)

# 구구단 2단을 출력하시오.
print(f"2단 입니다.")
for i in range(1, 10):
    print(f"2 x {i} = {2 * i}")
print("-" * 50)

# 1부터 250까지 짝수의 합은?
total = 0
for i in range(1, 251):
    if i % 2 == 0:
        total += i
print(total)
print("-" * 50)
